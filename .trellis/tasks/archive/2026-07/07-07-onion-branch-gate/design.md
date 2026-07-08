# Design: onion-sdd 开发前分支门禁

## 总体结构

新增一段 canonical 规则文本，落在 `plugins/onion-sdd/rules/onion-sdd.mdc`「写入门禁」小节，覆盖两类触发条件（受保护分支 + 跨 change 分支复用）共用的动作定义（拦截、路由、命名模板、auto 特化）。`tier-triage` 负责"跨 change 分支复用"的检测本身（复用其既有冲突扫描）；`mini-change`/`light-change`/`full-change`/`auto-flow` 四个 skill 各自只加一句引用 + 各自场景下的差异化处理，不复制完整判断逻辑，避免"改一处忘几处"。

```
rules/onion-sdd.mdc  ← 权威定义：两类触发条件 + 拦截行为 + 命名模板 + auto 差异
        ↑                  ↑              ↑                ↑              ↑ 检测跨 change 分支复用
  mini-change      light-change      full-change      auto-flow      tier-triage
```

## 1. `rules/onion-sdd.mdc`「写入门禁」新增「分支门禁」小节

插入位置：紧跟在现有「写入门禁」小节的既有条目之后（第 37-48 行区域），新增一个二级小节：

```markdown
### 分支门禁

修改业务代码前（即将进入 implement 阶段，与下方"修改业务代码前应已存在 `tasks.md`"是同一时间点），必须确认满足以下两条，否则触发门禁。OpenSpec `proposal.md`/`tasks.md` 草稿阶段不受此门禁约束——未提交的草稿文件会随 `git checkout -b` 一起带入新分支，不需要先建分支再写文档。

**触发条件 1：当前分支是受保护分支**（固定列表，不做可配置项）：
- 精确匹配：`master`、`main`、`develop`
- 前缀匹配：`release/*`
- `git branch --show-current` 输出为空（detached HEAD）按受保护分支同等处理

**触发条件 2：当前分支绑定着另一个活跃 change**（检测逻辑见 `tier-triage/SKILL.md`「冲突检测」，本节只定义命中后的动作）：
- 双层判定，优先级从高到低：① 存在 Trellis active task 且 `task.json.branch` 等于当前分支，取该 task 的 `meta.onion.change_id`；② 无 Trellis/未绑定时，解析当前分支名是否匹配 `feat/<change-id>` 格式且对应 `openspec/changes/` 下真实存在的未归档目录，取解析出的 change-id。
- 判定出的 change-id 不等于本次要处理的 change-id 时触发。
- 两层都无法判定归属（无 Trellis 绑定，且分支名不匹配 `feat/<change-id>` 或找不到对应目录）时不触发——避免信息不足导致误判。

**命中任一触发条件时**：
1. 停止修改业务代码，向用户说明当前处于受保护分支 / 当前分支已绑定另一个 change `<change-id-A>`（触发条件 2 时，必须点名 `<change-id-A>`，并说明"继续会把两次不相关改动混进同一分支的 commit 历史"，不能用受保护分支场景的通用文案带过）。
2. 用户提供了飞书项目卡片链接 → 按 `full-change/SKILL.md`「开发分支准备」调用 `create-feature-branch` 创建分支。
3. 用户没有飞书链接，或本次是 Tier 0++ 紧急修复 → 提供分支名 `feat/<change-id>`（`change-id` 为当前 OpenSpec change 的 `MM-DD-<slug>`）供用户确认后创建，或允许用户自行创建分支后告知分支名。
4. 用户明确要求"就在当前分支继续改" → 尊重用户选择，记录在最终输出或 `proposal.md` 中，本次 change 生命周期内不再重复拦截。

**`/onsf-auto`（无交互自动模式）特化**：不拦截、不停止。命中任一触发条件时，直接按模板 `feat/<change-id>` 生成分支名并 `git checkout -b` 切换，无需确认；在最终输出中说明已自动创建并切换的分支名。触发条件 2 命中时，最终输出必须在风险/blocker 清单里显式点名"检测到跨 change 分支复用，已自动切换到新分支 `feat/<change-id>`，原分支 `<原分支名>` 绑定的 `<change-id-A>` 未受影响"，不能和触发条件 1 的常规提示合并成一句话。若已有飞书链接上下文但 auto 模式无法交互确认，同样直接走 `feat/<change-id>` 模板，不额外尝试调用 `create-feature-branch`（该 skill 依赖飞书 MCP 查询迭代信息，在无交互场景下不适合自动触发）。

Tier 0（纯问答/排查/审阅，无写入动作）不受本门禁约束。
```

## 2. `tier-triage/SKILL.md`「冲突检测」扩展（跨 change 分支复用检测本体）

现有「冲突检测」小节末尾"如果 Trellis active task 或 `.onion-sdd/current.json` 中已有活跃 change，优先提示先完成该变更"这句话保留（文件重叠场景的软提示不变），紧接着新增一段判断逻辑：

```markdown
## 冲突检测

分级前扫描 `openspec/changes/` 下所有未归档的 change。如果本次变更涉及的文件与任一活跃 change 的 `proposal.md` 中「影响范围」所列文件重叠，在输出中标注警告。

不阻断流程，但要求用户确认知晓冲突。如果 Trellis active task 或 `.onion-sdd/current.json` 中已有活跃 change，优先提示先完成该变更。

### 跨 change 分支复用检测

判定"当前分支绑定的 change"，按优先级依次尝试：

1. **Trellis 优先**：如果存在 Trellis active task 且其 `branch` 字段等于 `git branch --show-current` 的结果，取该 task 的 `meta.onion.change_id`。这一层能覆盖 `create-feature-branch` 飞书驱动命名的分支（`feat/<迭代>-<任务名>-m-<ID>`，不含 OpenSpec change-id），因为该 skill 会调用 `task.py set-branch` 写入 Trellis。
2. **分支名兜底**（没有 Trellis，或 Trellis active task 不存在/未绑定 `branch` 字段时）：解析 `git branch --show-current` 的结果是否匹配 `feat/<change-id>` 格式（Decision 3 的固定命名模板），且 `<change-id>` 对应 `openspec/changes/` 下一个真实存在的未归档目录。命中则取该 change-id。这一层不依赖 Trellis，覆盖"没装 Trellis 但走了 Decision 3 兜底命名"的场景。
3. 以上两层都未命中：视为无法判定，不触发本检测。

如果判定出的 change-id 与本次判断要处理的 change 不同（新建 change，或用户明确要处理另一个 change），触发 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」的门禁动作（拦截+路由），而不是停留在上面的软提示。

已知盲区：没装 Trellis 且分支是飞书驱动命名（不含 change-id）时，两层都无法判定，检测不生效——这是当前方案在"不新增持久化状态文件"约束下的固有取舍，不在本次范围内用新的状态文件弥补。
```

要点：这是本任务里唯一新增"检测逻辑"本体的地方；`rules/onion-sdd.mdc` 只负责定义命中后做什么，不重复判断条件，保持"一处检测、一处动作定义"的收敛结构。分支名兜底解析的是 Decision 3 强制约定的固定格式，不是宽泛的启发式猜测。

## 3. `mini-change/SKILL.md` 改动

在「实施纪律」小节前新增一句引用（不新增独立小节，保持这个 skill 的轻量风格）：

```markdown
## 实施纪律

0. 开始修改业务代码前，先过分支门禁（见 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」）；OpenSpec 草稿阶段不受影响。
1. 写产物前先确认仍符合 Tier 0+。
...
```

## 4. `light-change/SKILL.md` 改动

同样在实现相关纪律前插入引用。`light-change` 目前没有单独的"实施纪律"小节（直接是「产物目录」→「模板」→「升级条件」→「完成标准」结构），选择在「产物目录」小节后、模板小节前新增一段简短说明：

```markdown
## 产物目录

...(不变)...

## 分支门禁

开始修改业务代码前，先过分支门禁（见 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」）；OpenSpec 草稿阶段不受影响。

## proposal.md 模板
...
```

## 5. `full-change/SKILL.md` 改动

现有「开发分支准备」小节改动：把开头的定性从"可选触发"改为"分支门禁的执行细节"，触发条件列表精简为门禁触发（不再需要用户主动要求）：

```markdown
## 开发分支准备

进入 implement 阶段前的分支门禁判定见 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」。本小节说明门禁判定"需要创建分支"且用户提供了飞书项目卡片时，具体如何调用 `create-feature-branch`；`create-feature-branch` 是 Common 插件提供的通用扩展能力，不属于 onion-sdd 自有基座，不要把分支创建逻辑复制到 onion-sdd 内。

触发条件（满足任一即调用本小节流程）：

- 分支门禁判定当前处于受保护分支，且用户提供了飞书项目卡片链接或卡片信息，包含可解析的工作项链接，例如 `/detail/<id>`。
- 用户表达"开始开发""创建分支""切开发分支"，希望在分支门禁触发前主动提前创建。

执行纪律：
1. 先完成需求事实、范围和 OpenSpec/`tasks.md` 的最小落盘，避免在需求不清时提前建分支。
2. 调用 `create-feature-branch` 前，遵守该 skill 自身门禁：工作区必须干净、默认从 `master` 更新后创建分支、需要飞书项目 MCP 和 git/network 权限。
3. 如果 Common 插件或 `create-feature-branch` 不可用，或用户没有飞书链接：按分支门禁的 `feat/<change-id>` 兜底路径处理，不阻塞 onion-sdd 需求分析。
4. （不变）分支创建成功后记录飞书卡片 ID/URL、需求文档来源和 feature branch 名称。
5. （不变）Trellis task 绑定时用 `task.py set-branch` 写入。
6. （不变）分支创建失败时不继续修改业务代码，说明失败原因。
```

要点：第 3 条从"不阻塞 onion-sdd 需求分析"（原意：分支创建失败可以静默跳过继续改代码）改为"按分支门禁的 `feat/<change-id>` 兜底路径处理"——因为门禁生效后，"不阻塞"不能再等价于"跳过分支直接在受保护分支改代码"，必须走兜底命名模板。这是本次改动里唯一一处需要谨慎措辞、避免和新门禁矛盾的地方。

## 6. `auto-flow/SKILL.md` 改动

在「产物生成」小节（Tier 路由，第 116-125 行）之前插入一个新的小节「分支门禁（auto 特化）」，覆盖两类触发条件的 auto 处理（见 `rules/onion-sdd.mdc` 的 auto 特化描述，这里只引用不复制判断逻辑）：

```markdown
## 分支门禁（auto 特化）

进入 `materialize` 阶段前，按 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」的 auto 模式特化规则处理，覆盖两类触发条件：

- **受保护分支**：自动生成 `feat/<change-id>` 分支并切换，不停止、不拦截、无需确认；在「验证收束」的最终输出中说明已自动创建的分支名。
- **跨 change 分支复用**（检测依据见 `tier-triage/SKILL.md`「冲突检测 > 跨 change 分支复用检测」）：同样自动生成 `feat/<change-id>` 并切换，但必须在「验证收束」最终输出的风险/blocker 清单中单独点名"检测到当前分支绑定另一个 change `<change-id-A>`，已自动切换到 `feat/<change-id-B>`"，不能与受保护分支场景的提示合并成一句话。
```

不在「风险门禁」的「必须停止」清单中新增条目（PRD Decision 4/6 已确认：两类触发在 auto 模式下都是自动处理而非停止）。

## 兼容性与回滚

- 新增内容集中在 6 个文件（`rules/onion-sdd.mdc`、`tier-triage`、`mini-change`、`light-change`、`full-change`、`auto-flow`）的局部小节/引用句，不改变现有目录结构、不修改 `create-feature-branch`、Trellis 源码或脚本。
- `full-change/SKILL.md` 第 3 条执行纪律的措辞变化是唯一有实质语义变化的一处（从"允许跳过分支直接改代码"变为"必须走兜底命名模板"），`tier-triage` 的「跨 change 分支复用检测」是唯一新增判断逻辑本体的地方，其余改动均为新增引用性文字。
- 回滚：`git revert` 对应 commit 即可，不涉及数据迁移或运行时状态。

## 验证方式

纯文档/协议变更，无自动化测试。验证方式：
1. 人工审阅六个文件的新增/改动内容与 `rules/onion-sdd.mdc` 权威定义是否语义一致（不要求逐字相同）。
2. 用 `grep -n "分支门禁"` 确认六个文件都能命中新增引用。
3. 检查 `full-change/SKILL.md` 改动后的「开发分支准备」小节与「分支门禁」小节之间没有互相矛盾的表述（尤其是"不阻塞"这句措辞）。
4. 检查 `tier-triage/SKILL.md`「跨 change 分支复用检测」与 `rules/onion-sdd.mdc`「分支门禁」触发条件 2 的判定依据（Trellis 优先 `task.json.branch`/`meta.onion.change_id`，无 Trellis 时 `feat/<change-id>` 分支名解析 + OpenSpec 目录核实兜底）描述一致，没有互相矛盾。
