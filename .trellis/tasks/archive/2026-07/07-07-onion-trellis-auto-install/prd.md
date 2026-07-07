# onion-sdd 检测缺失 Trellis 时交互式安装初始化

## Goal

当 onion-sdd 运行时发现当前项目没有安装/初始化 Trellis，主动询问用户是否要安装 CLI 并初始化项目（而不是像现状一样悄悄跳过、什么都不提），提高 Trellis 被采用的概率——尤其是在上一个任务（`07-07-onion-trellis-memory`）已经让"有 Trellis"的价值变得更高之后。

## Confirmed Facts（代码/文档核实）

- Trellis 安装分两步（`plugins/onion-sdd/USAGE.md` §8.2）：① `npm install -g @mindfoldhq/trellis` 装 CLI；② 项目根目录跑 `trellis init -u <name> [--claude] [--cursor] [--codex] [--opencode] [--gemini] [--pi] ...` 按平台生成对应目录。
- `trellis init` **不会**自动管理 `.gitignore`。核实方式：本仓库 `.gitignore` 里的 `.cursor/`、`.claude/`、`.codex/` 三行是 `e39f929`（`feat:onion-sdd流程初始化搭建`）这次提交手动加的，不是 Trellis CLI 自动写入的。
- 本仓库当前的 gitignore 写法是"整个平台目录一刀切忽略"；副作用是 `.cursor/commands/opsx-*.md`（第三方 OpenSpec 插件的手写文件，没有独立源头、直接放在共享目录下）需要 `git add -f` 才能保留追踪。这个"手写文件与生成目录混用"是本仓库特有场景，不是通用新项目会遇到的情况；且 gitignore 规则不会取消已追踪文件的追踪，不存在误伤风险。综合评估后（见 Decision 6）保留整目录忽略写法，与本仓库现状一致。
- `.agents/skills/` 是 Trellis 的跨平台规范技能包，始终被 git 追踪，不受这次改动影响。
- 当前 onion-sdd 检测"Trellis 是否可用"的方式（上个任务已定）：`.trellis/scripts/add_session.py` 文件是否存在。
- 当前 Trellis task 绑定门槛（不变）：Tier 0+/1 可选、Tier 2+ 询问、Tier 3 必须。
- 现状：Trellis 不可用时，onion-sdd 全流程（`onsf-plan`/`onsf-fix`/`onsf-tweak`/`onsf-continue`/`onsf-auto`/`onsf-finish`）都只是静默降级，从不主动提示"要不要装 Trellis"。
- **重要缺口（本次追加核实）**：`USAGE.md`/飞书文档描述"Tier 2+ 标准需求：Agent 会在规划阶段询问是否创建 Trellis task"，但翻遍 `full-change/SKILL.md`、`onsf-plan.md`、`tier-triage/SKILL.md` 全文，**没有任何一处写着这个执行指令**——这是文档描述了协议里实际不存在的行为。本次要挂"检测 Trellis 缺失并提议安装"这个新逻辑，需要在 `full-change/SKILL.md` 的需求接入入口顺手把这个锚点本身也正式写出来（属于让新功能有地方挂载的必要前提，不是额外范围蔓延）。
- `/onsf-auto`（自动化入口）现有边界已经写明"如果没有 active Trellis task，不自动创建"、"需要创建/启动/归档 Trellis task"是停止条件之一——本次新增的"询问要不要装 Trellis"同理，**不适用于 `/onsf-auto` 无交互场景**，只在 `/onsf-plan` 等手动入口的 Tier 2+/3 生效。

## Decisions（已与用户确认）

