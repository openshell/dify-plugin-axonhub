from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from dify_plugin.entities import I18nObject
from dify_plugin.entities.model import (
    AIModelEntity,
    DefaultParameterName,
    FetchFrom,
    ModelFeature,
    ModelPropertyKey,
    ModelType,
    ParameterRule,
    PriceConfig,
)

from axonhub.dify_compat import build_client, normalize_model_name
from axonhub.errors import AxonHubConfigurationError
from axonhub.model_mapper import map_model_cards

_DEFAULT_CONTEXT_SIZE = {
    ModelType.LLM: 4096,
    ModelType.TEXT_EMBEDDING: 512,
}
_DEFAULT_MAX_OUTPUT_TOKENS = 4096
_DEFAULT_MAX_CHUNKS = 1

_UNIT_ALIASES = {
    "per_1m_tokens": Decimal("0.000001"),
    "per_million_tokens": Decimal("0.000001"),
    "per_1k_tokens": Decimal("0.001"),
    "per_thousand_tokens": Decimal("0.001"),
    "per_token": Decimal("1"),
    "token": Decimal("1"),
}

_FEATURE_MAP = {
    "vision": [ModelFeature.VISION],
    "tool_call": [ModelFeature.MULTI_TOOL_CALL, ModelFeature.STREAM_TOOL_CALL],
    "reasoning": [ModelFeature.AGENT_THOUGHT],
    "structured_output": [ModelFeature.STRUCTURED_OUTPUT],
}

_MODEL_TYPE_VALUES = {
    ModelType.LLM: ModelType.LLM.value,
    ModelType.TEXT_EMBEDDING: ModelType.TEXT_EMBEDDING.value,
    ModelType.RERANK: ModelType.RERANK.value,
}


def get_customizable_model_schema_from_axonhub(
    model: str,
    credentials: dict,
    *,
    expected_model_type: ModelType,
) -> AIModelEntity:
    models = map_model_cards(build_client(credentials).list_models(include="all"))
    endpoint_model_name = normalize_model_name(model, credentials)
    model_card = _find_model_card(models, endpoint_model_name)
    return build_ai_model_entity(
        model_card,
        requested_model=model,
        expected_model_type=expected_model_type,
        display_name=credentials.get("display_name"),
    )


def build_ai_model_entity(
    model_card: dict,
    *,
    requested_model: str | None = None,
    expected_model_type: ModelType,
    display_name: Any = None,
) -> AIModelEntity:
    model_name = requested_model or model_card["model"]
    _validate_model_type(model_card, expected_model_type)

    label = _display_name(display_name) or model_card.get("display_name") or model_name
    return AIModelEntity(
        model=model_name,
        label=I18nObject(en_us=label, zh_hans=label),
        model_type=expected_model_type,
        features=_build_features(model_card.get("features", [])),
        fetch_from=FetchFrom.CUSTOMIZABLE_MODEL,
        model_properties=_build_model_properties(model_card, expected_model_type),
        parameter_rules=_build_parameter_rules(model_card, expected_model_type),
        pricing=_build_price_config(model_card.get("pricing", {})),
    )


def _find_model_card(models: list[dict], model_name: str) -> dict:
    for model_card in models:
        if model_card.get("model") == model_name:
            return model_card
    raise AxonHubConfigurationError(
        f"Model '{model_name}' was not found in AxonHub model discovery response"
    )


def _validate_model_type(model_card: dict, expected_model_type: ModelType) -> None:
    actual = model_card.get("model_type")
    expected = _MODEL_TYPE_VALUES[expected_model_type]
    if actual != expected:
        raise AxonHubConfigurationError(
            f"Model '{model_card.get('model')}' is type '{actual}', expected '{expected}'"
        )


def _display_name(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _build_features(features: list[str]) -> list[ModelFeature] | None:
    mapped = []
    for feature in features:
        for model_feature in _FEATURE_MAP.get(feature, []):
            if model_feature not in mapped:
                mapped.append(model_feature)
    return mapped or None


def _build_model_properties(
    model_card: dict,
    expected_model_type: ModelType,
) -> dict[ModelPropertyKey, Any]:
    if expected_model_type == ModelType.LLM:
        return {
            ModelPropertyKey.MODE: "chat",
            ModelPropertyKey.CONTEXT_SIZE: _positive_int(
                model_card.get("context_size"),
                default=_DEFAULT_CONTEXT_SIZE[ModelType.LLM],
            ),
        }
    if expected_model_type == ModelType.TEXT_EMBEDDING:
        return {
            ModelPropertyKey.CONTEXT_SIZE: _positive_int(
                model_card.get("context_size"),
                default=_DEFAULT_CONTEXT_SIZE[ModelType.TEXT_EMBEDDING],
            ),
            ModelPropertyKey.MAX_CHUNKS: _DEFAULT_MAX_CHUNKS,
        }
    return {}


def _build_parameter_rules(
    model_card: dict,
    expected_model_type: ModelType,
) -> list[ParameterRule]:
    if expected_model_type != ModelType.LLM:
        return []

    max_tokens = _positive_int(
        model_card.get("max_tokens_to_sample"),
        default=_DEFAULT_MAX_OUTPUT_TOKENS,
    )
    default_max_tokens = min(_DEFAULT_MAX_OUTPUT_TOKENS, max_tokens)
    templates = [
        DefaultParameterName.TEMPERATURE,
        DefaultParameterName.TOP_P,
        DefaultParameterName.PRESENCE_PENALTY,
        DefaultParameterName.FREQUENCY_PENALTY,
    ]
    rules = [
        ParameterRule(name=template.value, use_template=template.value)
        for template in templates
    ]
    rules.append(
        ParameterRule(
            name=DefaultParameterName.MAX_TOKENS.value,
            use_template=DefaultParameterName.MAX_TOKENS.value,
            default=default_max_tokens,
            min=1,
            max=max_tokens,
        )
    )
    return rules


def _build_price_config(pricing: dict) -> PriceConfig | None:
    if not pricing:
        return None

    unit = _pricing_unit(pricing.get("unit"))
    input_price = _decimal_or_none(pricing.get("input"))
    output_price = _decimal_or_none(pricing.get("output"))
    if unit is None or input_price is None:
        return None

    return PriceConfig(
        input=input_price,
        output=output_price,
        unit=unit,
        currency=str(pricing.get("currency") or "USD"),
    )


def _pricing_unit(value: Any) -> Decimal | None:
    if isinstance(value, str):
        key = value.strip().lower()
        if key in _UNIT_ALIASES:
            return _UNIT_ALIASES[key]
    return _decimal_or_none(value)


def _decimal_or_none(value: Any) -> Decimal | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _positive_int(value: Any, *, default: int) -> int:
    if isinstance(value, int) and value > 0:
        return value
    return default
