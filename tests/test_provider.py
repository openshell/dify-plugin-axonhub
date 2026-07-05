from __future__ import annotations

from dify_plugin.errors.model import CredentialsValidateFailedError

from axonhub.errors import AxonHubAPIError
import provider.axonhub as provider_module
from provider.axonhub import AxonHubProvider


def provider() -> AxonHubProvider:
    return AxonHubProvider.__new__(AxonHubProvider)


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    def list_models(self, include: str = "all") -> dict:
        self.calls.append(include)
        return {"data": [{"id": "m1"}]}


def test_provider_validates_credentials_with_auto_discovery(monkeypatch) -> None:
    fake_client = FakeClient()
    monkeypatch.setattr(provider_module, "build_client", lambda credentials: fake_client)

    provider().validate_provider_credentials(
        {
            "endpoint_url": "https://example.com",
            "api_key": "secret",
            "auto_discovery": "true",
        }
    )

    assert fake_client.calls == ["all"]


def test_provider_manual_fallback_validates_required_fields() -> None:
    provider().validate_provider_credentials(
        {
            "endpoint_url": "https://example.com",
            "api_key": "secret",
            "auto_discovery": "false",
        }
    )


def test_provider_manual_fallback_rejects_missing_api_key() -> None:
    try:
        provider().validate_provider_credentials(
            {"endpoint_url": "https://example.com", "auto_discovery": "false"}
        )
    except CredentialsValidateFailedError as exc:
        assert "API Key" in str(exc)
    else:
        raise AssertionError("Expected CredentialsValidateFailedError")


def test_provider_validation_redacts_api_key(monkeypatch) -> None:
    api_key = "secret-key"

    def fail(_credentials):
        raise AxonHubAPIError(f"invalid key {api_key}", status_code=401)

    monkeypatch.setattr(provider_module, "build_client", fail)

    try:
        provider().validate_provider_credentials(
            {
                "endpoint_url": "https://example.com",
                "api_key": api_key,
                "auto_discovery": "true",
            }
        )
    except CredentialsValidateFailedError as exc:
        text = str(exc)
        assert api_key not in text
        assert "<redacted>" in text
    else:
        raise AssertionError("Expected CredentialsValidateFailedError")
