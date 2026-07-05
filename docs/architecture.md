# Architecture

`dify-plugin-axonhub` is a Dify model provider plugin that exposes AxonHub as a dedicated provider for LLM, text embedding, and rerank use cases.

## Design goals

- Provide a first-class AxonHub provider in Dify.
- Reuse Dify's stable OpenAI-compatible model paths where appropriate.
- Support AxonHub-specific model metadata, custom model fallback, and tracing headers.
- Keep model invocation behavior predictable and easy to test.
- Degrade safely when AxonHub metadata is incomplete.

## Repository structure

```text
manifest.yaml
main.py
provider/
  axonhub.yaml
  axonhub.py
models/
  llm/
  text_embedding/
  rerank/
axonhub/
  client.py
  errors.py
  model_mapper.py
  tracing.py
docs/
tests/
```

## Core components

### `axonhub/client.py`

Shared HTTP client utilities for AxonHub:

- Base URL normalization.
- Bearer authentication headers.
- `GET /v1/models?include=all` discovery.
- `POST /v1/chat/completions`.
- `POST /v1/embeddings`.
- `POST /v1/rerank`.
- OpenAI-style error parsing with credential redaction.

### `axonhub/model_mapper.py`

Maps AxonHub model metadata to Dify-compatible concepts:

- AxonHub chat models to Dify `llm`.
- AxonHub embedding models to Dify `text-embedding`.
- AxonHub rerank models to Dify `rerank`.
- Context limits, max output tokens, features, and pricing where available.

Missing metadata should not block model usage. Unknown capabilities default to disabled until explicitly configured.

### `axonhub/tracing.py`

Generates AxonHub tracing headers:

- `AH-Trace-Id` per invocation.
- `AH-Thread-Id` derived from available invocation context or generated as a fallback.

### `provider/axonhub.py`

Handles Dify provider-level credential validation and coordinates model discovery behavior.

### `models/llm/llm.py`

Implements AxonHub chat model behavior through `/v1/chat/completions`, including model aliasing, streaming, tool-call compatibility where supported, and optional tracing headers.

### `models/text_embedding/text_embedding.py`

Implements AxonHub embedding behavior through `/v1/embeddings`, including batch input, float embedding format, and optional tracing headers.

### `models/rerank/rerank.py`

Implements AxonHub rerank behavior through `/v1/rerank`. Rerank is implemented separately because this endpoint follows a Jina-compatible shape rather than OpenAI's chat or embedding APIs.

## Model registration strategy

The plugin supports two model registration paths:

1. **Predefined models**: YAML files under `models/llm/`, `models/text_embedding/`, and `models/rerank/` allow Dify to display known models immediately after provider setup.
2. **Custom models**: Dify users can manually configure private, newly added, or tenant-specific AxonHub models.

Provider credential validation may call AxonHub model discovery, but Dify's visible model list still depends on packaged model YAML files and custom model configuration.

## Packaging requirements

A valid Dify plugin package must include:

```text
manifest.yaml
provider/axonhub.yaml
_assets/icon.svg
models/llm/_position.yaml
models/text_embedding/_position.yaml
models/rerank/_position.yaml
```

The `_assets/icon.svg` path is required because Dify remaps plugin and provider icons from the `_assets` directory.
