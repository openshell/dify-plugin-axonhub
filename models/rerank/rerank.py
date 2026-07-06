from __future__ import annotations

from urllib.parse import urljoin

import requests
from dify_plugin.entities.model import ModelType
from dify_plugin.entities.model.rerank import RerankDocument, RerankResult
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from dify_plugin.interfaces.model import rerank_model

from axonhub.client import AxonHubClient
from axonhub.dify_compat import (
    build_client,
    normalize_model_name,
    parse_bool,
    parse_timeout,
    redacted_error_message,
)
from axonhub.errors import AxonHubAPIError, AxonHubConfigurationError
from axonhub.model_schema import get_customizable_model_schema_from_axonhub
from axonhub.tracing import build_tracing_headers


class AxonHubRerankModel(rerank_model.RerankModel):
    model_type = ModelType.RERANK

    def _invoke(
        self,
        model: str,
        credentials: dict,
        query: str,
        docs: list[str],
        score_threshold: float | None = None,
        top_n: int | None = None,
        user: str | None = None,
    ) -> RerankResult:
        endpoint_url = AxonHubClient._normalize_endpoint_url(
            credentials.get("endpoint_url", "")
        )
        api_key = AxonHubClient._normalize_api_key(credentials.get("api_key", ""))
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if parse_bool(credentials.get("enable_tracing"), default=True):
            headers.update(build_tracing_headers(thread_id=user))

        payload = {
            "model": normalize_model_name(model, credentials),
            "query": query,
            "documents": docs,
        }
        if top_n is not None:
            payload["top_n"] = top_n

        try:
            response = requests.post(
                urljoin(f"{endpoint_url}/", "rerank"),
                headers=headers,
                json=payload,
                timeout=parse_timeout(credentials.get("request_timeout")),
            )
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.Timeout) as exc:
            raise InvokeConnectionError("AxonHub rerank request timed out") from exc
        except requests.ConnectionError as exc:
            raise InvokeConnectionError("AxonHub rerank connection failed") from exc
        except requests.RequestException as exc:
            raise InvokeBadRequestError(redacted_error_message(exc, credentials)) from exc

        if response.status_code >= 400:
            self._raise_invoke_error(response, credentials)

        try:
            payload = response.json()
        except ValueError as exc:
            raise InvokeServerUnavailableError(
                "AxonHub rerank response is not valid JSON"
            ) from exc

        return self._to_rerank_result(
            model=model,
            payload=payload,
            docs=docs,
            score_threshold=score_threshold,
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        del model
        try:
            if parse_bool(credentials.get("auto_discovery"), default=True):
                build_client(credentials).list_models(include="all")
                return

            if not credentials.get("endpoint_url"):
                raise AxonHubConfigurationError("AxonHub Base URL is required.")
            if not credentials.get("api_key"):
                raise AxonHubConfigurationError("AxonHub API Key is required.")
        except (AxonHubAPIError, AxonHubConfigurationError) as exc:
            raise CredentialsValidateFailedError(
                redacted_error_message(exc, credentials)
            ) from exc

    def get_customizable_model_schema(self, model: str, credentials: dict):
        return get_customizable_model_schema_from_axonhub(
            model,
            credentials,
            expected_model_type=ModelType.RERANK,
        )

    @property
    def _invoke_error_mapping(self):
        return {InvokeConnectionError: [ConnectionError, TimeoutError]}

    def _to_rerank_result(
        self,
        *,
        model: str,
        payload: object,
        docs: list[str],
        score_threshold: float | None,
    ) -> RerankResult:
        if not isinstance(payload, dict):
            raise InvokeServerUnavailableError("AxonHub rerank response must be a JSON object")

        results = payload.get("results") or payload.get("data")
        if not isinstance(results, list):
            raise InvokeServerUnavailableError("AxonHub rerank response must include results")

        reranked_docs = []
        for item in results:
            if not isinstance(item, dict):
                continue
            index = int(item.get("index", len(reranked_docs)))
            score = item.get("relevance_score", item.get("score", item.get("rerank_score", 0)))
            score = float(score)
            if score_threshold is not None and score < score_threshold:
                continue

            text = docs[index] if 0 <= index < len(docs) else ""
            document = item.get("document")
            if isinstance(document, dict):
                text = str(document.get("text", document.get("content", text)))
            elif isinstance(document, str):
                text = document

            reranked_docs.append(RerankDocument(index=index, text=text, score=score))

        return RerankResult(model=payload.get("model", model), docs=reranked_docs)

    def _raise_invoke_error(self, response: requests.Response, credentials: dict) -> None:
        message = f"AxonHub rerank request failed with status {response.status_code}"
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
