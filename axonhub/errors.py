from __future__ import annotations


class AxonHubError(Exception):
    """Base error for AxonHub helper utilities."""


class AxonHubConfigurationError(AxonHubError):
    """Raised when local AxonHub configuration is invalid."""


class AxonHubAPIError(AxonHubError):
    """Raised when AxonHub returns or triggers an API-level failure."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_type: str | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.code = code

    def __str__(self) -> str:
        parts = [self.message]
        details = []
        if self.status_code is not None:
            details.append(f"status={self.status_code}")
        if self.error_type:
            details.append(f"type={self.error_type}")
        if self.code:
            details.append(f"code={self.code}")
        if details:
            parts.append(f"({', '.join(details)})")
        return " ".join(parts)
