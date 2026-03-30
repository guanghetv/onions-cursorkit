# be-specflow

Superpowers + OpenSpec 融合的**后端** Spec-Driven 研发工作流编排。流水线从**仓库扫描与需求对齐**开始——飞书文档（feishu-mcp）、OpenAPI/Proto 等契约输入，经 **`superpowers:brainstorming`** 与**后端灰区讨论**后落盘 **`design.md` / `plan.md`** 与 OpenSpec 制品，再进入 TDD 实现、可选的前端契约/测试 spec 事件、交叉验证与归档。**不修改任何社区 skill 源码**，通过 Rule + Skills + Commands 编排串联。

**强制纪律**（OpenSpec CLI 分工、阶段卡点、`design.md`/`plan.md`、TDD、验证、Code Review、归档）**全部嵌入** **`skills/dev-workflow/SKILL.md`** 中的 **「OpenSpec + Superpowers 强制纪律」**一节。本 README 为入口说明；编排顺序与触发语见同文件后半部分。

## 适用场景

- 后端新需求希望 **先澄清与方案确认再写代码**，并与 **OpenSpec 变更目录** 一一对应。
- 团队使用 **Go**（或同类栈）+ **protobuf/OpenAPI**，需要 **`proposal.md` 中的服务端 API 契约**作为联调依据。
- T1 完成后需要拉取 **前端契约**（`frontend-*.md`）或 **QA/测试 spec**（`qa-*.md`），对齐实现并重跑测试。
- 合并前要求落实 **强制纪律**中的 **编译/测试/Lint、Scenario 覆盖、Code Review**；交叉验证以 **`e2e-verify`**（主通道为 `go test`/集成/契约测试）为主。

## 核心能力

| 能力 | 说明 |
|------|------|
| 工程化需求入口 | 飞书 MCP、失败须明确提示；可选 OpenAPI/Proto/gRPC 等契约，**不以 Figma 为后端权威来源** |
| 设计与计划落盘 | **`design.md` / `plan.md`** 与 `proposal.md`、`specs/**/spec.md`、`tasks.md` 同属 `openspec/changes/<change-id>/`（见 **`design-to-opsx`** 与 **`dev-workflow` 强制纪律**） |
| 后端灰区 | API 兼容性、数据一致性、安全、性能、可观测性、与前端契约对接等，在落盘前收敛决策 |
| 阶段推断 | 无独立状态文件，靠变更目录**产物** + 用户意图推断阶段（见「状态推断」） |
| 事件驱动 | T1 完成后可响应「前端契约到了」「测试 spec 到了」等，执行 **pull-spec** → 对齐或差异分析 |
| 验证与归档 | 交叉验证见 **`e2e-verify`**；合并与归档门禁以 **强制纪律**阶段 4～6 及 **`verify-report.md` / `e2e-report.md`** 为准 |

## 权威文档与编排入口

| 类型 | 路径 | 作用 |
|------|------|------|
| **纪律全文** | **`skills/dev-workflow/SKILL.md`** → **「OpenSpec + Superpowers 强制纪律」** | 六阶段：Brainstorming → Artifacts → 实现(TDD) → 验证 → Code Review → 归档；**openspec CLI 须用户在终端执行** |
| 全局 Rule | `rules/dev-workflow.mdc` | 匹配 `*.go`、`*.proto`、`openspec/**` 时注入后端流程意识 |
| 主编排 Skill | `skills/dev-workflow/SKILL.md` | 全流程阶段、事件 A/B、灰区、Git/commit 与审查；**上半部分为强制纪律，下半部分为编排表** |
| 落盘 Skill | `skills/design-to-opsx/SKILL.md` | brainstorming 与灰区确认后 → OpenSpec 目录；**内含 `design.md` / `plan.md` 全文模板** |
| 拉取 Skill | `skills/pull-spec/SKILL.md` | GitLab 拉取前端契约 / QA spec / 其它片段 → `openspec/changes/<change-id>/` |
| 验证 Skill | `skills/e2e-verify/SKILL.md` | `go test`/集成/契约测试为主；可选 Cursor 内置浏览器；报告模板 |
| Slash Command | `commands/be-sdd.md` | **`/be-sdd`**：本对话内强制「先 brainstorming 再落盘」，禁止抢跑写 `openspec/**` 或业务代码 |

