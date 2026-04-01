## 1. 规范与主文档

- [x] 1.1 在 `SKILL.md` 中明确默认基线为 `master`、禁止自动 `main`、门禁与显式例外
- [x] 1.2 更新快速执行清单与步骤 8 前置条件，与门禁一致
- [x] 1.3 在「错误处理」中增加 `git checkout master` 失败时的处理说明

## 2. 参考文档

- [x] 2.1 更新 `references/DETAILED_STEPS.md` 步骤 2（基线、`pull`、门禁、无 master 时停止）
- [x] 2.2 在 `references/TROUBLESHOOTING.md` 增加「无 master 分支 / 需显式基线」的表项与独立问题说明
- [x] 2.3 在 `SKILL.md` 与 `references/DETAILED_STEPS.md` 互指：门禁 /「创建并推送分支」对应关系（主文档步骤 8 ≡ 参考文档步骤 7）

## 3. OpenSpec 与校验

- [x] 3.1 维护 `proposal.md`、`specs/create-feature-branch/spec.md` 与 `design.md`（本变更）
- [x] 3.2 执行 `openspec validate create-feature-branch-base-gate` 并通过

## 4. 可选后续

- [ ] 4.1 同步 `.claude/skills/create-feature-branch/SKILL.md`（若个人环境依赖该副本）
- [x] 4.2 归档本 change 后，按需将能力合并入 `openspec/specs/`（`openspec-sync-specs` 或团队归档流程）— 归档时已新增主 spec：`openspec/specs/create-feature-branch/spec.md`
