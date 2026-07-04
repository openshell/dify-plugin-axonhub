# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

This repository is for an independent open-source Dify model provider plugin named `dify-plugin-axonhub`. The goal is to expose AxonHub as a first-class Dify provider instead of relying only on Dify's generic OpenAI-compatible provider.

The initial target is an enhanced MVP: stable OpenAI-compatible calls plus AxonHub-specific model discovery, model metadata mapping, rerank support, and tracing headers.

## Development status

The repository is currently in Phase 1 from `TASKS.md`: building the minimal plugin skeleton. Use `TASKS.md` for phase progress and acceptance checks. Use `dify-axonhub-dify-axonhub-glittery-cosmos.md` for the broader architecture and product scope.

## Common commands

Use `python -m uv` if `uv` is not directly available on PATH.

```bash
python -m uv sync
python -m uv run ruff check .
python -m uv run pytest
python -m uv run pytest tests/test_client.py
python -m uv run pytest tests/test_client.py::test_name
```

The Dify Plugin SDK is installed as the Python package `dify-plugin`; its module CLI currently exposes documentation generation:

```bash
python -m dify_plugin.cli --help
```

The Dify plugin daemon / packaging executable is expected at:

```bash
.tools/dify-plugin.exe
```

If it is not present, download the Windows amd64 release from `langgenius/dify-plugin-daemon` or ask the user to authorize downloading and executing that external binary.

## Local configuration

`.env.example` contains placeholders for local integration values. Do not assume these are configured until `.env` or environment variables are present.

Required for real AxonHub/Dify integration testing:

- `AXONHUB_BASE_URL`
- `AXONHUB_API_KEY`
- `DIFY_BASE_URL`
- `DIFY_API_KEY`
- `DIFY_PLUGIN_DEBUG_KEY`
- `DIFY_PLUGIN_DAEMON_URL`

Default local endpoints from the plan are:

- AxonHub: `http://localhost:8090`
- Dify API: `http://localhost:5001`

## Architecture direction

Expected plugin layout:

```text
manifest.yaml
main.py
provider/
  axonhub.yaml
  axonhub.py
models/
  llm/llm.py
  text_embedding/text_embedding.py
  rerank/rerank.py
axonhub/
  client.py
  errors.py
  model_mapper.py
  tracing.py
tests/
```

Core responsibilities:

- `axonhub/client.py`: normalize AxonHub base URLs, attach bearer auth, call `/v1/models?include=all`, `/v1/chat/completions`, `/v1/embeddings`, and `/v1/rerank`, and parse OpenAI-style errors without exposing API keys.
- `axonhub/model_mapper.py`: map AxonHub model metadata into Dify model types, features, context limits, max output token limits, and pricing. Missing metadata should degrade safely.
- `axonhub/tracing.py`: generate `AH-Trace-Id` per invocation and derive or generate `AH-Thread-Id`.
- `provider/axonhub.py`: validate provider-level credentials and coordinate model discovery/manual fallback.
- `models/llm/llm.py`: prefer Dify SDK OpenAI-compatible LLM support for `/v1/chat/completions`; add AxonHub model aliasing, tracing headers, streaming, tool calling, and schema customization where supported.
- `models/text_embedding/text_embedding.py`: prefer Dify SDK OpenAI-compatible embedding support for `/v1/embeddings`; support batch input, `encoding_format=float`, and optional dimensions.
- `models/rerank/rerank.py`: implement rerank separately because `/v1/rerank` is Jina-compatible rather than OpenAI standard.

## Implementation priorities

1. Build a coherent Dify plugin skeleton before deep feature work.
2. Implement AxonHub core utilities and unit tests before wiring model classes.
3. Prefer the Dify SDK OpenAI-compatible base classes for LLM and embedding stability.
4. Keep rerank as a dedicated model implementation.
5. Implement manual model configuration fallback first; dynamic model discovery can be added if the installed Dify SDK/provider interface supports it.

## Git workflow

Commit code at reasonable checkpoints instead of letting large unrelated diffs accumulate. A good checkpoint is a completed phase, a verified feature slice, or a coherent bug fix with passing relevant checks.

Before committing, review `git status` and the staged diff, stage specific files rather than broad adds, and avoid committing local secrets, virtual environments, tool binaries, or generated package artifacts.

## Verification expectations

Before considering the plugin ready for v0.1.0, verify:

- base URL normalization
- auth header construction
- `/v1/models?include=all` parsing
- OpenAI-style error parsing
- chat, embedding, and rerank request/response mapping
- tracing header injection
- plugin packaging with the Dify plugin daemon
- local smoke tests against AxonHub and Dify when credentials/services are available
