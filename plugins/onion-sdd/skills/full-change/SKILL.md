---
name: full-change
description: 为 Tier 2+ 标准需求编排 Onion SDD 完整流程，覆盖需求接入、澄清、任务规划、实现纪律、外部 spec 事件和验证收束。
---

# Full Change

Full change 适用于 Tier 2+：跨模块、接口契约、状态流、数据结果、权限、安全、支付、资金、核心链路、多人协作或需要 E2E 门禁的变更。它是 Onion SDD 的完整基座流程。

## 输入

- 用户原始需求、链接、截图、文字说明或本地文件。
- 现有 `openspec/changes/<change-id>/` 产物。
- 与本次变更直接相关的代码、测试、配置、设计稿、错误信息或运行证据。
- `.onion-sdd/current.json`（如存在）。

只读取与当前任务相关的上下文；不要把全仓扫描作为硬性前置。

## 阶段

| 阶段 | 产物 | 入口 |
|------|------|------|
| triage | Tier 判断、升级原因、验证策略 | `tier-triage` |
| discover | 结构化需求事实、范围边界、冲突点 | `trellis-brainstorm` |
| research | 外部资料调研，产出写入 `research/` 目录 | `trellis-research` |
| design | 方案澄清、关键决策、API/数据/交互契约 | 本技能 / `pull-yapi` |
| openspec | `proposal.md`、`specs/**/spec.md`、`tasks.md` | `openspec-change` |
| implement | 按 `tasks.md` 执行，遵守 TDD / 定向验证纪律（Tier 2+ 大范围改动建议派发 `trellis-implement` 子代理执行；不可用时主会话按本技能执行） | 本技能 |
| check | 四步复合审查：`trellis-check` → 暂存本次 change → `/cr` 审查暂存区 → 修复复审 | `trellis-check` + `/cr` |
| integrate | 后端/QA/YApi/外部 spec 接入与差异分析 | `external-spec` / `pull-yapi` / `re-check` |
| verify | E2E 或等价验收报告 | `verify-change` |
| finish | 归档判断、自动归档、带债检查 | `/onsf-finish` |

## Trellis 使用检查

进入需求接入前，先做一次性检测（仅本技能被触发，即 Tier 2+/3 时执行；`/onsf-auto` 无交互场景不触发，见 `onsf-auto.md` 的「Trellis 边界」）：

1. 检测 `.trellis/scripts/add_session.py` 是否存在。
   - 存在 → Trellis 可用，跳过下述安装流程；先执行下方「遗留变更扫描与确认归档」，再按「task 绑定询问」处理，最后进入需求接入。
   - 不存在 → 进入第 2 步。
2. 向用户说明"当前项目未安装 Trellis，其 journal/spec 积累/task 能力可以增强 onion-sdd 的记忆能力"，询问是否现在安装并初始化。每次触发 Tier 2+/3 且 Trellis 仍不可用时都重新询问，不记忆此前的拒绝。
3. 用户同意时：
   a. 确认开发者标识（优先复用 git 全局 `user.name`，取不到则询问用户）。
   b. 平台选择：默认只初始化当前 Agent 所在平台（例如当前运行在 Cursor 中就只用 `--cursor`），额外询问是否要顺带初始化其它平台（`--claude`/`--codex` 等）。
   c. 先探测 CLI：跑 `trellis --version`。
      - 成功（CLI 已全局安装，只是本项目未 `trellis init`）→ 跳过安装，直接执行 `trellis init -u <name> <平台 flag>`。
      - 失败/命令不存在 → 执行 `npm install -g @mindfoldhq/trellis`（需要 `full_network` 权限）→ `trellis --version` 确认安装成功 → `trellis init -u <name> <平台 flag>`。
   d. 安装/初始化成功后，按下方「gitignore 追加」更新根 `.gitignore`。
   e. 完成后视为 Trellis 已可用，先执行下方「遗留变更扫描与确认归档」（无候选则不问），再按「task 绑定询问」处理。