1. **触发时机**：仅 Tier 2+/3，挂在 `full-change/SKILL.md` 需求接入入口（和"是否创建 Trellis task"同一个检查点）。Trellis 不可用时，先问"要不要装"，不问"要不要建 task"（建 task 的前提是先有 Trellis）。
2. **反复打扰策略**：不记忆用户的拒绝，每次 Tier 2+/3 都问。不写额外状态字段。
3. **执行方式**：用户同意后，Agent 先探测 `trellis --version`；CLI 已存在则跳过安装直接 `trellis init`，不存在才跑 `npm install -g @mindfoldhq/trellis`（需要 `full_network` 权限）再 `trellis init`。不是只打印命令。
4. **平台选择**：默认只初始化当前正在交互的 Agent 所在平台（如当前是 Cursor 就只加 `--cursor`），额外问一句要不要顺带初始化其它平台。
5. **`/onsf-auto` 边界**：这次新增的"询问要不要装 Trellis"只在手动入口（`/onsf-plan` → `full-change`）生效，`/onsf-auto` 无交互场景不问，保持现状（不自动创建/安装，静默降级）。
6. **gitignore 范围**（讨论后由精确子路径改回整目录忽略）：为本次实际初始化的平台追加整目录忽略（`.cursor/`、`.claude/`、`.codex/`，与本仓库现状一致），不单独区分子路径。理由：gitignore 不会取消已追踪文件的追踪，不存在误伤风险；"手写文件与生成目录混用"（如本仓库的 `opsx-*.md`）是特例场景，遇到时后续新文件用 `git add -f` 处理即可，不需要为通用流程增加精确子路径的维护成本。

## Requirements（细化）

- 在 `full-change/SKILL.md` 需求接入入口新增一个显式"Trellis 使用检查"步骤：先测 Trellis 是否可用；不可用则按 Decision 1-4 询问并执行安装/初始化；可用则维持现状（询问是否创建 task，这部分现状文案后续如需补全再另行处理，不在本次任务内主动展开）。
- gitignore 更新：安装/初始化成功后，Agent 按 Decision 6，为本次实际初始化的平台追加整目录忽略到 `.gitignore`（如果条目已存在则跳过，不重复添加）。
- 失败处理：`npm install -g` 失败（网络/权限）或 `trellis init` 失败时，报告具体原因，不阻塞 onion 自身 Tier 2+/3 流程——按"未安装 Trellis"的现有降级路径继续。
- 用户拒绝安装时，onion-sdd 按现状继续走完全流程（Trellis 不可用降级路径），不阻塞。

## Acceptance Criteria

1. `full-change/SKILL.md` 新增显式步骤：Tier 2+/3 进入需求接入前检测 Trellis 可用性（`.trellis/scripts/add_session.py` 是否存在）。
2. Trellis 不可用时，Agent 询问用户是否安装；用户同意后先探测 `trellis --version`（已装则跳过安装），未安装才 `npm install -g @mindfoldhq/trellis`，再执行 `trellis init -u <name> --<当前平台>`，并追加询问是否顺带初始化其它平台。
3. 安装/初始化成功后，Agent 把本次涉及平台的整目录忽略规则（`.cursor/`/`.claude/`/`.codex/`）追加到根 `.gitignore`，已存在的条目不重复添加。
4. 用户拒绝安装、或安装/初始化失败时，onion-sdd 不阻塞，按现状"Trellis 不可用"的降级路径继续 Tier 2+/3 流程，并说明原因。
5. `/onsf-auto.md` 明确写出：本次新增的"询问安装 Trellis"不适用于自动模式，维持现有静默降级 + 停止条件不变。
6. 每次 Tier 2+/3 触发都重新询问（不引入拒绝记忆状态），符合 Decision 2。
7. 不修改 `.trellis/scripts/**`、`.trellis/.runtime/**`、Trellis CLI 自身源码。
8. `USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md`、`README.md`（如涉及同一张能力对照表）同步更新，避免出现"文档说会问，协议没写"的新缺口。

## Out of Scope

- 修改 Trellis CLI/`trellis init` 本身的行为。
- 上一个任务（`07-07-onion-trellis-memory`）已完成的 journal/spec 积累分支逻辑，本次不重复改。
- 非 cursor/claude/codex 之外平台（qoder/kiro/windsurf/opencode/gemini/pi 等）的专项适配细节，除非用户要求纳入。
- 已有 Trellis 但未创建 task 时"是否创建 Trellis task"这句话本身缺失执行指令的问题——本次只顺带把锚点点位写出来，不展开成独立的完整任务创建询问文案设计。
