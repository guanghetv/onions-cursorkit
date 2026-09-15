# onion-sdd-clarification

`/onsf-plan` 脑暴禁重问，以及无 Trellis 时的脑暴/全流程兜底。

## ADDED Requirements

### Requirement: 脑暴工作记忆按运行模式选择文件

系统 MUST 在脑暴阶段维护 `## 已确认决策` 工作记忆：有 Trellis 时写入 task `prd.md`；无 Trellis 时写入 `openspec/changes/<change-id>/brainstorm.md`。脑暴期 MUST NOT 要求写入 `proposal.md`。

#### Scenario: 有 Trellis 答完先写 prd

- **WHEN** Trellis 可用且用户回答脑暴问题
- **THEN** Agent 先更新 `prd.md` → `## 已确认决策`
- **AND** 然后才可提出下一问

#### Scenario: 无 Trellis 使用 brainstorm.md

- **WHEN** Trellis 不可用或用户拒绝安装
- **THEN** Agent 确定 `change-id` 并确保存在 `brainstorm.md`
- **AND** 将已确认决策写入该文件的 `## 已确认决策`
- **AND** 不得因缺少 Trellis 而停止脑暴或空转重问

### Requirement: 已确认决策禁止语义重问

系统 MUST NOT 对工作记忆中已确认条目再次提问（含换措辞）。

#### Scenario: 提问前读取工作记忆

- **WHEN** Agent 准备提出下一脑暴问题
- **THEN** 先读当前模式的 `## 已确认决策`
- **AND** 语义等价则跳过并沿用结论

### Requirement: 无 Trellis 全流程可完成

系统 MUST 在无 Trellis 时仍能完成 Tier 2+：运行态写 `current.json`，正文写 OpenSpec，调研/check 在主会话降级，恢复走 `/onsf-continue` 读 `current.json` + `brainstorm.md`/OpenSpec。

#### Scenario: 拒绝安装 Trellis 后继续 plan

- **WHEN** 用户在 Tier 2+ 入口拒绝安装 Trellis
- **THEN** Agent 进入无 Trellis 兜底并继续需求接入
- **AND** 不把安装 Trellis 作为继续的前置条件

#### Scenario: 无 Trellis 恢复会话

- **WHEN** 用户执行 `/onsf-continue` 且无 Trellis task
- **THEN** Agent 用 `current.json` 与 OpenSpec/`brainstorm.md` 恢复
- **AND** 不得因缺少 task 拒绝继续

### Requirement: OpenSpec 落盘迁移已确认决策

进入 OpenSpec 落盘时，系统 MUST 从 `prd.md` 或 `brainstorm.md` 迁移 `## 已确认决策` 到 `proposal.md`。

#### Scenario: 从 brainstorm.md 迁移

- **WHEN** 无 Trellis 且脑暴已收敛并进入落盘
- **THEN** `proposal.md` 的已确认决策来自 `brainstorm.md`
- **AND** 无 Trellis 不阻塞落盘
