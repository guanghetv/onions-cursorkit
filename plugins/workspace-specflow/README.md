# workspace-specflow

统一工作区多角色协作工作流插件：在 **specs 仓库** 内串联产品 PRD、测试 spec、开发启动与进度总览。

---

## 插件解决什么问题

- **单一真相源**：`requirements/<requirement-id>/` 下的 `prd.md` 与 `test/test-spec.md` 是产品与测试产出的权威版本；飞书文档可作为展示层，但以 specs 仓库为准。
- **角色分工清晰**：每人通过对应命令完成本角色步骤，减少在聊天里重复解释流程。
- **需求与代码分层、多根友好**：需求与讨论在 specs 仓库；编码与契约处理在各自业务仓完成。多根工作区下可直接读取本地需求资料，减少手工同步。

---

## 分层架构（必读）

| 层级 | 所在位置 | 插件 | 主要职责 |
|------|-----------|------|----------|
| **需求仓库** | specs 仓库（如 `<your-specs-repo>`） | **workspace-specflow** | PRD、结构化产品 spec、测试 spec、元数据与进度；依赖 Superpowers（如 brainstorming） |
| **代码仓库** | 各业务代码仓库 | 各仓库自身流程 | 技术设计、TDD、联调、验证、归档 |

两层通过需求语义与模块边界对齐；**prd.md** 是产品侧需求的锚点，**MODULE** ID 在产品 spec 与测试 spec 之间保持一致。

---

## 按角色说明

### 产品（PM）

**你在流程中的位置**：发起需求目录（最小初始化）→ 先生成并完善原型 → 执行 `/pm-spec` 补充与结构化 PRD → 确认后流转开发和测试。

| 能力 | 命令 | 说明 |
|------|------|------|
| 新建需求骨架 | `/req-new` | 输入需求想法或飞书需求文档链接，自动生成 `requirements/<id>/`（含 `metadata.yaml`、`prd.md` 模板、`test/test-spec.md` 空模板等）。目录名为 kebab-case。 |
| 原型快速生成（可选） | `/pm-proto` | 在需求目录生成或迭代 `prototypes/` 与可选 `assets/`，为 `prd.md` 提供可引用素材。 |
| PRD 结构化增强 | `/pm-spec` | 在原型基础上补充并增强 **已有** `prd.md`（不覆盖原文）：brainstorming、MODULE 拆分、验收标准、AI Review；详细评审记录写入 `prototypes/ai-review.md`，`prd.md` 仅保留可开工结论。 |
| 看进度 | `/req-status` | 查看各需求 PRD / 测试状态。 |

**典型顺序**：`/req-new` → `/pm-proto`（先原型）→ `/pm-spec`（补充并结构化 PRD）→ 确认后通知测试与开发可并行推进。

**权限与边界**（需求目录内）：可读写 `prd.md`、`metadata.yaml`、`prototypes/`、`assets/`；对代码仓库仅 **只读扫描**（用于业务影响分析，不写实现细节到 PRD）。**禁止**改业务代码仓库文件。

**依赖提示**：`/req-new`、`/pm-spec` 在需要读飞书文档时优先使用 **lark-cli**；`lark-cli` 不可用时可降级 **feishu-mcp**；两者都不可用时应提示安装 **lark-cli**。结构化讨论依赖 **Superpowers** 的 brainstorming。

---

### 测试（QA）

**你在流程中的位置**：在产品 PRD 已确认（`prd.status = confirmed`）后，基于 **仅** `prd.md`（及原型等）编写 `test/test-spec.md`，可与开发并行；可选经 **`/qa-sync-xmind`** 导出 XMind（**中间产物**，走 MCP 工作目录）导入飞书或本地编辑后再 **import** 回写，**不在 specs 仓库中保留 `.xmind`**。

| 能力 | 命令 | 说明 |
|------|------|------|
| 生成并确认测试 spec | `/qa-spec` | 读取 `prd.md`，brainstorming 测试策略，生成与 MODULE 对齐的 `test/test-spec.md`，做覆盖率校验后可将 `test_spec.status` 置为 `confirmed`。 |
| Markdown ↔ XMind | `/qa-sync-xmind` | `export`：从 `test-spec.md` 生成 XMind（经 MCP 工作目录）；`import`：从 XMind 回写 `test-spec.md`（需 diff 确认）。 |
| 看进度 | `/req-status` | 同上。 |

