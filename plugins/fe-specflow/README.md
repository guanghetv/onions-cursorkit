# fe-specflow

Superpowers + OpenSpec 融合的**前端** Spec-Driven 研发工作流编排。流水线从**需求自动提取**开始——飞书文档（feishu-mcp）、GitLab Spec 文档（pull-spec 机制）、截图、纯文字、本地文件等**多源可组合**，统一整理为需求事实后，再进入 Brainstorming → OpenSpec → TDD → 联调 → E2E 验证 → 归档。**不修改任何社区 skill 源码**，仅通过自建 Rule + Skills + Commands 编排串联。

## 适用场景

- 产品需求在**飞书**，或分散在**飞书 + GitLab Spec + 截图**，希望 Agent **先澄清再落盘**，而不是直接写页面。
- 团队已采用 **OpenSpec** 管理变更，希望前端开发与 **`openspec/changes/<change-id>/`** 目录结构一致。
- T1 完成后需要按**后端 spec / 测试 spec** 做联调与验收，并希望 **pull-spec** 把外部文档落到同一变更目录。
- 提测前需要 **Browser 交叉验证**（Cursor 内置浏览器），并在 **`e2e-report.md`** 中留下可追溯结论再归档。

## 核心能力

| 能力 | 说明 |
|------|------|
| 多源需求接入 | 飞书 MCP、GitLab Spec（只读）、截图、文字、本地文件可组合；失败须**明确提示**，禁止静默跳过 |
| 设计驱动 | 可选 **Figma MCP**；有稿时视觉规格以设计稿为准，局部需求禁止擅自全页改 |
| OpenSpec 一体 | `design-to-opsx` 将 brainstorming 结论写入 `proposal.md`、`specs/**/spec.md`、`tasks.md` 等（以技能内模板为准） |
| 阶段推断 | 无独立状态文件，靠变更目录**文件产物** + 用户意图推断当前阶段（见下「状态推断」） |
| 事件驱动 | T1 完成后可响应「后端 spec 到了」「测试 spec 到了」等，执行 pull-spec → 联调或差异分析 |
| E2E 与归档 | `e2e-verify` 以 **QA spec 置信度最高**；归档以 **`e2e-report.md` 中 `## 验收结论`** 为门禁 |

## 权威文档与编排入口

| 类型 | 路径 | 作用 |
|------|------|------|
| 全局 Rule | `rules/dev-workflow.mdc` | 匹配前端源码与 `openspec/**` 时注入流程意识（阶段、commit、E2E、归档） |
| 主编排 Skill | `skills/dev-workflow/SKILL.md` | **全流程**：阶段 1～5、事件 A/B、触发语表、灰区讨论、Git 与审查纪律 |
| 落盘 Skill | `skills/design-to-opsx/SKILL.md` | brainstorming 确认后 → OpenSpec 变更目录与设计文档转场 |
| 拉取 Skill | `skills/pull-spec/SKILL.md` | GitLab 上后端/测试等 spec → 写入 `openspec/changes/<change-id>/`（`backend-*.md` / `qa-*.md` 等） |
| 验证 Skill | `skills/e2e-verify/SKILL.md` | 清单化验证 → 内置浏览器自动化；报告模板与归档条件 |
| Slash Command | `commands/fe-sdd.md` | **`/fe-sdd`**：本对话内强制「先 brainstorming 再落盘」，禁止抢跑写 `openspec/**` 或业务代码 |

业务仓库若另有 **`docs/spec.md`**（OpenSpec + Superpowers 纪律），以该文档与**本插件 skills** 中更严者为准。

## OpenSpec 与 CLI 分工（必读）

与常见 OpenSpec 用法一致：

- **`openspec new change`、`openspec instructions`、`openspec validate`、`openspec archive` 等 CLI**：由**用户在终端**执行；Agent 在非交互 Shell 中直接调 `openspec` 可能静默失败，**不要代替用户跑**。
- **变更目录下的 Markdown 内容**：由 **Agent 按 skills 模板编写**，保证路径与标题符合 `openspec validate` 预期。
- Agent 可用 `which openspec` 判断是否安装；未安装时按 `dev-workflow` / 项目 `docs/spec.md` 中的**降级模式**手工等价步骤。

