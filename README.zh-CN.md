# Dify Plugin AxonHub

AxonHub 的 Dify 模型供应商插件，支持在 Dify 中以独立 provider 的形式使用 AxonHub 的大语言模型、文本嵌入模型和重排模型。

相比直接使用 Dify 的通用 OpenAI-compatible provider，本插件提供了更贴近 AxonHub 的模型配置、预定义模型列表、自定义模型兜底和请求追踪 Header。

## 功能特性

- 在 Dify 中显示为独立的 `AxonHub` 模型供应商。
- 支持 LLM：`/v1/chat/completions`。
- 支持 Text Embedding：`/v1/embeddings`。
- 支持 Rerank：`/v1/rerank`。
- 内置 AxonHub 预定义模型 YAML，安装后可直接在 Dify 中显示模型。
- 支持自定义模型，用于新增模型、私有模型或暂未内置的模型。
- 支持可选追踪 Header：
  - `AH-Trace-Id`
  - `AH-Thread-Id`
- 错误处理会避免在异常信息中暴露 API Key。

## 安装方式

### 方式一：从 GitHub Release 安装

1. 打开本项目 GitHub Releases 页面。
2. 下载对应版本的 `.difypkg` 文件，例如：

   ```text
   dify-plugin-axonhub-v0.1.0.difypkg
   ```

3. 打开 Dify 插件管理页面。
4. 上传 `.difypkg` 文件并安装。
5. 安装完成后，进入 AxonHub provider 配置页面，填写 AxonHub Base URL 和 API Key。

> 注意：Dify 的 GitHub 安装方式依赖 GitHub Release 中的 `.difypkg` 资产。只把源码 push 到 GitHub 不够。如果 Dify 提示“未找到发布版本”，请检查 GitHub Release 是否存在，以及 Release 中是否上传了 `.difypkg` 文件。

### 方式二：从源码打包安装

安装依赖：

```bash
python -m uv sync
```

运行检查：

```bash
python -m uv run ruff check .
python -m uv run pytest
```

使用 Dify plugin CLI 打包：

```bash
.tools/dify-plugin plugin package .
```

然后把生成的 `.difypkg` 上传到 Dify。

## Dify 凭据配置

在 Dify 的 AxonHub provider 配置页面填写：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `AxonHub Base URL` | 是 | AxonHub 地址。可以填写 `http://localhost:8090` 或 `http://localhost:8090/v1`。 |
| `AxonHub API Key` | 是 | AxonHub API Key。不要在 issue、截图或日志中公开。 |
| `Enable model auto discovery` | 否 | 启用后会通过 AxonHub 模型发现接口校验凭据。 |
| `Enable tracing headers` | 否 | 启用后请求会携带 `AH-Trace-Id` 和 `AH-Thread-Id`。 |
| `Request timeout seconds` | 否 | 请求 AxonHub API 的超时时间。 |

## 预定义模型与自定义模型

插件包中包含预定义模型文件：

```text
models/llm/
models/text_embedding/
models/rerank/
```

Dify 的“显示模型”依赖这些 YAML 文件。如果某个 AxonHub 模型没有出现在预定义列表中，可以在 Dify 中使用自定义模型配置。

如果 rerank 暂时没有预定义模型，也可以通过自定义模型方式配置，只要 AxonHub 端点支持 `/v1/rerank`。

## 常见问题

### 上传插件时报 `file not found: icon.svg`

请确认 `.difypkg` 包内存在：

```text
_assets/icon.svg
```

并确认 `.difyignore` 没有排除 `_assets/`。Dify plugin daemon 会从 `_assets/` 目录读取并重映射图标。

### 点击“显示模型”结果为 0

请确认：

1. `provider/axonhub.yaml` 中存在 `models:` 配置；
2. 包内存在 `models/llm/*.yaml`、`models/text_embedding/*.yaml`；
3. 包内存在 `_position.yaml` 文件；
4. 上传的是最新重新打包后的 `.difypkg`。

### GitHub 安装提示“未找到发布版本”

需要创建 GitHub Release，并在 Release 中上传 `.difypkg` 文件。Dify 不能只根据源码分支完成插件安装。

### Base URL 是否需要带 `/v1`

可以不带，也可以带。插件会规范化 Base URL，避免重复拼接 `/v1`。

## 本地开发

常用命令：

```bash
python -m uv sync
python -m uv run ruff check .
python -m uv run pytest
python -m uv run pytest tests/test_provider_schema.py
```

## 更多文档

- [安装说明](docs/installation.md)
- [配置说明](docs/configuration.md)
- [故障排查](docs/troubleshooting.md)
- [英文 README](README.md)

## 许可证

本项目使用 Apache License 2.0。详见 [LICENSE](LICENSE)。
