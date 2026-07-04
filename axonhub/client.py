class AxonHubClient:
    def __init__(self, endpoint_url: str, api_key: str, timeout: float = 60) -> None:
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.timeout = timeout

    def list_models(self, include: str = "all") -> dict:
        raise NotImplementedError("AxonHub model discovery is implemented in Phase 2.")
