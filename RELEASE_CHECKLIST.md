# Release Checklist

Use this checklist before publishing a new GitHub Release for `dify-plugin-axonhub`.

## Version

- [ ] `manifest.yaml` `version` matches the release tag.
- [ ] `manifest.yaml` `meta.version` matches the release tag.
- [ ] `pyproject.toml` version matches the release tag.
- [ ] `CHANGELOG.md` contains release notes for the version.

## Source hygiene

- [ ] No `.env` or local secret files are staged.
- [ ] No `.tools/` binaries are staged.
- [ ] No `.venv/` files are staged.
- [ ] No `.difypkg` package artifact is staged unless intentionally uploaded outside git.
- [ ] `_assets/icon.svg` exists.
- [ ] `.difyignore` does not exclude `_assets/`.
- [ ] `provider/axonhub.yaml` contains `models:` globs.
- [ ] Predefined model YAML files and `_position.yaml` files are included in git.

## Automated checks

Run:

```bash
python -m uv run ruff check .
python -m uv run pytest
```

Confirm:

- [ ] Ruff passes.
- [ ] Pytest passes.
- [ ] Provider schema test confirms predefined models load.

## Package

Build the plugin package:

```bash
.tools/dify-plugin plugin package .
```

Confirm the generated `.difypkg` contains:

- [ ] `manifest.yaml`
- [ ] `provider/axonhub.yaml`
- [ ] `_assets/icon.svg`
- [ ] `models/llm/*.yaml`
- [ ] `models/text_embedding/*.yaml`
- [ ] `models/*/_position.yaml`

Record:

- [ ] Package filename:
- [ ] Package size:
- [ ] SHA256 checksum:

## Manual Dify verification

Install the generated `.difypkg` in Dify and verify:

- [ ] AxonHub provider installs successfully.
- [ ] Provider icon displays correctly.
- [ ] Provider credentials validate.
- [ ] “Show models” displays predefined LLM models.
- [ ] Text embedding model is visible.
- [ ] LLM invocation succeeds.
- [ ] Streaming LLM invocation succeeds if tested.
- [ ] Text embedding invocation succeeds.
- [ ] Rerank invocation succeeds, or custom rerank model setup is documented.
- [ ] Tracing headers are visible in AxonHub when enabled.

## GitHub Release

- [ ] Create and push tag, for example `v0.1.0`.
- [ ] Create GitHub Release with the same version.
- [ ] Upload `.difypkg` as a release asset.
- [ ] Include SHA256 checksum in release notes.
- [ ] Include installation steps in release notes.
- [ ] Include known limitations in release notes.
- [ ] Download the uploaded asset and verify it can still be installed in Dify.

## Announcement

- [ ] Update README release link if needed.
- [ ] Publish Chinese release note.
- [ ] Publish English summary if targeting international users.
- [ ] Share in relevant Dify/AxonHub community channels.
