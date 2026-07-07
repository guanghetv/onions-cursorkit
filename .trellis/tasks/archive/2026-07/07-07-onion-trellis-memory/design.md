# Design: onion-sdd 记忆能力优先依赖 Trellis

## 边界

- 只改 `plugins/onion-sdd/**` 下的协议文档（skills/commands/rules/README/USAGE/docs），不改 `.trellis/scripts/**`、不改 Trellis 源码。
- 不改变 Trellis task 的创建/绑定门槛（Tier 2+ 询问、Tier 3 必须、其余可选）——这次只解决"journal 记录"和"是否绑定 task"的强耦合问题。
- 不影响 OpenSpec 是变更正文唯一真相源的硬约束；journal 只写摘要，不复制 `proposal.md`/`specs/**`/`tasks.md` 正文。
- 只在项目试点目录 `plugins/onion-sdd/` 内改；如项目本地存在 `.cursor/skills/*` / `.claude/skills/*` 的同步副本，视用户是否要求同步再决定（默认先改源插件，不主动扩散）。

## 触发条件：Trellis 是否可用

检测方式：`.trellis/scripts/add_session.py` 文件存在，即视为"Trellis 可用"。不要求 `.trellis/.developer` 已初始化——`add_session.py` 内部的 `ensure_developer` 会自动完成初始化。

## 行为变更：`/onsf-finish`

现状（第 9 步 + "Trellis 收尾分工"节）：只有"当前 change 绑定 Trellis task"时才提及 Trellis，收尾建议是让用户去跑 `/trellis:finish-work`。

新行为，在 OpenSpec 归档成功后（正常通过或带债归档均算成功）按以下分支处理：

| 分支 | 条件 | 动作 |
|------|------|------|
| A | Trellis 不可用 | 保持现状：只更新 `.onion-sdd/current.json`，不提 Trellis。 |
| B | Trellis 可用 且当前 change **绑定** Trellis task | 保持现状：提示用户"工作区提交干净后执行 `/trellis:finish-work`"，由它负责 task 归档 + journal。**不**在 `/onsf-finish` 内直接调用 `add_session.py`，避免和 `/trellis:finish-work` 的 Step 4 重复记一次 journal。spec 积累（`trellis-update-spec`）也不在这里重复接——绑定 task 时整体会话已经在遵循 Trellis workflow.md 的 Phase 3.3（`trellis-implement -> trellis-check -> trellis-update-spec -> commit`）。 |
| C（新增） | Trellis 可用 且当前 change **未绑定** Trellis task | `/onsf-finish` 自身直接：① 调用 `add_session.py` 记一条 journal（见下方参数规则）；② 加载 `trellis-update-spec` 技能做一次 spec 积累判断（见下方"spec 积累判断"节）。两者都不涉及 task 创建/启动/归档，不需要用户额外确认（沿用 OpenSpec 归档门禁本身已经是确认点）。 |

### 为什么"两层记忆"都挂在分支 C，而不是"任意 Trellis 可用就触发"

journal 和 spec 积累在分支 B 场景下已经由 Trellis 自己的 workflow.md 覆盖（有 task 在，Phase 3.3/`/trellis:finish-work` 自然会跑到）。分支 C 是"有 Trellis 装置，但这次变更完全在 Trellis workflow 之外运行"（未绑定 task，不会有任何 Trellis 侧的 Phase 3.3/finish-work 触发点），所以需要 onion 自己接手，否则这部分变更（大概率是高频的 Tier 0+/1 小改动）永远不会给 Trellis 留下任何记忆。

### 分支 C 的 `add_session.py` 调用参数

- `--title`：优先取 `proposal.md` 的一级标题（去掉 `# ` 前缀）；取不到则用 `change-id`。
- `--summary`：Agent 用 1-2 句话总结这次变更做了什么（可参考 `tasks.md` 完成情况或 `proposal.md` 的目标段落改写），**不得整段复制** `proposal.md`/`specs/**` 正文。
- `--commit`：
  - 调用前先跑 `git status --porcelain`。
  - 干净（无未提交改动）→ 用 `git log -1 --format=%h` 取最近一次 commit hash 传入 `--commit`。
  - 不干净 → 传 `-`（即不传该参数，`add_session.py` 默认值就是 `-`，对应"(No commits - planning session)"语义）。
