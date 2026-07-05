# Contributing

Thank you for your interest in improving `dify-plugin-axonhub`.

## Development setup

Install dependencies:

```bash
python -m uv sync
```

Run checks:

```bash
python -m uv run ruff check .
python -m uv run pytest
```

Run a focused provider schema regression test:

```bash
python -m uv run pytest tests/test_provider_schema.py
```

See [docs/development.md](docs/development.md) for additional local development and integration testing notes.

## Packaging locally

Use the Dify plugin CLI:

```bash
.tools/dify-plugin plugin package .
```

Do not commit generated `.difypkg` files. Upload packages as GitHub Release assets instead.

## Adding predefined models

When adding a predefined LLM model:

1. Add a YAML file under `models/llm/`.
2. Add the model name to `models/llm/_position.yaml`.
3. Set model features conservatively. Do not claim `vision`, `tool call`, `reasoning`, or `structured output` support unless it is verified.
4. Run tests.

When adding a text embedding model:

1. Add a YAML file under `models/text_embedding/`.
2. Add the model name to `models/text_embedding/_position.yaml`.
3. Include safe context or chunk limits when known.
4. Run tests.

When adding a rerank model:

1. Add a YAML file under `models/rerank/` if the AxonHub rerank model name is stable.
2. Add the model name to `models/rerank/_position.yaml`.
3. Verify `/v1/rerank` behavior in Dify.

## Provider schema changes

If you change `provider/axonhub.yaml`, make sure:

- `models:` globs remain present.
- `_position.yaml` paths remain valid.
- `extra.python.model_sources` still points to all model implementations.
- `tests/test_provider_schema.py` still passes.

## Packaging asset rules

Dify remaps icons from `_assets/`. Keep this invariant:

```text
_assets/icon.svg
```

Do not add `_assets/` to `.difyignore`.

## Pull request checklist

Before opening a PR:

- [ ] Run `python -m uv run ruff check .`.
- [ ] Run `python -m uv run pytest`.
- [ ] Do not commit `.env` or secrets.
- [ ] Do not commit `.tools/` binaries.
- [ ] Do not commit `.difypkg` artifacts.
- [ ] If adding models, update the matching `_position.yaml` file.
- [ ] If changing packaging rules, confirm `_assets/icon.svg` is still packaged.
- [ ] If changing user-facing behavior, update README or docs.

## Reporting issues

Please use the GitHub issue templates and remove any API keys, Authorization headers, private URLs, or screenshots containing secrets.
