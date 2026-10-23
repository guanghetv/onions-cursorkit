# workspace-specflow

统一工作区多角色协作工作流插件：在 **specs 仓库** 内串联产品 PRD、测试 spec、开发启动与进度总览。

---

## 插件解决什么问题

- **单一真相源**：`requirements/<中文目录名>/` 下的 `prd.md` 与 `test/test-spec.md` 是权威版本；`metadata.id` 为稳定英文 slug。
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

**你在流程中的位置**：发起需求目录（含创建飞书文档）→ 原型 → `/pm-spec` 多轮改本地文档 → `/prd-publish` 发布基线 → 通知需求群并引导提交代码。

| 能力 | 命令 | 说明 |
|------|------|------|
| 新建需求骨架 | `/req-new` | 中文目录 + `id`；本地骨架；目录创建后**必须** `/prd-feishu-sync create`（失败不得假装已绑定） |
| 原型 | `/pm-proto` | 只留核心页面流程和交互，不写占位文案和操作引导 |
| 编写需求 | `/pm-spec` | 多轮只改本地 `prd.md`。每一轮先提示三端差异。写完后二次确认，再引导 `/prd-publish`。不在这一步设 `confirmed` |
| 产品需求风险预检 | `/prd-risk` | 报告落 `prototypes/prd-risk-precheck.md`。发布时按新鲜度自动跑；「需调整」阻止发布，「待补信息」可继续 |
| 飞书同步 | `/prd-feishu-sync` | create / reconcile / status / rebind。用户说同步到飞书时不走这里，改走 `/prd-publish` |
| 发布前检查 | `/prd-check` | 内容、对齐、可读性一次完成。旧命令 `/prd-consistency-check` 走这里 |
| 发布基线 | `/prd-publish` | 本地已写完且用户第二次确认发布，或单独说「同步到飞书」时走这里。预检 → push → `/prd-check` → 快照、版本表、`revision_id`，然后发短通知并引导提交代码。第一次成功才 `confirmed`。再次发布时，只给相对上一份基线新变化的正文加红，已有红色和版本表旧行保留。无群时发布仍成功 |
| 看进度 | `/req-status` | 是否已确认、基线 revision、测试状态 |

**典型顺序**：`/req-new` → `/pm-proto` → `/pm-spec`（可多轮）→ `/prd-publish`。

**三端**：原型、飞书文档、`prd.md`。任一端先改时，先按 `references/three-way-sync.md` 提示差异，确认前不写另外两端。工作区改需求，或从飞书拉回，都先写入本地 `prd.md`，再二次确认并引导 `/prd-publish`。产品先手改飞书再贴回工作区：走 `/prd-feishu-sync reconcile`，或在对话里贴链接要求同步回来时按同一规程；拉回不跑 `/prd-check`、不钉基线。禁止用粘贴正文直接覆盖 `prd.md`。

**文档角色**：飞书文档给人读，`prd.md` 给 Agent。两端都保留当前有效规则，变更记在版本表。已发布后，飞书序号不等于 `prd.baseline.revision_id`，或本地 `prd.md` 正文偏离基线快照时，除 `/qa-spec` 外的下游读基线快照。群内查询不是产品命令，由葱明-multica 使用技能 `prd-change`。

**PRD 模板**：新建文档标题用需求名。骨架是需求概述、版本表、背景与目标、需求详情，文末一块「文档状态」。关键关注、回归范围等有内容才加。旧飞书七章模板只作兼容：https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg

