# Security Policy

## Reporting a vulnerability

Please do not report security vulnerabilities by opening a public GitHub issue if the report contains sensitive details.

For now, contact the project maintainer through the repository owner's preferred private channel. If no private channel is listed, open a minimal public issue that says you would like to report a security issue, without including secrets, exploit details, API keys, or private endpoint information.

## Sensitive information

Do not include the following in issues, pull requests, screenshots, logs, or release discussions:

- AxonHub API keys
- Dify API keys
- `Authorization` headers
- `.env` contents
- private endpoint URLs, if they identify internal infrastructure
- request or response logs containing secrets

## Project security expectations

This plugin should:

- Never log API keys.
- Never include API keys in raised error messages.
- Redact credentials in validation failures.
- Avoid committing local `.env` files or generated package artifacts.
- Keep provider and model credentials scoped to Dify's credential handling.

## Supported versions

The first public release line is expected to be `0.1.x`. Security fixes will target the latest released version unless otherwise stated in a GitHub Release note.
