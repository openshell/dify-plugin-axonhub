from __future__ import annotations

import json
from decimal import Decimal

import requests
from dify_plugin.entities.model.text_embedding import EmbeddingUsage
import models.text_embedding.text_embedding as embedding_module
from models.text_embedding.text_embedding import AxonHubTextEmbeddingModel


class FakeResponse:
    def __init__(self, status_code: int, payload: object = None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeRequests:
    def __init__(self, response: FakeResponse | Exception):
        self.response = response
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def embedding_model() -> AxonHubTextEmbeddingModel:
    return AxonHubTextEmbeddingModel.__new__(AxonHubTextEmbeddingModel)


def fake_usage(tokens: int) -> EmbeddingUsage:
    return EmbeddingUsage(
        tokens=tokens,
        total_tokens=tokens,
        unit_price=Decimal("0"),
        price_unit=Decimal("0"),
        total_price=Decimal("0"),
        currency="USD",
        latency=0,
    )


def test_embedding_invoke_builds_float_payload_with_tracing(monkeypatch) -> None:
    fake_requests = FakeRequests(
        FakeResponse(
            200,
            {
                "data": [{"embedding": [0.1, 0.2]}],
                "usage": {"total_tokens": 3},
            },
        )
    )
    monkeypatch.setattr(embedding_module.requests, "post", fake_requests.post)

    model = embedding_model()
    monkeypatch.setattr(model, "_get_context_size", lambda _model, _credentials: 100)
    monkeypatch.setattr(model, "_get_max_chunks", lambda _model, _credentials: 10)
    monkeypatch.setattr(model, "_get_num_tokens_by_gpt2", lambda _text: 3)
    monkeypatch.setattr(
        model,
        "_calc_response_usage",
        lambda model, credentials, tokens: fake_usage(tokens),
    )

    result = model._invoke(
        model="dify-embed",
        credentials={
            "endpoint_url": "https://example.com/",
            "api_key": " secret ",
            "endpoint_model_name": "real-embed",
            "enable_tracing": "true",
            "request_timeout": "8",
        },
        texts=["hello"],
        user="thread-1",
    )

    assert result.embeddings == [[0.1, 0.2]]
    assert result.model == "dify-embed"
    assert result.usage.total_tokens == 3
    call = fake_requests.calls[0]
    assert call["url"] == "https://example.com/v1/embeddings"
    assert call["headers"]["Authorization"] == "Bearer secret"
    assert call["headers"]["AH-Thread-Id"] == "thread-1"
    assert call["headers"]["AH-Trace-Id"].startswith("dify-")
    assert json.loads(call["data"]) == {
        "input": ["hello"],
        "model": "real-embed",
        "encoding_format": "float",
        "user": "thread-1",
    }
    assert call["timeout"] == 8


def test_embedding_post_helper_uses_timeout() -> None:
    fake_requests = FakeRequests(FakeResponse(200, {"data": [], "usage": {"total_tokens": 0}}))
    original_post = embedding_module.requests.post
    embedding_module.requests.post = fake_requests.post
    try:
        response = embedding_model()._post_embeddings(
            endpoint_url="https://example.com/v1",
            headers={"Authorization": "Bearer secret", "AH-Trace-Id": "trace"},
            payload={"input": ["hello"], "model": "embed", "encoding_format": "float"},
            credentials={"request_timeout": "8"},
        )
    finally:
        embedding_module.requests.post = original_post

    assert response.status_code == 200
    assert fake_requests.calls == [
        {
            "url": "https://example.com/v1/embeddings",
            "headers": {"Authorization": "Bearer secret", "AH-Trace-Id": "trace"},
            "data": json.dumps(
                {"input": ["hello"], "model": "embed", "encoding_format": "float"}
            ),
            "timeout": 8,
        }
    ]


def test_embedding_maps_timeout(monkeypatch) -> None:
    fake_requests = FakeRequests(requests.Timeout("boom"))
    monkeypatch.setattr(embedding_module.requests, "post", fake_requests.post)

    try:
        embedding_model()._post_embeddings(
            endpoint_url="https://example.com/v1",
            headers={},
            payload={},
            credentials={},
        )
    except Exception as exc:
        assert exc.__class__.__name__ == "InvokeConnectionError"
    else:
        raise AssertionError("Expected InvokeConnectionError")
