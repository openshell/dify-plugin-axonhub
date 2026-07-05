from __future__ import annotations

from axonhub.errors import AxonHubConfigurationError
from axonhub.model_mapper import map_model_card, map_model_cards


def test_maps_chat_model_card_to_llm() -> None:
    card = {
        "id": "claude-opus-4-8-cus",
        "name": "Claude Opus",
        "description": "flagship model",
        "type": "chat",
        "context_length": 1_000_000,
        "max_output_tokens": 128_000,
        "capabilities": {
            "vision": True,
            "tool_call": True,
            "reasoning": True,
            "structured_output": False,
        },
        "pricing": {"unit": "per_1m_tokens", "input": 3, "output": 15},
    }

    mapped = map_model_card(card)

    assert mapped == {
        "model": "claude-opus-4-8-cus",
        "display_name": "Claude Opus",
        "description": "flagship model",
        "model_type": "llm",
        "context_size": 1_000_000,
        "max_tokens_to_sample": 128_000,
        "features": ["reasoning", "tool_call", "vision"],
        "pricing": {
            "raw": {"unit": "per_1m_tokens", "input": 3, "output": 15},
            "unit": "per_1m_tokens",
            "input": 3,
            "output": 15,
        },
        "raw": card,
    }


def test_maps_embedding_and_rerank_model_types() -> None:
    embedding = map_model_card({"id": "embed", "type": "text_embedding"})
    rerank = map_model_card({"id": "rerank", "type": "reranker"})

    assert embedding["model_type"] == "text-embedding"
    assert rerank["model_type"] == "rerank"


def test_unknown_or_missing_type_defaults_to_llm() -> None:
    assert map_model_card({"id": "m1"})["model_type"] == "llm"
    assert map_model_card({"id": "m2", "type": "unknown"})["model_type"] == "llm"


def test_missing_metadata_degrades_safely() -> None:
    mapped = map_model_card({"id": "m1"})

    assert mapped["model"] == "m1"
    assert mapped["display_name"] == "m1"
    assert mapped["description"] == ""
    assert mapped["context_size"] is None
    assert mapped["max_tokens_to_sample"] is None
    assert mapped["features"] == []
    assert mapped["pricing"] == {}


def test_capabilities_can_be_list_like() -> None:
    mapped = map_model_card(
        {
            "id": "m1",
            "capabilities": ["vision", "function_call", "structured_output"],
        }
    )

    assert mapped["features"] == ["structured_output", "tool_call", "vision"]


def test_numeric_strings_are_mapped_to_ints() -> None:
    mapped = map_model_card(
        {"id": "m1", "context_length": "1024", "max_output_tokens": "256"}
    )

    assert mapped["context_size"] == 1024
    assert mapped["max_tokens_to_sample"] == 256


def test_missing_model_id_is_rejected() -> None:
    try:
        map_model_card({"type": "chat"})
    except AxonHubConfigurationError as exc:
        assert "model id" in str(exc)
    else:
        raise AssertionError("Expected AxonHubConfigurationError")


def test_maps_model_cards_from_payload() -> None:
    mapped = map_model_cards({"data": [{"id": "m1"}, {"id": "m2", "type": "rerank"}]})

    assert [item["model"] for item in mapped] == ["m1", "m2"]
    assert [item["model_type"] for item in mapped] == ["llm", "rerank"]
