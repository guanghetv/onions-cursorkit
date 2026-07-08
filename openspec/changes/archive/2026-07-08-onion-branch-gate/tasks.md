# Tasks: onion-branch-gate

> 执行约束
> - 每个任务先明确验证点，再做最小实现。
> - 只改文档/协议文本，不涉及代码或自动化测试；验证方式以人工审阅 + 关键字核对为主。
> - 严禁修改 `create-feature-branch/SKILL.md`、Trellis 源码、`.trellis/scripts/**`、`.trellis/.runtime/**`。
> - 改动前后必须用 `git diff` 核对没有夹带无关格式改动。

## 1. `rules/onion-sdd.mdc` 新增「分支门禁」权威定义

- [x] 1.1 在「写入门禁」小节内新增「分支门禁」二级小节：两类触发条件（受保护分支列表；跨 change 分支复用的双层判定）、拦截+路由、auto 模式特化、Tier 0 不受约束。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/rules/onion-sdd.mdc` 命中；人工核对两类触发条件、拦截路由、命名模板、auto 特化均覆盖。

## 2. `tier-triage/SKILL.md` 新增跨 change 分支复用检测（检测逻辑本体）

- [x] 2.1 在「冲突检测」小节末尾追加「跨 change 分支复用检测」子节：双层判定（Trellis 优先，无 Trellis 时按 `feat/<change-id>` 分支名解析 + OpenSpec 目录核实兜底）。
      验证点：`grep -n "跨 change 分支复用" plugins/onion-sdd/skills/tier-triage/SKILL.md` 命中；人工核对判定依据与 `rules/onion-sdd.mdc` 触发条件 2 描述一致。

## 3. Tier 0+/1 挂载点

- [x] 3.1 `mini-change/SKILL.md`「实施纪律」小节前插入第 0 条引用。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/mini-change/SKILL.md` 命中。
- [x] 3.2 `light-change/SKILL.md` 新增独立「分支门禁」小节，位置在「产物目录」之后、`proposal.md` 模板之前。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/light-change/SKILL.md` 命中。

## 4. Tier 2+ 衔接改造（谨慎处理措辞冲突）

- [x] 4.1 改写 `full-change/SKILL.md`「开发分支准备」小节：定性从"可选触发"改为"分支门禁判定后的执行细节"，消除与新门禁的矛盾措辞。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/full-change/SKILL.md` 命中；人工核对「开发分支准备」小节不再出现"不阻塞...继续修改业务代码"这类允许跳过门禁的措辞。

## 5. `/onsf-auto` 特化

- [x] 5.1 `auto-flow/SKILL.md` 在「产物生成」小节前插入「分支门禁（auto 特化）」小节，覆盖两类触发条件的自动处理。
      验证点：`grep -n "分支门禁" plugins/onion-sdd/skills/auto-flow/SKILL.md` 命中；确认「风险门禁 > 必须停止」清单没有新增分支相关条目。

## 6. 跨文件一致性检查

- [x] 6.1 对六个改动文件运行 `grep -n "分支门禁" <file>`，确认全部命中且用词一致。
- [x] 6.2 人工过一遍 `full-change/SKILL.md`「分支门禁」引用 + 「开发分支准备」小节，确认是"门禁判定 vs 执行细节"的引用关系，没有互相矛盾或重复定义受保护分支列表。
- [x] 6.3 人工核对 `tier-triage/SKILL.md`「跨 change 分支复用检测」与 `rules/onion-sdd.mdc`「分支门禁」触发条件 2 的判定依据描述一致，没有互相矛盾。
- [x] 6.4 确认改动范围内没有夹带无关的 Markdown 表格重排版或格式改动；发现并还原了会话前遗留的意外格式噪音（`README.md`/`USAGE.md`/`docs/feishu-wiki-onion-sdd-usage.md` 及 `mini-change`/`light-change`/`full-change`/`auto-flow`），复核 `git diff` 为干净。

## 7. OpenSpec 留痕

- [x] 7.1 创建 `openspec/changes/onion-branch-gate/` 产物（`proposal.md`、`design.md`、`specs/onion-branch-gate/spec.md`、`tasks.md`），补记本次已完成的实现，作为可追溯的变更记录。
