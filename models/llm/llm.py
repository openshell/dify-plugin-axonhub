from dify_plugin.entities.model import ModelType
from dify_plugin.interfaces.model.openai_compatible import llm as oai_llm


class AxonHubLargeLanguageModel(oai_llm.OAICompatLargeLanguageModel):
    model_type = ModelType.LLM
