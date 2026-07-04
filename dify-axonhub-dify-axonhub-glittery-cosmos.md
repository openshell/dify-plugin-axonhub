# dify-plugin-axonhub 增强版开发方案

## Context

目标是做一个独立开源项目 `dify-plugin-axonhub`，让 Dify 能把 AxonHub 当作一等模型供应商使用，而不是仅通过通用 OpenAI-compatible Provider 勉强接入。

用户选择的项目边界：

- 项目定位：Dify 插件优先
- 首个开源仓库形态：独立仓库
- 目标版本：增强版，不止稳定调用，还要体现 AxonHub 相比普通 OpenAI-compatible endpoint 的差异化体验

AxonHub 已具备增强版需要的核心接口：

- `POST /v1/chat/completions`：OpenAI-compatible 文本生成，支持 streaming 和 function tools
- `POST /v1/embeddings`：OpenAI-compatible embedding
- `POST /v1/rerank`：Jina-compatible rerank
- `GET /v1/models`：基础模型列表
- `GET /v1/models?include=all`：扩展模型列表，返回 `name`、`description`、`context_length`、`max_output_tokens`、`modalities`、`capabilities`、`pricing`、`type` 等元数据
- `AH-Trace-Id`、`AH-Thread-Id`：用于 AxonHub 请求追踪

因此增强版的核心不是重写协议，而是：

1. 复用 Dify OpenAI-compatible 模型调用路径保证稳定性。
2. 通过 AxonHub `/v1/models?include=all` 自动发现模型和能力。
3. 把 AxonHub 的模型类型、能力、上下文、价格信息映射成 Dify 模型实体。
4. 在调用时注入 AxonHub tracing headers，为后续 trace/cost/治理能力打基础。

## Product scope

### 增强版必须完成

1. Dify 中出现独立 Provider：`AxonHub`。
2. Provider credential 支持：
   - AxonHub Base URL
   - AxonHub API Key
   - 是否启用模型自动发现
   - 是否启用 tracing headers
3. 自动发现 AxonHub 模型：
   - 调用 `/v1/models?include=all`
   - 识别 chat/embedding/rerank 类型
   - 读取模型能力：vision、tool_call、reasoning
   - 读取上下文长度与最大输出 token
   - 读取价格信息并映射到 Dify 模型价格展示
4. 支持三类模型调用：
   - `llm` → `/v1/chat/completions`
   - `text-embedding` → `/v1/embeddings`
   - `rerank` → `/v1/rerank`
5. 支持手动模型兜底：
   - 当 AxonHub 模型列表缺少 ModelCard 或 `/v1/models` 不可用时，允许用户手动配置模型名和能力。
6. 请求追踪：
   - 每次调用生成/透传 `AH-Trace-Id`
   - 尽量使用 Dify conversation/user/request 上下文生成稳定 `AH-Thread-Id`
   - 在 debug log 中记录 trace id，方便用户回到 AxonHub 查看链路
7. 文档和开源发布：
   - README
   - 安装指南
   - AxonHub 配置指南
   - Dify 配置指南
   - 常见问题
   - 示例截图或流程说明

### 增强版暂不做

这些能力保留为后续版本，避免首版过大：

- 在 Dify UI 内直接展示 AxonHub trace/cost dashboard iframe 或深链
- 在 Dify 内管理 AxonHub channel/model association/profile
- 自动创建 AxonHub API Key/Profile
- image generation、TTS、STT、Realtime
- 修改 Dify 主仓前端

## Repository layout

独立仓库建议结构：

```text
dify-plugin-axonhub/
  manifest.yaml
  main.py
  pyproject.toml
  uv.lock
  provider/
    axonhub.yaml
    axonhub.py
  models/
    llm/
      llm.py
    text_embedding/
      text_embedding.py
    rerank/
      rerank.py
  axonhub/
    client.py
    errors.py
    model_mapper.py
    tracing.py
  tests/
    test_client.py
    test_model_mapper.py
    test_llm.py
    test_embedding.py
    test_rerank.py
  _assets/
    icon.svg
  README.md
  README.zh-CN.md
  .env.example
  .difyignore
```

## Critical files to implement

### `manifest.yaml`

声明插件基础信息：

- `type: plugin`
- `name: axonhub`
- `label: AxonHub`
- `plugins.models: ["provider/axonhub.yaml"]`
- `resource.permission.model.enabled: true`
- 开启 `llm`、`text_embedding`、`rerank` 权限
- Python runner 使用 3.12

### `provider/axonhub.yaml`

Provider 配置建议分 provider-level 和 model-level 两层。

Provider-level credential：

