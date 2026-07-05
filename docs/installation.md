# Installation

This guide explains how to install the AxonHub model provider plugin in Dify.

## Prerequisites

- A Dify workspace that supports third-party plugins.
- An AxonHub endpoint and API key.
- A plugin package file ending in `.difypkg`.

## Install from GitHub Release

1. Open the GitHub Releases page for this repository.
2. Download the `.difypkg` asset for the target version.
3. In Dify, open **Plugins** / **Plugin Management**.
4. Upload the `.difypkg` file.
5. After installation, open the AxonHub provider settings.
6. Configure AxonHub credentials.
7. Click the model list / show models action in Dify and confirm predefined models are visible.

Dify's GitHub installation flow expects a release asset. If the repository only contains source code and no GitHub Release with a `.difypkg` file, Dify may report that no release was found.

## Build from source

Install dependencies:

```bash
python -m uv sync
```

Run local checks:

```bash
python -m uv run ruff check .
python -m uv run pytest
```

Package with the Dify plugin CLI:

```bash
.tools/dify-plugin plugin package .
```

Upload the generated `.difypkg` file to Dify.

## Package verification

Before uploading, verify the package includes these paths:

```text
_assets/icon.svg
manifest.yaml
provider/axonhub.yaml
models/llm/_position.yaml
models/llm/*.yaml
models/text_embedding/_position.yaml
models/text_embedding/*.yaml
models/rerank/_position.yaml
```

The `_assets/icon.svg` file is required because Dify remaps plugin and provider icons from the `_assets` directory.

## Upgrade

For a manual upgrade:

1. Download or build the newer `.difypkg`.
2. Upload it in Dify's plugin management page.
3. Re-check provider credentials.
4. Confirm predefined models still appear.
5. Run a small chat or embedding request to verify runtime behavior.

If a Dify workspace caches old plugin metadata, remove the old plugin version and install the new package again.
