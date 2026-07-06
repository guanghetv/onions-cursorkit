# 改造 onsf-finish 实现自动归档

## Goal

将 onion-sdd 的 `/onsf-finish` 命令从「仅检查并提示用户手动归档」升级为「检查通过后自动归档 OpenSpec change」，使其与 Trellis `/trellis:finish-work` 的自动归档体验保持一致，减少用户手动执行 `openspec archive` 的遗漏。

## Requirements

1. **自动归档门禁**
   - `/onsf-finish` 必须先完成现有检查：产物完整性、任务状态、验证证据、带债项、Tier 2+ E2E/等价验收。
   - 只有门禁全部通过，或用户明确同意带债归档时，才执行自动归档。
   - 未通过门禁时，只输出检查结论和待补齐项，不自动归档。

2. **OpenSpec 归档执行**
   - 通过门禁后，Agent 调用 `openspec archive <change-id>` 自动归档当前活跃 change。
   - 如果 `openspec` CLI 不可用，Agent 使用等效手工操作：把 `openspec/changes/<change-id>/` 移动到 `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/`，并生成或保留最小归档元数据。
   - 归档成功后，更新 `.onion-sdd/current.json`：`active_change_id` 置为 `null`，`phase` 置为 `idle`，`last_action` 记录归档时间。

3. **与 Trellis 的衔接**
   - 自动归档 OpenSpec 后，若当前 change 绑定 Trellis task，提示用户继续执行 `/trellis:finish-work` 完成 Trellis task 归档。
   - 不自动执行 Trellis task 归档，不替代 `/trellis:finish-work`。

4. **文档与规则同步**
   - 同步修改所有声明「不自动执行 `openspec archive`」的文档和规则，改为「检查通过后自动归档」。
   - 涉及的文件包括：命令说明、skills、rules、README、DESIGN-SUPPLEMENT 和使用文档。

5. **降级与异常**
   - 归档失败时（CLI 返回非零、目录移动失败、change 不存在），输出错误原因并保留当前 `.onion-sdd/current.json` 状态，不静默失败。
   - 如果 OpenSpec 未安装且手工移动也无法完成，停止并提示用户手动处理。

## Acceptance Criteria

- [ ] `/onsf-finish.md` 命令文档描述自动归档流程与门禁条件。
- [ ] `rules/onion-sdd.mdc` 中移除「不自动执行 `openspec archive`」的约束，改为自动归档条件。
- [ ] `skills/mini-change/SKILL.md`、`skills/verify-change/SKILL.md`、`skills/auto-flow/SKILL.md`、`skills/full-change/SKILL.md` 中所有相关归档描述同步更新。
- [ ] `commands/onsf-auto.md`、`onsf-fix.md`、`onsf-tweak.md` 中不再声明「不自动归档」或已更新为自动归档行为。
- [ ] `README.md`、`DESIGN-SUPPLEMENT.md`、`docs/feishu-wiki-onion-sdd-usage.md` 中流程描述与归档说明一致。
- [ ] 自动归档后 `.onion-sdd/current.json` 正确切回 `idle` 状态。
- [ ] 自动归档失败时输出明确错误，不破坏现有产物状态。
- [ ] 未通过门禁时不会执行自动归档。

## Non-goals

- 不改变 Trellis task 的归档逻辑；仍然通过 `/trellis:finish-work` 完成。
- 不自动执行 `git commit`、push、创建 PR/MR。
- 不改造 OpenSpec CLI 本身，只使用现有命令或等效手工操作。
- 不自动归档未绑定 `/onsf-finish` 的 change（仍然需要用户显式触发 finish）。

## Constraints

- 必须保持 OpenSpec 为变更正文唯一真相源。
- 自动归档是不可逆操作，门禁条件必须严格对齐现有 `/onsf-finish` 的检查项。
- 修改必须保持文档语言规范（中文正文，专有名词保留英文）。