4. 用户拒绝，或安装/初始化过程报错：说明失败原因（网络、权限、CLI 报错内容），**仍执行「遗留变更扫描与确认归档」**（此时只扫 OpenSpec），再按本技能各阶段已有的"如果 Trellis 不可用，回退到 XXX"分支继续 Tier 2+/3 流程。不因未装 Trellis 而跳过上一轮 OpenSpec 归档确认。

### 遗留变更扫描与确认归档

手动 Tier 2+/3 **新任务**入口、进入需求接入之前执行。Trellis 与 OpenSpec 视为一对变更单元：有 Trellis 就必须同步归档对应 OpenSpec；未装 Trellis 时只确认归档上一轮 OpenSpec。本次会话要**继续**的那条 change / task 排除在外。mini、light 与 `/onsf-auto` 不执行。

1. 收集候选并按 `change_id` 去重（无 `change_id` 的 Trellis task 单独成项）：
   - **OpenSpec**：优先 `.onion-sdd/current.json` 的 `active_change_id`（目录仍在则列入）。无 Trellis 且 idle 时，再列出 `openspec/changes/` 下未归档目录（跳过 `archive/`）。有 Trellis 时不要把未绑定 onion 的其它 OpenSpec 目录一律当成遗留。
   - **Trellis**（仅 Trellis 可用时）：`.trellis/tasks/*/task.json`（跳过 `archive`、非目录、读失败）。纳入 `completed` 未入库；以及 `planning` / `in_progress` / `review` 且 bound OpenSpec 目录已不存在的 stale task。有 bound `change_id` 时与对应 OpenSpec 合成一项。
2. 排除：用户本轮明确要继续的 change/task（`/onsf-continue` 或本会话已绑定且继续同一需求）。**新开 `/onsf-plan` 时**，`.onion-sdd/current.json` 里的上一轮 `active_change_id` **算遗留**，要列入确认，不当成「继续」。
3. 无候选 → 不问，进入下一步（有 Trellis 则 task 绑定，否则需求接入）。
4. 有候选 → 一次列出：OpenSpec `change_id`（无则「仅 Trellis」）、task 目录与 status（无则「仅 OpenSpec」）。请用户确认集合；全选 / 多选 / 全否。未经确认不得归档。
5. 对确认项保持 **成对归档**，不得把本轮将要新建或继续的 change/task 收进去：
   a. OpenSpec 目录仍在：对该 leftover 跑 `finish_check.py --change-id <id>`，通过后 `openspec archive <id>`（CLI 不可用则按 `/onsf-finish` 等效移动）。这是上一轮收尾，不是本轮 finish。
   b. 有对应 Trellis task：再 `python3 ./.trellis/scripts/task.py archive <name>`。
   c. OpenSpec 预检失败：报告后 **整项跳过**（不单独归档 Trellis，避免 task 与 spec 分裂）。用户明确说「只归档 Trellis / 只归档 OpenSpec」时除外。
   d. leftover 若等于当前 `active_change_id`，OpenSpec 归档成功后 `onion_state.py set --idle`（不要把尚未开始的新任务置 idle）。
6. 单条失败继续其余项；全部拒绝或失败不阻塞新任务。提示稍后对 leftover 跑 `/onsf-finish` 或 `/trellis:finish-work`。

### gitignore 追加

为**本次实际初始化的平台**追加整目录忽略：

| 平台 | 追加条目 |
|------|----------|
| `--cursor` | `.cursor/` |
| `--claude` | `.claude/` |
| `--codex` | `.codex/` |

规则：
- 追加前检查 `.gitignore` 是否已有等价条目（如已存在 `.cursor/` 则跳过）。
- 只在文件末尾追加，追加前加注释 `# Trellis / AI 平台生成文件（本地初始化产物，无需同步到仓库）`。
- 不删除或重写用户已有内容；不处理 `.agents/skills/`（Trellis 跨平台真相源，始终追踪）。
- 整目录忽略不会影响已经被 git 追踪的文件（gitignore 只对未追踪文件生效）。如果该平台目录下已有被追踪的文件（例如其它插件手写并直接提交在同一目录下的文件），忽略规则加入后这些文件不会被自动取消追踪，但后续该目录下的新文件默认不会被暂存，需要时手动 `git add -f`；发现已有追踪文件时在输出中提示用户知晓这一点。

