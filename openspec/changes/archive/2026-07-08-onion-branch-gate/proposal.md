## Why

使用 onion-sdd（Tier 0+/1/2+/3 任一入口）开发时，当前不会强制检查所在分支：如果用户没有显式提供飞书链接或说"创建分支"，Agent 会直接在当前分支（往往是 `master`）上修改代码；此外，如果用户停留在**另一个**活跃 change 的 feature 分支上开始一个新/不同的 change，也没有任何检测，会导致两个不相关需求的改动混进同一分支的 commit 历史。需要在进入实现前新增一个分支门禁堵住这两类场景。

## What Changes

- 在 `plugins/onion-sdd/rules/onion-sdd.mdc`「写入门禁」小节新增「分支门禁」二级小节，作为受保护分支列表、拦截+路由动作、`feat/<change-id>` 命名模板、`/onsf-auto` 特化行为的唯一权威定义。
- 在 `plugins/onion-sdd/skills/tier-triage/SKILL.md`「冲突检测」小节新增「跨 change 分支复用检测」子节：双层判定当前分支绑定的 change（Trellis active task 的 `branch` 字段优先；无 Trellis 时按 `feat/<change-id>` 命名约定解析并核对 OpenSpec 目录），判定出的 change-id 与本次要处理的不同时触发分支门禁。
- `plugins/onion-sdd/skills/mini-change/SKILL.md`、`plugins/onion-sdd/skills/light-change/SKILL.md`、`plugins/onion-sdd/skills/full-change/SKILL.md` 各自补充分支门禁挂载点引用；`full-change`「开发分支准备」小节定性从"可选触发"改为"分支门禁判定后的执行细节"，消除与新门禁的措辞矛盾。
- `plugins/onion-sdd/skills/auto-flow/SKILL.md` 新增「分支门禁（auto 特化）」小节：`/onsf-auto` 无交互模式下两类触发都自动生成 `feat/<change-id>` 分支并切换、不拦截，跨 change 分支复用命中时须在最终输出单独点名风险。

## Capabilities

### New Capabilities

- `onion-branch-gate`：onion-sdd 开发前分支门禁能力——检测受保护分支与跨 change 分支复用两类风险场景，命中后拦截并路由到分支创建/复用流程。

### Modified Capabilities

（无：本次不修改 `openspec/specs/` 下任何既有能力的需求，`onion-sdd` 插件规则/技能文件本身不在 `openspec/specs/` 建模范围内）

## Impact

- 影响范围：`plugins/onion-sdd/rules/onion-sdd.mdc`、`plugins/onion-sdd/skills/{tier-triage,mini-change,light-change,full-change,auto-flow}/SKILL.md`，共 6 个文件，纯文档/协议文本改动。
- 不影响业务代码、不新增依赖、不修改 `create-feature-branch/SKILL.md`、Trellis 源码或 `.trellis/scripts/**`。
- 已知盲区（本次不解决，记录见 `design.md` 的 Non-Goals）：没装 Trellis 且分支由飞书链接驱动命名（不含 OpenSpec change-id）时，跨 change 分支复用检测的双层判定都无法覆盖。
