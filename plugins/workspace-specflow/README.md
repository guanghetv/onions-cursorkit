# workspace-specflow

统一工作区多角色协作工作流插件：在 **specs 仓库（需求层）** 内串联产品 PRD、测试 spec、开发桥接与进度总览，并与 **fe-specflow / be-specflow（执行层）** 通过 `requirement_ref` 衔接。

---

## 插件解决什么问题

- **单一真相源**：`requirements/<requirement-id>/` 下的 `prd.md` 与 `test/test-spec.md` 是产品与测试产出的权威版本；飞书文档可作为展示层，但以 specs 仓库为准。
- **角色分工清晰**：每人通过对应命令完成本角色步骤，减少在聊天里重复解释流程。
- **需求与代码分层、多根友好**：需求与讨论在 specs 仓库；OpenSpec change、编码与契约拉取在各自业务仓由 **fe-specflow / be-specflow** 处理。多根工作区下 **`pull-spec`（workspace-aware）** 可从本地仓读 spec，无需反复切分支或手搓同步文件。

---

## 双层架构（必读）

| 层级 | 所在位置 | 插件 | 主要职责 |
|------|-----------|------|----------|
| **需求层** | specs 仓库（如 `<your-specs-repo>`） | **workspace-specflow** | PRD、结构化产品 spec、测试 spec、元数据与进度；依赖 Superpowers（如 brainstorming） |
| **执行层** | 各业务代码仓库 | **fe-specflow** / **be-specflow** | 技术设计、OpenSpec change、TDD、联调、验证、归档；依赖 Superpowers + OpenSpec |

两层通过 **`requirement_ref`**（通常写在执行层 `proposal.md` 中，并回连到需求目录）对齐；**prd.md** 是产品侧需求的锚点，**MODULE** ID 在产品 spec、测试 spec、change 之间保持一致。

---

## 按角色说明

### 产品（PM）

**你在流程中的位置**：发起需求目录 → 撰写或同步 PRD → 做结构化增强（MODULE、验收标准）→ 可选同步飞书 / 生成交互演示。

| 能力 | 命令 | 说明 |
|------|------|------|
| 新建需求骨架 | `/req-new` | 贴飞书需求文档链接，自动生成 `requirements/<id>/`（含 `metadata.yaml`、`prd.md` 模板、`test/test-spec.md` 空模板等）。目录名为 kebab-case。 |
| PRD 结构化增强 | `/pm-spec` | 在 **已有** `prd.md` 上做增强（不覆盖原文）：brainstorming、MODULE 拆分、验收标准、业务规则；可将 `prd.status` 置为 `confirmed`。 |
| 看进度 | `/req-status` | 查看各需求 PRD / 测试 / 各仓库 change 进度。 |

**典型顺序**：`/req-new` → 在 `prd.md` 中写完初稿（或从飞书拉取）→ `/pm-spec` → 确认后通知测试与开发可并行推进。

**权限与边界**（需求目录内）：可读写 `prd.md`、`metadata.yaml`、`prototypes/`；对代码仓库仅 **只读扫描**（用于业务影响分析，不写实现细节到 PRD）。交互演示仅写入本仓库的 `prodspecs/`，**禁止**改业务代码仓库文件。

**依赖提示**：`/req-new`、`/pm-spec` 在需要读飞书文档时依赖 **feishu-mcp**；结构化讨论依赖 **Superpowers** 的 brainstorming。

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

**你在流程中的位置**：在产品 PRD 已确认后，从需求层 **桥接** 到目标代码仓库的 **dev-workflow**（fe-specflow 或 be-specflow）。**不需要**等待测试 spec 才能开始开发（验证阶段会再汇合）。

| 能力 | 命令 | 说明 |
|------|------|------|
| 从需求进入编码流程 | `/dev-start` | 选择需求、扫描可能涉及的仓库、用自然语言对齐 MODULE，检测工作区是否包含目标仓库，然后 **在同一会话** 中启动 dev-workflow。**本命令不写任何文件、不创建 change**。 |
| 看进度 | `/req-status` | 查看需求与各仓库 change 的任务进度。 |

