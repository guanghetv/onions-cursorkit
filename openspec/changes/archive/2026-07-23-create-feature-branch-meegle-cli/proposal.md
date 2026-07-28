# create-feature-branch-meegle-cli

## 背景

- `create-feature-branch` 技能当前通过飞书项目 MCP（`get_workitem_brief`）查询工作项名称与规划迭代。
- 团队已具备 Meegle CLI（`@lark-project/meegle` / `meegle`），CLI 在授权与可脚本化调用上更稳定；MCP 仍可作为无 CLI 或 CLI 失败时的备选。
- 分支命名、基线门禁、多链接拼接、推送与追踪等核心流程不变，仅调整「查询飞书任务信息」的工具优先级。

## 目标

- 创建 feature 分支时，**优先**用 Meegle CLI 查询第一个工作项及规划迭代名称。
- CLI 不可用、未授权或查询失败时，**回退**到飞书项目 MCP（`FeishuProjectMcp` / `get_workitem_brief`）。
- 保持现有分支名格式、`master` 基线门禁、多链接 ID 拼接与错误处理语义不变。

## 变更

- 更新 `plugins/common/skills/create-feature-branch/SKILL.md`：步骤 4/5 与快速清单改为 CLI 优先、MCP 备选。
- 同步 `references/DETAILED_STEPS.md`（及必要时 `EXAMPLES.md`、`TROUBLESHOOTING.md`）中的查询示例、失败提示与回退路径。
- 明确 CLI 命令形态：`meegle workitem get`（及迭代工作项二次查询），需遵守 meegle 技能的授权前置。

## 影响范围

- 页面/模块: `plugins/common/skills/create-feature-branch/`（技能文档与 references）
- 数据/API: 无业务 API 变更；仍读取飞书项目工作项「名称 / 规划迭代 / ID」
- 兼容性: 有 Meegle CLI 时走 CLI；无 CLI 或失败时行为与现网 MCP 路径等价

## 不做范围

- 不改分支命名规则、基线门禁、推送/追踪逻辑
- 不把 Meegle CLI 打包进 cursorkit 插件依赖，也不改 MCP server 实现
- 不新增 Trellis / onion-sdd 流程耦合
- 不扩展为批量建分支、自动关联飞书状态流转等新能力

## 验证计划

- 对照检查：`SKILL.md` 与 `DETAILED_STEPS.md` 中步骤 4/5 均写明 CLI 优先与 MCP 回退条件
- 命令可用性：`meegle --help` 或 `meegle workitem get --help` 可发现（本机已装 CLI 时）
- 路径演练（手动/对话）：给定飞书 detail URL，Agent 按技能先尝试 CLI；模拟 CLI 失败时应改用 MCP，且分支名格式仍为 `feat/<迭代>-<名称>-m-<ID>`
- 回归：确认基线门禁（须在 `master` 上 `checkout -b`）与多链接 `-m-ID` 拼接描述未被删改
