# Implement: onion-sdd 记忆能力优先依赖 Trellis

## 执行清单

1. `plugins/onion-sdd/commands/onsf-finish.md`
   - 第 9 步：从"若当前 change 绑定 Trellis task，提示继续执行 `/trellis:finish-work`"改为按 `design.md` 的分支 A/B/C 描述。
   - "Trellis 收尾分工"节：拆成绑定（分支 B，行为不变）和未绑定但 Trellis 可用（分支 C，新增自动记 journal + spec 积累判断）两种情况：
     - 写清 `add_session.py` 的调用参数规则（title/summary/commit 取值规则）。
     - 写清加载 `trellis-update-spec` 做判断的步骤、判断素材来源、"无需更新"也要显式输出的要求。
   - 新增输出格式要求（分支 C 的两行说明：journal + spec 积累）。
   - 边界小节补一句：分支 C 的两个动作都不是 task 创建/启动/归档，不需要额外用户确认。

2. `plugins/onion-sdd/commands/onsf-auto.md`
   - "Trellis 边界"节新增说明：记 journal（`add_session.py`）和 spec 积累判断（`trellis-update-spec`）都不算 task 生命周期操作，不在"需要创建/启动/归档 Trellis task"停止条件之列，`/onsf-finish` 门禁通过时按分支 C 自动执行。

3. `plugins/onion-sdd/README.md` / `plugins/onion-sdd/USAGE.md` / `plugins/onion-sdd/docs/feishu-wiki-onion-sdd-usage.md`
   - 找到"开发者 journal、会话摘要"对照行（当前写"仅绑定 Trellis task 才有 journal"隐含逻辑），改为区分：绑定 task → `/trellis:finish-work` 写；未绑定但 Trellis 可用 → `/onsf-finish` 自动写。
   - 新增"spec 经验积累"对照行：绑定 task → 走 Trellis workflow.md Phase 3.3；未绑定但 Trellis 可用 → `/onsf-finish` 分支 C 自动判断；Trellis 不可用 → 无此能力。
   - FAQ "只装 onion-sdd 不装 Trellis" 相关问答如果暗示"没 task 就没 journal/没 spec 积累"，同步措辞。

4. `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`
   - "Phase 1 Trellis Adapter"章节的"同步时机"表格里 finish 行，补充"未绑定 task 时 `/onsf-finish` 直接调用 `add_session.py` + `trellis-update-spec`"这一分支。

5. 全文搜索确认没有遗漏矛盾表述：
   ```bash
   grep -rn "绑定 Trellis task" plugins/onion-sdd/
   grep -rn "journal" plugins/onion-sdd/
   grep -rn "trellis-update-spec\|\.trellis/spec" plugins/onion-sdd/
   ```
   逐条检查每处"journal"/"spec"相关表述是否已经和新的分支 A/B/C 规则一致。

## 验证

- 纯文档改动，无可执行测试；验证方式为人工走查：
  - [ ] 通读修改后的 `onsf-finish.md`，模拟三种场景（无 Trellis / 有 Trellis 无 task / 有 Trellis 有 task）在脑内走一遍，确认动作和输出符合 `design.md` 的分支表，包括分支 C 下 journal 和 spec 积累判断两个动作都齐全。
  - [ ] `grep -rn "绑定 Trellis task" plugins/onion-sdd/` 逐条确认改完后语义一致，没有和新分支矛盾的残留表述。
  - [ ] `grep -rn "trellis-update-spec\|\.trellis/spec" plugins/onion-sdd/` 确认新增的调用点措辞一致，且没有和"只读不写"的旧表述冲突。
  - [ ] 如果本项目 `.cursor/skills/` 或 `.claude/skills/` 下存在 onion-sdd 源插件的同步副本，提醒用户是否需要同步（默认不主动改，除非用户要求）。

## Rollback

- 全部是 markdown 文档改动，`git revert` 对应 commit 即可回滚，无数据迁移风险。
