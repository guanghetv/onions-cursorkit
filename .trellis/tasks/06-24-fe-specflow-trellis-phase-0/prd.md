# 按技术方案开发 Phase 0

## 目标

按飞书技术方案 revision `188` 的 Phase 0 范围，新建试点插件 `plugins/onion-sdd/`，并保持试点目录外既有插件不受影响。

Phase 0 交付一个新的通用 `onion-sdd` 流程。它不是既有插件的包装层，也不把其他插件作为运行时依赖：

- **本期重点**：Tier 路由命令层、轻量 OpenSpec 模板（Tier 0+/1）、剔除「全仓扫描」等过重约束。
- **独立流程策略**：Tier 2+ 的标准 OpenSpec、TDD、联调、E2E 等阶段以 onion 自有命令、技能、模板和门禁沉淀；后续成熟能力也应归入 onion 自有维护。
- **演进方向**：先小幅度调整跑通 hotfix/tweak/plan/continue/finish，验证通过后再逐步收敛到最终 `onion-sdd` 通用方案；Trellis adapter、workflow-state 强恢复等留待后续阶段。

本期先聚焦人工可控的 hotfix、tweak、plan、continue、finish 路径；`/onion-auto` 延后。

## 已确认事实

- 来源方案：飞书 Wiki `https://guanghe.feishu.cn/wiki/FcsSwnZ1TiqLdskGa8EcO9U2nmb`，最新读取 revision `188`。
- Phase 0 推荐目录为 `plugins/onion-sdd/`，命令统一改为 `/onion-*`。
- Phase 0 **不直接改**试点目录外既有插件，避免影响现网流程。
- Phase 0 只做流程命令层、轻量模板和门禁规则，**不接 Trellis runtime**。
- Phase 0 先只承诺 slash command 触发，即用户显式使用 `/onion-hotfix`、`/onion-tweak`、`/onion-plan`、`/onion-continue`、`/onion-finish`；自然语言弱触发不作为本期验收项。
- `/onion-auto` 本期先不做；不交付 `onion-auto.md` 和 `auto-spec-review/SKILL.md`。
- Phase 0 不做 Trellis adapter、workflow-state 强恢复、metrics 平台、Spec Pack registry，也不做既有插件改造。
- 需要剔除既有流程中不合理或过重的要求，例如「每次进入需求对齐前全量扫描项目」。`onion-sdd` 只要求**按当前任务需要**读取相关上下文（需求来源、OpenSpec 产物、用户指定范围、必要邻近代码）。
- **试点隔离**：Phase 0 **不**注册 `.cursor-plugin/marketplace.json`，**不**改顶层 README；试用时手动指定 `plugins/onion-sdd/` 路径；待试点验证通过后再补分发入口与 `validate-template.mjs` 校验。
- 本仓库当前没有 `package.json` 或自动测试脚本；本次主要通过文件结构、内容完整性、frontmatter 规范和文本规则检查验证。

## 需求

- 新增 `plugins/onion-sdd/` 插件目录，至少包含：
  - `.cursor-plugin/plugin.json`
  - `README.md`
  - `DESIGN-SUPPLEMENT.md`
  - `commands/onion-hotfix.md`
  - `commands/onion-tweak.md`
  - `commands/onion-plan.md`
  - `commands/onion-continue.md`
  - `commands/onion-finish.md`
  - `skills/tier-triage/SKILL.md`
  - `skills/mini-change/SKILL.md`
  - `skills/light-change/SKILL.md`
  - `rules/onion-sdd.mdc`
  - `templates/current.example.json`
- 所有 commands、skills、rules 须符合 `docs/add-a-plugin.md` 的 frontmatter 要求。
- 所有面向用户的产物内容使用中文，包括 README、commands、skills、rules 中的说明、流程、模板字段和验收口径。
- `plugin.json` 必须使用独立插件名 `onion-sdd`，并声明 commands、skills、rules 三类入口。
- 命令入口必须表达以下路径：
  - `/onion-hotfix`：Tier 0+ 快修路径，跳过复杂 brainstorming，调用 `mini-change` 生成 mini OpenSpec 和定向验证项。
  - `/onion-tweak`：Tier 1 轻量路径，跳过完整 brainstorming，最多一轮范围确认，调用 `light-change`。
  - `/onion-plan`：标准入口，先 `tier-triage` 定 Tier；Tier 0+/1 路由到 hotfix/tweak；**Tier 2+ 进入 onion 自有完整 SDD 路径**（按需上下文 + 需求澄清 + 完整 OpenSpec + 实现 + E2E/验收），但**不得**保留「全量扫描项目」硬约束。
  - `/onion-continue`：基于 OpenSpec 产物弱恢复（`proposal.md`、`tasks.md`、`specs/`、`e2e-report.md`），不读 Trellis runtime。
  - `/onion-finish`：整理变更内验收证据与归档提示；**journal 指 OpenSpec 变更记录/会话摘要**，不是 Trellis workspace journal；不包含 commit，不自动 archive。