**飞书正文写作规范**：[产品组 PRD 写作规范 V1.0](https://guanghe.feishu.cn/docx/Cqtqd9BxJoUYAFxbXFocp2qYnWd)，插件内副本为 `references/产品组PRD写作规范.md`。

**权限与边界**（需求目录内）：可读写 `prd.md`、`metadata.yaml`、`prototypes/`、`assets/`；对代码仓库仅 **只读扫描**。**禁止**改业务代码仓库文件。

**依赖提示**：飞书读写优先 **lark-cli**。**`/pm-proto`、`/pm-spec` 须先 brainstorming 并获用户放行**。查询现有实现先调用 CodeWiki `search_wiki`。

---

### 测试（QA）

**你在流程中的位置**：基于 `prd.md` 或飞书需求文档链接编写 `test/test-spec.md`，可与开发并行。未确认、一致性失败或基线漂移时仍生成，并在结果里提示。可选经 **`/qa-sync-xmind`** 导出 XMind（**中间产物**，走 MCP 工作目录）导入飞书或本地编辑后再 **import** 回写，**不在 specs 仓库中保留 `.xmind`**。

| 能力 | 命令 | 说明 |
|------|------|------|
| 生成并确认测试 spec | `/qa-spec` | 从需求详情提取规则。输入可以是 `prd.md` 或飞书链接。门禁只提示，不阻断生成。 |
| Markdown ↔ XMind | `/qa-sync-xmind` | `export`：从 `test-spec.md` 生成 XMind（经 MCP 工作目录）；`import`：从 XMind 回写 `test-spec.md`（需 diff 确认）。 |
| 上传 Case Flow 执行 | `/qa-execute` | 将 `test/*.md` 上传至 [Case Flow 快速模式](https://ai-case-flow.yc345.tv/quick)；自动识别 test-spec 格式或嵌套列表直传。 |
| 看进度 | `/req-status` | 同上。 |

**输入隔离（重要）**：`/qa-spec` **不得**读取 `openspec/changes/` 等开发产出。主输入是需求详情（`prd.md`、飞书文档或基线快照）及原型。

**典型顺序**：确认 specs 仓库已 `git pull` → `/qa-spec` → 需要时 `/qa-sync-xmind export` → 飞书导入或 XMind 编辑 → `/qa-sync-xmind import` → **`/qa-execute`** 导入 Case Flow 执行。

**权限与边界**：可写 **`test/test-spec.md`**（测试 spec 唯一长期落盘处）、**`metadata.yaml`** 中与测试相关的状态字段；**`.xmind` 仅作中间产物**（由 `/qa-sync-xmind` 在 **MCP 工作目录**生成或编辑），**不纳入 Git、不保留在 specs 仓库**。对代码仓库只读扫描（识别可测行为与入口，不写代码）。

**依赖提示**：brainstorming；可选 **mcp-xmind**（`@41px/mcp-xmind`）用于 XMind 双向转换；**`/qa-execute`** 需 Python 3.9+ 与 `curl`。

---

### 开发（前端 / 后端）

**你在流程中的位置**：在产品 PRD 已确认（`prd.status = confirmed`）后，在目标代码仓库按 **fe-specflow / be-specflow / onion-sdd** 启动开发。**不需要**等待测试 spec 才能开始开发（验证阶段会再汇合）。本插件**不再提供** `/dev-start`。

| 能力 | 做法 | 说明 |
|------|------|------|
| 进入编码流程 | 代码仓库既有 SDD 命令 | 已确认且未漂移时读 `prd.md`。漂移或只有旧快照时读基线快照；可用 `/req-status` 定位需求 |
| 看进度 | `/req-status` | 查看需求层 PRD / 测试状态 |

**典型顺序**：specs 仓库 `git pull` → 确认需求已发布且未漂移 → 在目标仓库会话执行开发流程（brainstorming → tasks → TDD）→ 按需同步测试 spec / 对方 API 契约。

**多仓库**：推荐 **「对齐单窗 + 实现分会话（或分阶段单窗）」**（见下文同名章节）：对齐阶段可单会话通览；实现阶段每会话尽量只盯一个仓。

**权限与边界**：**禁止**随意改 `requirements/` 下文件。可读取 `prd.md` 与 `test/test-spec.md`（用于理解与验证）。

---

### TL / 工程负责人（环境与仓库）

**一次性准备**（团队共享同一套约定时）：

- 建立 **specs 仓库**，包含 `requirements/`、`scripts/workspace-repos.json`、可选 `_archive/`、`docs/context/` 等。
- 配置 **`.code-workspace`**，把 specs 与各业务仓库列入多根工作区，便于开发时快速定位需求资料。
- 在团队环境安装 **workspace-specflow**，并确保成员安装 **Superpowers**；建议优先安装 **lark-cli**，并按需配置 **feishu-mcp**、**mcp-xmind**。
- 与 **fe-specflow / be-specflow** 的版本配套关系在团队内约定一致。

**`workspace-repos.json`**：登记各仓库逻辑名到路径，供 `/pm-spec`、`/qa-spec` 等扫描与解析，避免硬编码绝对路径。

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

- 每仓进入实现前，在该仓会话直接引用已确认的 `prd.md` / MODULE，避免重复追问来源。
- 跨仓契约与测试 spec 在代码仓库流程内处理。
- 进度用 **`/req-status`** 汇总需求层状态。

### 未安装 workspace-specflow 时

上述 **「对齐 vs 按仓实现」** 习惯仍适用；仅缺少 specs 仓命令与部分自动化能力，开发仍以当前仓库流程为界。

---

## 命令速查（与角色对照）

| 命令 | 主要角色 | 一句话 |
|------|----------|--------|
| `/req-new` | 产品 / TL | 中文目录 + 写作规范骨架 |
| `/pm-proto` | 产品 | 原型（可选） |
| `/pm-spec` | 产品 | 多轮编写本地需求文档，提示三端差异；写完后二次确认再引导发布 |
| `/prd-risk` | 产品 | 产品需求风险预检 |
| `/prd-feishu-sync` | 产品 | 创建、回收、状态、换绑。同步到飞书走 `/prd-publish` |
| `/prd-check` | 产品 | 发布前一次检查内容、对齐和可读性 |
| `/prd-publish` | 产品 | 本地写完并二次确认后，或单独说同步到飞书时，发布基线并做三端校验 |
| `/qa-spec` | 测试 | PRD → 测试 spec |
| `/qa-sync-xmind` | 测试 | test-spec.md ↔ XMind |
| `/qa-execute` | 测试 | test/*.md → Case Flow 快速模式 |
| `/req-status` | 全员 | 进度总览 |

---

## 激活条件

通过 `rules/workspace-awareness.mdc` 的 **globs** 生效：工作区需同时包含 **`requirements/`** 目录与 **`workspace-repos.json`**（通常在 `scripts/` 下）。不满足时这条流程规则不会注入，不影响常规代码仓库开发。

`rules/agent-hard-rules.mdc` 为 `alwaysApply`。插件启用后，写飞书需求文档、处理评论、查询现有功能或代码时都必须执行。

## 权威副本

`plugins/workspace-specflow/` 是唯一维护源。Cursor 已安装副本在插件缓存里，保存本仓库不会自动更新缓存。specs 仓库里的产品会话要用到新技能，需要在 Cursor 里重新安装或刷新该插件。

在 cursorkit 本仓库改插件、评审流程时，只读本目录。缓存里的 `workspace-specflow` 与本目录不一致时，以本目录为准。

当前版本 `2.0.2`。Codex 分发包不跟着 Cursor 缓存走。源技能、`references/` 或 `rules/` 变了之后，在仓库根执行 `python3 codex-plugins/workspace-specflow/scripts/pack.py sync`，再 `check`。未 sync 之前，Codex 的 `source-lock.json` 会落后于本目录。

---

## specs 仓库结构（参考）

```
<specs-repo>/
  requirements/
    订单退款流程优化/           # 中文目录名（新需求）
      prd.md                    # 写作规范 + MODULE
      metadata.yaml             # id: order-refund-flow-opt
      snapshots/                # prd-v5-*.md, prd-v9-*.md
      prototypes/
      assets/
      test/test-spec.md
    contract-subject-tree/      # 既有英文目录（共存）
  _archive/
  scripts/workspace-repos.json
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
- **Python 3.9+**、**curl**（用于 `/qa-execute` 上传 Case Flow）
- 多根工作区中的代码仓库开发流程能力（按团队实际配置）

> 若此前单独安装过 `cursor-plugin-qa-execute`，合并后请卸载该独立插件，避免 Cursor 中出现重复的 `/qa-execute` 命令。
