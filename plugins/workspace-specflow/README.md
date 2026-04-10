# workspace-specflow

统一工作区多角色协作工作流插件：在 **specs 仓库（需求层）** 内串联产品 PRD、测试 spec、开发桥接与进度总览，并与 **fe-specflow / be-specflow（执行层）** 通过 `requirement_ref` 衔接。

---

## 插件解决什么问题

- **单一真相源**：`requirements/<requirement-id>/` 下的 `prd.md` 与 `test/test-spec.md` 是产品与测试产出的权威版本；飞书文档可作为展示层，但以 specs 仓库为准。
- **角色分工清晰**：每人通过对应命令完成本角色步骤，减少在聊天里重复解释流程。
- **与代码仓库解耦**：需求讨论与文档在 specs 仓库完成；创建 OpenSpec change、写代码、拉取对方契约等在各自代码仓库由执行层插件处理。
- **多根工作区友好**：开发在 Cursor 中同时打开 specs 与前后端仓库时，`pull-spec`（workspace-aware）可从本地仓库读取 spec，无需反复切换分支或手工拷贝。

---

## 双层架构（必读）

| 层级 | 所在位置 | 插件 | 主要职责 |
|------|-----------|------|----------|
| **需求层** | specs 仓库（如 `channel-specs`） | **workspace-specflow** | PRD、结构化产品 spec、测试 spec、元数据与进度；依赖 Superpowers（如 brainstorming） |
| **执行层** | 各业务代码仓库 | **fe-specflow** / **be-specflow** | 技术设计、OpenSpec change、TDD、联调、验证、归档；依赖 Superpowers + OpenSpec |

两层通过 **`requirement_ref`**（通常写在执行层 `proposal.md` 中，并回连到需求目录）对齐；**prd.md** 是产品侧需求的锚点，**MODULE** ID 在产品 spec、测试 spec、change 之间保持一致。

> 测试 spec、前后端 API 契约等到齐后的 **同步**，由执行层的 **`pull-spec`（workspace-aware）** 完成，不在本插件里手搓文件。

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

**你在流程中的位置**：在产品 PRD 已确认（`prd.status = confirmed`）后，基于 **仅** `prd.md`（及原型等）编写 `test/test-spec.md`，可与开发并行；可选导出 XMind 导入飞书或本地编辑后再回写。

| 能力 | 命令 | 说明 |
|------|------|------|
| 生成并确认测试 spec | `/qa-spec` | 读取 `prd.md`，brainstorming 测试策略，生成与 MODULE 对齐的 `test/test-spec.md`，做覆盖率校验后可将 `test_spec.status` 置为 `confirmed`。 |
| Markdown ↔ XMind | `/qa-sync-xmind` | `export`：从 `test-spec.md` 生成 XMind（经 MCP 工作目录）；`import`：从 XMind 回写 `test-spec.md`（需 diff 确认）。 |
| 看进度 | `/req-status` | 同上。 |

**输入隔离（重要）**：`/qa-spec` **不得**读取 `openspec/changes/` 等开发产出，避免测试用例被实现细节「污染」；唯一主输入是产品 spec（`prd.md`）及原型等。

**典型顺序**：确认 specs 仓库已 `git pull` → `/qa-spec` → 需要时 `/qa-sync-xmind export` → 飞书导入或 XMind 编辑 → `/qa-sync-xmind import`。

**权限与边界**：可写 `test/test-spec.md`、`test/test-cases.xmind`（若采用）、以及 `metadata.yaml` 中与测试相关的状态字段；对代码仓库只读扫描（识别可测行为与入口，不写代码）。

**依赖提示**：brainstorming；可选 **mcp-xmind**（`@41px/mcp-xmind`）用于 XMind 双向转换。

---

### 开发（前端 / 后端）

**你在流程中的位置**：在产品 PRD 已确认后，从需求层 **桥接** 到目标代码仓库的 **dev-workflow**（fe-specflow 或 be-specflow）。**不需要**等待测试 spec 才能开始开发（验证阶段会再汇合）。

| 能力 | 命令 | 说明 |
|------|------|------|
| 从需求进入编码流程 | `/dev-start` | 选择需求、扫描可能涉及的仓库、用自然语言对齐 MODULE，检测工作区是否包含目标仓库，然后 **在同一会话** 中启动 dev-workflow。**本命令不写任何文件、不创建 change**。 |
| 看进度 | `/req-status` | 查看需求与各仓库 change 的任务进度。 |

**典型顺序**：specs 仓库 `git pull` → `/dev-start` → 进入目标仓库上下文后的 **brainstorming → design-to-opsx**（在此创建 `openspec/changes/<change-id>/` 并回写 `metadata.yaml` 的 `changes`）→ tasks → TDD → 需要时由执行层 **`pull-spec`** 拉取测试 spec / 对方 API 契约。

**多仓库**：若同一需求要改多个仓库，在 **不同会话** 中分别 `/dev-start`，每个仓库一个 change。

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
| 测试 | prd.md 等 | test/test-spec.md、相关 xmind、metadata.yaml | 只读 |
| 开发 | prd.md、test/test-spec.md | **仅** metadata.yaml 的 **changes**（由 design-to-opsx 回写） | 读写 |

---

## 依赖

- **Superpowers**（brainstorming 等）
- **feishu-mcp**（读飞书文档；缺失时技能应明确提示）
- **mcp-xmind**（`@41px/mcp-xmind`，可选，用于 `/qa-sync-xmind`）
- 多根工作区中的 **fe-specflow** / **be-specflow**（执行层与 workspace-aware **pull-spec**）

---

## 延伸阅读

- 完整阶段说明与时序图：`docs/superpowers/specs/2026-04-07-workspace-specflow-workflow.md`
- 设计决策与背景：`docs/superpowers/specs/2026-04-07-workspace-specflow-design.md`
