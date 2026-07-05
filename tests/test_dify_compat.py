from __future__ import annotations

from axonhub.dify_compat import (
    normalize_model_name,
    parse_bool,
    parse_timeout,
    redacted_error_message,
    to_llm_credentials,
    to_oai_credentials,
)


def test_parse_bool_handles_dify_switch_values() -> None:
    assert parse_bool("true") is True
    assert parse_bool("false", default=True) is False
    assert parse_bool("support") is True
    assert parse_bool(None, default=True) is True


def test_parse_timeout_uses_positive_numeric_values() -> None:
    assert parse_timeout("12") == 12
    assert parse_timeout("0") == 60
    assert parse_timeout("bad", default=30) == 30


def test_normalize_model_name_prefers_endpoint_model_name() -> None:
    assert normalize_model_name("dify-name", {"endpoint_model_name": "real-name"}) == "real-name"
    assert normalize_model_name("dify-name", {}) == "dify-name"


def test_to_oai_credentials_normalizes_endpoint_model_and_tracing() -> None:
    credentials = {
        "endpoint_url": "https://example.com/",
        "api_key": " secret ",
        "endpoint_model_name": "real-model",
        "enable_tracing": "true",
    }

    normalized = to_oai_credentials(
        "dify-model",
        credentials,
        user="thread-1",
        include_tracing=True,
    )

    assert normalized["endpoint_url"] == "https://example.com/v1"
    assert normalized["api_key"] == "secret"
    assert normalized["endpoint_model_name"] == "real-model"
    assert normalized["extra_headers"]["AH-Thread-Id"] == "thread-1"
    assert normalized["extra_headers"]["AH-Trace-Id"].startswith("dify-")


def test_to_llm_credentials_sets_openai_compatible_defaults() -> None:
    normalized = to_llm_credentials(
        "model",
        {
            "endpoint_url": "https://example.com",
            "api_key": "secret",
            "tool_call_support": "true",
            "vision_support": "true",
        },
    )

    assert normalized["mode"] == "chat"
    assert normalized["function_calling_type"] == "tool_call"
    assert normalized["stream_function_calling"] == "supported"
    assert normalized["vision_support"] == "support"


def test_redacted_error_message_removes_api_key() -> None:
    message = redacted_error_message(Exception("bad secret-key"), {"api_key": "secret-key"})

    assert message == "bad <redacted>"
