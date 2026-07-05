# AxonHub Dify 插件

[![CI](https://github.com/openshell/dify-plugin-axonhub/actions/workflows/ci.yml/badge.svg)](https://github.com/openshell/dify-plugin-axonhub/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-6C5CE7.svg)](https://dify.ai)

`dify-plugin-axonhub` 是一个面向 [Dify](https://dify.ai) 的 AxonHub 模型供应商插件。安装后，Dify 可以把 AxonHub 作为独立模型供应商使用，并通过 AxonHub 兼容接口调用大语言模型、文本嵌入模型和重排模型。

相比只使用 Dify 的通用 OpenAI-compatible provider，本插件提供了更贴近 AxonHub 的配置体验、预定义模型列表、自定义模型兜底和请求追踪能力。

## 功能亮点

- 在 Dify 中提供独立的 **AxonHub** 模型供应商。
- 通过 `/v1/chat/completions` 支持 Chat LLM。
- 通过 `/v1/embeddings` 支持 Text Embedding，并使用 `encoding_format=float`。
- 通过 `/v1/rerank` 支持 Rerank。
- 内置预定义模型 YAML，安装后可在 Dify 中直接显示已知 AxonHub 模型。
- 支持自定义模型，适用于新增模型、私有模型或租户专属模型。
- 支持可选追踪 Header：`AH-Trace-Id` 和 `AH-Thread-Id`。
- 错误处理会避免在异常信息中暴露 API Key。

## 支持的模型类型

| Dify 模型类型 | AxonHub 端点 | 状态 | 说明 |
| --- | --- | --- | --- |
| LLM | `/v1/chat/completions` | 已支持 | 通过 Dify OpenAI-compatible 模型路径支持流式输出。 |
| Text Embedding | `/v1/embeddings` | 已支持 | 支持批量输入和 float embedding。 |
| Rerank | `/v1/rerank` | 已支持 | 使用 AxonHub Jina-compatible rerank API。 |

## 快速开始

### 方式一：安装 Release 包

1. 打开项目的 [GitHub Releases](https://github.com/openshell/dify-plugin-axonhub/releases) 页面。
2. 下载目标版本的 `.difypkg` 文件。
3. 在 Dify 中打开 **Plugins** / **Plugin Management**。
4. 上传 `.difypkg` 文件。
5. 安装完成后，进入 AxonHub provider 配置页面并填写凭据。

> Dify 的 GitHub 安装方式依赖 GitHub Release 中的 `.difypkg` 资产。只有源码分支还不够。

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

打包插件：

```bash
.tools/dify-plugin plugin package .
```

然后在 Dify 中上传生成的 `.difypkg` 文件。

## 配置说明

在 Dify 的 AxonHub provider 配置页填写：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `AxonHub Base URL` | 是 | AxonHub 地址。可以填写 `http://localhost:8090` 或 `http://localhost:8090/v1`。 |
| `AxonHub API Key` | 是 | AxonHub Bearer Token。不要在 issue、截图或日志中公开。 |
| `Enable model auto discovery` | 否 | 启用后会通过 AxonHub 模型发现接口校验凭据。 |
| `Enable tracing headers` | 否 | 启用后请求会携带 `AH-Trace-Id` 和 `AH-Thread-Id`。 |
| `Request timeout seconds` | 否 | 请求 AxonHub API 的超时时间。 |

如果某个 AxonHub 模型不在预定义模型列表中，可以在 Dify 中添加自定义模型，并将模型类型设置为 `llm`、`text-embedding` 或 `rerank`。当 Dify 展示名和实际 AxonHub 模型名不一致时，可以填写 `AxonHub endpoint model name`。

## 文档

- [安装说明](docs/installation.md)
- [配置说明](docs/configuration.md)
- [故障排查](docs/troubleshooting.md)
- [架构说明](docs/architecture.md)
- [开发指南](docs/development.md)
- [路线图](ROADMAP.md)
- [English README](README.md)

## 项目结构

```text
manifest.yaml                 # Dify 插件元数据
provider/axonhub.yaml          # Provider schema 和模型注册
provider/axonhub.py            # Provider 凭据校验
models/llm/                    # LLM 实现与预定义模型
models/text_embedding/         # Embedding 实现与预定义模型
models/rerank/                 # Rerank 实现
axonhub/                       # AxonHub client、模型映射、错误处理和 tracing
docs/                          # 用户和贡献者文档
tests/                         # 单元测试和 schema 回归测试
```

## 本地开发

```bash
python -m uv sync
python -m uv run ruff check .
python -m uv run pytest
```

贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。发布前请参考 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)。

## 安全说明

请不要在 GitHub issue 或 pull request 中发布 API Key、`Authorization` Header、`.env` 内容或私有端点信息。漏洞报告方式见 [SECURITY.md](SECURITY.md)。

## 许可证

本项目使用 Apache License 2.0。详见 [LICENSE](LICENSE)。
