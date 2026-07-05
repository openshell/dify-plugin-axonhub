from __future__ import annotations

import requests

from axonhub.client import AxonHubClient
from axonhub.errors import AxonHubAPIError, AxonHubConfigurationError


class FakeResponse:
    def __init__(self, status_code: int, payload: object = None, *, json_error=False):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error
        self.ok = 200 <= status_code < 300

    def json(self):
        if self._json_error:
            raise ValueError("not json")
        return self._payload


class FakeSession:
    def __init__(self, response: FakeResponse | Exception):
        self.response = response
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_normalizes_endpoint_url_without_v1() -> None:
    client = AxonHubClient("https://example.com", "key")

    assert client.endpoint_url == "https://example.com/v1"


def test_normalizes_endpoint_url_with_v1_and_trailing_slash() -> None:
    client = AxonHubClient("https://example.com/v1/", "key")

    assert client.endpoint_url == "https://example.com/v1"


def test_normalizes_endpoint_url_with_deployment_prefix() -> None:
    client = AxonHubClient("https://example.com/axonhub", "key")

    assert client.endpoint_url == "https://example.com/axonhub/v1"


def test_rejects_invalid_endpoint_url() -> None:
    try:
        AxonHubClient("example.com", "key")
    except AxonHubConfigurationError as exc:
        assert "endpoint URL" in str(exc)
    else:
        raise AssertionError("Expected AxonHubConfigurationError")


def test_rejects_empty_api_key() -> None:
    try:
        AxonHubClient("https://example.com", "  ")
    except AxonHubConfigurationError as exc:
        assert "API key" in str(exc)
    else:
        raise AssertionError("Expected AxonHubConfigurationError")


def test_list_models_calls_models_endpoint_with_include_all() -> None:
    session = FakeSession(FakeResponse(200, {"object": "list", "data": [{"id": "m1"}]}))
    client = AxonHubClient("https://example.com", "secret-key", timeout=12, session=session)

    payload = client.list_models()

    assert payload == {"object": "list", "data": [{"id": "m1"}]}
    assert session.calls == [
        {
            "method": "GET",
            "url": "https://example.com/v1/models",
            "headers": {
                "Authorization": "Bearer secret-key",
                "Accept": "application/json",
            },
            "timeout": 12,
            "params": {"include": "all"},
        }
    ]


def test_list_models_wraps_raw_list_response() -> None:
    session = FakeSession(FakeResponse(200, [{"id": "m1"}]))
    client = AxonHubClient("https://example.com", "secret-key", session=session)

    assert client.list_models() == {"data": [{"id": "m1"}]}


def test_openai_style_error_is_parsed_without_leaking_api_key() -> None:
    api_key = "ah-secret-value"
    session = FakeSession(
        FakeResponse(
            401,
            {
                "error": {
                    "message": f"invalid api key {api_key}",
                    "type": "authentication_error",
                    "code": "invalid_api_key",
                }
            },
        )
    )
    client = AxonHubClient("https://example.com", api_key, session=session)

    try:
        client.list_models()
    except AxonHubAPIError as exc:
        text = str(exc)
        assert "<redacted>" in text
        assert api_key not in text
        assert "status=401" in text
        assert "type=authentication_error" in text
        assert "code=invalid_api_key" in text
    else:
        raise AssertionError("Expected AxonHubAPIError")


def test_non_json_error_uses_safe_fallback() -> None:
    session = FakeSession(FakeResponse(500, json_error=True))
    client = AxonHubClient("https://example.com", "secret-key", session=session)

    try:
        client.list_models()
    except AxonHubAPIError as exc:
        assert str(exc) == "AxonHub API request failed with status 500 (status=500)"
    else:
        raise AssertionError("Expected AxonHubAPIError")


def test_timeout_is_mapped_to_api_error() -> None:
    session = FakeSession(requests.Timeout("boom"))
    client = AxonHubClient("https://example.com", "secret-key", session=session)

    try:
        client.list_models()
    except AxonHubAPIError as exc:
        assert str(exc) == "AxonHub API request timed out"
    else:
        raise AssertionError("Expected AxonHubAPIError")
