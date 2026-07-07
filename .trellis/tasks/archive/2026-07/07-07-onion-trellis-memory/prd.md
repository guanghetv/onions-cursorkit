# onion-sdd 记忆能力优先依赖 Trellis

## Goal

让 onion-sdd 具备和 Trellis 一样的"记忆"能力，且优先复用 Trellis 已有实现，而不是在 onion 侧另建一套。记忆分两层，都要接上：

1. **事件记忆（journal）**：能回答"上次这个项目改了什么"——复用 `add_session.py` / `.trellis/workspace/<dev>/journal-*.md`。
2. **经验记忆（code-spec 积累）**：能回答"这次学到的东西下次还能不能用上"——复用 `trellis-update-spec` skill / `.trellis/spec/<layer>/*.md`。

OpenSpec 的 `openspec/changes/**/specs/**/spec.md`（这次变更的行为契约）继续作为变更正文唯一真相源不变，和 Trellis 的 `.trellis/spec/`（跨变更持续积累的编码规范）是两套不同的东西，不重复、不复制。

## Confirmed Facts（代码/文档核实）

- Trellis 的记忆落在 `.trellis/workspace/<dev>/journal-*.md` + `index.md`，由 `add_session.py` 写入。
- **`add_session.py` 不要求存在 active Trellis task**：它只需要 developer 身份（`ensure_developer` 自动初始化），task 只是可选的 branch/package 推断来源，没有 task 时会退回 git 自动探测分支。也就是说"记 journal"这个动作本身和"是否创建了 Trellis task"是解耦的。
- 现状 `/onsf-finish`（`plugins/onion-sdd/commands/onsf-finish.md` 第 9 步 + "Trellis 收尾分工"节）把"提示执行 `/trellis:finish-work`"完全挂在"**当前 change 绑定了 Trellis task**"这个条件上；没绑定 task 时只字不提 Trellis，即使 Trellis 已安装可用。
- Trellis task 绑定门槛（现状，本次不改）：Tier 0+/1 可选、Tier 2+ 询问用户是否创建、Tier 3 必须；且任何 Tier 都不会自动创建/启动/归档 task（需用户同意）。
- `/trellis:finish-work`（`.agents/skills/trellis-finish-work/SKILL.md`）Step 3 归档 task、Step 4 记 journal；Step 3 在无 active task 时会自行跳过，Step 4 不依赖 task。但该 skill 会归档"当前 active 的 Trellis task"——如果开发者手头有其它不相关的 Trellis task 处于 active 状态，直接建议跑 `/trellis:finish-work` 有误归档风险。
- 结论 1：真正的缺口在于——**Tier 0+/1 等未绑定 Trellis task 的 onion 变更，即使 Trellis 已安装，也完全没有写入 journal，导致这部分（很可能是最高频的）变更完成后没有留下任何"上次改了什么"的记录**。
- 结论 2（本次追加核实）：`plugins/onion-sdd/**` 全文只在 `trellis-before-dev` 处**读** `.trellis/spec/`，**没有任何地方调用 `trellis-update-spec`**。这个缺口和是否绑定 Trellis task 无关——即使 Tier 2+/3 绑定了 task，onion 自己的 `/onsf-finish` 流程里也没有主动触发"这次学到的东西要不要写回 `.trellis/spec/`"的判断。绑定 task 的情况下之所以还能间接触发，是因为**整体会话在遵循 Trellis workflow.md 的 Phase 3.3（`trellis-implement -> trellis-check -> trellis-update-spec -> commit`）**，而不是 onion 自己主动接的；未绑定 task 时（`workflow-state: no_task`）没有这层约束，onion 也没补，所以完全漏了。

## Requirements（待细化）

- `/onsf-finish` 归档 OpenSpec change 成功后，检测 Trellis 是否可用（如 `.trellis/scripts/add_session.py` 存在 + developer 已初始化）。
- Trellis 可用时，不论当前 change 是否绑定 Trellis task，都应把这次变更记录进 Trellis journal；具体记录方式（直接调用 `add_session.py`，还是仍建议用户跑某个命令）待定，见下方待决问题。
- Trellis 不可用时，行为保持现状不变（仅 `.onion-sdd/current.json` + OpenSpec 归档）。
- 不改变 Trellis task 的创建/绑定门槛（Tier 2+ 询问、Tier 3 必须、其余可选）——本次只解决"journal 记录"这一层的耦合问题。
- 不违反现有硬边界：不把 OpenSpec 正文复制进 journal，journal 只写摘要/commit/验证结果。

