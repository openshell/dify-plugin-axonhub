from uuid import uuid4


def build_tracing_headers(thread_id: str | None = None) -> dict[str, str]:
    trace_id = f"dify-{uuid4()}"
    return {
        "AH-Trace-Id": trace_id,
        "AH-Thread-Id": thread_id or trace_id,
    }
