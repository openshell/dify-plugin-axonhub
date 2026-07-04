from dify_plugin.errors.model import CredentialsValidateFailedError
from dify_plugin.interfaces.model.openai_compatible import provider as oai_provider


class AxonHubProvider(oai_provider.OAICompatProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        endpoint_url = credentials.get("endpoint_url")
        api_key = credentials.get("api_key")
        if not endpoint_url:
            raise CredentialsValidateFailedError("AxonHub Base URL is required.")
        if not api_key:
            raise CredentialsValidateFailedError("AxonHub API Key is required.")
