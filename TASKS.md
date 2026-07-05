# TASKS

This file tracks the phased execution plan for building `dify-plugin-axonhub`. The source architecture and product scope remain in `dify-axonhub-dify-axonhub-glittery-cosmos.md`; this file is only for implementation progress and stage acceptance.

## Phase 1: Project skeleton

**Goal:** Create a minimal Dify plugin repository structure that can be installed, inspected, and extended.

**Deliverables:**

- [x] `manifest.yaml`
- [x] `main.py`
- [x] `pyproject.toml`
- [x] Provider config skeleton under `provider/`
- [x] Model entry skeletons for LLM, embedding, and rerank
- [x] Shared AxonHub package skeleton under `axonhub/`
- [x] Basic asset and ignore files if required by the Dify plugin format

**Acceptance criteria:**

- [x] Repository has a coherent Dify plugin layout.
- [x] Plugin metadata identifies the provider as `AxonHub`.
- [x] No model implementation is required yet, but all planned extension points exist.

**Verification completed:**

- [x] Dify SDK `PluginRegistration` loads `manifest.yaml` and `provider/axonhub.yaml` successfully.
- [x] `python -m uv run ruff check .`
- [x] `.venv/Scripts/python.exe -m pytest`

## Phase 2: AxonHub core utilities

**Goal:** Implement reusable AxonHub protocol support shared by all model types.

**Deliverables:**

- [x] Base URL normalization
- [x] Auth header handling
- [x] `GET /v1/models?include=all` client
- [x] OpenAI-style error parsing
- [x] Model metadata mapper
- [x] Tracing header generation
- [x] Unit tests for client, mapper, and tracing

**Acceptance criteria:**

- [x] AxonHub model metadata can be fetched and mapped without calling Dify model classes.
- [x] Missing or partial AxonHub metadata degrades safely.
- [x] API keys are never logged or included in raised error messages.

## Phase 3: Dify model integrations

**Goal:** Connect AxonHub to Dify as a provider supporting LLM, text embedding, and rerank.

**Deliverables:**

- [x] Provider credential validation
- [x] LLM implementation for `/v1/chat/completions`
- [x] Streaming LLM support
- [x] Tool/function calling compatibility where supported by Dify SDK
- [x] Text embedding implementation for `/v1/embeddings`
- [x] Rerank implementation for `/v1/rerank`
- [x] Manual model configuration fallback
- [x] Tracing headers injected into model calls when enabled

**Acceptance criteria:**

- [x] AxonHub appears as an independent Dify provider.
- [x] Chat, embedding, and rerank calls can be executed with configured credentials.
- [x] Manual model configuration still works if model discovery is unavailable.

## Phase 4: Verification

**Goal:** Prove the plugin works locally and catch regressions with automated checks.

**Deliverables:**

- [x] Unit tests for request payloads and response mapping
- [x] Unit tests for credential validation paths
- [x] Local AxonHub/Dify smoke test notes
- [x] Dify plugin packaging/build check
- [x] Lint/test command documentation

**Acceptance criteria:**

- [x] Automated tests pass locally.
- [x] Plugin can be packaged successfully.
- [x] Manual smoke tests cover Dify installation, model display, and configured AxonHub usage.

**Verification completed:**

- [x] `python -m uv run ruff check .`
- [x] `python -m uv run pytest`
- [x] Dify plugin CLI package build completed with Linux amd64 CLI.
- [x] `_assets/icon.svg` included in the package to satisfy Dify asset remapping.
- [x] Predefined model YAML files included so Dify model display is not empty.
- [x] User confirmed the plugin can be used normally in Dify.

## Phase 5: Documentation and release readiness

**Goal:** Prepare the repository for open-source use and first GitHub release.

**Deliverables:**

- [x] `README.md`
- [x] `README.zh-CN.md`
- [x] Installation guide
- [x] AxonHub configuration guide
- [x] Dify configuration guide
- [x] FAQ / troubleshooting notes
- [x] `.env.example`
- [x] Release checklist
- [x] Open-source license
- [x] Changelog
- [x] Contribution and security guidelines
- [x] GitHub issue/PR templates
- [x] CI workflow

**Acceptance criteria:**

- [x] A new user can install and configure the plugin from the documentation.
- [x] The docs clearly explain auto discovery, manual fallback, and tracing behavior.
- [ ] The repository has a v0.1.0 GitHub Release with a `.difypkg` asset.

## Current status

- Current phase: Phase 5 documentation and release readiness in progress.
- Completed: core plugin implementation, Dify installation/use verification, package asset fixes, predefined model loading fixes, open-source documentation baseline, license, changelog, release checklist, CI, and contribution/security files.
- Next action: run final lint/test/package verification, copy the `.difypkg` to `/mnt/workspace/dev/chajian`, commit and push the release-readiness changes, then create GitHub Release `v0.1.0` with the `.difypkg` asset.
- Known blockers: GitHub installation will continue to fail until a GitHub Release exists and includes a `.difypkg` asset.
