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

- [ ] Base URL normalization
- [ ] Auth header handling
- [ ] `GET /v1/models?include=all` client
- [ ] OpenAI-style error parsing
- [ ] Model metadata mapper
- [ ] Tracing header generation
- [ ] Unit tests for client, mapper, and tracing

**Acceptance criteria:**

- [ ] AxonHub model metadata can be fetched and mapped without calling Dify model classes.
- [ ] Missing or partial AxonHub metadata degrades safely.
- [ ] API keys are never logged or included in raised error messages.

## Phase 3: Dify model integrations

**Goal:** Connect AxonHub to Dify as a provider supporting LLM, text embedding, and rerank.

**Deliverables:**

- [ ] Provider credential validation
- [ ] LLM implementation for `/v1/chat/completions`
- [ ] Streaming LLM support
- [ ] Tool/function calling compatibility where supported by Dify SDK
- [ ] Text embedding implementation for `/v1/embeddings`
- [ ] Rerank implementation for `/v1/rerank`
- [ ] Manual model configuration fallback
- [ ] Tracing headers injected into model calls when enabled

**Acceptance criteria:**

- [ ] AxonHub appears as an independent Dify provider.
- [ ] Chat, embedding, and rerank calls can be executed with configured credentials.
- [ ] Manual model configuration still works if model discovery is unavailable.

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

- Current phase: Phase 1 complete; ready for Phase 2.
- Next action: implement AxonHub core utilities: URL normalization, auth headers, `/v1/models?include=all`, error parsing, metadata mapping, and tracing tests.
- Known blockers: real integration and packaging still require AxonHub/Dify credentials and the Dify plugin daemon binary.