### task 绑定询问

Trellis 可用时，进入「需求接入」前检查本次 Tier 2+/3 变更是否已绑定 Trellis task：

1. 已绑定 → 跳过本步骤，不重复询问。判断依据（任一命中即视为已绑定）：
   - `.onion-sdd/current.json` 或对话上下文已记录 active Trellis task；
   - 本次是 Tier 3 拆分出的子任务：`/onsf-plan` 第 6 步已用 `trellis-adapter` 创建 parent/child task 树，视为已绑定。
2. 未绑定 → 向用户说明本次是 Tier 2+ 标准需求，询问是否现在创建 Trellis task：
   - 用户同意 → 执行 `task.py create "<任务标题>" [--slug <目录名>]`，创建后通过 `trellis-adapter` 把 `change_id` 写入新 task 的 `meta.onion`，再继续需求接入。
   - 用户拒绝 → 不创建，继续走 `.onion-sdd/current.json` + OpenSpec 独立运行；本次 change 生命周期内不再重复询问。
3. 后续阶段写 `meta.onion.tier`/`change_path` 等字段（见 `DESIGN-SUPPLEMENT.md`「同步时机」表）的前提都是本步骤已产生绑定或用户已明确拒绝。

## 需求接入

加载 `trellis-brainstorm` 技能并按以下协议探索需求：
- 一次只问用户一个问题，优先给选项而非让用户填空。
- 优先通过代码、文档、API 自己查，尽量不打断用户。
- 用户每回答一个问题，立刻回写到 `proposal.md` 对应章节。
- 探索过程中保持需求聚焦，不提前进入技术设计。
- 如果 Trellis 环境不可用（`trellis-brainstorm` 无法加载），回退到本技能的「澄清纪律」收敛问答模式。

需求来源可以组合使用：

| 来源 | 处理 |
|------|------|
| 飞书项目卡片 | 提取卡片信息、工作项 ID、需求文档链接和验收口径；卡片链接只作为需求与分支准备的输入，不替代需求正文 |
| 飞书文档 | 使用可用的飞书文档能力读取；失败时说明权限、认证或工具问题，并要求用户粘贴正文或导出文件；若文档涉及接口变更，提取其中 YApi 链接/ID |
| YApi 接口 | 使用 `pull-yapi` 读取接口契约；设计期只读参考，T1 后可落盘为 `backend-yapi-*.md` |
| GitLab / 远程 spec | 使用可用 API、工作区文件或用户粘贴内容读取；失败时明确提示 |
| 截图 | 提取页面、控件、状态、标注文案和范围边界 |
| 纯文字 | 提取目标、行为变化、验收口径和不做范围 |
| 本地文件 | 读取用户指定文件；只取与本次范围相关的章节 |

多源内容冲突时，不自行裁决；列出冲突并向用户确认。

## 接口改动与 YApi

当前端需求出现以下任一情况，视为接口变更：

- 新增、修改或废弃后端 HTTP API。
- 前端新增 endpoint、修改 method/path、请求字段、响应字段、错误码或权限语义。
- mock、L1 契约测试或 L2 行为测试依赖后端返回范围。

处理纪律：

- 飞书卡片或需求文档包含 YApi 链接/ID 时，加载 `pull-yapi`。在 discover/design 阶段只读拉取契约摘要，不直接写入 OpenSpec；在 T1 后或用户说“只落盘接口契约”时，写入当前 change 的 `backend-yapi-*.md` 并做差异分析。
- 需求涉及接口变更但没有 YApi 链接/ID 时，向用户确认；在确认前可把接口契约标记为 `contract_source: inferred`，不得伪造 YApi 依据。
- 不默认搜索 YApi。只有用户明确要求搜索接口，或文档只有接口名称且用户同意搜索时，才使用 `pull-yapi` 的搜索流程，并让用户确认候选。
- `user-yapi-common-mcp`、`YAPI_BASE_URL` 或 `YAPI_GLOBAL_TOKEN` 不可用时，要求用户粘贴接口文档；主会话按 `pull-yapi` 模板整理摘要或落盘，并在输出中说明降级。
- 请求/响应字段、类型、必填、method/path 以 `backend-yapi-*.md` 为最高依据；E2E 验收口径以 `qa-*.md` 为最高依据。冲突必须写入差异分析或 `e2e-report.md`。

