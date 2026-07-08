# Implement: onion-sdd 开发前分支门禁

> 执行约束
> - 每个任务先明确验证点，再做最小实现。
> - 只改文档/协议文本，不涉及代码或自动化测试；验证方式以人工审阅 + 关键字核对为主。
> - 严禁修改 `create-feature-branch/SKILL.md`、Trellis 源码、`.trellis/scripts/**`、`.trellis/.runtime/**`。
> - 改动前后必须用 `git diff` 核对没有夹带无关格式改动（见 `.trellis/spec/guides/incidental-formatting-guide.md`）。

## 1. `rules/onion-sdd.mdc` 新增「分支门禁」权威定义

- [x] 1.1 在「写入门禁」小节内新增「分支门禁」二级小节，落实 `design.md` 第 1 节原文：两类触发条件（受保护分支列表：精确 `master`/`main`/`develop` + 前缀 `release/*` + detached HEAD；跨 change 分支复用：双层判定——Trellis 优先，无 Trellis 时按 `feat/<change-id>` 分支名解析 + OpenSpec 目录核实兜底，判定依据详情引用 `tier-triage`，本处只定义命中后动作）、拦截+路由（飞书优先 `create-feature-branch`，否则 `feat/<change-id>`，用户坚持当前分支则记录例外）、auto 模式特化（两类触发都自动生成不拦截，跨 change 复用需在 auto 输出里单独点名）、Tier 0 不受约束。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/rules/onion-sdd.mdc` 命中；人工核对两类触发条件（含跨 change 分支复用的双层判定）、拦截路由、命名模板、auto 特化均覆盖。

## 2. `tier-triage/SKILL.md` 新增跨 change 分支复用检测（检测逻辑本体）

- [x] 2.1 在「冲突检测」小节末尾追加「跨 change 分支复用检测」子节，落实 `design.md` 第 2 节原文：双层判定当前分支绑定的 change——① Trellis active task 的 `branch` 字段 + `meta.onion.change_id`；② 无 Trellis/未绑定时，解析分支名是否匹配 `feat/<change-id>` 且对应 OpenSpec 未归档目录真实存在。判定出的 change-id 与本次要处理的 change 不同则触发 `rules/onion-sdd.mdc`「分支门禁」；两层都无法判定时不触发。
      验证点：`grep -n "跨 change 分支复用" plugins/onion-sdd/skills/tier-triage/SKILL.md` 命中；人工核对双层判定依据与 `rules/onion-sdd.mdc` 触发条件 2 描述一致。

## 3. Tier 0+/1 挂载点

- [x] 3.1 `mini-change/SKILL.md`「实施纪律」小节前插入第 0 条引用（`design.md` 第 3 节原文）。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/mini-change/SKILL.md` 命中。
- [x] 3.2 `light-change/SKILL.md` 新增独立「分支门禁」小节（`design.md` 第 4 节原文），位置在「产物目录」之后、`proposal.md` 模板之前。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/light-change/SKILL.md` 命中。

## 4. Tier 2+ 衔接改造（谨慎处理措辞冲突）

- [x] 4.1 按 `design.md` 第 5 节，改写 `full-change/SKILL.md`「开发分支准备」小节：
      - 开头定性从"可选触发"改为"分支门禁判定后的执行细节"。
      - 触发条件精简（分支门禁判定 + 用户主动提前要求两种）。
      - 执行纪律第 3 条措辞从"不阻塞 onion-sdd 需求分析"改为"按分支门禁的 `feat/<change-id>` 兜底路径处理"，消除与新门禁"不能跳过直接在受保护分支改代码"的矛盾。
      - 其余执行纪律条目（1、2、4、5、6）保持原意不变。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/full-change/SKILL.md` 命中；人工核对「开发分支准备」小节不再出现"不阻塞...继续修改业务代码"这类允许跳过门禁的措辞。

## 5. `/onsf-auto` 特化

- [x] 5.1 `auto-flow/SKILL.md` 在「产物生成」小节前插入「分支门禁（auto 特化）」小节（`design.md` 第 6 节原文），覆盖两类触发条件的自动处理，跨 change 分支复用需在最终输出单独点名。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/auto-flow/SKILL.md` 命中；确认「风险门禁 > 必须停止」清单没有新增分支相关条目（按 PRD Decision 4/6，auto 模式两类触发都是自动处理不是停止）。

## 6. 跨文件一致性检查

- [x] 6.1 对六个改动文件（`rules/onion-sdd.mdc`、`tier-triage`、`mini-change`、`light-change`、`full-change`、`auto-flow`）运行 `grep -n "分支门禁" <file>`，确认全部命中且用词一致（受保护分支列表、`feat/<change-id>` 模板名称在各处一致，不要求逐字相同但语义不能冲突）。
- [x] 6.2 人工过一遍 `full-change/SKILL.md` 改动后的「分支门禁」引用 + 「开发分支准备」小节，确认两者是"门禁判定 vs 执行细节"的引用关系，没有互相矛盾或重复定义受保护分支列表。
- [x] 6.3 人工核对 `tier-triage/SKILL.md`「跨 change 分支复用检测」与 `rules/onion-sdd.mdc`「分支门禁」触发条件 2 的判定依据描述一致，没有互相矛盾。
- [x] 6.4 确认改动范围内没有夹带无关的 Markdown 表格重排版或格式改动（`git diff` 逐个文件检查，只保留本次新增段落）。发现 `README.md`/`USAGE.md`/`docs/feishu-wiki-onion-sdd-usage.md`（本次不涉及）及 `mini-change`/`light-change`/`full-change`/`auto-flow`（本次涉及但改动前已带有会话前遗留的表格重排版噪音）均有意外格式改动，已用 `git checkout HEAD -- <file>` 还原后重新只应用本次新增内容，`git diff` 复核为干净。

## Rollback

每个文件的改动都是新增段落/引用句 + `full-change/SKILL.md` 一处措辞修正，未删除既有结构性内容；如需回滚，直接 `git revert` 对应 commit。
