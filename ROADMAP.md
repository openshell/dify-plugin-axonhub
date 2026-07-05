# Roadmap

This roadmap describes planned improvements for `dify-plugin-axonhub`. Scope and priority may change based on Dify plugin SDK capabilities, AxonHub API changes, and community feedback.

## v0.1.x — Stabilization

- Publish signed or checksum-documented `.difypkg` release assets.
- Keep predefined model YAML files aligned with commonly used AxonHub models.
- Improve troubleshooting coverage based on installation feedback.
- Add focused regression tests for reported edge cases.

## v0.2.0 — Dify experience improvements

- Expand model metadata mapping where Dify exposes stable interfaces.
- Improve custom model schema defaults from AxonHub metadata.
- Add clearer examples for chat, embedding, and rerank setup in Dify workflows.
- Document recommended Knowledge Base and RAG configurations.
- Add release automation for packaging and checksum generation.

## v0.3.0 — AxonHub observability and governance

- Document AxonHub trace lookup workflows using `AH-Trace-Id` and `AH-Thread-Id`.
- Add compatibility notes for AxonHub profile, quota, and cost-management workflows where applicable.
- Publish a compatibility matrix for supported Dify and AxonHub versions.
- Explore marketplace submission if the plugin has sufficient production validation.

## Later ideas

- Optional model discovery helper tooling if Dify's dynamic model interfaces remain limited.
- Example Dify apps or workflow exports for common AxonHub use cases.
- Additional model types only after the core model provider paths remain stable.
