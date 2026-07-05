from __future__ import annotations

import requests

import models.rerank.rerank as rerank_module
from dify_plugin.entities.model.rerank import RerankResult
from dify_plugin.errors.model import InvokeAuthorizationError, InvokeConnectionError
from models.rerank.rerank import AxonHubRerankModel


class FakeResponse:
    def __init__(self, status_code: int, payload: object = None, *, json_error=False):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise ValueError("not json")
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


def rerank_model() -> AxonHubRerankModel:
    return AxonHubRerankModel.__new__(AxonHubRerankModel)


def test_rerank_posts_jina_compatible_payload(monkeypatch) -> None:
    fake_requests = FakeRequests(
        FakeResponse(
            200,
            {
                "model": "rerank-model",
                "results": [
                    {"index": 1, "relevance_score": 0.9},
                    {"index": 0, "relevance_score": 0.5},
                ],
            },
        )
    )
    monkeypatch.setattr(rerank_module.requests, "post", fake_requests.post)

    result = rerank_model()._invoke(
        model="dify-name",
        credentials={
            "endpoint_url": "https://example.com",
            "api_key": "secret",
            "endpoint_model_name": "rerank-model",
            "enable_tracing": "true",
            "request_timeout": "9",
        },
        query="query",
        docs=["doc0", "doc1"],
        top_n=2,
        score_threshold=0.6,
        user="thread-1",
    )

    assert isinstance(result, RerankResult)
    assert result.model == "rerank-model"
    assert [(doc.index, doc.text, doc.score) for doc in result.docs] == [(1, "doc1", 0.9)]
    assert fake_requests.calls == [
        {
            "url": "https://example.com/v1/rerank",
            "headers": {
                "Authorization": "Bearer secret",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "AH-Trace-Id": fake_requests.calls[0]["headers"]["AH-Trace-Id"],
                "AH-Thread-Id": "thread-1",
            },
            "json": {
                "model": "rerank-model",
                "query": "query",
                "documents": ["doc0", "doc1"],
                "top_n": 2,
            },
            "timeout": 9,
        }
    ]
    assert fake_requests.calls[0]["headers"]["AH-Trace-Id"].startswith("dify-")


def test_rerank_maps_auth_error_without_leaking_api_key(monkeypatch) -> None:
    api_key = "secret-key"
    fake_requests = FakeRequests(
        FakeResponse(401, {"error": {"message": f"bad {api_key}"}})
    )
    monkeypatch.setattr(rerank_module.requests, "post", fake_requests.post)

    try:
        rerank_model()._invoke(
            model="m",
            credentials={"endpoint_url": "https://example.com", "api_key": api_key},
            query="q",
            docs=["d"],
        )
    except InvokeAuthorizationError as exc:
        assert api_key not in str(exc)
        assert "<redacted>" in str(exc)
    else:
        raise AssertionError("Expected InvokeAuthorizationError")


def test_rerank_maps_timeout(monkeypatch) -> None:
    fake_requests = FakeRequests(requests.Timeout("boom"))
    monkeypatch.setattr(rerank_module.requests, "post", fake_requests.post)

    try:
        rerank_model()._invoke(
            model="m",
            credentials={"endpoint_url": "https://example.com", "api_key": "secret"},
            query="q",
            docs=["d"],
        )
    except InvokeConnectionError as exc:
        assert "timed out" in str(exc)
    else:
        raise AssertionError("Expected InvokeConnectionError")