- `endpoint_url`：AxonHub Base URL，例如 `http://localhost:8090/v1`
- `api_key`：AxonHub API Key
- `auto_discovery`：是否启用 `/v1/models?include=all`
- `enable_tracing`：是否注入 `AH-Trace-Id`、`AH-Thread-Id`
- `request_timeout`：请求超时

Model-level credential：

- `model`：Dify 侧模型 ID
- `endpoint_model_name`：发送给 AxonHub 的模型 ID，可选；默认等于 `model`
- `display_name`
- `model_type`：llm/text-embedding/rerank
- `context_size`
- `max_tokens_to_sample`
- `vision_support`
- `tool_call_support`
- `reasoning_support`
- `structured_output_support`
- `compatibility_mode`

### `axonhub/client.py`

封装 AxonHub HTTP 调用：

- `list_models(include="all")`
- `validate_credentials()`
- `chat_completions(...)`
- `embeddings(...)`
- `rerank(...)`

注意：

- Base URL 统一规范化，允许用户填 `http://host:8090` 或 `http://host:8090/v1`
- 认证统一使用 `Authorization: Bearer <api_key>`
- 错误响应统一解析 OpenAI-style `{error: {message,type,code}}`
- 不记录 API Key

### `axonhub/model_mapper.py`

把 AxonHub `/v1/models?include=all` 返回值映射到 Dify 模型实体。

映射规则：

- `type=chat` → Dify `llm`
- `type=embedding` → Dify `text-embedding`
- `type=rerank` → Dify `rerank`
- `context_length` → Dify context size / max token parameter
- `max_output_tokens` → Dify upper bound for max tokens
- `capabilities.vision=true` → Dify `ModelFeature.VISION`
- `capabilities.tool_call=true` → Dify tool/function calling support
- `capabilities.reasoning=true` → Dify thinking/reasoning 参数
- `pricing.input/output/cache_read/cache_write` → Dify price config，单位从 per_1m_tokens 转换为 Dify 使用的 token price unit
- `name` → label
- `description` → model description

容错：

- 没有 extended metadata 时仍返回基础模型。
- `type` 缺失时，默认按 LLM 处理，但允许用户手动指定。
- capability 缺失时默认关闭，不猜测。

### `axonhub/tracing.py`

生成 AxonHub tracing headers：

- `AH-Trace-Id`
- `AH-Thread-Id`

建议策略：

- `AH-Trace-Id`：每次 invoke 生成唯一值，格式如 `dify-<uuid>`
- `AH-Thread-Id`：优先从 Dify user/conversation/request 可用上下文派生；拿不到时按当前 invoke 生成
- headers 通过 OpenAI client default headers 或 requests headers 注入

### `provider/axonhub.py`

职责：

- 继承 `dify_plugin.ModelProvider`
- 校验 provider-level credentials
- 调用 `AxonHubClient.list_models(include="all")` 或基础请求验证 API Key
- 如果 Dify SDK 支持 provider 动态模型列表，在这里暴露自动发现模型；否则通过 model class 的 `get_customizable_model_schema` 和文档/辅助脚本实现半自动配置

### `models/llm/llm.py`

职责：

- 继承 Dify SDK 的 `OAICompatLargeLanguageModel`
- 复用 OpenAI-compatible 调用逻辑
- 在 `_invoke` 前处理：
  - `endpoint_model_name or model`
  - tracing headers
  - structured output
  - tool calling
  - reasoning/thinking 参数
  - token 参数名兼容
- 在 `get_customizable_model_schema` 中使用 AxonHub metadata 设置 Dify model features 和 parameter rules
- 在 `validate_credentials` 中执行轻量 chat 请求

### `models/text_embedding/text_embedding.py`

职责：

- 继承 `OAICompatEmbeddingModel`
- 调用 `/v1/embeddings`
- 支持 batch input
- 支持 `encoding_format=float`
- 支持 `dimensions`
- 使用 AxonHub metadata 设置 context size、price、display name

### `models/rerank/rerank.py`

职责：

- 实现 Dify rerank model interface
- 调用 `/v1/rerank`
- 请求格式：`model`、`query`、`documents`、`top_n`、`return_documents`
- 响应映射：`results[].index`、`results[].relevance_score`、`usage`

## Dynamic discovery design

增强版的关键是模型自动发现，但需要注意 Dify 插件系统可能对动态模型列表有限制。因此采用双路径：

### Path A：插件内动态发现

如果 Dify SDK 当前 model provider interface 支持动态 `get_models`/model schema list：

1. 用户配置 provider credentials。
2. 插件调用 `GET /v1/models?include=all`。
3. 插件按 type/capability 映射模型。
4. Dify UI 中展示 AxonHub 返回的模型。