## OpenSpec 与 CLI 分工（必读）

与 **`dev-workflow` 强制纪律**「前置条件 0.1」一致：

- **`openspec new change`、`openspec instructions`、`openspec validate`、`openspec archive` 等**：由**用户在终端**执行；Agent 在非交互环境中直接调用 `openspec` 可能 **exit=1 且无输出**，**不要代替用户跑**。
- **变更目录下的文件内容**：由 **Agent** 按 skills 与**强制纪律**编写。
- Agent 可用 `which openspec` 判断是否安装；未安装时按**强制纪律**降级手工步骤，**不得跳过实质阶段**。

## 命令与常见触发语

### Slash Command

| 命令 | 作用 |
|------|------|
| `/be-sdd` | 激活 Spec-Driven **门禁**：须先完成阶段 1（设计探索）+ **`superpowers:brainstorming`** +（可选）**后端灰区**，用户**明确放行**后才可创建/修改 `openspec/changes/**` 或写业务代码。详见 `commands/be-sdd.md`。 |

### 自然语言触发（摘自 `dev-workflow`）

| 用户说法（示例） | 典型阶段 |
|------------------|----------|
| 新需求 / 新功能 / 开始开发 | 设计探索 |
| 继续开发 / 接着做（已有 proposal、尚无 tasks） | 任务规划 |
| 继续写（tasks 有未完成项） | T1 后端开发 |
| 前端契约到了 / 前端 OpenAPI / 对齐前端接口 `<链接>` | 事件：拉契约 → 对齐 API/DTO → 重跑测试 |
| 测试 spec 到了 / QA 文档到了 `<链接>` | 事件：拉 `qa-*.md`；可询问是否交叉验证 |
| 跑自动化验证 / 跑集成测试 / 契约测试 / 跑验收 | `e2e-verify` |
| 用这个 spec 跑验收 `<链接>`（无活跃变更） | `e2e-verify` 延迟模式 |
| 归档 / archive（验证与强制纪律门禁已满足） | 归档 |

完整推断表见 **`skills/dev-workflow/SKILL.md`**。

## 插件结构

```
<插件根目录>/
├── .cursor-plugin/
│   └── plugin.json        # 插件清单（name: be-specflow）
├── rules/
│   └── dev-workflow.mdc   # 全局 Rule：后端流程阶段与约束
├── commands/
│   └── be-sdd.md          # /be-sdd：Spec-Driven 门禁
├── skills/
│   ├── dev-workflow/      # 强制纪律 + 主编排
│   ├── design-to-opsx/    # design.md / plan.md 模板 + OpenSpec 落盘
│   ├── pull-spec/         # GitLab → openspec/changes/<change-id>/
│   └── e2e-verify/        # 交叉验证 + verify-report / e2e-report
└── README.md
```

## 变更目录与产出物（概念）

单一需求对应一个 **`change-id`**，目录 **`openspec/changes/<change-id>/`**。常见文件包括：

- **`design.md`、`plan.md`**（模板见 **`design-to-opsx`**）
- **`proposal.md`、`tasks.md`、`specs/<capability>/spec.md`**
- T1 后外部拉取的 **`frontend-*.md`**（前端契约）、**`qa-*.md`**（测试 spec）、**`backend-*.md`**（其它来源，如有）
- 验证阶段 **`verify-report.md`** 或团队约定的 **`e2e-report.md`**

精确清单与 validate 规则以 **`dev-workflow` 强制纪律**与 **`design-to-opsx`** 为准。

## 前置条件

