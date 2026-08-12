# E2E Report: move-aicr-to-check-phase

## 验证范围

- 依据: OpenSpec `specs/onion-sdd-review-flow/spec.md` + `proposal.md` 验收项 + `tasks.md` dogfooding；用户 2026-08-12 确认人工验证通过
- 场景数: 6（四步顺序、降级路径、暂存边界、提交门禁条件化、职责切分、口径残留检索）
- 执行时间: 2026-08-12 18:03

## 验证清单结论

- TDD / 静态检查: 通过（规则/文档类交付，无自动化测试；以 `rg` 检索与路径走读替代）
- 文档对照: 一致
- 浏览器验证: 未执行（无 UI）

## 与 QA spec / YApi 的显著差异

| 来源 | 预期 | 当前实现或其它 spec | 结论 |
|------|------|----------------------|------|
| 无 | | | 无 QA / YApi 依赖 |

## 通过

- `tasks.md` 全部完成；§4.3 dogfooding：`trellis-check` → 逐文件暂存 → `/cr` 不可用时按 `aicr-local` Skill 降级审查 → 修复复审通过。
- 验收检索：`git diff --stat -- plugins/common .claude/skills .trellis/scripts` 为空；`plugins/onion-sdd/` 无「AICR 仅在提交前触发」「check 阶段不暂存」残留口径（CHANGELOG 历史条目除外）。
- 用户于 2026-08-12 确认人工验证通过。

## 失败

- 无。

## 阻塞项

- 无。

## 验收结论

- 结论: 通过
- 阻塞项: 无
- 归档建议: 可归档
