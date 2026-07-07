# AxonHub Dify Plugin

[![CI](https://github.com/openshell/dify-plugin-axonhub/actions/workflows/ci.yml/badge.svg)](https://github.com/openshell/dify-plugin-axonhub/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-6C5CE7.svg)](https://dify.ai)

**Language:** [English](README.md) | [中文](README.zh-CN.md)

<img width="2362" height="1669" alt="动画" src="https://github.com/user-attachments/assets/e9717620-424e-4df9-8306-15d66de01ce8" />

`dify-plugin-axonhub` connects [Dify](https://dify.ai) to AxonHub as a dedicated model provider. It lets Dify users configure AxonHub once and use chat LLMs, text embeddings, and rerank models through AxonHub-compatible APIs.

The plugin is designed for teams that want a first-class AxonHub provider experience instead of configuring AxonHub only through Dify's generic OpenAI-compatible provider.


## About AxonHub

AxonHub is the upstream model gateway project for this plugin. See the [AxonHub GitHub repository](https://github.com/looplj/axonhub) for the core project. It exposes OpenAI-compatible chat and embedding APIs, a Jina-compatible rerank API, model discovery metadata, and tracing headers. This plugin focuses on bringing those AxonHub capabilities into Dify as a dedicated provider.

## Highlights

- **Custom model schema discovery**: enter an AxonHub model name in Dify and the plugin loads metadata from AxonHub `/v1/models`.
- **Chat LLM support** through AxonHub `/v1/chat/completions`.
- **Text embedding support** through AxonHub `/v1/embeddings` with `encoding_format=float`.
- **Rerank support** through AxonHub `/v1/rerank`.
- **Model name aliasing** with `AxonHub endpoint model name` for private or tenant-specific AxonHub model IDs.
- **Optional tracing headers** with `AH-Trace-Id` and `AH-Thread-Id` for AxonHub-side observability.
- **Safe error handling** that avoids exposing API keys in raised exceptions.

## Supported model types

| Dify model type | AxonHub endpoint | Status | Notes |
| --- | --- | --- | --- |
| LLM | `/v1/chat/completions` | Supported | Includes streaming support through Dify's OpenAI-compatible model path. |
| Text Embedding | `/v1/embeddings` | Supported | Uses float embeddings and supports batch input. |
| Rerank | `/v1/rerank` | Supported | Uses AxonHub's Jina-compatible rerank API. |

## Quick start

### Option 1: Install a release package

1. Open the repository's [GitHub Releases](https://github.com/openshell/dify-plugin-axonhub/releases) page.
2. Download the `.difypkg` asset for the version you want.
3. In Dify, open **Plugins** / **Plugin Management**.
4. Upload the `.difypkg` file.
5. Open the AxonHub provider settings and configure your credentials.

> Dify's GitHub installation flow requires a GitHub Release that contains a `.difypkg` asset. Source code alone is not enough for that install path.

### Option 2: Build from source

Install dependencies:

```bash
python -m uv sync
```

Run local checks:

```bash
python -m uv run ruff check .
python -m uv run pytest
```

Package the plugin:

```bash
.tools/dify-plugin plugin package .
```

Then upload the generated `.difypkg` file in Dify.

## Configuration

Configure these provider credentials in Dify:

| Field | Required | Description |
| --- | --- | --- |
| `AxonHub Base URL` | Yes | AxonHub endpoint. Both `http://localhost:8090` and `http://localhost:8090/v1` are accepted. |
| `AxonHub API Key` | Yes | AxonHub bearer token. Do not share it in issues, screenshots, or logs. |
| `Enable model auto discovery` | No | Validates credentials by calling AxonHub model discovery when enabled. |
| `Enable tracing headers` | No | Adds `AH-Trace-Id` and `AH-Thread-Id` to model requests. |
| `Request timeout seconds` | No | Timeout for AxonHub API requests. |

After configuring provider credentials, add custom models in Dify with type `llm`, `text-embedding`, or `rerank`. Enter the AxonHub model identifier as the Dify model name; the plugin calls AxonHub `/v1/models?include=all` and fills the single model schema from discovery metadata. If the Dify model name should be a friendly alias, set `AxonHub endpoint model name` to the actual AxonHub model identifier.

The current Dify plugin SDK does not expose a credential-aware hook for listing all models dynamically in the provider UI. For that reason this plugin ships only generic AxonHub placeholder predefined models for installation and provider credential compatibility; real deployment-specific models should be added as custom models, where discovery happens after a custom model name is entered.

## Documentation

- [Installation guide](docs/installation.md)
- [Configuration guide](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture overview](docs/architecture.md)
- [Development guide](docs/development.md)
- [Roadmap](ROADMAP.md)

## Project layout

```text
manifest.yaml                 # Dify plugin metadata
provider/axonhub.yaml          # Provider schema and model registration
provider/axonhub.py            # Provider credential validation
models/llm/                    # LLM model implementation
models/text_embedding/         # Embedding model implementation
models/rerank/                 # Rerank model implementation
axonhub/                       # Shared AxonHub client, mapping, errors, tracing
docs/                          # User and contributor documentation
tests/                         # Unit and schema regression tests
```

## Development

```bash
python -m uv sync
python -m uv run ruff check .
python -m uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for release steps.

## Security

Do not publish API keys, `Authorization` headers, `.env` contents, or private endpoint details in GitHub issues or pull requests. See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

Apache License 2.0. See [LICENSE](LICENSE).
