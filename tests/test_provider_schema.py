from __future__ import annotations

from dify_plugin.core.utils.yaml_loader import load_yaml_file
from dify_plugin.entities.model import ModelType
from dify_plugin.entities.model.provider import (
    ConfigurateMethod,
    ModelProviderConfiguration,
)


def test_provider_schema_keeps_credential_entry_and_generic_models() -> None:
    provider = ModelProviderConfiguration(**load_yaml_file("provider/axonhub.yaml"))

    assert provider.configurate_methods == [
        ConfigurateMethod.PREDEFINED_MODEL,
        ConfigurateMethod.CUSTOMIZABLE_MODEL,
    ]
    assert provider.provider_credential_schema is not None
    assert provider.model_credential_schema is not None

    models = {model.model: model for model in provider.models}
    assert models["axonhub-custom-llm"].model_type == ModelType.LLM
    assert models["axonhub-custom-embedding"].model_type == ModelType.TEXT_EMBEDDING
    assert models["axonhub-custom-rerank"].model_type == ModelType.RERANK
    assert "claude-opus-4-8-cus" not in models

    assert provider.position is not None
    assert provider.position.llm == ["axonhub-custom-llm"]
    assert provider.position.text_embedding == ["axonhub-custom-embedding"]
    assert provider.position.rerank == ["axonhub-custom-rerank"]
