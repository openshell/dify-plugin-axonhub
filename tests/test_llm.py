from __future__ import annotations

from dify_plugin.entities.model import ModelPropertyKey, ModelType
import models.llm.llm as llm_module
from models.llm.llm import AxonHubLargeLanguageModel


class FakeClient:
    def list_models(self, include="all"):
        assert include == "all"
        return {
            "data": [
                {
                    "id": "real-model",
                    "name": "Real Model",
                    "type": "chat",
                    "context_length": 1000000,
                    "max_output_tokens": 128000,
                    "capabilities": {"vision": True, "tool_call": True},
                }
            ]
        }


def llm_model() -> AxonHubLargeLanguageModel:
    return AxonHubLargeLanguageModel.__new__(AxonHubLargeLanguageModel)


def test_llm_invoke_passes_normalized_credentials_with_tracing(monkeypatch) -> None:
    calls = []

    def fake_invoke(self, **kwargs):
        calls.append(kwargs)
        return "result"

    monkeypatch.setattr(llm_module.oai_llm.OAICompatLargeLanguageModel, "_invoke", fake_invoke)

    result = llm_model()._invoke(
        model="dify-model",
        credentials={
            "endpoint_url": "https://example.com/",
            "api_key": " secret ",
            "endpoint_model_name": "real-model",
            "enable_tracing": "true",
            "tool_call_support": "true",
            "vision_support": "true",
        },
        prompt_messages=[],
        model_parameters={},
        tools=None,
        stop=None,
        stream=True,
        user="thread-1",
    )

    assert result == "result"
    credentials = calls[0]["credentials"]
    assert credentials["endpoint_url"] == "https://example.com/v1"
    assert credentials["api_key"] == "secret"
    assert credentials["endpoint_model_name"] == "real-model"
    assert credentials["mode"] == "chat"
    assert credentials["function_calling_type"] == "tool_call"
    assert credentials["stream_function_calling"] == "supported"
    assert credentials["vision_support"] == "support"
    assert credentials["extra_headers"]["AH-Thread-Id"] == "thread-1"
    assert credentials["extra_headers"]["AH-Trace-Id"].startswith("dify-")


def test_llm_invoke_enables_tool_call_when_tools_are_present(monkeypatch) -> None:
    calls = []

    def fake_invoke(self, **kwargs):
        calls.append(kwargs)
        return "result"

    monkeypatch.setattr(llm_module.oai_llm.OAICompatLargeLanguageModel, "_invoke", fake_invoke)

    llm_model()._invoke(
        model="dify-model",
        credentials={"endpoint_url": "https://example.com/", "api_key": "secret"},
        prompt_messages=[],
        model_parameters={},
        tools=[{"type": "function"}],
        stop=None,
        stream=True,
    )

    credentials = calls[0]["credentials"]
    assert credentials["function_calling_type"] == "tool_call"
    assert credentials["stream_function_calling"] == "supported"


def test_llm_validate_credentials_uses_normalized_credentials(monkeypatch) -> None:
    calls = []

    def fake_validate(self, model, credentials):
        calls.append((model, credentials))

    monkeypatch.setattr(
        llm_module.oai_llm.OAICompatLargeLanguageModel,
        "validate_credentials",
        fake_validate,
    )

    llm_model().validate_credentials(
        "dify-model",
        {
            "endpoint_url": "https://example.com/",
            "api_key": "secret",
            "endpoint_model_name": "real-model",
        },
    )

    assert calls[0][0] == "dify-model"
    assert calls[0][1]["endpoint_url"] == "https://example.com/v1"
    assert calls[0][1]["endpoint_model_name"] == "real-model"
    assert calls[0][1]["mode"] == "chat"


def test_llm_customizable_schema_is_loaded_from_axonhub(monkeypatch) -> None:
    monkeypatch.setattr("axonhub.model_schema.build_client", lambda _credentials: FakeClient())

    schema = llm_model().get_customizable_model_schema(
        "dify-model",
        {"endpoint_model_name": "real-model"},
    )

    assert schema.model == "dify-model"
    assert schema.label.en_us == "Real Model"
    assert schema.model_type == ModelType.LLM
    assert schema.model_properties[ModelPropertyKey.CONTEXT_SIZE] == 1000000
    max_tokens = next(rule for rule in schema.parameter_rules if rule.name == "max_tokens")
    assert max_tokens.max == 128000