### Path B：半自动发现 + 手动注册兜底

如果 Dify SDK 不支持动态 provider model list 或 UI 不支持动态下拉：

1. 插件 provider credential 校验时检查 `/v1/models?include=all` 是否可用。
2. README 提供 `axonhub-discover` 辅助命令或脚本，输出可复制到 Dify 的模型配置。
3. Dify 里仍允许用户手动新增模型。
4. `get_customizable_model_schema` 根据模型名从 AxonHub metadata cache 获取能力；拿不到时使用用户手动配置。

建议优先实现 Path B 保证兼容，再根据实际 Dify SDK 能力补 Path A。

## Open-source project plan

### Release v0.1.0：Enhanced MVP

目标：稳定调用 + 模型发现基础能力。

包含：

- Provider branding：AxonHub
- LLM chat/completion
- streaming
- embedding
- rerank
- `/v1/models?include=all` client
- metadata mapper
- manual fallback
- tracing headers
- README/中文 README
- 基础单元测试

### Release v0.2.0：Dify 体验增强

包含：

- 更完整的能力映射
- 更好的模型发现缓存
- 更详细错误提示
- Dify 安装包发布流程
- 示例 Chatflow/Knowledge Base 配置文档

### Release v0.3.0：AxonHub 网关能力增强

包含：

- Trace deep link 文档或字段展示
- Profile 使用指南
- Cost/Quota 文档化
- 与 AxonHub 版本兼容矩阵

## Verification plan

### Unit tests

- `AxonHubClient`：
  - base URL normalization
  - auth header
  - `/v1/models?include=all` parsing
  - OpenAI-style error parsing
- `model_mapper`：
  - chat → llm
  - embedding → text-embedding
  - rerank → rerank
  - vision/tool_call/reasoning capability mapping
  - pricing mapping
  - missing metadata fallback
- LLM/Embedding/Rerank：
  - credential validation
  - request payload
  - response mapping
  - error mapping

### Local integration tests

1. 启动 AxonHub：`http://localhost:8090`
2. 配置至少三个模型：
   - chat model
   - embedding model
   - rerank model
3. 使用 AxonHub API Key 测试：
   - `GET /v1/models?include=all`
   - `POST /v1/chat/completions`
   - `POST /v1/embeddings`
   - `POST /v1/rerank`
4. 在 Dify 中安装插件并验证：
   - 新增 AxonHub Provider
   - 校验 credentials
   - Chatflow 非流式调用
   - Chatflow 流式调用
   - Knowledge Base embedding
   - RAG rerank
   - AxonHub trace 页面能看到带 `AH-Trace-Id` 的请求

### Packaging checks

- `uv sync`
- `uv run ruff check .`
- `uv run pytest`
- Dify plugin package/build 命令
- 在干净 Dify 环境安装 `.difypkg`

## Risks and mitigations

### Risk 1：Dify 动态模型列表能力不足

Mitigation：保留手动模型配置和半自动发现脚本；不要把自动发现作为唯一入口。

### Risk 2：AxonHub metadata 不完整

Mitigation：缺字段不阻塞调用，能力默认关闭，允许用户手动覆盖。

### Risk 3：不同上游模型 tool/reasoning/vision 兼容性不同

Mitigation：以 AxonHub `/v1/models?include=all` capability 为准；用户可在 Dify 模型 credential 中覆盖。

### Risk 4：Tracing headers 在 Dify SDK OpenAI-compatible 基类中不易注入

Mitigation：优先使用 OpenAI client default headers；若基类不支持，则在 AxonHub LLM/Embedding/Rerank 中覆盖 client 创建逻辑。

### Risk 5：Rerank 不是 OpenAI 标准接口

Mitigation：单独实现 rerank model，不复用 OpenAI-compatible 基类。

## Required decisions before implementation

- 是否首版必须包含 rerank：建议包含，因为 AxonHub 已支持 `/v1/rerank`，且 Dify RAG 场景价值明显。
- 是否首版支持 image generation：建议不包含，避免扩散范围。
- 是否需要中英文 README：建议必须包含，符合项目开源传播场景。
- 是否需要发布到 Dify Marketplace：首版先提供 GitHub Release `.difypkg`，稳定后再提交 Marketplace 或 dify-official-plugins。

## External references

- AxonHub OpenAI API: `docs/en/api-reference/openai-api.md`
- AxonHub Embedding API: `docs/en/api-reference/embedding-api.md`
- AxonHub Rerank API: `docs/en/api-reference/rerank-api.md`
- AxonHub Model Management: `docs/en/guides/model-management.md`
- Dify official OpenAI-compatible plugin: `models/openai_api_compatible`
