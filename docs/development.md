# Development Guide

This guide is for contributors working on `dify-plugin-axonhub` locally.

## Requirements

- Python 3.13 for local development.
- `uv` for dependency management.
- Dify plugin daemon / CLI for packaging.
- Optional: a Dify workspace and AxonHub endpoint for integration testing.

The plugin runtime declared in `manifest.yaml` targets Python 3.12 for Dify compatibility, while local development currently uses Python 3.13 as configured in `pyproject.toml`.

## Setup

Install dependencies:

```bash
python -m uv sync
```

Copy local configuration placeholders if you need integration testing:

```bash
cp .env.example .env
```

Then fill the values required by your local environment. Never commit `.env`.

## Common commands

Run lint checks:

```bash
python -m uv run ruff check .
```

Run the test suite:

```bash
python -m uv run pytest
```

Run a focused test file:

```bash
python -m uv run pytest tests/test_client.py
```

Run a focused test case:

```bash
python -m uv run pytest tests/test_client.py::test_name
```

## Packaging

Package the plugin with the Dify plugin CLI:

```bash
.tools/dify-plugin plugin package .
```

Do not commit generated `.difypkg` files. Publish release packages as GitHub Release assets.

## Integration testing

Required values for real AxonHub/Dify integration testing are documented in `.env.example`:

- `AXONHUB_BASE_URL`
- `AXONHUB_API_KEY`
- `DIFY_BASE_URL`
- `DIFY_API_KEY`
- `DIFY_PLUGIN_DEBUG_KEY`
- `DIFY_PLUGIN_DAEMON_URL`

Recommended smoke checks before a release:

1. Install the generated `.difypkg` in Dify.
2. Configure AxonHub provider credentials.
3. Add one custom LLM, embedding, and rerank model by entering AxonHub model names and confirm their schemas load.
4. Run one non-streaming LLM request.
5. Run one streaming LLM request when supported by the target model.
6. Run one embedding request.
7. Run one rerank model request.
8. Enable tracing headers and verify AxonHub receives `AH-Trace-Id` and `AH-Thread-Id`.

## Implementation notes

- Keep AxonHub HTTP behavior in `axonhub/client.py`.
- Keep model metadata conversion in `axonhub/model_mapper.py`.
- Keep tracing header generation in `axonhub/tracing.py`.
- Keep provider credential validation in `provider/axonhub.py`.
- Prefer Dify SDK OpenAI-compatible model support for LLM and embedding behavior when possible.
- Keep rerank as a dedicated implementation because `/v1/rerank` is Jina-compatible rather than OpenAI standard.
- Treat missing AxonHub metadata as non-fatal and degrade safely.
- Never include API keys in raised errors, logs, tests, or documentation examples.

## Release workflow

Use [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) before publishing a release. A Dify GitHub installation requires a GitHub Release with a `.difypkg` asset; source code alone is not enough.
