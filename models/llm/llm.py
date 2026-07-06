from dify_plugin.entities.model import ModelType
from dify_plugin.interfaces.model.openai_compatible import llm as oai_llm

from axonhub.dify_compat import to_llm_credentials
from axonhub.model_schema import get_customizable_model_schema_from_axonhub


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
        normalized_credentials = to_llm_credentials(
            model,
            credentials,
            user=user,
            include_tracing=True,
        )
        if tools:
            normalized_credentials["function_calling_type"] = "tool_call"
            normalized_credentials["stream_function_calling"] = "supported"

        return super()._invoke(
            model=model,
            credentials=normalized_credentials,
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
        return get_customizable_model_schema_from_axonhub(
            model,
            credentials,
            expected_model_type=ModelType.LLM,
        )
