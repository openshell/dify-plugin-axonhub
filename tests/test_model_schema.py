from __future__ import annotations

from decimal import Decimal

from dify_plugin.entities.model import (
    FetchFrom,
    ModelFeature,
    ModelPropertyKey,
    ModelType,
)

from axonhub.errors import AxonHubConfigurationError
from axonhub.model_schema import (
    build_ai_model_entity,
    get_customizable_model_schema_from_axonhub,
)


class FakeClient:
    def __init__(self, payload: object):
        self.payload = payload
        self.calls = []

    def list_models(self, include="all"):
        self.calls.append(include)
        return self.payload


def test_builds_llm_schema_from_model_card() -> None:
    schema = build_ai_model_entity(
        {
            "model": "real-llm",
            "display_name": "Real LLM",
            "model_type": "llm",
            "context_size": 128000,
            "max_tokens_to_sample": 32000,
            "features": ["vision", "tool_call", "reasoning", "structured_output"],
            "pricing": {
                "unit": "per_1m_tokens",
                "input": "3",
                "output": "15",
            },
        },
        requested_model="dify-llm",
        expected_model_type=ModelType.LLM,
    )

    assert schema.model == "dify-llm"
    assert schema.label.en_us == "Real LLM"
    assert schema.model_type == ModelType.LLM
    assert schema.fetch_from == FetchFrom.CUSTOMIZABLE_MODEL
    assert schema.model_properties[ModelPropertyKey.MODE] == "chat"
    assert schema.model_properties[ModelPropertyKey.CONTEXT_SIZE] == 128000
    assert schema.features == [
        ModelFeature.VISION,
        ModelFeature.MULTI_TOOL_CALL,
        ModelFeature.STREAM_TOOL_CALL,
        ModelFeature.AGENT_THOUGHT,
        ModelFeature.STRUCTURED_OUTPUT,
    ]
    max_tokens = next(rule for rule in schema.parameter_rules if rule.name == "max_tokens")
    assert max_tokens.default == 4096
    assert max_tokens.min == 1
    assert max_tokens.max == 32000
    assert schema.pricing is not None
    assert schema.pricing.input == Decimal("3")
    assert schema.pricing.output == Decimal("15")
    assert schema.pricing.unit == Decimal("0.000001")
    assert schema.pricing.currency == "USD"


def test_builds_embedding_schema_with_defaults() -> None:
    schema = build_ai_model_entity(
        {
            "model": "embed",
            "display_name": "Embed",
            "model_type": "text-embedding",
            "context_size": None,
            "max_tokens_to_sample": None,
            "features": [],
            "pricing": {},
        },
        expected_model_type=ModelType.TEXT_EMBEDDING,
    )

    assert schema.model == "embed"
    assert schema.model_type == ModelType.TEXT_EMBEDDING
    assert schema.fetch_from == FetchFrom.CUSTOMIZABLE_MODEL
    assert schema.model_properties[ModelPropertyKey.CONTEXT_SIZE] == 512
    assert schema.model_properties[ModelPropertyKey.MAX_CHUNKS] == 1
    assert schema.parameter_rules == []
    assert schema.pricing is None


def test_builds_rerank_schema() -> None:
    schema = build_ai_model_entity(
        {
            "model": "rerank",
            "display_name": "Rerank",
            "model_type": "rerank",
            "context_size": None,
            "max_tokens_to_sample": None,
            "features": [],
            "pricing": {},
        },
        expected_model_type=ModelType.RERANK,
    )

    assert schema.model_type == ModelType.RERANK
    assert schema.fetch_from == FetchFrom.CUSTOMIZABLE_MODEL
    assert schema.model_properties == {}
    assert schema.parameter_rules == []


def test_fetch_schema_matches_endpoint_model_name(monkeypatch) -> None:
    client = FakeClient(
        {
            "data": [
                {"id": "other", "type": "chat"},
                {"id": "real-model", "name": "Real Model", "type": "chat"},
            ]
        }
    )
    monkeypatch.setattr("axonhub.model_schema.build_client", lambda _credentials: client)

    schema = get_customizable_model_schema_from_axonhub(
        "dify-name",
        {"endpoint_model_name": "real-model"},
        expected_model_type=ModelType.LLM,
    )

    assert schema.model == "dify-name"
    assert schema.label.en_us == "Real Model"
    assert client.calls == ["all"]


def test_fetch_schema_raises_when_model_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "axonhub.model_schema.build_client",
        lambda _credentials: FakeClient({"data": [{"id": "other", "type": "chat"}]}),
    )

    try:
        get_customizable_model_schema_from_axonhub(
            "missing",
            {},
            expected_model_type=ModelType.LLM,
        )
    except AxonHubConfigurationError as exc:
        assert "missing" in str(exc)
        assert "not found" in str(exc)
    else:
        raise AssertionError("Expected AxonHubConfigurationError")


def test_build_schema_rejects_model_type_mismatch() -> None:
    try:
        build_ai_model_entity(
            {
                "model": "embed",
                "display_name": "Embed",
                "model_type": "text-embedding",
                "context_size": 1024,
                "max_tokens_to_sample": None,
                "features": [],
                "pricing": {},
            },
            expected_model_type=ModelType.LLM,
        )
    except AxonHubConfigurationError as exc:
        assert "expected 'llm'" in str(exc)
    else:
        raise AssertionError("Expected AxonHubConfigurationError")
