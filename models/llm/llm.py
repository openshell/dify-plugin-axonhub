from dify_plugin.entities.model import ModelType
from dify_plugin.interfaces.model.openai_compatible import llm as oai_llm

from axonhub.dify_compat import to_llm_credentials


class AxonHubLargeLanguageModel(oai_llm.OAICompatLargeLanguageModel):
    model_type = ModelType.LLM

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list,
        model_parameters: dict,
        tools: list | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ):
        return super()._invoke(
            model=model,
            credentials=to_llm_credentials(
                model,
                credentials,
                user=user,
                include_tracing=True,
            ),
            prompt_messages=prompt_messages,
            model_parameters=model_parameters,
            tools=tools,
            stop=stop,
            stream=stream,
            user=user,
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        return super().validate_credentials(
            model,
            to_llm_credentials(model, credentials),
        )

    def get_customizable_model_schema(self, model: str, credentials: dict):
        return super().get_customizable_model_schema(
            model,
            to_llm_credentials(model, credentials),
        )
