# onion-sdd 开发前分支门禁：禁止在 master 直接开发

## Goal

当前使用 onion-sdd（Tier 0+/1/2+/3 任一入口）开发时，不会强制检查当前所在分支；如果用户没有显式提供飞书链接或说"创建分支"，Agent 会直接在当前分支上修改代码。需要在进入实现前新增一个分支门禁，覆盖两类风险场景：

1. 当前在受保护分支（`master`/`main`/`develop`/`release/*`）时直接开发。
2. 当前分支其实绑定着**另一个**活跃 change（如需求 1 的 feature 分支），却在上面直接开始一个新/不同的 change（如需求 2），导致两个不相关需求的改动混进同一分支。

两类场景命中后走同一套拦截+路由动作，而不是静默直接改代码。

## Confirmed Facts（代码/文档核实）

- `plugins/onion-sdd/skills/full-change/SKILL.md` 的「开发分支准备」小节里，分支创建**只是可选触发**：仅当用户粘贴飞书卡片链接、或用户明确说"开始开发/创建分支/切开发分支"、或"团队约定"时才调用 `create-feature-branch`；这不是强制门禁，Tier 2+ 用户不特意要求就不会创建分支。
- `plugins/onion-sdd/skills/mini-change/SKILL.md`（Tier 0+）和 `plugins/onion-sdd/skills/light-change/SKILL.md`（Tier 1）**完全没有**任何分支相关的步骤或提示——从「适用条件」到「实施纪律」通篇不提分支，直接进入 `proposal.md`/`tasks.md` 编写和实现。这是最容易导致直接在当前分支（含 master）修改代码的入口，因为 Tier 0+/1 是日常最高频的变更类型。
- `plugins/onion-sdd/skills/auto-flow/SKILL.md`（`/onsf-auto` 无交互自动流程）的「风险门禁」「必须停止」清单中**没有**任何与当前分支相关的检查项；`/onsf-auto` 会直接进入 `materialize`/`implement` 阶段而不管当前分支是什么。
- `plugins/onion-sdd/rules/onion-sdd.mdc`（全局常驻规则）只提到"飞书项目卡片进入实现前如需创建开发分支，可调用 `create-feature-branch`"，同样是条件触发，不是门禁。
- `.trellis/workflow.md` 里 Trellis 自身只有 `task.py set-branch`/`set-base-branch` 用于记录分支元数据，不做任何分支切换前置检查——分支门禁不是 Trellis 现成能力，需要 onion-sdd 自己实现。
- `.cursor/skills/create-feature-branch/SKILL.md`（Common 插件扩展能力）是**飞书链接驱动**的分支创建工具：分支命名规则强依赖飞书工作项 ID 和迭代信息（`feat/<迭代>-<任务名>-m-<ID>`），触发条件是"用户提供飞书项目需求链接"。它本身有严格的"当前分支必须是 `master` 才允许创建"门禁（第 3 步），但这个门禁只在**该 skill 被调用时**生效，而它本身是否被调用是可选的——不解决"没有飞书链接的日常 Tier 0+/1 变更"场景。
- 仓库当前默认基线分支是 `master`（`create-feature-branch` 硬编码，明确禁止自动改用 `main`）。
- `plugins/onion-sdd/skills/tier-triage/SKILL.md`「冲突检测」小节已有雏形可复用：分级前会扫描 `openspec/changes/` 下所有未归档 change，并识别 Trellis active task / `.onion-sdd/current.json` 记录的当前活跃 change；命中时"优先提示先完成该变更"，但目前只是**软提示**（不阻断），且完全没有检查"当前 git 分支是否就是那个活跃 change 绑定的分支"。这是「跨 change 分支复用」检测的现成挂载点，不需要另起一套扫描逻辑。

## Decisions（已与用户确认）

1. **门禁行为（受保护分支时）**：拦截 + 询问。停止修改代码，向用户说明当前处于受保护分支：
   - 用户提供了飞书卡片链接 → 调用 `create-feature-branch` 按飞书信息创建分支。
   - 用户没有飞书链接，或本次是紧急修复（Tier 0++）→ 提供分支名选项（按 Decision 3 的模板 `feat/<change-id>`）供用户确认，或允许用户自行创建后告知分支名。
   - 用户明确要求"就在当前分支继续改" → 尊重用户选择，不重复拦截同一 change。
