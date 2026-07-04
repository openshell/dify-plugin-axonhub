class AxonHubError(Exception):
    pass


class AxonHubAPIError(AxonHubError):
    pass


class AxonHubConfigurationError(AxonHubError):
    pass
