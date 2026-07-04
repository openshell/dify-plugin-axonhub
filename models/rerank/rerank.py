from dify_plugin.entities.model import ModelType
from dify_plugin.entities.model.rerank import RerankResult
from dify_plugin.errors.model import CredentialsValidateFailedError, InvokeConnectionError
from dify_plugin.interfaces.model import rerank_model


class AxonHubRerankModel(rerank_model.RerankModel):
    model_type = ModelType.RERANK

    def _invoke(
        self,
        model: str,
        credentials: dict,
        query: str,
        docs: list[str],
        score_threshold: float | None = None,
        top_n: int | None = None,
        user: str | None = None,
    ) -> RerankResult:
        raise NotImplementedError("AxonHub rerank invocation is implemented in Phase 3.")

    def validate_credentials(self, model: str, credentials: dict) -> None:
        if not credentials.get("endpoint_url"):
            raise CredentialsValidateFailedError("AxonHub Base URL is required.")
        if not credentials.get("api_key"):
            raise CredentialsValidateFailedError("AxonHub API Key is required.")

    @property
    def _invoke_error_mapping(self):
        return {InvokeConnectionError: [ConnectionError, TimeoutError]}