## Decisions（已与用户确认）

1. **是否自动写 journal**：当 Trellis 可用但当前 change 未绑定 Trellis task 时，`/onsf-finish` 自动直接调用 `add_session.py` 记录，不需要额外征求用户同意（沿用 OpenSpec 归档门禁本身作为确认点）。
2. **commit hash 处理**：调用前检查 `git status --porcelain`；工作区干净则取 `git log -1 --format=%h` 作为 `--commit`；不干净则不传（对应 `add_session.py` 的"(No commits - planning session)"语义）。
3. **spec 积累也纳入本次范围**：`/onsf-finish` 在 Trellis 可用且未绑定 task 的分支（分支 C）里，除了写 journal，还要加载 `trellis-update-spec` 技能，判断这次变更是否有值得沉淀进 `.trellis/spec/` 的经验（新模式、踩坑、技术决策），需要则写入；即使结论是"无需更新"也要过一遍判断（对齐 Trellis Phase 3.3 的要求）。绑定 task 的分支（B）不用 onion 额外接，因为整体会话已经在走 Trellis workflow.md 的 Phase 3.3。

## Acceptance Criteria

- [ ] Trellis 不可用时，`/onsf-finish` 行为与改动前完全一致（不提 Trellis、不调用任何 Trellis 脚本）。
- [ ] Trellis 可用且当前 change 绑定 Trellis task 时，行为与改动前一致（仍是提示用户跑 `/trellis:finish-work`，不在 `/onsf-finish` 内直接调用 `add_session.py`，避免重复记 journal）。
- [ ] Trellis 可用且当前 change **未绑定** Trellis task 时，`/onsf-finish` 在 OpenSpec 归档成功（含带债归档）后自动调用 `add_session.py`，按 `design.md` 的参数规则传入 title/summary/commit，且不复制 OpenSpec 正文。
- [ ] 同一分支（Trellis 可用、未绑定 task）下，`/onsf-finish` 还会加载 `trellis-update-spec` 技能对本次变更做一次"是否需要沉淀经验"的判断；需要则写入 `.trellis/spec/` 对应文件，不需要也要在输出里说明"已判断，无需更新"。
- [ ] `/onsf-finish` 输出中新增两行说明：本次是否记录了 Trellis journal、本次 spec 积累判断结论（写了什么 / 无需更新）。
- [ ] `/onsf-auto` 文档明确"记 journal"和"spec 积累判断"都不算 task 生命周期操作，不触发"需要创建/启动/归档 Trellis task"停止条件。
- [ ] `README.md`/`USAGE.md`/飞书文档/`DESIGN-SUPPLEMENT.md` 中关于"journal 只在绑定 task 时才有"的表述全部同步更新，无自相矛盾残留；同时更新 Trellis 能力对照表，补充"spec 经验积累"这一行的 onion/Trellis 分工。
- [ ] 不修改 Trellis task 的创建/绑定 Tier 门槛；不修改 `.trellis/scripts/**`；不修改 `trellis-update-spec` skill 本身。

## Out of Scope

- 调整 Trellis task 创建/绑定的 Tier 门槛（仍按现状：2+ 询问、3 必须、其余可选）。
- 修改 Trellis 源码 / `.trellis/scripts/**` / `trellis-update-spec` skill 本身。
- `.onion-sdd/current.json` 的跨会话恢复机制（本次只涉及"事后记忆"，不涉及"进行中恢复"）。
- 项目内 `.cursor/skills/` 或 `.claude/skills/` 下 onion-sdd 的同步副本（如存在），默认不主动同步，除非用户要求。
- 绑定 Trellis task 分支（B）下补一条 onion 专属的 spec-update 触发——该分支已经由 Trellis workflow.md Phase 3.3 覆盖，不重复接。
