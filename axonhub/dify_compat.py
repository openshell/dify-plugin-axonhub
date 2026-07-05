from __future__ import annotations

from typing import Any

from axonhub.client import AxonHubClient
from axonhub.tracing import build_tracing_headers


def parse_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on", "enable", "enabled", "support", "supported"}:
            return True
        if normalized in {"0", "false", "no", "n", "off", "disable", "disabled", "not_support", "not-supported"}:
            return False
    return bool(value)


def parse_timeout(value: Any, *, default: float = 60) -> float:
    if value in (None, ""):
        return default
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        return default
    return timeout if timeout > 0 else default


def build_client(credentials: dict) -> AxonHubClient:
    return AxonHubClient(
        endpoint_url=credentials.get("endpoint_url", ""),
        api_key=credentials.get("api_key", ""),
        timeout=parse_timeout(credentials.get("request_timeout")),
    )


def normalize_model_name(model: str, credentials: dict) -> str:
    endpoint_model_name = credentials.get("endpoint_model_name")
    if isinstance(endpoint_model_name, str) and endpoint_model_name.strip():
        return endpoint_model_name.strip()
    return model


def to_oai_credentials(
    model: str,
    credentials: dict,
    *,
    user: str | None = None,
    include_tracing: bool = False,
) -> dict:
    normalized = dict(credentials)
    normalized["endpoint_url"] = AxonHubClient._normalize_endpoint_url(
        credentials.get("endpoint_url", "")
    )
    normalized["api_key"] = AxonHubClient._normalize_api_key(
        credentials.get("api_key", "")
    )
    normalized["endpoint_model_name"] = normalize_model_name(model, credentials)

    if include_tracing and parse_bool(credentials.get("enable_tracing"), default=True):
        extra_headers = dict(credentials.get("extra_headers") or {})
        extra_headers.update(build_tracing_headers(thread_id=user))
        normalized["extra_headers"] = extra_headers

    return normalized


def to_llm_credentials(
    model: str,
    credentials: dict,
    *,
    user: str | None = None,
    include_tracing: bool = False,
) -> dict:
    normalized = to_oai_credentials(
        model,
        credentials,
        user=user,
        include_tracing=include_tracing,
    )
    normalized.setdefault("mode", "chat")

    if "function_calling_type" not in normalized:
        normalized["function_calling_type"] = (
            "tool_call" if parse_bool(credentials.get("tool_call_support")) else "no_call"
        )
    if "stream_function_calling" not in normalized and normalized["function_calling_type"] == "tool_call":
        normalized["stream_function_calling"] = "supported"
    vision_support = normalized.get("vision_support")
    if vision_support not in {"support", "not_support"}:
        normalized["vision_support"] = (
            "support" if parse_bool(vision_support) else "not_support"
        )
    return normalized


def redacted_error_message(error: Exception, credentials: dict) -> str:
    message = str(error)
    api_key = credentials.get("api_key")
    if isinstance(api_key, str) and api_key:
        message = message.replace(api_key, "<redacted>")
    if "Bearer " in message:
        prefix, _, _ = message.partition("Bearer ")
        message = f"{prefix}Bearer <redacted>"
    return message
