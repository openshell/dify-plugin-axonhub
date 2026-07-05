from dify_plugin.errors.model import CredentialsValidateFailedError
from dify_plugin.interfaces.model.openai_compatible import provider as oai_provider

from axonhub.dify_compat import build_client, parse_bool, redacted_error_message
from axonhub.errors import AxonHubAPIError, AxonHubConfigurationError


class AxonHubProvider(oai_provider.OAICompatProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        try:
            if parse_bool(credentials.get("auto_discovery"), default=True):
                build_client(credentials).list_models(include="all")
                return

            if not credentials.get("endpoint_url"):
                raise AxonHubConfigurationError("AxonHub Base URL is required.")
            if not credentials.get("api_key"):
                raise AxonHubConfigurationError("AxonHub API Key is required.")
        except (AxonHubAPIError, AxonHubConfigurationError) as exc:
            raise CredentialsValidateFailedError(
                redacted_error_message(exc, credentials)
            ) from exc
