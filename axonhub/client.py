from __future__ import annotations

from urllib.parse import urlparse

import requests

from axonhub.errors import AxonHubAPIError, AxonHubConfigurationError


class AxonHubClient:
    def __init__(
        self,
        endpoint_url: str,
        api_key: str,
        timeout: float = 60,
        session: requests.Session | None = None,
    ) -> None:
        self.endpoint_url = self._normalize_endpoint_url(endpoint_url)
        self.api_key = self._normalize_api_key(api_key)
        self.timeout = timeout
        self._session = session or requests.Session()

    def list_models(self, include: str = "all") -> dict:
        payload = self._request("GET", "/models", params={"include": include})
        if isinstance(payload, list):
            return {"data": payload}
        if not isinstance(payload, dict):
            raise AxonHubAPIError("AxonHub models response must be a JSON object or array")
        data = payload.get("data")
        if data is not None and not isinstance(data, list):
            raise AxonHubAPIError("AxonHub models response field 'data' must be an array")
        return payload

    @classmethod
    def _normalize_endpoint_url(cls, endpoint_url: str) -> str:
        value = (endpoint_url or "").strip().rstrip("/")
        if not value:
            raise AxonHubConfigurationError("AxonHub endpoint URL is required")

        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise AxonHubConfigurationError(
                "AxonHub endpoint URL must include http(s) scheme and host"
            )

        if parsed.path.rstrip("/").endswith("/v1"):
            return value
        return f"{value}/v1"

    @staticmethod
    def _normalize_api_key(api_key: str) -> str:
        value = (api_key or "").strip()
        if not value:
            raise AxonHubConfigurationError("AxonHub API key is required")
        return value

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> object:
        url = f"{self.endpoint_url}{path}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._headers(),
                timeout=self.timeout,
                **kwargs,
            )
        except requests.Timeout as exc:
            raise AxonHubAPIError("AxonHub API request timed out") from exc
        except requests.RequestException as exc:
            message = self._redact(str(exc)) or "AxonHub API request failed"
            raise AxonHubAPIError(message) from exc

        if not response.ok:
            raise self._api_error_from_response(response)

        try:
            return response.json()
        except ValueError as exc:
            raise AxonHubAPIError("AxonHub API response is not valid JSON") from exc

    def _api_error_from_response(self, response: requests.Response) -> AxonHubAPIError:
        fallback = f"AxonHub API request failed with status {response.status_code}"
        message = fallback
        error_type = None
        code = None

        try:
            payload = response.json()
        except ValueError:
            payload = None

        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                raw_message = error.get("message")
                if isinstance(raw_message, str) and raw_message.strip():
                    message = raw_message.strip()
                raw_type = error.get("type")
                if isinstance(raw_type, str) and raw_type.strip():
                    error_type = raw_type.strip()
                raw_code = error.get("code")
                if raw_code is not None:
                    code = str(raw_code)
            elif isinstance(error, str) and error.strip():
                message = error.strip()

        return AxonHubAPIError(
            self._redact(message),
            status_code=response.status_code,
            error_type=self._redact(error_type),
            code=self._redact(code),
        )

    def _redact(self, value: str | None) -> str | None:
        if value is None:
            return None
        redacted = value.replace(self.api_key, "<redacted>")
        if "Bearer " in redacted:
            prefix, _, _ = redacted.partition("Bearer ")
            redacted = f"{prefix}Bearer <redacted>"
        return redacted