## 命令与常见触发语

### Slash Command

| 命令 | 作用 |
|------|------|
| `/fe-sdd` | 激活 Spec-Driven **门禁**：必须先完成阶段 1 设计探索 + `superpowers:brainstorming` +（可选）灰区讨论，用户**明确放行**后才可创建/修改 `openspec/changes/**` 或写业务代码。详见 `commands/fe-sdd.md`。 |

### 自然语言触发（摘自 `dev-workflow`）

| 用户说法（示例） | 典型阶段 |
|------------------|----------|
| 新需求 / 新功能 / 开始开发 | 设计探索 |
| 继续开发 / 接着做（已有 proposal、尚无 tasks） | 任务规划 |
| 继续写（tasks 有未完成项） | T1 开发 |
| 后端 spec 到了 / API 文档到了 `<链接>` | 事件：拉 spec → 联调向 |
| 测试 spec 到了 / QA 文档到了 `<链接>` | 事件：拉 qa → 可询问是否 e2e |
| 跑 e2e / 浏览器验证 / 跑自动化验证 | `e2e-verify` |
| 用这个 spec 跑 e2e `<链接>`（无活跃变更） | `e2e-verify` 延迟模式 |
| 归档 / archive（且验收结论允许） | 归档 |

具体推断规则以 **`skills/dev-workflow/SKILL.md`** 中的表格为准。

## 插件结构

```
<仓库根目录>/
├── .cursor-plugin/
│   └── plugin.json        # 插件清单（name: fe-specflow）
├── rules/
│   └── dev-workflow.mdc   # 全局 Rule：前端流程阶段与约束
├── commands/
│   └── fe-sdd.md          # /fe-sdd：Spec-Driven 门禁
├── skills/
│   ├── dev-workflow/      # 主编排：阶段识别 + 事件分发 + 灰区 + commit
│   ├── design-to-opsx/    # brainstorming → OpenSpec 落盘（proposal / specs / tasks）
│   ├── pull-spec/         # GitLab 拉取 spec → openspec/changes/<change-id>/
│   └── e2e-verify/        # Browser 交叉验证 + e2e-report.md
└── README.md
```

## 变更目录与产出物（概念）

单一需求对应一个 **`change-id`**（kebab-case），目录 **`openspec/changes/<change-id>/`**，通常包含：

- `proposal.md`、`tasks.md`
- `specs/<capability>/spec.md`
- 设计类文档（以 `design-to-opsx` 与项目约定为准）
- T1 后外部拉取的 **`backend-*.md`**、**`qa-*.md`** 等（与 `proposal.md` 同级）
- 验证阶段输出的 **`e2e-report.md`**（验收结论决定是否可归档）

精确文件清单与标题格式以 **`design-to-opsx`**、**`pull-spec`** 及业务项目中的 OpenSpec 配置为准。

## 前置条件