- 不传 `--branch`、`--package`：让脚本按自身默认逻辑（git 自动探测分支；单仓库项目忽略 package）处理。
- 使用默认 `auto_commit=True`（脚本默认行为），允许其对 journal/index 自身做一次范围受限的 auto-commit（脚本已保证只 add `.trellis/workspace/**` 等安全路径，不碰业务代码）。

### 分支 C 的 spec 积累判断（`trellis-update-spec`）

在调用 `add_session.py` 之前（或之后均可，二者互不依赖），额外执行一步：

1. 加载 `trellis-update-spec` skill（`.claude/skills/trellis-update-spec/SKILL.md`）。
2. 依据"Interactive Mode"的三个问题（学到了什么 / 为什么重要 / 属于哪个 spec 文件）对本次 change 做判断，判断素材来自当前 change 的 `proposal.md`、`tasks.md`、实现过程中的 diff/决策，**不需要**额外的用户访谈。
3. 结论只有两种：
   - **无需更新**：一次性的实现细节，没有可复用的模式/约定/坑。输出里如实写"已判断，无需更新"。
   - **需要更新**：按该 skill 的模板（Design Decision / Convention / Pattern / Forbidden Pattern / Common Mistake / Gotcha）写入 `.trellis/spec/<package>/<layer>/` 对应文件，必要时同步该 layer 的 `index.md`。
4. 边界：只写"这次学到的可复用经验"，不写"这次变更做了什么"（那是 journal 的职责）；不把 OpenSpec `proposal.md`/`specs/**` 正文整段搬进 `.trellis/spec/`。

### 输出要求

`/onsf-finish` 完成后的输出中，分支 C 需要新增两行说明，例如：

```
- Trellis journal: 已通过 add_session.py 记录本次变更（未绑定 Trellis task）
- Trellis spec 积累: 已判断，无需更新 / 已写入 .trellis/spec/<path>
```

分支 A / B 保持现有输出格式不变。

## 行为变更：`/onsf-auto`

现状 `skills/auto-flow/SKILL.md` 和 `commands/onsf-auto.md` 里"需要创建/启动/归档 Trellis task"是停止条件之一；这次新增的"记 journal"和"spec 积累判断"都不属于 task 生命周期操作（不创建、不启动、不归档 task），因此不受该停止条件约束，但需要在文档里明确写出来，避免未来读到该规则的 Agent 误判为"涉及 Trellis 操作要停下来问"。

`onsf-auto.md` "Trellis 边界"节新增一句：记录 journal（`add_session.py`）和 spec 积累判断（`trellis-update-spec`）都不算 task 生命周期操作，`/onsf-finish` 门禁通过时可按分支 C 规则自动执行，不在停止条件之列。

## 文档同步范围

除核心行为文档 `commands/onsf-finish.md` 外，以下文档中提到"只有绑定 Trellis task 才有 journal"的对照表 / FAQ 需要同步更新，避免文档自相矛盾：

- `plugins/onion-sdd/README.md`
- `plugins/onion-sdd/USAGE.md`
- `plugins/onion-sdd/docs/feishu-wiki-onion-sdd-usage.md`
- `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`（Phase 1 Trellis Adapter 章节的同步时机表）
- `plugins/onion-sdd/commands/onsf-auto.md`（Trellis 边界节）

以上文档里"Trellis 能力对照表"（对照"依赖缺失时的降级"）目前只有"开发者 journal、会话摘要"一行，需要新增"spec 经验积累"一行，说明：绑定 task → 走 Trellis workflow.md Phase 3.3；未绑定但 Trellis 可用 → `/onsf-finish` 分支 C 自动判断；Trellis 不可用 → 无此能力（onion 没有等价替代）。

不改 `skills/trellis-adapter/SKILL.md` 的 `meta.onion` 协议本身——分支 C 场景下没有 Trellis task，也就没有 `task.json` 可写，`trellis-adapter` 协议不受影响；也不改 `trellis-update-spec` skill 本身，只是新增一处调用方。

## 兼容性 / 回滚

- 纯文档协议变更，无 schema、无脚本改动，可直接回滚（git revert 相关 commit）。
- 对已归档的历史 change 无影响；只影响本次变更之后新走 `/onsf-finish` 分支 C 的场景。
- 风险点：分支 C 会在无 Trellis task 时对 `.trellis/workspace/**` 做一次 auto-commit（脚本自带行为）。如果用户不希望 onion 触发任何 git 操作，需要在 Trellis 侧关闭 `session_auto_commit`（`.trellis/config.yaml`），这不是本次改动引入的新开关，是复用脚本已有配置项。
