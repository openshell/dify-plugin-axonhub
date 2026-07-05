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

- [ ] Unit tests for request payloads and response mapping
- [ ] Unit tests for credential validation paths
- [ ] Local AxonHub API smoke test notes
- [ ] Dify plugin packaging/build check
- [ ] Lint/test command documentation

**Acceptance criteria:**

- [ ] Automated tests pass locally.
- [ ] Plugin can be packaged successfully.
- [ ] Manual smoke tests cover non-streaming chat, streaming chat, embedding, rerank, and tracing visibility.

## Phase 5: Documentation and release readiness

**Goal:** Prepare the repository for open-source use and first GitHub release.

**Deliverables:**

- [ ] `README.md`
- [ ] `README.zh-CN.md`
- [ ] Installation guide
- [ ] AxonHub configuration guide
- [ ] Dify configuration guide
- [ ] FAQ / troubleshooting notes
- [ ] `.env.example`
- [ ] Release checklist

**Acceptance criteria:**

- [ ] A new user can install and configure the plugin from the documentation.
- [ ] The docs clearly explain auto discovery, manual fallback, and tracing behavior.
- [ ] The repository is ready for a v0.1.0 release package.

## Current status

- Current phase: Phase 3 complete; ready for Phase 4 verification.
- Next action: complete broader verification: request/response mapping tests, credential path tests, local smoke notes, plugin packaging/build check, and manual Dify smoke tests.
- Known blockers: full Dify integration and packaging still require Dify API credentials and validation of the plugin daemon/runner configuration.
