from __future__ import annotations

from axonhub.tracing import build_tracing_headers


def test_build_tracing_headers_returns_trace_and_thread_ids() -> None:
    headers = build_tracing_headers()

    assert set(headers) == {"AH-Trace-Id", "AH-Thread-Id"}
    assert headers["AH-Trace-Id"].startswith("dify-")
    assert headers["AH-Thread-Id"] == headers["AH-Trace-Id"]


def test_build_tracing_headers_uses_supplied_thread_id() -> None:
    headers = build_tracing_headers(thread_id="thread-123")

    assert headers["AH-Trace-Id"].startswith("dify-")
    assert headers["AH-Thread-Id"] == "thread-123"


def test_build_tracing_headers_generates_unique_trace_ids() -> None:
    first = build_tracing_headers()
    second = build_tracing_headers()

    assert first["AH-Trace-Id"] != second["AH-Trace-Id"]
