# onion-sdd-runtime

Onion SDD 运行态与 finish 预检能力。

## ADDED Requirements

### Requirement: 运行态读写优先级

系统 MUST 通过 `onion_state.py` 按以下优先级读写运行态：读为 Trellis `meta.onion` → `current.json` → idle；写为已绑定 Trellis task 时主写 `meta.onion` 并镜像 `current.json`，否则只写 `current.json`。

#### Scenario: 有绑定 Trellis task 时写入

- **WHEN** Agent 调用 `onion_state.py set` 且已绑定有效 Trellis task
- **THEN** 主写 `task.json.meta.onion`，并镜像更新 `.onion-sdd/current.json`，输出 `primary_write=trellis`

#### Scenario: 无 Trellis 时写入

- **WHEN** Agent 调用 `onion_state.py set` 且未绑定 Trellis task
- **THEN** 只写 `.onion-sdd/current.json`，输出 `primary_write=current`

#### Scenario: meta 写失败降级

- **WHEN** 绑定的 task 目录不存在或 `task.json` 不可写
- **THEN** 发出警告并降级为只写 `current.json`，不阻塞流程

### Requirement: Finish 归档前置预检

`/onsf-finish` MUST 在 archive 前运行 `finish_check.py`；hard fail 时 MUST NOT 执行 `openspec archive` 或手工移动归档目录。

#### Scenario: Tier 2+ 缺验收结论

- **WHEN** tier 为 2 或以上且缺少 `e2e-report.md` 或其中无 `## 验收结论`
- **THEN** finish_check hard fail，禁止归档

#### Scenario: Tier 0++ 逾期无带债项

- **WHEN** `tier0pp_openspec_pending` 为 true 且当前时间已过 `tier0pp_deadline`，且 `proposal.md` 无 `## 带债项`
- **THEN** finish_check hard fail

#### Scenario: 逾期但已落盘带债项

- **WHEN** 同上逾期条件，但 `proposal.md` 含 `## 带债项`
- **THEN** 该条 hard 解除；仍须用户同意带债归档后方可 archive

#### Scenario: openspec validate 不可用

- **WHEN** `openspec` CLI 不可用或 validate 失败
- **THEN** 记为 soft，不单独导致 finish_check 失败