## 调研

当需求涉及以下情况时，调用或派发 `trellis-research`：

- 使用不熟悉的第三方库、API 或框架特性。
- 需要对比多个技术方案（如选型、性能评估）。
- 涉及团队未使用过的模式或架构决策。

调研纪律：

- 产出必须写入当前 change 对应的 `research/` 目录（每个主题一个 `.md` 文件）。
- 调研与需求探索可以交叉进行：遇到技术问题立刻调研，然后回到 discover。
- 如果 Trellis 不可用，在主会话内自行完成调研并写入文件。

## 开发分支准备

进入 implement 阶段前的分支门禁判定见 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」。本小节说明门禁判定"需要创建分支"且用户提供了飞书项目卡片时，具体如何调用 `create-feature-branch`；`create-feature-branch` 是 Common 插件提供的通用扩展能力，不属于 onion-sdd 自有基座，不要把分支创建逻辑复制到 onion-sdd 内。

触发条件（满足任一即调用本小节流程）：

- 分支门禁判定当前处于受保护分支，且用户提供了飞书项目卡片链接或卡片信息，包含可解析的工作项链接，例如 `/detail/<id>`。
- 用户表达“开始开发”“创建分支”“切开发分支”，希望在分支门禁触发前主动提前创建。

执行纪律：

1. 先完成需求事实、范围和 OpenSpec/`tasks.md` 的最小落盘，避免在需求不清时提前建分支。
2. 调用 `create-feature-branch` 前，遵守该 skill 自身门禁：工作区必须干净、默认从 `master` 更新后创建分支、需要飞书项目 MCP 和 git/network 权限。
3. 如果 Common 插件或 `create-feature-branch` 不可用，或用户没有飞书链接：按分支门禁的 `feat/<change-id>` 兜底路径处理，不阻塞 onion-sdd 需求分析。
4. 分支创建成功后，在当前 change 的 `proposal.md` 或最终摘要中记录飞书卡片 ID/URL、需求文档来源和 feature branch 名称。
5. 如果当前 change 绑定 Trellis task，优先用 `task.py set-branch <task> <branch>` 写入 Trellis 标准 `branch` 字段，不把分支名重复写入 `meta.onion`。
6. 分支创建失败时，不继续修改业务代码；说明失败原因和下一步处理方式。

## 前端设计稿与灰区

当变更涉及前端页面、组件、交互、样式或端到端验收时，完整流程必须补充前端专项上下文；这不是 brainstorming 硬门禁，但属于 Tier 2+ 前端设计纪律。

### Figma / 设计稿

- 用户提供 Figma、设计稿链接、截图或节点信息时，优先读取与本次变更范围直接相关的 Frame、组件、布局和视觉规格。
- UI 实现应遵守与本次范围相关的颜色、字号、字重、行高、间距、圆角、状态和组件使用约定。
- 局部改版时，只实现用户指定的页面区域或组件。若同一页面其它区域与设计稿不一致，不得为了“顺手对齐”而扩大改动；需要先向用户二次确认。
- 设计稿读取失败时，说明是权限、认证、工具不可用还是链接/节点问题，并要求用户提供截图、导出文件或文字规格。

### 前端灰区决策

进入 `openspec-change` 前，按本次实际范围挑选相关维度并补齐决策；无关维度不展开。

| 维度 | 需要明确的问题 |
|------|----------------|
| UI 状态 | 空态、加载态、错误态、部分失败、禁用态 |
| 交互行为 | 表单校验时机、防重复提交、破坏性操作确认、乐观更新或接口返回后刷新 |
| 数据展示 | 长文本、分页/无限滚动/虚拟列表、极端值、时间格式、数值精度 |
| 响应式 | 目标端、断点、容器宽度、内容溢出策略 |
| 权限与条件渲染 | 不同角色可见性、无权限时隐藏/禁用/提示、feature flag |
| 动效 | 列表增删、页面切换、操作反馈 |

