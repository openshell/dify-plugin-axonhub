from dify_plugin.entities.model import ModelType
from dify_plugin.interfaces.model.openai_compatible import text_embedding as oai_embedding


class AxonHubTextEmbeddingModel(oai_embedding.OAICompatEmbeddingModel):
    model_type = ModelType.TEXT_EMBEDDING