**输入隔离（重要）**：`/qa-spec` **不得**读取 `openspec/changes/` 等开发产出，避免测试用例被实现细节「污染」；唯一主输入是产品 spec（`prd.md`）及原型等。

**典型顺序**：确认 specs 仓库已 `git pull` → `/qa-spec` → 需要时 `/qa-sync-xmind export` → 飞书导入或 XMind 编辑 → `/qa-sync-xmind import`。

**权限与边界**：可写 **`test/test-spec.md`**（测试 spec 唯一长期落盘处）、**`metadata.yaml`** 中与测试相关的状态字段；**`.xmind` 仅作中间产物**（由 `/qa-sync-xmind` 在 **MCP 工作目录**生成或编辑），**不纳入 Git、不保留在 specs 仓库**。对代码仓库只读扫描（识别可测行为与入口，不写代码）。

**依赖提示**：brainstorming；可选 **mcp-xmind**（`@41px/mcp-xmind`）用于 XMind 双向转换。

---

### 开发（前端 / 后端）

**你在流程中的位置**：在产品 PRD 已确认后，从需求层进入目标代码仓库开发流程。**不需要**等待测试 spec 才能开始开发（验证阶段会再汇合）。

| 能力 | 命令 | 说明 |
|------|------|------|
| 从需求进入编码流程 | `/dev-start` | 选择需求、扫描可能涉及的仓库、用自然语言对齐 MODULE，检测工作区是否包含目标仓库，然后在同一会话中进入开发流程。**本命令不写需求层文件**。 |
| 看进度 | `/req-status` | 查看需求层 PRD / 测试状态。 |

**典型顺序**：specs 仓库 `git pull` → `/dev-start` → 进入目标仓库上下文后的 **brainstorming → tasks → TDD** → 按需同步测试 spec / 对方 API 契约。

**多仓库**：若同一需求要改多个仓库，推荐 **「对齐单窗 + 实现分会话（或分阶段单窗）」**（见下文同名章节）：对齐阶段可单会话通览；**实现阶段**在 **不同会话** 中分别 `/dev-start`，每会话尽量只盯一个仓，避免混仓暂存区。

**权限与边界**：**禁止**随意改 `requirements/` 下文件。可读取 `prd.md` 与 `test/test-spec.md`（用于理解与验证）。代码仓库内按 fe-specflow / be-specflow 规范执行。

**代码仓库流程说明**：具体命令以目标仓库现有流程为准（前端与后端可能不同）。

---

### TL / 工程负责人（环境与仓库）

**一次性准备**（团队共享同一套约定时）：

- 建立 **specs 仓库**，包含 `requirements/`、`scripts/workspace-repos.json`、可选 `_archive/`、`docs/context/` 等。
- 配置 **`.code-workspace`**，把 specs 与各业务仓库列入多根工作区，便于开发时快速定位需求资料。
- 在团队环境安装 **workspace-specflow**，并确保成员安装 **Superpowers**；建议优先安装 **lark-cli**，并按需配置 **feishu-mcp**、**mcp-xmind**。
- 与 **fe-specflow / be-specflow** 的版本配套关系在团队内约定一致。

**`workspace-repos.json`**：登记各仓库逻辑名到路径，供 `/pm-spec`、`/qa-spec`、`/dev-start` 扫描与解析，避免硬编码绝对路径。

---

### 全员通用

| 能力 | 命令 | 适用场景 |
|------|------|----------|
| 需求进度一览 | `/req-status` | 项目经理、任何角色快速看 PRD / 测试状态；可指定单个需求看 MODULE 级详情。 |
| 新建需求 | `/req-new` | 通常由产品发起，也可由 TL 代建目录。 |

**协作习惯**：在读取或汇总 `requirements/` 前，建议在 specs 仓库执行 **`git pull`**，避免基于过期 PRD 讨论（规则 `workspace-awareness.mdc` 中亦强调）。

---

## 单人多仓：对齐单窗 + 实现分会话（或分阶段单窗）

适用于：**同一需求**要改 **多个代码仓库**（典型：前后端各一仓，或两个前端仓），且已在 Cursor 中打开 **多根工作区**、各仓分支已手动对齐。产品 spec（如 `prd.md`）已在 specs 仓库就绪。

