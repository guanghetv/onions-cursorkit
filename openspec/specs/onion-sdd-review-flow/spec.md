# onion-sdd-review-flow Specification

## Purpose
TBD - created by archiving change move-aicr-to-check-phase. Update Purpose after archive.
## Requirements
### Requirement: check 阶段复合审查顺序

系统 MUST 在实现完成后按固定顺序执行四步：`trellis-check`（含其自身的问题修复）→ 暂存本次 change 范围内的改动 → `/cr` 审查暂存区 → 发现问题则修复、回跑受影响的门禁、重新暂存、复审并循环至通过。

顺序 MUST NOT 调换。`trellis-check` 会修改代码，若先暂存则其修复落在工作区而不在暂存区，导致审查对象与最终产物脱节。规则文档 MUST 同时写出顺序与该理由。

四步由 Agent 自动串联执行，MUST NOT 要求用户输入命令触发。

第 4 步的通过判据 MUST 为：CR 报告中属于本次 change 的 🔴 严重问题清零。🟠 改进建议 MUST 由 Agent 逐条判断，修或不修都 MUST 在 check 输出中说明理由，且 MUST NOT 作为循环条件。

#### Scenario: 实现完成后自动执行完整四步

- **WHEN** Agent 完成当前 change 的实现，进入 check 阶段
- **THEN** 先派发 `trellis-check` 完成 lint、typecheck、测试与 `.trellis/spec/` 对齐，并修复其发现的问题
- **AND** 待 `trellis-check` 完成后再暂存本次 change 范围内的改动
- **AND** 调用 `/cr` 审查暂存区
- **AND** 全过程不要求用户输入任何命令

#### Scenario: CR 提出逻辑性修复后回跑门禁

- **WHEN** `/cr` 提出触及逻辑的修复建议（如抽取共享常量、补充边界判断）
- **AND** 修复完成
- **THEN** 系统重跑受该修复影响的 lint / typecheck / 测试
- **AND** 重新暂存后再次 `/cr` 复审
- **AND** 不要求全量重跑 `trellis-check`

#### Scenario: CR 提出纯格式修复不回跑门禁

- **WHEN** `/cr` 提出的修复仅涉及命名或格式，不改变逻辑
- **THEN** 系统直接重新暂存并复审，不回跑 lint / typecheck / 测试

#### Scenario: CR 只报改进建议

- **WHEN** `/cr` 报告中属于本次 change 的问题只有 🟠 改进建议，无 🔴 严重问题
- **THEN** 系统判定第 4 步通过，不因 🟠 未清零而继续循环
- **AND** 在 check 输出中逐条说明每条 🟠 的处理决定与理由

#### Scenario: 暂存后暂存区为空

- **WHEN** 执行暂存后暂存区中没有本次 change 的任何改动
- **THEN** 系统输出提示并跳过 `/cr`，不报错、不阻塞 check 阶段

### Requirement: 暂存范围限于本次 change 且只增不减

系统 MUST 只暂存属于本次 change 的改动，MUST NOT 使用 `git add -A`。归属无法判断的文件 MUST 列出清单请用户确认，MUST NOT 默认纳入。

暂存区已存在本次 change 之外的内容时，系统 MUST 提示用户，但 MUST NOT 执行 `git reset` 或以任何其它方式移除用户已暂存的内容。

#### Scenario: 工作区含无关本地改动

- **WHEN** 工作区同时存在本次 change 的改动和与之无关的本地改动（如调试代码、个人配置）
- **THEN** 系统只暂存本次 change 的改动
- **AND** 无关改动保留在工作区未暂存状态

#### Scenario: 文件归属存疑

- **WHEN** 某个改动文件无法判断是否属于本次 change
- **THEN** 系统列出存疑文件清单请用户确认
- **AND** 用户确认前不将其纳入暂存

#### Scenario: 用户已手动暂存其它内容

- **WHEN** 进入 check 阶段时暂存区已含用户手动暂存的、本次 change 之外的内容
- **THEN** 系统提示暂存区含本次 change 之外的内容
- **AND** 不执行 `git reset`，保留用户已暂存的内容
- **AND** `/cr` 审出该部分内容的问题时只列出并标注归属，不计入 check 第 4 步的通过判据

