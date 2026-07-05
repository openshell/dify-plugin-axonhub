from __future__ import annotations

from dify_plugin.core.utils.yaml_loader import load_yaml_file
from dify_plugin.entities.model import ModelType
from dify_plugin.entities.model.provider import ModelProviderConfiguration


def test_provider_schema_loads_predefined_axonhub_models() -> None:
    provider = ModelProviderConfiguration(**load_yaml_file("provider/axonhub.yaml"))

    llm_models = [model.model for model in provider.models if model.model_type == ModelType.LLM]
    embedding_models = [
        model.model
        for model in provider.models
        if model.model_type == ModelType.TEXT_EMBEDDING
    ]

    assert len(llm_models) >= 1
    assert "claude-opus-4-8-cus" in llm_models
    assert "Qwen3-Embedding-8B" in embedding_models
    assert provider.position is not None
    assert "claude-opus-4-8-cus" in provider.position.llm