- `tier-triage` 必须覆盖 Tier 0、0+、1、2、3 的判定、升级红线和验证策略。
- `tier-triage` 必须覆盖 Tier 0++ 紧急 hotfix、活跃冲突检测和 Phase 0 固定人工的 auto 预留字段。
- `mini-change` 必须提供 Tier 0+ 的 mini OpenSpec 模板要求。
- `light-change` 必须提供 Tier 1 的 light OpenSpec 模板要求。
- `mini-change` 与 `light-change` 必须包含最低质量门禁，避免形式化空洞产物。
- `/onion-continue` 必须说明 `.onion-sdd/current.json` 轻量状态的读取优先级和 OpenSpec fallback。
- `/onion-finish` 必须定义带债归档的可接受/不可接受条件。
- 规则文件必须提供 slash command 配套的 Tier 路由、按 Tier 分级的 OpenSpec 写入门禁、人工确认点和 Phase 0 明确不做范围；自然语言弱触发只作为后续可扩展方向。
- README 必须说明：Phase 0 试点目标、onion 独立流程定位、本期新建内容、删去的重约束、Tier 路由、验收方式、后续演进方向。

## 验收标准

- [ ] `plugins/onion-sdd/` 按 Phase 0 建议结构创建完整。
- [ ] 试点目录外既有插件文件没有被修改。
- [ ] 五个命令文档均存在，frontmatter 含 `name` 与 `description`，且明确 command → skill 路由。
- [ ] 三个 onion 自有 skill 均存在，覆盖 Tier 判定、mini/light 模板和风险升级规则。
- [ ] Phase 0 补充项 S1-S6 已落地：Tier 决策树、Tier 0++、轻量状态模板、mini/light 质量门禁、活跃冲突检测、带债归档定义。
- [ ] `/onion-plan` 与 README 明确 Tier 2+ 进入 onion 自有完整 SDD 路径，不要求安装或调用其他插件。
- [ ] README 与规则文件明确 Phase 0 不做 Trellis adapter、workflow-state 强恢复、metrics、Spec Pack registry、marketplace 注册和既有插件改造。
- [ ] README 明确试点安装/试用方式：手动指定 `plugins/onion-sdd/` 路径，不进入插件市场。
- [ ] README 与规则文件明确 Phase 0 仅承诺 slash command 触发，不把自然语言弱触发作为验收项。
- [ ] 所有面向用户的 Markdown 产物使用中文表达。
- [ ] 文本中明确剔除「全量扫描项目」硬性要求，改为按需读取相关上下文。
- [ ] 文本中包含 Phase 0 验收重点：小任务跳过复杂 brainstorming，仍可落 OpenSpec 并归档。
- [ ] 文本中明确 `/onion-auto`、Trellis 接入、AI spec self-review 属于后续阶段。
- [ ] 本地验证通过：文件清单、frontmatter 抽检、command→skill 路由检查、关键短语检查、试点目录外既有插件 diff 为空。

## 不做范围

- 不改动试点目录外既有插件。
- 不实现 Trellis adapter、Trellis npm 接入或 runtime 状态恢复。
- 不实现真实 CLI/runtime 程序，只交付 Cursor plugin 的命令、技能、规则和文档制品。
- 不在 Phase 0 内实现 Tier 2+ 的全套独立 skills；先通过命令文档沉淀 onion 自有完整 SDD 路径，后续再拆出独立 skills。
- 不交付 `/onion-auto`、`auto-spec-review` 或自动化无交互执行流程。
- 不注册 marketplace、不跑本插件的 `validate-template.mjs`（试点隔离；手动指定 `plugins/onion-sdd/` 路径试用；后续单独 PR 补注册）。
- 不实现 metrics 平台、Spec Pack registry、跨仓模板分发。
- 不代表用户执行 `openspec archive` 或 `git commit`。

## 演进说明（非本期交付）

| 阶段 | 方向 |
| --- | --- |
| Phase 0（本期） | 命令层 + Tier 0+/1 轻量模板 + 去全仓扫描；Tier 2+ 沉淀 onion 自有完整 SDD 路径 |
| 后续 | `/onion-auto`、AI spec self-review、Trellis adapter、workflow-state 强恢复 |
| 最终 | 通用 `onion-sdd` 收敛，视试点结果决定是否合并回前端流程或独立灰度 |