### 为何不全靠「一个 Agent 窗改到底」

单会话同时改多仓，模型虽能**通览全局**，但容易：

- 混淆不同仓库下的任务边界，误写路径；
- **暂存区**混含多仓 diff，`/cr` 与 revert 变重；
- 上下文过长后反而丢失端到端一致性。

因此推荐把 **「全局对齐」** 与 **「按仓落地」** 拆开。

### 推荐节奏

| 阶段 | 建议的 Agent 用法 | 目标 |
|------|-------------------|------|
| **1. 对齐** | **单一会话**即可：读 `prd.md` / MODULE，必要时 **只读**扫前后端目录，把 **API 形状、错误码、MODULE 边界、先后依赖** 说清。本阶段尽量少改业务代码，或只改一处契约源。 |
| **2. 实现** | **分会话（推荐）**：每个代码仓库一个会话，在该会话内完整跑该仓流程（含 TDD、提交前审查、合并前 CR 等），一次只 commit 一个仓。 |
| **2′. 分阶段单会话（备选）** | 若坚持用单会话：须 **显式 checkpoint**——例如「本段仅改后端仓，直至 `git commit` 完成；下一段仅改前端仓」，每段前后核对 `git status` **只出现一个仓库**的变更。 |

### 与现有命令的配合

- 每仓进入实现前，可在该仓会话执行 **`/dev-start`**，避免重复追问来源。
- 跨仓契约与测试 spec 在代码仓库流程内处理。
- 进度用 **`/req-status`** 汇总需求层状态。

### 未安装 workspace-specflow 时

上述 **「对齐 vs 按仓实现」** 习惯仍适用；仅缺少 specs 仓命令与部分自动化能力，开发仍以当前仓库流程为界。

---

## 命令速查（与角色对照）

| 命令 | 主要角色 | 一句话 |
|------|----------|--------|
| `/req-new` | 产品 / TL | 最小初始化需求目录（想法或飞书链接） |
| `/pm-proto` | 产品 | 原型快速生成与迭代（可选） |
| `/pm-spec` | 产品 | PRD 结构化增强 + AI Review |
| `/qa-spec` | 测试 | PRD → 测试 spec |
| `/qa-sync-xmind` | 测试 | test-spec.md ↔ XMind |
| `/dev-start` | 开发 | 需求层资料导入当前仓库开发流程 |
| `/req-status` | 全员 | 进度总览 |

---

## 激活条件

通过 `rules/workspace-awareness.mdc` 的 **globs** 生效：工作区需同时包含 **`requirements/`** 目录与 **`workspace-repos.json`**（通常在 `scripts/` 下）。不满足时本插件规则不会注入，不影响常规代码仓库开发。

---

## specs 仓库结构（参考）

```
<specs-repo>/
  requirements/                 # 活跃需求（扁平：一级子目录即需求）
    <requirement-id>/
      prd.md                    # 产品 PRD（撰写 + /pm-spec 增强）
      metadata.yaml             # prd / test_spec 等状态
      prototypes/               # 原型（可选）
      assets/                   # 截图、流程图等可视化素材（可选）
      test/
        test-spec.md            # 测试 spec
  _archive/                     # 历史需求（与 requirements 同级）
  docs/context/                 # 业务上下文知识库
  scripts/
    workspace-repos.json        # 仓库路径注册表
```

---

## 权限模型（摘要）

| 角色 | `requirements/` 读 | `requirements/` 写 | 代码仓库 |
|------|---------------------|---------------------|----------|
| 产品 | prd.md、metadata.yaml 等 | prd.md、prototypes/、metadata.yaml | 只读 |
| 测试 | prd.md 等 | `test/test-spec.md`、`metadata.yaml`（测试相关字段）；XMind 为中间产物不入库 | 只读 |
| 开发 | prd.md、test/test-spec.md | 不修改 `requirements/` 下文件 | 读写 |

---

## 依赖

- **Superpowers**（brainstorming 等）
- **lark-cli**（飞书文档读取首选；建议团队统一安装）
- **feishu-mcp**（飞书读取兜底方案；当 `lark-cli` 不可用时使用）
- **mcp-xmind**（`@41px/mcp-xmind`，可选，用于 `/qa-sync-xmind`）
- 多根工作区中的代码仓库开发流程能力（按团队实际配置）
