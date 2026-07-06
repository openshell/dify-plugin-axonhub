# Configuration

This document describes the AxonHub provider and custom model configuration fields exposed in Dify.

## Provider credentials

Configure these fields once for the AxonHub provider.

| Field | Required | Description |
| --- | --- | --- |
| AxonHub Base URL | Yes | AxonHub API base URL. Both `http://localhost:8090` and `http://localhost:8090/v1` are accepted. |
| AxonHub API Key | Yes | Bearer token used to call AxonHub. Keep it secret. |
| Enable model auto discovery | No | When enabled, provider validation calls AxonHub model discovery. |
| Enable tracing headers | No | When enabled, model calls include `AH-Trace-Id` and `AH-Thread-Id`. |
| Request timeout seconds | No | Request timeout for AxonHub HTTP calls. |

## Base URL handling

The plugin normalizes common AxonHub URL forms. For example:

```text
http://localhost:8090
http://localhost:8090/
http://localhost:8090/v1
http://localhost:8090/v1/
```

All forms are normalized to a single `/v1` API base internally. Deployment prefixes are preserved.

## Custom models and schema discovery

This plugin uses Dify custom models as the primary model configuration path. Add a custom model in Dify and choose `llm`, `text-embedding`, or `rerank` as the model type.

When Dify asks the plugin for that model schema, the plugin calls AxonHub:

```text
GET /v1/models?include=all
```

It then finds the requested model and fills the Dify model schema from AxonHub discovery metadata, including context size, max output tokens, supported capabilities, and pricing where available.

Custom model fields:

| Field | Description |
| --- | --- |
| Model name | The Dify model identifier. If `AxonHub endpoint model name` is empty, this is also the AxonHub model ID used for discovery and invocation. |
| AxonHub endpoint model name | Optional actual AxonHub model ID. Use it when the Dify model name is a friendly alias. |
| Display name | Optional display label override. |
| Model type | `llm`, `text-embedding`, or `rerank`. |

Example mappings:

| Dify model name | AxonHub endpoint model name | Model sent to AxonHub |
| --- | --- | --- |
| `my-chat-model` | empty | `my-chat-model` |
| `company-gpt` | `tenant-a/gpt-prod` | `tenant-a/gpt-prod` |

The current Dify plugin SDK does not provide a provider-credential-aware hook for listing all models dynamically in the provider UI. Therefore this plugin does not ship maintainer-specific predefined YAML models. Model discovery happens after a user enters a custom model name.

## Tracing headers

When tracing is enabled, the plugin attaches AxonHub tracing headers to model calls:

```text
AH-Trace-Id: <generated trace id>
AH-Thread-Id: <thread id or trace id>
```

These headers help correlate Dify invocations with AxonHub-side traces.

## Security notes

- Do not commit `.env`.
- Do not share AxonHub API keys in GitHub issues.
- Do not include API keys in screenshots or logs.
- The plugin should not include API keys in raised error messages.
