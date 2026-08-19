# Tasks: move-aicr-to-check-phase

> 执行约束
> - 每个任务必须有验证点。
> - 本次交付物全为规则与文档，无自动化测试可写；验证点为静态检索与路径走读，不得虚构已跑测试。
> - 不得修改 `plugins/common/**`、`.claude/skills/**`、`.trellis/scripts/**`。

## 1. 规则层：审查章节

- [x] 1.1 在 `plugins/onion-sdd/rules/onion-sdd.mdc` 定义 check 阶段四步顺序，并写明顺序不可调换的理由（`trellis-check` 会改代码，先暂存会导致审查对象与产物脱节）
      验证点: `rg -n "trellis-check" plugins/onion-sdd/rules/onion-sdd.mdc` 能读到顺序与理由两部分，缺任一视为未完成
- [x] 1.2 定义修复循环的回跑规则：触及逻辑的修复须回跑受影响门禁，纯格式修复直接重新暂存，不要求全量重跑 `trellis-check`
      验证点: 走读规则文本，确认未出现「每次重跑 trellis-check」类表述
- [x] 1.3 定义暂存范围：限本次 change、禁止 `git add -A`、归属存疑需用户确认、禁止 `git reset`
      验证点: 四项在规则中均可检索到；`rg -n "git add -A|git reset" plugins/onion-sdd/rules/onion-sdd.mdc` 命中的均为禁止性表述
- [x] 1.4 定义授权边界：check 阶段允许自动 `git add` 与 `/cr`，仍禁止自动 `commit`/push/PR，两者分开表述
      验证点: 走读确认暂存授权与提交授权是两条独立表述，不在同一句中混写
- [x] 1.5 定义提交门禁条件化：未变化直接 commit、有变化（含新增暂存文件）重审、无法判定重审；明示不引入指纹机制
      验证点: 判定条件中可检索到「新增暂存文件」；可检索到不改 `onion_state.py` 的明示
- [x] 1.6 更新职责切分与降级表述，覆盖 `trellis-check` 边界、弱约束说明、`/cr` 不可用与 `aicr-local` 未安装两条降级
      验证点: 走读四条路径（正常、`/cr` 不可用、未安装、暂存后为空）均不阻塞

## 2. 技能与命令层口径

- [x] 2.1 更新 `plugins/onion-sdd/skills/full-change/SKILL.md`「质量审查」章节为四步复合阶段，指向规则而非复述细节
      验证点: 章节内无与规则冲突的旧口径；提交前审查段落已改写
- [x] 2.2 更新 `plugins/onion-sdd/skills/auto-flow/SKILL.md`：`/onsf-auto` 下暂存与 `/cr` 可自动执行，commit 仍停止；改写现行「不暂存文件，也不调用 `aicr-local` 或 `/cr`」表述
      验证点: `rg -n "不暂存|不调用" plugins/onion-sdd/skills/auto-flow/SKILL.md` 无与新规则冲突的残留
- [x] 2.3 理清 `auto-flow` 的 `diff-review` 与 check 阶段 CR 的关系，避免被读成重复动作
      验证点: 走读两段，能明确区分各自职责与触发时机
- [x] 2.4 更新 `plugins/onion-sdd/commands/onsf-continue.md` 的 check 行与恢复优先级
      验证点: check 行描述与规则一致

## 3. 用户文档与发版

- [x] 3.1 同步 `README.md`、`USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md` 的 Commit review 段、扩展能力表与收尾流程图
      验证点: 三处口径一致；扩展能力表中 `aicr-local` 使用时机已从「用户授权提交后」改为覆盖 check 阶段
- [x] 3.2 `plugins/onion-sdd/.cursor-plugin/plugin.json` 版本 0.1.4 → 0.1.5，追加 CHANGELOG 条目
      验证点: `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 通过；CHANGELOG 含新版本段落
- [x] 3.3 按需同步 `.cursor-plugin/marketplace.json` 的 onion-sdd description
      验证点: `node scripts/validate-template.mjs` 通过

## 4. 全局一致性验收

- [x] 4.1 全量检索确认无旧口径残留
      验证点: `rg -n -i "aicr|/cr" plugins/onion-sdd/ .cursor-plugin/` 无「仅在提交前触发」「check 阶段不暂存」类表述（CHANGELOG 0.1.4 及更早的历史条目按惯例保留不改写）
- [x] 4.2 确认范围外零改动
      验证点: `git diff --stat -- plugins/common .claude/skills .trellis/scripts` 输出为空
- [x] 4.3 用新流程自身走一遍收尾（dogfooding），验证规则可执行
      验证点: 按四步顺序完成本 change 的 check，记录实际执行情况
      实际执行: ① 派发 `trellis-check`（声明聚焦可执行门禁与 `.trellis/spec/` 对齐），修复 3 处口径不一致；② 逐文件 `git add` 15 项（未用 `git add -A`），暂存前暂存区为空、无归属存疑文件；③ `/cr` slash command 不可用，按降级路径读取 `aicr-local` 的 `SKILL.md` 审查暂存区，产出 3 条 🟠；④ 修复后因均为文档口径调整未回跑门禁，直接重新暂存复审通过。
      规则缺口: CR 发现规则未说明「暂存区含本次 change 之外内容时，CR 审出的问题如何处理」，已补入规则与 spec。
