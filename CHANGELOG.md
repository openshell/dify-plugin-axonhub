# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows semantic versioning before the first stable release as closely as practical.

## [0.1.0] - 2026-07-05

### Added

- Add AxonHub as an independent Dify model provider.
- Add provider credential validation for AxonHub Base URL and API Key.
- Add LLM support through AxonHub `/v1/chat/completions`.
- Add streaming LLM support through Dify's OpenAI-compatible model interface.
- Add text embedding support through AxonHub `/v1/embeddings`.
- Add rerank support through AxonHub `/v1/rerank`.
- Add custom model fallback for models not included in predefined YAML files.
- Add optional AxonHub tracing headers: `AH-Trace-Id` and `AH-Thread-Id`.
- Add AxonHub client utilities for base URL normalization, auth headers, model discovery, and OpenAI-style error parsing.
- Add model metadata mapping utilities.
- Add predefined LLM and text embedding model YAML files.
- Add provider schema regression test to ensure predefined models are loaded by Dify.

### Fixed

- Include `_assets/icon.svg` in plugin packages so Dify can remap plugin and model icons.
- Add `models:` globs to `provider/axonhub.yaml` so Dify's “show models” view does not return zero models.
- Redact credentials from AxonHub API error messages.

### Verified

- `ruff check` passed locally.
- `pytest` passed locally.
- Plugin package succeeded with Dify plugin CLI for Linux amd64.
- The package was installed and used successfully in Dify.

### Known limitations

- GitHub installation requires a GitHub Release with a `.difypkg` asset.
- Rerank may need custom model configuration when no predefined rerank model is available in the current AxonHub model list.
- Release packaging is currently manual; automated release workflow can be added in a later version.