2. **受保护分支列表**：固定写死，不做成可配置项（与仓库现状一致，`create-feature-branch` 也是硬编码 `master`）。精确匹配 `master`、`main`、`develop`，前缀匹配 `release/*`。
3. **无飞书链接时的分支命名模板**：统一使用 `feat/<change-id>`，不区分 Tier/紧急修复/普通需求。`change-id` 沿用 OpenSpec 的 `MM-DD-<slug>` 格式，天然唯一。
4. **`/onsf-auto`（无交互自动模式）行为**：不拦截、不停止。检测到受保护分支且无飞书链接时，直接按 Decision 3 的模板自动生成分支名并切换，无需确认，在最终输出中说明已自动建分支。若未来需要飞书链接驱动的 auto 分支创建，不在本次范围内（auto 模式当前无飞书交互能力）。
5. **规则收敛位置**：不在 mini-change/light-change/full-change/auto-flow 四个文件里分别重复完整的门禁描述。分支门禁的判断逻辑（受保护分支列表、拦截行为、命名模板）写在 `rules/onion-sdd.mdc`「写入门禁」小节一处，作为 Onion SDD 全局常驻规则；四个 Tier 入口 skill 只需引用该规则并在自己的流程位置标注"此处触发分支门禁检查"，不复制判断细节。
6. **跨 change 分支复用检测**（原计划拆分独立任务，讨论后决定合并进本任务）：
   - **检测触发条件**：当前分支存在一个"绑定的活跃 change"，且本次请求经 `tier-triage` 判断是**新的/不同的** change（不是对该绑定 change 的延续）。判定"绑定的活跃 change"用双层判定，优先级从高到低：
     1. **Trellis 优先**：存在 Trellis active task 且 `task.json.branch` 等于 `git branch --show-current` 的结果 → 该 task 的 `meta.onion.change_id` 即为绑定 change-id。这一层能覆盖 `create-feature-branch` 飞书驱动命名（不含 change-id 的分支名，如 `feat/<迭代>-<任务名>-m-<ID>`），因为该 skill 本身会调用 `task.py set-branch` 写入 Trellis。
     2. **无 Trellis / 无绑定 task 时的分支名兜底**：解析当前分支名是否匹配 Decision 3 的模板 `feat/<change-id>`（这是我们自己强制的命名约定，不是猜测），且解析出的 `<change-id>` 对应 `openspec/changes/` 下一个真实存在的未归档目录 → 该 change-id 即为绑定 change-id。这一层不需要 Trellis，覆盖"没装 Trellis 但走了 Decision 3 兜底命名"的场景。
     3. 以上两层都无法判定（无 Trellis 绑定，且分支名也不匹配 `feat/<change-id>` 格式或找不到对应目录，例如没装 Trellis + 走飞书驱动命名的分支）→ 视为无法判定，不触发本检测，避免误判打断用户正常工作。
   - **检测位置**：扩展 `tier-triage/SKILL.md`「冲突检测」小节的现有扫描逻辑，新增分支绑定判断，不另起一套扫描；不新增任何持久化状态文件（`.onion-sdd/current.json` 不记录分支信息，维持不变）。
   - **命中后动作**：与「受保护分支」完全复用同一套路由（Decision 1：飞书链接优先 `create-feature-branch`；无链接/紧急修复走 `feat/<change-id>` 兜底；用户坚持当前分支则放行并记录例外）。区别在提示文案：需要明确说明"当前分支已绑定 `<change-id-A>`，继续在此处理 `<change-id-B>` 会把两次不相关改动混进同一个分支的 commit 历史"，比"受保护分支"场景的风险更隐蔽，因此文案要更直白地点出后果，不能只是一句通用提示。
   - **`/onsf-auto` 特化**：与受保护分支同一套自动处理（Decision 4）——检测到跨 change 分支复用时自动生成 `feat/<change-id-B>` 并切换，不停止；但由于这属于"两个 change 混在一起"的更高风险场景，auto 模式下必须在最终输出的 blocker/风险清单里显式点名（不能只是常规的"已自动创建分支"一句话带过）。

## Requirements（细化）

- 新增统一的分支门禁判断逻辑，写在 `rules/onion-sdd.mdc`「写入门禁」小节：给出受保护分支列表（Decision 2）、拦截+分支创建路由（Decision 1）、命名模板（Decision 3）、auto 模式差异（Decision 4）。
- Tier 0+（`mini-change`）、Tier 1（`light-change`）、Tier 2+（`full-change`）三个 skill 各自在"开始修改业务代码"前补一句「先过分支门禁（见 `rules/onion-sdd.mdc`「写入门禁」）」，作为显式挂载点（目前这三个 skill 完全没提分支，需要让读者知道这一步存在；OpenSpec 草稿阶段不受影响）。
- `auto-flow`（`/onsf-auto`）在 `materialize` 阶段前补充分支门禁的 auto 特化行为（自动生成+切换，不拦截）。
- 触发时机：**修改业务代码前**（即将进入 implement 阶段，与 `full-change/SKILL.md` 现有「开发分支准备」触发条件 3「当前工作区准备进入 implement 阶段」、`rules/onion-sdd.mdc` 现有「修改业务代码前应已存在当前 change 的 `tasks.md`」是同一个时间点）检查一次；不卡在 OpenSpec `proposal.md`/`tasks.md` 草稿阶段——draft 阶段的未提交文件本就会随 `git checkout -b` 一起带到新分支，不需要提前建分支。检查本身是一次性的 `git branch --show-current`，用户没有主动切回受保护分支就不会重复触发，不需要额外维护"是否已检查过"的状态字段。
- Tier 0（纯问答/排查/审阅，不修改任何文件）不触发本门禁——没有写入动作，没有分支风险。
- 检测方式：`git branch --show-current`；结果为空（detached HEAD）按"受保护分支"同等处理（保守默认，同样拦截+询问）。
- 扩展 `tier-triage/SKILL.md`「冲突检测」：新增"当前分支绑定到另一个活跃 change"的判断（Decision 6 的双层判定：Trellis 优先，无 Trellis 时按 `feat/<change-id>` 分支名解析 + OpenSpec 目录核实兜底），命中且本次是新/不同 change 时，触发与受保护分支相同的门禁动作，而不是维持现状的软提示。

