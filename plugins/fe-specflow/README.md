# fe-specflow

（本仓库目录名与插件标识一致，为 **`fe-specflow`**；亦见 `.cursor-plugin/plugin.json` 的 `name`。）

Superpowers + OpenSpec 融合的**前端** Spec-Driven 研发工作流编排。流水线从**需求自动提取**开始——飞书文档（feishu-mcp）、GitLab Spec 文档（pull-spec 机制）、截图、纯文字、本地文件等**多源可组合**，统一整理为需求事实后，再进入 Brainstorming → OpenSpec → TDD → 联调 → E2E 验证 → 归档。**不修改任何社区 skill 源码**，仅通过自建 Rule + Skills + Commands 编排串联。

## 前置条件

| 依赖 | 用途 | 安装检查 |
|------|------|---------|
| [Superpowers](https://cursor.directory/superpowers) | brainstorming / TDD / verification 纪律 | Cursor 插件已安装 |
| [OpenSpec CLI](https://openspec.pro) | 变更生命周期（new / continue / validate / archive） | `which openspec` |
| **Cursor 内置浏览器**（`cursor-ide-browser` / `browser_*`，通常不在 `mcp.json`） | E2E 交叉验证（`e2e-verify`） | 勿用 `mcp.json` 中的 chrome-devtools-mcp 跑本流程自动化 |
| `GITLAB_TOKEN` 环境变量 | `pull-spec`：阶段 1 读取 GitLab 上的需求 Spec 文档；T1 后拉取后端/测试 spec | `echo ${GITLAB_TOKEN:+ok}` |
| feishu-mcp（或工作区等价的 `user-feishu-mcp`） | 读取飞书产品需求文档；未启用或 token 失效时须提示用户处理 | Cursor MCP 已启用 |
| user-Figma MCP（可选） | 读取 Figma 设计稿，按设计稿实现 UI | Cursor MCP 已启用 |
| **aicr-local** 技能（可选） | 用户同意提交后：有则**必须**用 `/cr` 或该技能审查暂存区；无则由 **Agent 自审暂存区**（仍须完成审查，不可跳过） | 见 `dev-workflow` / `rules/dev-workflow.mdc` |

## 插件结构

```
<仓库根目录>/
├── .cursor-plugin/
│   └── plugin.json        # 插件清单（name: fe-specflow）
├── rules/
│   └── dev-workflow.mdc   # 全局 Rule，注入前端研发流程意识
├── commands/
│   └── fe-sdd.md          # /fe-sdd：Spec-Driven 门禁（先 brainstorming 再落盘）
├── skills/
│   ├── dev-workflow/      # 主编排：全生命周期阶段识别 + 事件分发
│   ├── design-to-opsx/    # 转场胶水：brainstorming → OpenSpec 落盘
│   ├── pull-spec/         # spec 拉取：阶段 1 读取 GitLab 需求 Spec；T1 后写入 openspec/changes/<change-id>/（前后端同一 change-id）
│   └── e2e-verify/        # 交叉验证：Browser Agent E2E 验证
└── README.md
```

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

### 方式 1：团队插件市场（推荐）

在 Cursor **Settings → Plugins → Team Marketplaces** 中配置本组织维护的插件市场仓库（如 **onions-plugins** / cursorkit），在列表中启用 **fe-specflow** 并安装；安装后按提示重载窗口。

### 方式 2：官方文档中的 symlink（可选）

Cursor 文档说明可将插件目录链到 `~/.cursor/plugins/local/<插件名>` 后重载窗口；需自行保证 `plugin.json` 与路径一致。

### 方式 3：手动复制到业务项目（不推荐）

```bash
cp -r <插件目录>/rules/*.mdc .cursor/rules/
cp -r <插件目录>/skills/* .cursor/skills/
```

## Cursor Marketplace 发布与更新

1. **首次上架**：在 [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) 提交你的 **公开** Git 仓库地址；清单需符合 [Plugins 参考文档](https://cursor.com/docs/reference/plugins.md)。团队/私有分发可用 **Team Marketplaces**（见上）。

2. **后续更新**：
   - 在 `.cursor-plugin/plugin.json` 里**提高 `version`**（语义化版本，例如 `0.0.1` → `0.0.2`）。
   - 将变更 **push 到 GitHub 上 Cursor 已关联的默认分支**（与提审时一致）。
   - 根据 [Marketplace 安全说明](https://cursor.com/help/security-and-privacy/marketplace-security.md)，**公开 Marketplace 上的每次更新会经 Cursor 审核后再对用户可见**；具体提交流程以提审时或后台说明为准（若后台提供「请求更新」或重新关联仓库，按指引操作）。

3. **建议**：发版前在 Cursor 中通过团队市场安装本插件并走一遍关键技能验证；README 与 `version` 同步更新，便于审核与用户感知变更。

## 与社区工具的关系

本项目**不修改** Superpowers 和 OpenSpec 的任何原生文件，仅在外部定义调用顺序、产出物归属和阶段转场规则。两个社区工具各自升级不影响本项目。
