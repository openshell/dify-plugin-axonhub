# Installation

This guide explains how to install the AxonHub model provider plugin in Dify.

## Prerequisites

- A Dify workspace that supports third-party plugins.
- An AxonHub endpoint and API key.
- A packaged plugin file ending in `.difypkg`.

## Install from GitHub Release

1. Open the repository's GitHub Releases page.
2. Download the `.difypkg` asset for the target version.
3. In Dify, open **Plugins** / **Plugin Management**.
4. Upload the `.difypkg` file.
5. Open the AxonHub provider settings.
6. Configure AxonHub credentials.
7. Add a custom model in Dify and enter an AxonHub model name; the plugin fills its schema from AxonHub model discovery metadata.

Dify's GitHub installation flow expects a GitHub Release with a `.difypkg` asset. If the repository contains source code but no release asset, Dify may report that no release was found.

## Build from source

Install dependencies:

```bash
uv sync
```

Run local checks:

```bash
uv run ruff check .
uv run pytest
```

Package with the Dify plugin CLI:

```bash
.tools/dify-plugin plugin package .
```

Upload the generated `.difypkg` file in Dify.

If the Dify plugin CLI is not available locally, download the appropriate plugin daemon release from `langgenius/dify-plugin-daemon` and keep the binary outside git.

## Package verification

Before uploading, verify the package contains these required paths:

```text
_assets/icon.svg
manifest.yaml
provider/axonhub.yaml
models/llm/llm.py
models/text_embedding/text_embedding.py
models/rerank/rerank.py
```

The `_assets/icon.svg` file is required because Dify remaps plugin and provider icons from the `_assets` directory.

## Upgrade

For a manual upgrade:

1. Download or build the newer `.difypkg`.
2. Upload it in Dify's plugin management page.
3. Re-check provider credentials.
4. Re-check custom model configuration; model schema is loaded from AxonHub discovery after the model name is entered.
5. Run a small chat, embedding, or rerank request to verify runtime behavior.

If a Dify workspace caches old plugin metadata, remove the old plugin version and install the new package again.
