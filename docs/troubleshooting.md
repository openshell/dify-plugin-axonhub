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

Cause: Dify's model list is loaded from predefined model YAML files included in the plugin package. Provider credential validation and AxonHub model discovery do not automatically populate Dify's model list.

Fix:

1. Ensure `provider/axonhub.yaml` contains a `models:` section.
2. Ensure model YAML files exist under `models/llm/`, `models/text_embedding/`, or `models/rerank/` as needed.
3. Ensure each model directory includes `_position.yaml`.
4. Rebuild and reinstall the plugin package.
5. Run the provider schema regression test:

   ```bash
   python -m uv run pytest tests/test_provider_schema.py
   ```

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

## Rerank model is not listed

If no predefined rerank model appears, configure a custom model in Dify:

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