| 依赖 | 用途 | 安装检查 |
|------|------|---------|
| [Superpowers](https://cursor.directory/superpowers) | brainstorming、TDD、verification、requesting-code-review 等 | Cursor 插件已安装 |
| [OpenSpec CLI](https://openspec.pro) | `new` / `instructions` / `validate` / `archive`（**用户终端执行**） | `which openspec` |
| feishu-mcp（或等价 MCP） | 读取飞书需求；失败须提示，勿静默跳过 | Cursor MCP 已启用 |
| `GITLAB_TOKEN` | **pull-spec** 从 GitLab 拉取契约与 spec | `echo ${GITLAB_TOKEN:+ok}` |
| **aicr-local**（推荐） | **每次 commit 前**（用户同意后）：优先 **`/cr`**；否则 Agent 自审暂存区。与 Superpowers **纪律阶段 5**（合并前 `requesting-code-review`）**互补、不冲突** | 见 `dev-workflow`「两类审查」与「Git commit」 |

可选：交叉验证中若需浏览器（BFF/SSR 等），使用 **Cursor 内置** `browser_*`，勿以 **`chrome-devtools-mcp`** 作为本流程主通道（见 **`e2e-verify`**）。

## 状态推断

通过变更目录产物推断阶段（无独立状态文件）：

| 产物 | 阶段 |
|------|------|
| 无变更目录 | 设计探索 |
| 有 `proposal.md` 无 `tasks.md` | 任务规划 |
| `tasks.md` 有未勾选项 | T1 后端开发 |
| `tasks.md` 全部勾选 | 等待事件驱动或交叉验证；用户只说「继续开发」时**先澄清**是增补任务还是进入验证/Code Review |
| `verify-report.md` / `e2e-report.md` 且结论满足归档条件 | 可归档（另须满足 **强制纪律**阶段 5、与 `openspec validate`）；纪律/编排编号见 **`dev-workflow`**「编号约定」 |

## 流程总览

```
线性阶段：
  仓库扫描(cmd/internal/api/proto…)
    → 采集需求(飞书 MCP；OpenAPI/Proto 可选)
    → Brainstorming + 后端灰区(API/数据/安全/性能/可观测性/与前端契约)
    → OpenSpec 落盘(design-to-opsx：design.md / plan.md + proposal + specs；`tasks.md` 多在「任务规划」阶段写入)
    → T1 后端开发(TDD：L1 单元 → L2 集成 → …)

事件驱动（T1 后，可选）：
  [前端契约到达] → pull-spec → frontend-*.md → 对齐 handler/DTO → 重跑 go test
  [测试 spec 到达] → pull-spec → qa-*.md → 差异分析；用户确认后可交叉验证

验证与收尾（对齐 dev-workflow 强制纪律；可迭代多轮，非严格单行顺序）：
  编译/测试/Lint、Scenario 对照
  ↔ e2e-verify（测试命令 + 契约 + 可选浏览器）与 合并前 Code Review(Superpowers)
     （开发期 commit 链上另有 aicr-local `/cr`，见「两类审查」）
  → 门禁满足后：用户终端 openspec archive
  → 收尾 push（T1 中已有多次 commit/push 者按团队规范，不必等到本步才首次提交）
```

## 安装

在 Cursor **Settings → Plugins → Team Marketplaces** 中配置本组织维护的插件市场仓库（**onions-plugins** / cursorkit），在列表中启用 **be-specflow** 并安装；安装后按提示重载窗口。

## 命令

- **`/be-sdd`** — Spec-Driven 门禁，见 `commands/be-sdd.md`。

## 与社区工具的关系

本项目**不修改** Superpowers 和 OpenSpec 的原生仓库内容，仅在外部定义调用顺序与产出物归属。升级 Superpowers/OpenSpec 后，以 **`skills/dev-workflow/SKILL.md` 强制纪律**与各 skill 的衔接为准做增量调整。

## 常见问题

| 现象 | 建议 |
|------|------|
| Agent 执行 `openspec` 无输出且失败 | 由用户在终端执行；Agent 只写文件（见**强制纪律** 0.1）。 |
| 阶段 2.3 制品确认被跳过 | **强制纪律**规定须用户明确确认 `proposal`/`spec`/`tasks`，不可凭「继续」隐式通过。 |
| 声称验证通过但未跑命令 | 违反 **`superpowers:verification-before-completion`** 与**强制纪律**阶段 4。 |
| 与调用方共用 `change-id` | 约定同一需求使用同一 **`change-id`**，外部契约落在各自仓库的 **`openspec/changes/<change-id>/`**，便于范围对齐。 |
