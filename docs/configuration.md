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

All are normalized to a single `/v1` API base internally. Deployment prefixes are preserved.

## Predefined models

The plugin package includes model YAML files under:

```text
models/llm/
models/text_embedding/
models/rerank/
```

Dify uses these files to populate the model list. Provider credential validation alone does not populate Dify's model list; the `models:` globs in `provider/axonhub.yaml` and the packaged YAML files are required.

## Custom models

Use custom models when:

- AxonHub exposes a new model that is not in the predefined list.
- You want a Dify display name that differs from the AxonHub endpoint model name.
- You need to configure a private or tenant-specific AxonHub model.
- You need rerank support but no predefined rerank model is listed.

Custom model fields:

| Field | Description |
| --- | --- |
| Model name | The Dify model identifier. |
| AxonHub endpoint model name | Optional actual AxonHub model name. Leave empty to use the Dify model name. |
| Display name | Optional display label. |
| Model type | `llm`, `text-embedding`, or `rerank`. |
| Context size | Optional model context size. |
| Max output tokens | Optional max output token limit for LLMs. |
| Vision support | Mark the model as supporting vision where applicable. |
| Tool call support | Mark the model as supporting tool/function calling where applicable. |
| Reasoning support | Mark the model as a reasoning model where applicable. |
| Structured output support | Mark the model as supporting structured output where applicable. |

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