**典型顺序**：specs 仓库 `git pull` → `/dev-start` → 进入目标仓库上下文后的 **brainstorming → design-to-opsx**（在此创建 `openspec/changes/<change-id>/` 并回写 `metadata.yaml` 的 `changes`）→ tasks → TDD → 需要时由执行层 **`pull-spec`** 拉取测试 spec / 对方 API 契约。

**多仓库**：若同一需求要改多个仓库，推荐 **「对齐单窗 + 实现分会话（或分阶段单窗）」**（见下文同名章节）：对齐阶段可单会话通览；**实现阶段**在 **不同会话** 中分别 `/dev-start`，**每仓库一个 change、每会话尽量只盯一个仓**，避免混仓 OpenSpec 与混仓暂存区。

**权限与边界**：**禁止**随意改 `requirements/` 下文件；允许由 **design-to-opsx** 回写 `metadata.yaml` 的 **`changes`** 字段。可读取 `prd.md` 与 `test/test-spec.md`（用于理解与验证）。代码仓库内按 fe-specflow / be-specflow 规范执行。

**衔接执行层**：具体命令以目标仓库激活的 **dev-workflow** 为准（前端与后端插件略有差异，例如 design-to-opsx 产出结构）。

---

### TL / 工程负责人（环境与仓库）

**一次性准备**（团队共享同一套约定时）：

- 建立 **specs 仓库**，包含 `requirements/`、`scripts/workspace-repos.json`、可选 `_archive/`、`docs/context/`、`prodspecs/` 等。
- 配置 **`.code-workspace`**，把 specs 与各业务仓库列入多根工作区，便于开发与 `pull-spec` 本地发现。
- 在团队环境安装 **workspace-specflow**，并确保成员安装 **Superpowers**；按需配置 **feishu-mcp**、**mcp-xmind**。
- 与 **fe-specflow / be-specflow** 的版本配套关系在团队内约定一致。

**`workspace-repos.json`**：登记各仓库逻辑名到路径，供 `/pm-spec`、`/qa-spec`、`/dev-start` 扫描与解析，避免硬编码绝对路径。

---

### 全员通用

| 能力 | 命令 | 适用场景 |
|------|------|----------|
| 需求进度一览 | `/req-status` | 项目经理、任何角色快速看 PRD / 测试 / 各 change 状态；可指定单个需求看 MODULE 级详情。 |
| 新建需求 | `/req-new` | 通常由产品发起，也可由 TL 代建目录。 |

**协作习惯**：在读取或汇总 `requirements/` 前，建议在 specs 仓库执行 **`git pull`**，避免基于过期 PRD 讨论（规则 `workspace-awareness.mdc` 中亦强调）。

---

## 单人多仓：对齐单窗 + 实现分会话（或分阶段单窗）

适用于：**同一需求**要改 **多个代码仓库**（典型：前后端各一仓，或两个前端仓），且已在 Cursor 中打开 **多根工作区**、各仓分支已手动对齐。产品 spec（如 `prd.md`）已在 specs 仓库就绪。

### 为何不全靠「一个 Agent 窗改到底」

单会话同时改多仓，模型虽能**通览全局**，但容易：

- 混淆不同仓库下的 **`openspec/changes/<change-id>/`**，误写路径；
- **暂存区**混含多仓 diff，`/cr` 与 revert 变重；
- 上下文过长后反而丢失端到端一致性。

因此推荐把 **「全局对齐」** 与 **「按仓落地」** 拆开。

### 推荐节奏

