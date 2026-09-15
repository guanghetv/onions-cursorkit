# `/onsf-plan` 脑暴禁重问 + 无 Trellis 兜底

## Goal

1. 修复 `/onsf-plan` 脑暴答完再问卡死：工作记忆先写后问、已决禁重问。  
2. 用户不做 Trellis 能力增强时，脑暴与完整流程仍可跑通（OpenSpec + `current.json` + `brainstorm.md`）。

## Background

正确流程：`/onsf-plan` → 简单脑暴 → 收敛后再 OpenSpec 落盘。  
卡死主因是脑暴失忆/重问，不是缺 `proposal.md`。  
Trellis 是增强项，不是硬依赖；无 Trellis 时必须有对等工作记忆与全流程降级路径。

## Requirements

1. 有 Trellis：脑暴工作记忆 = `prd.md` → `## 已确认决策`。  
2. 无 Trellis：先定 `change-id`，工作记忆 = `openspec/changes/<id>/brainstorm.md` → `## 已确认决策`；仍不写 `proposal.md` 直到收敛。  
3. 两种模式共用：先写记忆再问下一题；已决禁重问。  
4. 收敛后 `openspec-change` 从 `prd.md` 或 `brainstorm.md` 迁移已确认决策到 `proposal.md`。  
5. `/onsf-continue`：未落盘读对应工作记忆；已落盘读 `proposal.md`；无 Trellis 不得因缺 task 拒绝恢复。  
6. 无 Trellis 全流程：运行态只写 `current.json`；调研/check 主会话降级；正文真相源仍是 OpenSpec。  
7. Tier 3 无 Trellis：用 OpenSpec 目录 + `current.json` 表达多阶段，不强制 task 树。

## Out of Scope

- AskQuestion 产品改动、`onion_state.py` 大改、业务代码

## Acceptance Criteria

- [x] 有/无 Trellis 双路径工作记忆写清
- [x] 脑暴不强制写 `proposal.md`
- [x] 先写再问 + 已决禁重问
- [x] continue / plan 含无 Trellis 兜底
- [x] OpenSpec 模板注明决策表来源含 `brainstorm.md`

## Constraints

- Tier 1；Trellis 可选增强

## Notes

- 用户要求：收回脑暴写 proposal；补无 Trellis 简单脑暴与全流程兜底。