输出灰区决策时使用：

```markdown
| 维度 | 灰区问题 | 决策 | 依据 |
|------|----------|------|------|
| 空状态 | <场景> | <决策> | <设计稿/项目既有模式/用户确认> |
```

纯文案、纯样式微调或用户明确说“跳过灰区讨论”时，可以跳过，但要在最终设计摘要或 `proposal.md` 中写明跳过理由。

## 澄清纪律

进入 OpenSpec 落盘前必须形成以下信息：

- 目标：为什么做、服务哪个用户或流程。
- 范围：本次改什么、不改什么。
- 契约：接口、数据、状态、权限、错误码、交互边界。
- 验收：必须通过哪些场景，是否需要 E2E。
- 风险：升级红线、兼容性、回滚或带债可能性。

若这些信息不能从证据中得到，按最高价值问题逐个向用户确认。

## 任务规划纪律

`tasks.md` 必须按可验证交付物拆分，并包含执行约束。若当前 change 绑定 Trellis task，分工如下：

- OpenSpec `tasks.md`：产品/验收维度的可验证交付物，是 `/onsf-finish` 的检查对象。
- Trellis `implement.md`：工程执行计划、验证命令、review gates 和 rollback points。
- 两者可以互相引用，但不要复制整段正文；保持 OpenSpec 为变更正文真相源，Trellis 为任务运行时和工程计划。

```markdown
# Tasks: <change-id>

> 执行约束
> - 每个实现任务先明确验证点，再做最小实现。
> - 能写自动化测试时遵守 TDD：失败用例 → 最小实现 → 通过。
> - 前端任务优先分层验证：L1 契约/mock、L2 行为 Scenario、L3 联调/真实 API、L4 Browser 交叉验证。
> - 无测试工具时必须记录静态检查、手动验证或浏览器验证步骤。
> - 发现升级红线或范围膨胀时，暂停并回到 triage/design。

## 1. <模块或能力>

- [ ] 1.1 <任务描述>
      验证点: <命令、测试、手动步骤或验收场景>
```

## 任务粒度约束

`tasks.md` 按**可验证交付物**拆分，不按代码改动行数拆分。

- 一个 task 对应一个可独立验证的交付物（组件、hook、store、页面、API 模块、能力等），不是一行代码或一个文件操作。
- Tier 2 通常 3-8 个 task；Tier 3 拆分子任务后每个子任务同理。超过 10 个 task 时先自检是否过度拆分。
- 每个 task 必须有独立可执行的验证点，不能只是"完成 X 的一部分"或"准备 Y"。
- ❌ 过度拆分示例：把"创建文件""添加 import""写第一个函数""写样式"拆成 4 个 task——这些应合并为 1 个"实现 X 组件"task。
- ✅ 合理拆分示例：把"实现退款列表组件（含空态、加载态、错误态）"作为 1 个 task，验证点是组件渲染 + 3 种状态展示 + 对应 L2 行为测试通过。
- 拆分时优先按 OpenSpec `specs/**/spec.md` 中的 Requirement / Scenario 边界对齐，而非按文件层级或代码量。

## 实现纪律

按 `tasks.md` 执行实现时遵守以下纪律：

- 能写自动化测试的任务走 TDD 红绿循环：失败用例 → 最小实现 → 通过；不得先实现再补测试。
- 前端任务优先分层验证：L1 契约/mock、L2 行为 Scenario、L3 联调/真实 API、L4 Browser 交叉验证；逐 task 在 `tasks.md` 勾选时附上对应层级的验证证据。
- 无测试工具或任务性质不适合 TDD（纯配置、文档、紧急 Tier 0++）时，记录静态检查、手动验证或浏览器验证步骤代替，不得虚构已跑测试。
- Tier 2+ 大范围改动建议派发 `trellis-implement` 子代理执行；不可用时主会话按本技能执行。
- 发现升级红线或范围膨胀时，暂停并回到 triage/design。
- 各阶段结束（triage / openspec / implement / integrate / verify）**必须**调用 `onion_state.py set`（有绑定 task 时主写 meta + 镜像 current）；输出核对 `primary_write`。