| 阶段 | 建议的 Agent 用法 | 目标 |
|------|-------------------|------|
| **1. 对齐** | **单一会话**即可：读 `prd.md` / MODULE，必要时 **只读**扫前后端目录，把 **API 形状、错误码、MODULE 边界、先后依赖** 说清；产出落在 **契约真相源**（常见：后端 `proposal` API 段落、或 OpenAPI，再经执行层 **`pull-spec`** 到前端）。本阶段**尽量少改业务代码**，或只改一处「契约源」。 |
| **2. 实现** | **分会话（推荐）**：**每个代码仓库一个会话**，在该会话内完整跑该仓的 **fe-specflow / be-specflow `dev-workflow`**（含 TDD、提交前审查、合并前 CR 等），**一次只 commit 一个仓**。 |
| **2′. 分阶段单会话（备选）** | 若坚持用单会话：须 **显式 checkpoint**——例如「本段仅改后端仓，直至 `git commit` 完成；下一段仅改前端仓」，每段前后核对 `git status` **只出现一个仓库**的变更。 |

### 与现有命令的衔接

- 每仓进入实现前，可在该仓会话执行 **`/dev-start`**（或依赖 `proposal` frontmatter **步骤 1.5** 恢复需求层上下文），避免重复追问来源。
- 跨仓契约与测试 spec 仍由各仓的 **`pull-spec`（workspace-aware）** 落盘，**同一需求**在各仓使用团队约定的 **同一 `change-id` 命名**（见执行层 **design-to-opsx**）。
- 进度用 **`/req-status`** 与 `metadata.yaml` 的 **`changes`** 字段总览。

### 未安装 workspace-specflow 时

上述 **「对齐 vs 按仓实现」** 习惯仍适用；仅缺少 specs 仓命令与部分自动化衔接，执行层 **dev-workflow** 仍以**当前仓库**为界。

---

## 命令速查（与角色对照）

| 命令 | 主要角色 | 一句话 |
|------|----------|--------|
| `/req-new` | 产品 / TL | 飞书链初始化需求目录 |
| `/pm-spec` | 产品 | PRD 结构化增强至可开发、可测 |
| `/qa-spec` | 测试 | PRD → 测试 spec |
| `/qa-sync-xmind` | 测试 | test-spec.md ↔ XMind |
| `/dev-start` | 开发 | 需求层 → 执行层 dev-workflow |
| `/req-status` | 全员 | 进度总览 |

---

## 激活条件

通过 `rules/workspace-awareness.mdc` 的 **globs** 生效：工作区需同时包含 **`requirements/`** 目录与 **`workspace-repos.json`**（通常在 `scripts/` 下）。不满足时本插件规则不会注入，**不影响**仅使用 fe-specflow / be-specflow 的团队。

---

## specs 仓库结构（参考）

```
<specs-repo>/
  requirements/                 # 活跃需求（扁平：一级子目录即需求）
    <requirement-id>/
      prd.md                    # 产品 PRD（撰写 + /pm-spec 增强）
      metadata.yaml             # prd / test_spec / changes 等状态
      prototypes/               # 原型（可选）
      test/
        test-spec.md            # 测试 spec
  _archive/                     # 历史需求（与 requirements 同级）
  docs/context/                 # 业务上下文知识库
  prodspecs/                    # 交互演示（如 GitLab Pages）
  scripts/
    workspace-repos.json        # 仓库路径注册表
```

---

## 权限模型（摘要）

| 角色 | `requirements/` 读 | `requirements/` 写 | 代码仓库 |
|------|---------------------|---------------------|----------|
| 产品 | prd.md、metadata.yaml 等 | prd.md、prototypes/、metadata.yaml | 只读 |
| 测试 | prd.md 等 | `test/test-spec.md`、`metadata.yaml`（测试相关字段）；XMind 为中间产物不入库 | 只读 |
| 开发 | prd.md、test/test-spec.md | **仅** metadata.yaml 的 **changes**（由 design-to-opsx 回写） | 读写 |

---

## 依赖

- **Superpowers**（brainstorming 等）
- **feishu-mcp**（读飞书文档；缺失时技能应明确提示）
- **mcp-xmind**（`@41px/mcp-xmind`，可选，用于 `/qa-sync-xmind`）
- 多根工作区中的 **fe-specflow** / **be-specflow**（执行层与 workspace-aware **pull-spec**）
