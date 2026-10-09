# Tasks

- [x] 确认 Tier 1 范围与升级红线
- [x] 写入 proposal/spec/tasks
- [x] 改为基线第一父历史 + 拿掉 merge 后比树；暂存区用 commit-tree
- [x] 在 `aicr-local/SKILL.md` 步骤 1 之后写入该检查，并让步骤 10 不得忽略已确认的 🔴
- [x] 检查提升到两种模式都会进入的小节；撤销改为提交说明与 patch-id，失败时不阻断
- [x] MR 与空暂存区在确认混入且无撤销提交时 🔴；patch-id 只豁免暂存区正在撤销
- [x] 祖先检查只留在 MR 模式；暂存区改为最近 5 条 subject 是否 merge 基线
- [ ] 对照 spec：最近 5 条 merge、5 条内已 revert、早于 5 条、干净分支、合进基线、MR 未撤销、MR 已 revert、从基线切出、人在基线上、MR 不在源分支、引用缺失
- [ ] 更新任务状态与验证记录
