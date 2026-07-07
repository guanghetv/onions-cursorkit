# Implement: onion-sdd 检测缺失 Trellis 时交互式安装初始化

> 执行约束
> - 每个任务先明确验证点，再做最小实现。
> - 只改文档/协议文本，不涉及代码测试；验证方式以人工审阅 + 关键字核对为主。
> - 严禁修改 `.trellis/scripts/**`、`.trellis/.runtime/**`、Trellis CLI 源码。

## 1. full-change 新增「Trellis 使用检查」步骤

- [x] 1.1 在 `plugins/onion-sdd/skills/full-change/SKILL.md` 的「需求接入」章节之前插入新小节，落实 `design.md` 中「触发与检测」的 4 步流程原文（检测 → 询问 → 同意后安装/初始化 + gitignore → 拒绝或失败后降级）。
      验证点：`grep -n "Trellis 使用检查" plugins/onion-sdd/skills/full-change/SKILL.md` 命中；人工核对步骤 1-4 均覆盖，且明确"不阻塞"「拒绝/失败继续走现状降级路径」。

## 2. gitignore 精确追加规则落地为可执行文案

- [x] 2.1 在新小节中写清 `design.md`「gitignore 精确更新范围」表格（按平台列出条目）与追加规则（去重、只追加本次选中平台、末尾追加+注释、不动 `.agents/skills/`、`commands` 只忽略 `trellis-*` 相关子路径）。
      验证点：人工核对表格条目与 `design.md` 一致；确认没有出现"整目录一刀切"的写法。

## 3. onsf-auto 边界说明

- [x] 3.1 在 `plugins/onion-sdd/commands/onsf-auto.md`「Trellis 边界」小节追加 `design.md` 中「auto 边界」的说明句，明确该询问不适用于 `/onsf-auto`。
      验证点：`grep -n "无交互场景不触发该询问" plugins/onion-sdd/commands/onsf-auto.md` 命中。

## 4. 文档同步

- [x] 4.1 `plugins/onion-sdd/USAGE.md` §8.2 后补充"Tier 2+/3 首次触发且未装 Trellis 时会询问安装"的说明段落，及 gitignore 精确追加行为的一句话概述。
- [x] 4.2 `plugins/onion-sdd/docs/feishu-wiki-onion-sdd-usage.md` 同步相同内容（保持两份文档一致，参考上个任务 `07-07-onion-trellis-memory` 的同步方式）。
- [x] 4.3 检查 `plugins/onion-sdd/README.md` 是否有对应的能力对照表/说明位置，若有则同步补充一行；若无对应位置可跳过并在 check 阶段说明理由。
- [x] 4.4 检查 `plugins/onion-sdd/DESIGN-SUPPLEMENT.md` 是否描述了 Trellis 可用性检测逻辑，若有则补充"检测到不可用时交互式安装"的分支说明。
      验证点：对四个文件运行 `grep -n "安装并初始化\|询问是否安装" <file>`，确认新增内容互相一致、没有互相矛盾的措辞。

## 5. 跨文档一致性检查

- [x] 5.1 汇总核对：`full-change/SKILL.md`、`onsf-auto.md`、`USAGE.md`、飞书文档、（如适用）`README.md`、`DESIGN-SUPPLEMENT.md` 六处关于本次新行为的描述用词是否一致（安装询问的触发条件、auto 模式不触发、gitignore 精确追加），不要求逐字相同但语义不能冲突。

## Rollback

- 每个文件的改动都是新增段落/小节，未删除既有内容；如需回滚，直接 `git revert` 对应 commit。
