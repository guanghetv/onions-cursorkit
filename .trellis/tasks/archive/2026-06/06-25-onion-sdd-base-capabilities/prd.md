# onion-sdd 补齐 fe-specflow 基座能力

## 目标

在现有 `plugins/onion-sdd/` 命令流程基础上，补齐原 `fe-specflow` 的基础 SDD 闭环能力，使 `onion-sdd` 不只是 mini/light 命令壳，而是具备完整 Tier 2+ 流程的通用 SDD 基座。

## 已确认事实

- 飞书技术方案 revision `201` 明确：保留现有 `fe-specflow` 主流程能力，抽象通用 SDD 流程层为 `onion-sdd`，后续再接 Trellis 运行时。
- 当前 `onion-sdd` Phase 0 已有：
  - `/onion-hotfix`
  - `/onion-tweak`
  - `/onion-plan`
  - `/onion-continue`
  - `/onion-finish`
  - `tier-triage`
  - `mini-change`
  - `light-change`
  - `rules/onion-sdd.mdc`
  - `templates/current.example.json`
- 当前 `onion-sdd` Phase 0 对 Tier 2+ 只做了“进入 onion 完整 SDD 路径”的说明，尚未拆出完整 skills。
- `fe-specflow` 基础闭环由以下能力构成：
  - `dev-workflow`：阶段推断、需求接入、brainstorming、任务规划、TDD、事件驱动、归档纪律。
  - `design-to-opsx`：brainstorming 结论转 OpenSpec 变更目录。
  - `pull-spec`：GitLab / workspace / 粘贴等外部 spec 接入与差异分析。
  - `e2e-verify`：基于 QA / frontend / backend spec 的 E2E 清单、浏览器验证和 `e2e-report.md` 门禁。
- Phase 1 要求迁移/通用化这些能力，但不能让 `onion-sdd` 运行时依赖 `fe-specflow`。

## 需求

- 在 `plugins/onion-sdd/skills/` 中新增 onion 自有完整流程 skills，覆盖：
  - Tier 2+ 标准流程编排。
  - 完整 OpenSpec 落盘。
  - 外部 spec 接入与差异分析。
  - E2E / 验收报告。
- 更新现有 `/onion-plan`：
  - Tier 0+/1 继续路由到 mini/light。
  - Tier 2+ 调用 onion 自有完整流程能力，而不是只写“完整 SDD 路径”占位。
- 更新 `/onion-continue`：
  - 能根据 `proposal.md`、`specs/**/spec.md`、`tasks.md`、`backend-*.md`、`qa-*.md`、`e2e-report.md` 推断下一步。
  - 继续保持 `.onion-sdd/current.json` 优先、OpenSpec fallback。
- 更新 `/onion-finish`：
  - 对 Tier 2+ 检查 `e2e-report.md` 的 `## 验收结论` 或等价验收证据。
  - 对 Tier 0+/1 保持定向验证和带债归档规则。
- 更新 `README.md` 与 `rules/onion-sdd.mdc`：
  - 明确 `onion-sdd` 已具备基座能力。
  - 明确它不依赖 `fe-specflow` 执行。
  - 保留“按需上下文”，不得恢复“全量扫描项目”硬约束。
- 所有新增或修改的面向用户 Markdown 使用中文表达。
- 保留试点隔离：本子任务不注册 marketplace，不改顶层 README。

## 验收标准

- [ ] `plugins/onion-sdd/skills/` 新增完整流程相关 onion 自有 skills。
- [ ] `/onion-plan` 的 Tier 2+ 路由指向 onion 自有 skills。
- [ ] `/onion-continue` 能描述并执行完整流程阶段恢复。
- [ ] `/onion-finish` 能区分 mini/light 定向验证与 Tier 2+ E2E/验收门禁。
- [ ] README 有完整命令地图和能力地图，说明现有命令流程已具备原 `fe-specflow` 基础能力。
- [ ] 规则文件保留轻量路径门禁，同时补齐 Tier 2+ 写入门禁。
- [ ] 文本中不出现要求用户调用 `/fe-sdd` 或依赖 `plugins/fe-specflow` 执行的说明。
- [ ] 文本中不重新引入“全量扫描项目”硬约束。
- [ ] 本地结构、frontmatter、关键短语和 JSON 校验通过。

## 不做范围

- 不实现 Trellis adapter 或 `.trellis/scripts/**` 改动；该内容留给子任务 `.trellis/tasks/06-25-onion-sdd-trellis-adapter`。
- 不实现 `/onion-auto`、AI spec self-review、metrics 聚合或 marketplace 分发。
- 不修改既有 `plugins/fe-specflow/`、`plugins/be-specflow/`、`plugins/workspace-specflow/`。
- 不自动执行 `openspec archive` 或 git commit。

## 开放问题

- 无阻塞性开放问题。默认实现策略是迁移 `fe-specflow` 的基础能力为 onion 自有口径，同时保持 Tier 0+/1 轻量化。
