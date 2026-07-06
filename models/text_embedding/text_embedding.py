from __future__ import annotations

import json

import requests
from dify_plugin.entities.model import EmbeddingInputType, ModelType
from dify_plugin.entities.model.text_embedding import TextEmbeddingResult
from dify_plugin.errors.model import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from dify_plugin.interfaces.model.openai_compatible import text_embedding as oai_embedding

from axonhub.dify_compat import (
    normalize_model_name,
    parse_bool,
    parse_timeout,
    redacted_error_message,
    to_oai_credentials,
)
from axonhub.model_schema import get_customizable_model_schema_from_axonhub
from axonhub.tracing import build_tracing_headers


class AxonHubTextEmbeddingModel(oai_embedding.OAICompatEmbeddingModel):
    model_type = ModelType.TEXT_EMBEDDING

    def _invoke(
        self,
        model: str,
        credentials: dict,
        texts: list[str],
        user: str | None = None,
        input_type: EmbeddingInputType = EmbeddingInputType.DOCUMENT,
    ) -> TextEmbeddingResult:
        del input_type

        normalized = to_oai_credentials(model, credentials)
        endpoint_url = normalized["endpoint_url"]
        api_key = normalized["api_key"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if parse_bool(credentials.get("enable_tracing"), default=True):
            headers.update(build_tracing_headers(thread_id=user))

        context_size = self._get_context_size(model, normalized)
        max_chunks = self._get_max_chunks(model, normalized)
        inputs = []
        used_tokens = 0
        for text in texts:
            num_tokens = self._get_num_tokens_by_gpt2(text)
            if num_tokens >= context_size:
                cutoff = int((len(text) * context_size) // num_tokens)
                inputs.append(text[0:cutoff])
            else:
                inputs.append(text)

        batched_embeddings = []
        for i in range(0, len(inputs), max_chunks):
            payload = {
                "input": inputs[i : i + max_chunks],
                "model": normalize_model_name(model, normalized),
                "encoding_format": "float",
            }
            if user:
                payload["user"] = user
            dimensions = credentials.get("dimensions")
            if dimensions not in (None, ""):
                payload["dimensions"] = int(dimensions)

            response = self._post_embeddings(endpoint_url, headers, payload, credentials)
            response_data = response.json()
            batched_embeddings.extend(data["embedding"] for data in response_data["data"])
            used_tokens += int(response_data.get("usage", {}).get("total_tokens", 0))

        usage = self._calc_response_usage(
            model=model,
            credentials=normalized,
            tokens=used_tokens,
        )
        return TextEmbeddingResult(embeddings=batched_embeddings, usage=usage, model=model)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        return super().validate_credentials(
            model,
            to_oai_credentials(model, credentials),
        )

    def get_customizable_model_schema(self, model: str, credentials: dict):
        return get_customizable_model_schema_from_axonhub(
            model,
            credentials,
            expected_model_type=ModelType.TEXT_EMBEDDING,
        )

    def _post_embeddings(
        self,
        endpoint_url: str,
        headers: dict[str, str],
        payload: dict,
        credentials: dict,
    ) -> requests.Response:
        try:
            response = requests.post(
                f"{endpoint_url}/embeddings",
                headers=headers,
                data=json.dumps(payload),
                timeout=parse_timeout(credentials.get("request_timeout"), default=300),
            )
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.Timeout) as exc:
            raise InvokeConnectionError("AxonHub embedding request timed out") from exc
        except requests.ConnectionError as exc:
            raise InvokeConnectionError("AxonHub embedding connection failed") from exc
        except requests.RequestException as exc:
            raise InvokeBadRequestError(redacted_error_message(exc, credentials)) from exc

        if response.status_code >= 400:
            self._raise_invoke_error(response, credentials)
        try:
            response.json()
        except ValueError as exc:
            raise InvokeServerUnavailableError(
                "AxonHub embedding response is not valid JSON"
            ) from exc
        return response

    def _raise_invoke_error(self, response: requests.Response, credentials: dict) -> None:
        message = f"AxonHub embedding request failed with status {response.status_code}"
        try:
            payload = response.json()
        except ValueError:
            payload = None
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict) and isinstance(error.get("message"), str):
                message = error["message"]
            elif isinstance(error, str):
                message = error
        message = redacted_error_message(Exception(message), credentials)

        if response.status_code in {401, 403}:
            raise InvokeAuthorizationError(message)
        if response.status_code == 429:
            raise InvokeRateLimitError(message)
        if response.status_code >= 500:
            raise InvokeServerUnavailableError(message)
        raise InvokeBadRequestError(message)
