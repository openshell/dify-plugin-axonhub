# Troubleshooting

## Upload fails with `file not found: icon.svg`

Typical error:

```text
file not found: icon.svg failed to remap model icon small en_US failed to remap assets failed to save package
```

Cause: Dify plugin daemon remaps icons from the package's `_assets/` directory. If `_assets/icon.svg` is not inside the `.difypkg`, icon remapping fails.

Fix:

1. Ensure `_assets/icon.svg` exists.
2. Ensure `.difyignore` does not exclude `_assets/`.
3. Rebuild the `.difypkg`.
4. Upload the rebuilt package.

Root-level `icon.svg` or `provider/icon.svg` is not sufficient by itself. The package must include `_assets/icon.svg`.

## Dify shows 0 models

This is expected for the provider-level model list. The current Dify plugin SDK does not expose a provider-credential-aware hook that lets a plugin dynamically list all AxonHub models in the provider UI.

Fix:

1. Configure AxonHub provider credentials.
2. Add a custom model in Dify.
3. Enter the AxonHub model ID as the model name, or enter a friendly Dify model name and set `AxonHub endpoint model name` to the real AxonHub model ID.
4. The plugin calls `/v1/models?include=all` and fills the single custom model schema from AxonHub discovery metadata.
5. Run the provider and schema regression tests:

   ```bash
   uv run pytest tests/test_provider_schema.py tests/test_model_schema.py
   ```

## Custom model schema does not load

Check that:

- AxonHub Base URL is reachable from the Dify runtime.
- The API key is valid.
- AxonHub exposes `/v1/models`.
- The entered model name, or `AxonHub endpoint model name` when configured, exactly matches a model ID returned by AxonHub discovery.
- The selected Dify model type matches the AxonHub model type (`llm`, `text-embedding`, or `rerank`).

## GitHub install reports no release found

Cause: Dify expects a GitHub Release with a `.difypkg` asset. Source files alone are not enough.

Fix:

1. Create a GitHub tag, for example `v0.1.0`.
2. Create a GitHub Release for that tag.
3. Upload the packaged `.difypkg` file as a release asset.
4. Retry the Dify GitHub installation flow.

## Provider credential validation fails

Check that:

- AxonHub Base URL is reachable from the Dify runtime.
- The API key is valid.
- The Base URL points to AxonHub, not to Dify.
- Network access from Dify to AxonHub is allowed.
- AxonHub exposes OpenAI-compatible `/v1` endpoints.

## Base URL confusion

The plugin accepts both forms:

```text
http://localhost:8090
http://localhost:8090/v1
```

It normalizes the URL internally and avoids adding `/v1` twice.

## Rerank model setup

Configure a custom model in Dify:

- Model type: `rerank`
- Model name: the AxonHub rerank model name
- AxonHub endpoint model name: optional override if the Dify display name differs

The plugin sends rerank requests to AxonHub's `/v1/rerank` endpoint.

## Do not share secrets

When reporting issues, remove:

- AxonHub API Key
- Dify API Key
- Authorization headers
- `.env` contents
- private endpoint URLs if needed
- screenshots containing credentials
