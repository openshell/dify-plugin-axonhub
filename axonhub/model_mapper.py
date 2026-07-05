from __future__ import annotations

from typing import Any

from axonhub.errors import AxonHubConfigurationError

_MODEL_TYPE_ALIASES = {
    "chat": "llm",
    "llm": "llm",
    "completion": "llm",
    "text-generation": "llm",
    "text_generation": "llm",
    "embedding": "text-embedding",
    "text-embedding": "text-embedding",
    "text_embedding": "text-embedding",
    "rerank": "rerank",
    "reranker": "rerank",
}

_FEATURE_ALIASES = {
    "vision": "vision",
    "tool_call": "tool_call",
    "tool_calls": "tool_call",
    "function_call": "tool_call",
    "function_calls": "tool_call",
    "reasoning": "reasoning",
    "structured_output": "structured_output",
    "structured_outputs": "structured_output",
}


def map_model_card(model_card: dict) -> dict:
    if not isinstance(model_card, dict):
        raise AxonHubConfigurationError("AxonHub model card must be a dictionary")

    model = _first_string(model_card, "id", "name", "model")
    if not model:
        raise AxonHubConfigurationError("AxonHub model card is missing model id")

    display_name = _first_string(model_card, "name", "label", "id", "model") or model
    description = _string_or_empty(model_card.get("description"))

    return {
        "model": model,
        "display_name": display_name,
        "description": description,
        "model_type": _normalize_model_type(model_card.get("type")),
        "context_size": _optional_int(model_card.get("context_length")),
        "max_tokens_to_sample": _optional_int(model_card.get("max_output_tokens")),
        "features": _normalize_features(model_card.get("capabilities")),
        "pricing": _normalize_pricing(model_card.get("pricing")),
        "raw": model_card,
    }


def map_model_cards(payload: dict | list) -> list[dict]:
    if isinstance(payload, dict):
        data = payload.get("data", [])
    else:
        data = payload
    if not isinstance(data, list):
        raise AxonHubConfigurationError("AxonHub models payload data must be an array")
    return [map_model_card(card) for card in data]


def _normalize_model_type(value: Any) -> str:
    if isinstance(value, str):
        key = value.strip().lower()
        return _MODEL_TYPE_ALIASES.get(key, "llm")
    return "llm"


def _normalize_features(capabilities: Any) -> list[str]:
    features = set()
    if isinstance(capabilities, dict):
        for key, enabled in capabilities.items():
            feature = _FEATURE_ALIASES.get(str(key).strip().lower())
            if feature and bool(enabled):
                features.add(feature)
    elif isinstance(capabilities, (list, tuple, set)):
        for item in capabilities:
            feature = _FEATURE_ALIASES.get(str(item).strip().lower())
            if feature:
                features.add(feature)
    return sorted(features)


def _normalize_pricing(pricing: Any) -> dict:
    if not isinstance(pricing, dict):
        return {}

    normalized = {"raw": pricing}
    unit = pricing.get("unit") or pricing.get("billing_unit")
    if isinstance(unit, str) and unit.strip():
        normalized["unit"] = unit.strip()

    for source_key, target_key in (
        ("input", "input"),
        ("input_price", "input"),
        ("prompt", "input"),
        ("output", "output"),
        ("output_price", "output"),
        ("completion", "output"),
    ):
        if source_key in pricing and target_key not in normalized:
            normalized[target_key] = pricing[source_key]

    return normalized


def _first_string(data: dict, *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _string_or_empty(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    return None