### Requirement: check 阶段授权边界

系统 MUST 在 check 阶段允许自动执行 `git add`（限本次 change 范围）与 `/cr`，同时 MUST NOT 自动执行 `git commit`、push 或创建 PR/MR。

规则文档 MUST 将暂存授权与提交授权分开表述，避免被理解为 check 阶段可以自动提交。

#### Scenario: check 阶段自动暂存并审查

- **WHEN** Agent 在 check 阶段需要暂存本次 change 改动并调用 `/cr`
- **THEN** 无需用户授权即可执行，因为 `git add` 可通过 `git reset` 撤销、`/cr` 为只读

#### Scenario: check 阶段不得自动提交

- **WHEN** check 阶段的 `/cr` 审查通过
- **THEN** 系统 MUST NOT 自动执行 `git commit`，须等待用户明确授权提交

#### Scenario: `/onsf-auto` 下的边界

- **WHEN** `/onsf-auto` 无交互模式运行到 check 阶段
- **THEN** 暂存与 `/cr` 可自动执行，不停止
- **AND** 遇到 `git commit`、push、创建 PR/MR 时仍按既有高风险清单停止

### Requirement: 提交门禁条件化复审

用户明确授权提交后，系统 MUST 判断暂存区自 CR 通过后是否发生变化：未变化则直接 commit 不重复审查；发生任何变化（**含新增暂存文件**）则 MUST 重新 `/cr` 后再 commit；无法判定时 MUST 按重审处理。

判定 MUST 由 Agent 依据会话内上下文完成，MUST NOT 引入审查指纹机制，MUST NOT 为此修改 `onion_state.py`。

#### Scenario: CR 通过后未改动直接提交

- **WHEN** check 阶段 `/cr` 审查通过，此后暂存区内容未发生任何变化
- **AND** 用户明确授权提交
- **THEN** 系统直接执行 `git commit`，不重复调用 `/cr`

#### Scenario: CR 通过后新增暂存文件必须重审

- **WHEN** check 阶段 `/cr` 审查通过后，用户或 Agent 又暂存了新的文件
- **AND** 用户明确授权提交
- **THEN** 系统重新调用 `/cr` 审查当前暂存区后才执行 `git commit`

#### Scenario: 跨会话无法判定时重审

- **WHEN** 用户在新会话中授权提交，Agent 无法确认暂存区自上次 CR 通过后是否变化
- **THEN** 系统按重审处理，重新调用 `/cr`

### Requirement: 审查职责切分

系统 MUST 将可执行门禁（lint、typecheck、测试）、`.trellis/spec/` 对齐与 spec 回写归属 `trellis-check`；将团队前后端规范、安全风险检测、影响范围分析与 `openspec/specs/` 业务需求对齐归属 `/cr`。

派发 `trellis-check` 时 MAY 声明人工 review 维度由后续 `/cr` 覆盖，但系统 MUST 将该切分视为弱约束——`trellis-check` 仍会按自身 `SKILL.md` 执行，重叠结论在合并时去重即可，MUST NOT 为强制切分而修改 Trellis 源码。

#### Scenario: 两侧结论合并去重

- **WHEN** `trellis-check` 与 `/cr` 对同一问题都给出了结论
- **THEN** 系统在合并报告时去重，只保留一条
- **AND** 不因重复而修改 `trellis-check` 的 `SKILL.md`

### Requirement: AICR 不可用时的降级

系统 MUST 在 AICR 能力不可用时降级并继续，MUST NOT 阻塞 check 阶段。`/cr` slash command 不可用时读取并按 `aicr-local` 的 `SKILL.md` 审查暂存区；`aicr-local` 未安装时由 Agent 对暂存区自审并注明团队规范维度未覆盖。

#### Scenario: slash command 不可用

- **WHEN** check 阶段无法执行 `/cr` slash command，但 `aicr-local` 已安装
- **THEN** 系统读取 `aicr-local` 的 `SKILL.md` 并按其流程审查暂存区

#### Scenario: `aicr-local` 未安装

- **WHEN** 环境中不存在 `aicr-local`
- **THEN** 系统由 Agent 对暂存区自审，并在输出中注明团队规范维度未覆盖
- **AND** check 阶段继续，不阻塞

