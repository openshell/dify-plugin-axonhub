from __future__ import annotations

from dify_plugin.core.utils.yaml_loader import load_yaml_file
from dify_plugin.entities.model.provider import (
    ConfigurateMethod,
    ModelProviderConfiguration,
)


def test_provider_schema_uses_customizable_models_only() -> None:
    provider = ModelProviderConfiguration(**load_yaml_file("provider/axonhub.yaml"))

    assert provider.configurate_methods == [ConfigurateMethod.CUSTOMIZABLE_MODEL]
    assert provider.models == []
    assert provider.position is not None
    assert provider.position.llm == []
    assert provider.position.text_embedding == []
    assert provider.position.rerank == []
    assert provider.model_credential_schema is not None