## 事件驱动

实现阶段后可以由用户一句话触发：

| 用户表达 | 动作 |
|----------|------|
| 后端 spec 到了 / API 文档到了 | 使用 `external-spec` 写入 `backend-*.md` 并做差异分析 |
| YApi 接口到了 / re-check / 对齐 YApi | 使用 `re-check` 先落盘 `backend-yapi-*.md`，再按范围对齐 mock、类型、API 层和测试 |
| 只拉 YApi / 只落盘接口契约 | 使用 `pull-yapi` 写入 `backend-yapi-*.md` 并做差异分析，不修改业务代码 |
| 测试 spec 到了 / QA 文档到了 | 使用 `external-spec` 写入 `qa-*.md` 并做差异分析 |
| 跑 E2E / 浏览器验证 / 验证一下 | 使用 `verify-change` 生成或更新 `e2e-report.md` |
| 需求变了 / spec 改了 / 验收口径调整 | 暂停实现，按 `openspec-change` 的「已落盘产物的更新协议」同步 proposal/specs/tasks，再继续；触发升级红线则回到 `tier-triage` |
| 可以收尾 / 能归档吗 | 使用 `/onsf-finish`（先跑 `finish_check.py`）检查并自动归档 |

## 质量审查

check 是**四步复合阶段**，实现完成后、进入 integrate 之前由 Agent 自动串联执行，用户无需输入命令。完整口径（顺序理由、暂存范围、授权边界、降级）以 `rules/onion-sdd.mdc`「代码审查」为准，本节不复述细节：

1. 调用或派发 `trellis-check` 做工程质量审查，含其自身发现问题的修复。
2. 暂存本次 change 范围内的改动（禁止 `git add -A`）。
3. `/cr` 审查暂存区。
4. 修复 → 回跑受影响的门禁 → 重新暂存 → 复审，循环至通过。

顺序不可调换：`trellis-check` 会修改代码，必须在其完成后再暂存，否则审查对象与最终产物脱节。

第 1 步的 `trellis-check` 覆盖：

- 代码是否符合项目规范（lint、类型、约定）与 `.trellis/spec/` 对齐。
- 实现是否与 `proposal.md` 和 `specs/` 对齐。
- 是否存在明显回归或遗漏的边界情况。
- 是否有本次变更范围外的无关改动。

派发时可声明本阶段聚焦可执行门禁与 `.trellis/spec/` 对齐，团队规范、安全风险与影响范围由后续 `/cr` 覆盖；该切分是弱约束，结论重叠时合并去重即可。

如果 Trellis 不可用，第 1 步降级为项目可用的 lint、类型检查、测试和 OpenSpec 对照，并记录未能执行的检查与原因；第 2–4 步仍照常执行。`/cr` 或 `aicr-local` 不可用时按规则的降级路径处理，均不阻塞 check。

check 阶段不自动 `git commit`。用户明确授权提交时，按规则的提交门禁判断暂存区自 CR 通过后是否变化：未变化直接 commit，有变化或无法判定则重新 `/cr`。

## 完成标准

- 完整 OpenSpec 产物存在且能解释目标、变更、验收和不做范围。
- `tasks.md` 已更新，未完成项有明确状态。
- 外部 spec / YApi 差异已处理或记录。
- Tier 2+ 有 `e2e-report.md` 或用户认可的等价验收证据。
- `/onsf-finish` 必须先跑 `finish_check.py`；预检失败不得 archive。通过后自动执行 `openspec archive <change-id>`，并 `onion_state.py set --idle`；CLI 不可用时使用等效手工归档。

## 停止条件

- 用户未确认关键需求或验收口径。
- 发现权限、安全、支付、资金等风险但验证方案不足。
- 外部 spec 与当前方案冲突且无法在本轮解决。
- 浏览器验证缺账号、环境或权限，且用户无法提供。
