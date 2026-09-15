# fix-clarify-reask-ledger

## 背景

`/onsf-plan` 脑暴偶发答完再问导致卡死；同时不少用户不会启用 Trellis。Onion SDD 必须以 OpenSpec 为正文真相源，Trellis 仅为可选增强。

## 目标

- 脑暴：先写工作记忆再问；已决禁重问；不写 `proposal.md` 直到收敛。
- 有 Trellis → `prd.md`；无 Trellis → `brainstorm.md`。
- 无 Trellis 仍可跑完 Tier 2+（`current.json` + OpenSpec + 主会话降级调研/check）。

## 变更

- `full-change`：增加「无 Trellis 全流程兜底」；需求接入双模式。
- `onsf-plan` / `onsf-continue` / `openspec-change`：对齐兜底与迁移来源。
- `trellis-brainstorm`：禁重问 + 先写 `prd.md`（有 Trellis 时）。

## 影响范围

- onion-sdd skills/commands；brainstorm 副本

## 不做范围

- AskQuestion 产品、业务代码、强制安装 Trellis

## 验证计划

- 文档对照双路径表
- 场景：有/无 Trellis 脑暴不重问；无 Trellis continue 可恢复

## 已确认决策

| 决策点 | 结论 | 来源 |
|--------|------|------|
| 脑暴记忆 | 有 Trellis→prd；无→brainstorm.md | 用户 |
| 阶段 | 收敛前不写 proposal | 用户 |
| 全流程 | 无 Trellis 不阻塞 | 用户 |
| 兜底落点 | openspec/changes/\<id\>/brainstorm.md | 推荐方案 A |
