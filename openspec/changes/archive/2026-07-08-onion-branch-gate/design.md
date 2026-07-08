## Context

`plugins/onion-sdd/skills/full-change/SKILL.md`「开发分支准备」只是可选触发（用户主动要求才建分支）；`mini-change`/`light-change`（Tier 0+/1，日常最高频入口）完全不提分支；`auto-flow`（`/onsf-auto`）的风险门禁清单里也没有分支相关检查项。`create-feature-branch`（Common 插件扩展能力，飞书链接驱动）自身虽有"当前分支必须是 `master`"的硬门禁，但只在被调用时生效，调用与否是可选的。这些空白共同导致"不提供飞书链接就默认在当前分支（含 `master`）直接改代码"的现状。

`plugins/onion-sdd/skills/tier-triage/SKILL.md`「冲突检测」已有雏形可复用：分级前扫描 `openspec/changes/` 下所有未归档 change，并识别 Trellis active task / `.onion-sdd/current.json` 记录的当前活跃 change，命中时给软提示（不阻断）。这是"跨 change 分支复用"检测的现成挂载点。

## Goals / Non-Goals

**Goals:**
- 覆盖两类风险场景：① 在受保护分支（`master`/`main`/`develop`/`release/*`）直接开发；② 在绑定着另一个活跃 change 的分支上开始新/不同的 change。
- 两类场景命中后走同一套拦截 + 路由动作（飞书优先 `create-feature-branch`，否则 `feat/<change-id>` 兜底，用户坚持当前分支则放行并记录例外）。
- 规则收敛：判断逻辑只在 `rules/onion-sdd.mdc` 定义一处，`tier-triage`/`mini-change`/`light-change`/`full-change`/`auto-flow` 只引用，不复制。
- 跨 change 分支复用检测不强依赖 Trellis：没装 Trellis 时，只要分支遵循 `feat/<change-id>` 命名约定仍可被检测到。

**Non-Goals:**
- 不改动 `create-feature-branch` 自身的飞书链接驱动分支命名逻辑与其内部门禁。
- 不改动 Trellis `task.py set-branch`/`set-base-branch` 行为，不修改 Trellis 源码或 `.trellis/scripts/**`。
- 不引入受保护分支列表的可配置化（固定写死）。
- 不新增任何持久化状态文件（不给 `.onion-sdd/current.json` 加分支字段，不给 change 目录加 sidecar 元数据）。
- 已知盲区不在本次解决：没装 Trellis 且分支是飞书链接驱动命名（`feat/<迭代>-<任务名>-m-<ID>`，不含 OpenSpec change-id）时，跨 change 分支复用检测的两层判定都覆盖不到——这需要新的持久化机制才能补齐，留作后续独立评估。

## Decisions

1. **门禁行为（命中任一触发条件时）**：拦截 + 询问。停止修改代码，说明当前处于受保护分支 / 当前分支已绑定另一个 change：
   - 用户提供飞书卡片链接 → 调用 `create-feature-branch` 创建分支。
   - 用户没有飞书链接，或本次是 Tier 0++ 紧急修复 → 提供 `feat/<change-id>` 选项供确认，或允许用户自行创建后告知分支名。
   - 用户明确要求"就在当前分支继续改" → 尊重选择，记录例外，本次 change 生命周期内不再重复拦截。
   - *替代方案考虑*：曾考虑对跨 change 场景采用更严格的"强制阻断，不给例外"，但会破坏"用户在同一分支处理多个小改动"的合理场景，最终统一采用与受保护分支相同的例外机制。
2. **受保护分支列表**：固定写死（`master`/`main`/`develop` 精确匹配 + `release/*` 前缀 + detached HEAD），不做可配置项，与仓库现状及 `create-feature-branch` 硬编码 `master` 一致。
3. **无飞书链接时的分支命名模板**：统一 `feat/<change-id>`，`change-id` 沿用 OpenSpec 的 `MM-DD-<slug>` 格式，天然唯一，不区分 Tier。
4. **`/onsf-auto` 行为**：不拦截、不停止，自动按 Decision 3 模板生成分支名并切换；跨 change 分支复用命中时必须在最终输出单独点名风险，不能与受保护分支场景的提示合并。
5. **规则收敛位置**：权威定义只写在 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」；`tier-triage`/`mini-change`/`light-change`/`full-change`/`auto-flow` 各自只加引用/差异化处理。
6. **跨 change 分支复用检测——双层判定**（*替代方案考虑*：最初设计只依赖 Trellis `task.json.branch` + `meta.onion.change_id`；经复核发现 onion-sdd 明确支持"不装 Trellis、OpenSpec 独立跑"的路径，纯 Trellis 依赖会让这部分用户的检测完全失效，因此改为双层）：
   - 优先级 1（Trellis）：存在 Trellis active task 且 `task.json.branch` 等于当前分支 → 取该 task 的 `meta.onion.change_id`。能覆盖飞书驱动命名（不含 change-id）的分支，因为 `create-feature-branch` 会调用 `task.py set-branch` 写入 Trellis。
   - 优先级 2（分支名兜底，无 Trellis/未绑定时）：解析当前分支名是否匹配 `feat/<change-id>`，且 `<change-id>` 对应 `openspec/changes/` 下真实存在的未归档目录 → 取该 change-id。这是对 Decision 3 强制命名约定的精确解析，不是模糊猜测。
   - 两层都未命中：视为无法判定，不触发——避免信息不足导致误判打断用户正常工作。
   - 检测位置：扩展 `tier-triage/SKILL.md`「冲突检测」的现有扫描逻辑，不另起一套扫描；不新增持久化状态文件。

## Risks / Trade-offs

- [Risk] 跨 change 分支复用检测对没装 Trellis + 飞书驱动命名的分支仍是盲区 → Mitigation：已在 Non-Goals/proposal 中显式记录为已知盲区，待后续单独评估是否值得引入 sidecar 元数据文件解决。
- [Risk] `full-change/SKILL.md`「开发分支准备」执行纪律第 3 条措辞变化（从"不阻塞可以跳过"改为"走兜底命名模板"）可能与历史习惯冲突 → Mitigation：已在实现中确认不再出现"允许跳过门禁直接改代码"的措辞，且其余执行纪律条目保持不变，改动范围最小。
- [Risk] 纯文档改动缺少自动化测试保障一致性 → Mitigation：用 `grep -n "分支门禁"` 对六个改动文件做关键字命中核对 + 人工审阅语义一致性，作为验证方式。

## Migration Plan

无需迁移：新增内容为局部小节/引用句，不改变现有目录结构。回滚方式为 `git revert` 对应 commit。
