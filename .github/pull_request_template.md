# Pull Request Checklist

## Summary

<!-- Describe what changed and why. -->

## Checks

- [ ] I ran `python -m uv run ruff check .`
- [ ] I ran `python -m uv run pytest`
- [ ] I did not commit `.env` files or secrets
- [ ] I did not commit `.tools/` binaries
- [ ] I did not commit `.difypkg` package artifacts
- [ ] If I changed predefined models, I updated the matching `_position.yaml`
- [ ] If I changed packaging rules, `_assets/icon.svg` is still included in the package
- [ ] If I changed user-facing behavior, I updated README or docs

## Dify verification

<!-- If applicable, describe how you installed or tested the plugin in Dify. -->