## Out of Scope

- 不改动 `create-feature-branch` 自身的飞书链接驱动分支命名逻辑与其内部门禁（步骤 3 的"当前分支必须是 master 才能创建"）。
- 不改动 Trellis 的 `task.py set-branch`/`set-base-branch` 行为。
- 不引入受保护分支列表的可配置化（Decision 2 已确定为固定写死）。
- `/onsf-auto` 场景下基于飞书链接的分支命名，本次不做（auto 模式当前没有交互获取飞书链接的能力）。
- 跨 change 分支复用检测（Decision 6）不新增任何持久化状态文件（不新增 `.onion-sdd/current.json` 的分支记录字段，不新增 change 目录下的 sidecar 元数据文件）；分支名兜底判定只解析 Decision 3 规定的 `feat/<change-id>` 固定格式，不做更宽泛的自然语言/模糊匹配。
- 没装 Trellis 且分支是通过飞书链接由 `create-feature-branch` 创建（命名为 `feat/<迭代>-<任务名>-m-<ID>`，不含 OpenSpec change-id）的场景，双层判定都覆盖不到，仍视为无法判定、不触发——这是已知盲区，不在本次范围内解决（需要新的持久化机制才能覆盖，见 Decision 6 的方案取舍）。

## Acceptance Criteria

1. `rules/onion-sdd.mdc`「写入门禁」新增分支门禁描述，覆盖：受保护分支列表（`master`/`main`/`develop` 精确 + `release/*` 前缀 + detached HEAD）、拦截+飞书优先创建分支、无飞书链接时提供 `feat/<change-id>` 选项、用户明确要求继续当前分支时的例外、auto 模式自动生成不拦截。
2. `mini-change/SKILL.md`、`light-change/SKILL.md`、`full-change/SKILL.md` 各自在"开始修改业务代码"前补充分支门禁挂载点引用，不复制完整判断逻辑。
3. `auto-flow/SKILL.md` 在 `materialize` 前补充 auto 模式下"检测到受保护分支自动生成 `feat/<change-id>` 分支并切换，写入最终输出"的行为，且不在「必须停止」清单中新增本项（因为 auto 模式选择的是自动处理而非停止）。
4. Tier 0 明确不受影响（无需改动，纯问答路径本就不涉及写入）。
5. `full-change/SKILL.md` 现有「开发分支准备」小节的触发条件 3（"当前工作区准备进入 implement 阶段"）与新分支门禁的触发时机是同一个点；本次改动把该小节从"仅当用户主动要求才创建分支"（可选）改为"进入 implement 前必须通过分支门禁"（强制），门禁负责判断该不该拦截/怎么建分支，「开发分支准备」负责飞书路径下具体怎么调用 `create-feature-branch`——写清楚这是门禁的一种路由结果，而不是与门禁并列的另一套规则。
6. `tier-triage/SKILL.md`「冲突检测」新增"当前分支绑定到另一个活跃 change"的判断，双层判定：优先依据 Trellis active task 的 `branch` 字段；无 Trellis 或未绑定时，解析当前分支名是否匹配 `feat/<change-id>` 且对应 OpenSpec 未归档目录真实存在。命中且本次是新/不同 change 时，触发与「分支门禁」相同的拦截+路由动作，并在提示文案中明确指出"会把两个不相关需求的改动混进同一分支"的风险，而不是维持现状的软提示。两层都无法判定归属时不拦截。
7. `auto-flow/SKILL.md` 的 auto 特化行为覆盖两类触发（受保护分支 + 跨 change 分支复用）；跨 change 分支复用命中时，最终输出必须显式点名这一风险，不能和普通的"已自动创建分支"混在一句话里。
8. 不修改 `create-feature-branch/SKILL.md`、Trellis 源码、`.trellis/scripts/**`、`.trellis/.runtime/**`。