| 依赖 | 用途 | 安装检查 |
|------|------|---------|
| [Superpowers](https://cursor.directory/superpowers) | brainstorming / TDD / verification 纪律 | Cursor 插件已安装 |
| [OpenSpec CLI](https://openspec.pro) | 变更生命周期（new / continue / validate / archive） | `which openspec` |
| **Cursor 内置浏览器**（`cursor-ide-browser` / `browser_*`，通常不在 `mcp.json`） | E2E 交叉验证（`e2e-verify`） | 勿用 `mcp.json` 中的 chrome-devtools-mcp 跑本流程自动化 |
| `GITLAB_TOKEN` 环境变量 | `pull-spec`：阶段 1 读取 GitLab 上的需求 Spec；T1 后拉取后端/测试 spec | `echo ${GITLAB_TOKEN:+ok}` |
| feishu-mcp（或工作区等价的 `user-feishu-mcp`） | 读取飞书产品需求文档；未启用或 token 失效时须提示用户处理 | Cursor MCP 已启用 |
| user-Figma MCP（可选） | 读取 Figma 设计稿，按设计稿实现 UI | Cursor MCP 已启用 |
| **aicr-local** 技能（可选） | 用户同意提交后：有则**必须**用 `/cr` 或该技能审查暂存区；无则由 **Agent 自审暂存区**（仍须完成审查，不可跳过） | 见 `dev-workflow` / `rules/dev-workflow.mdc` |

## 状态推断

不使用独立状态文件，通过变更目录中的**文件产物**推断当前阶段：

| 产物 | 阶段 |
|------|------|
| 无变更目录 | 设计探索 |
| `proposal.md` + `specs/` | 任务规划 |
| `tasks.md` 有未勾选项 | T1 前端开发 |
| `tasks.md` 全部勾选 | 事件驱动 / Browser 验证 |
| `e2e-report.md` 且 **`## 验收结论`** 允许归档（通过，或带已知问题且用户已同意） | 可归档 |
| `e2e-report.md` 但结论不通过且未同意带债 | 须继续修 E2E / 重跑，不归档 |

## 流程总览

```
线性阶段：
  仓库扫描(技术栈/目录/现有模块)
    → 需求提取(多源可组合: 飞书MCP / GitLab Spec文档 / 截图 / 文字 / 本地文件)
    → Figma设计稿(Figma MCP, 可选)
    → Brainstorming(Superpowers, 以工程约束+需求事实+设计稿为输入)
    → 灰区讨论(空态/错误态/分页等决策)
    → OpenSpec 落盘(design-to-opsx)
    → Tasks 规划(按组件/页面拆分) → T1 前端开发(TDD, 按设计稿实现UI)

事件驱动（T1 后，顺序不定，均可选）：
  [后端 spec 到达] → pull-spec(GitLab API) → 切换真实API → 全量重跑前端 TDD
  [测试 spec 到达] → pull-spec(GitLab API) → 差异分析

验证阶段：
  触发条件满足 → Browser 交叉验证(e2e-verify)
    有测试 spec → 以 QA spec 为主交叉验证(验收结论)
    无测试 spec → 以前端 spec 为验证依据
  → 验收结论允许归档 → Archive
```

## 安装

在 Cursor **Settings → Plugins → Team Marketplaces** 中配置本组织维护的插件市场仓库（**onions-plugins** / cursorkit），在列表中启用 **fe-specflow** 并安装；安装后按提示重载窗口。

## Cursor Marketplace 发布与更新

1. **首次上架**：在 [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) 提交你的 **公开** Git 仓库地址；清单需符合 [Plugins 参考文档](https://cursor.com/docs/reference/plugins.md)。团队/私有分发可用 **Team Marketplaces**（见上）。

2. **后续更新**：
   - 在 `.cursor-plugin/plugin.json` 里**提高 `version`**（语义化版本，例如 `0.0.1` → `0.0.2`）。
   - 将变更 **push 到 GitHub 上 Cursor 已关联的默认分支**（与提审时一致）。
   - 根据 [Marketplace 安全说明](https://cursor.com/help/security-and-privacy/marketplace-security.md)，**公开 Marketplace 上的每次更新会经 Cursor 审核后再对用户可见**；具体提交流程以提审时或后台说明为准（若后台提供「请求更新」或重新关联仓库，按指引操作）。

3. **建议**：发版前在 Cursor 中通过团队市场安装本插件并走一遍关键技能验证；README 与 `version` 同步更新，便于审核与用户感知变更。

## 与社区工具的关系

本项目**不修改** Superpowers 和 OpenSpec 的任何原生文件，仅在外部定义调用顺序、产出物归属和阶段转场规则。两个社区工具各自升级不影响本项目。

## 常见问题

| 现象 | 建议 |
|------|------|
| Agent 执行 `openspec` 无输出且失败 | 由用户在终端执行 CLI；Agent 只写文件内容（见「OpenSpec 与 CLI 分工」）。 |
| 飞书 / GitLab 拉取失败 | 检查 MCP 与 `GITLAB_TOKEN`；向用户说明原因并提供粘贴正文等替代路径。 |
| E2E 无法自动登录 | 按 `e2e-verify`：用户在内置浏览器中手动登录到验收页后，再由 Agent 接管自动化。 |
| 与后端仓库对齐 change-id | 约定同一需求共用同一 `change-id`，外部 spec 落在各自仓库的 `openspec/changes/<change-id>/`（后端插件侧自行维护其目录规范）。 |
