# 改造 onsf-finish 实现自动归档 — 执行计划

## 执行顺序

### 步骤 1：核心命令文档改造

**目标文件**：`plugins/onion-sdd/commands/onsf-finish.md`

- 重写「执行顺序」：在输出可归档结论后增加「执行自动归档」步骤。
- 重写「完成标准」：把「如需归档，只提示用户执行」改为「门禁通过后自动执行 `openspec archive <change-id>`，CLI 不可用时手工移动目录」。
- 增加「自动归档流程」小节，描述门禁、CLI 调用、降级路径、失败处理。
- 增加「状态同步」小节，说明归档成功后 `current.json` 切为 `idle`。
- 保留「Trellis 收尾分工」：OpenSpec 归档后提示 `/trellis:finish-work`。
- 保留「带债归档规则」和约束，但更新约束表述。

**验证**：
- `plugins/onion-sdd/commands/onsf-finish.md` 中不再出现「不自动执行 `openspec archive`」。
- 文档包含自动归档的触发条件、降级路径、失败处理。

### 步骤 2：规则文档更新

**目标文件**：`plugins/onion-sdd/rules/onion-sdd.mdc`

- 找到「收束纪律」中「不自动执行 `openspec archive`」这一条，改为：
  > 门禁通过或用户明确同意带债归档时，自动执行 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档；失败时停止并报告。
- 同步检查 `/onsf-auto` 的停止条件列表，移除或更新 `openspec archive` 相关条目（说明在门禁通过后可自动执行，而不是无条件停止）。

**验证**：
- `rules/onion-sdd.mdc` 中不再出现「不自动执行 `openspec archive`」。
- `/onsf-auto` 停止条件不再把 `openspec archive` 列为必须停止项。

### 步骤 3：Skills 文档更新

**目标文件**：
- `plugins/onion-sdd/skills/mini-change/SKILL.md`
- `plugins/onion-sdd/skills/verify-change/SKILL.md`
- `plugins/onion-sdd/skills/auto-flow/SKILL.md`
- `plugins/onion-sdd/skills/full-change/SKILL.md`
- `plugins/onion-sdd/skills/trellis-adapter/SKILL.md`

**改动内容**：
- `mini-change`：把「归档提示」改为「完成并定向验证通过后，调用 `/onsf-finish` 自动归档」。
- `verify-change`：归档门禁中明确 `/onsf-finish` 自动执行归档；`e2e-report.md` 的验收结论作为触发条件。
- `auto-flow`：
  - 把 `openspec archive` 从「必须停止」列表中移除。
  - 在「收束边界」中说明 `/onsf-auto` 可以自动执行 `openspec archive`（但 git commit、push、PR/MR 仍然不自动）。
  - 在「验证收束」中说明 `/onsf-auto` 到达 finish 阶段时自动归档。
- `full-change`：完成标准中「`/onsf-finish` 能判断是否可归档」更新为「`/onsf-finish` 自动归档」。
- `trellis-adapter`：finish 时同步 `current.json` 到 `idle`，并记录 last_action。

**验证**：
- 使用 `rg -n "不自动执行 openspec archive|只提示.*归档|openspec archive" plugins/onion-sdd/skills` 检查所有相关条目已更新。

### 步骤 4：其他命令文档更新

**目标文件**：
- `plugins/onion-sdd/commands/onsf-auto.md`
- `plugins/onion-sdd/commands/onsf-fix.md`
- `plugins/onion-sdd/commands/onsf-tweak.md`

**改动内容**：
- `onsf-auto.md`：
  - 在「停止条件」中移除 `openspec archive` 或改为「门禁通过后可自动执行」。
  - 在「收束边界」中说明 `openspec archive` 可以自动执行。
- `onsf-fix.md`、`onsf-tweak.md`：移除或更新「不自动执行 `openspec archive`」的承诺。

**验证**：
- 三个命令文档中关于自动归档的描述与 `onsf-finish.md` 一致。

### 步骤 5：README / DESIGN-SUPPLEMENT / 使用文档更新

**目标文件**：
- `plugins/onion-sdd/README.md`
- `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`
- `plugins/onion-sdd/docs/feishu-wiki-onion-sdd-usage.md`

**改动内容**：
- `README.md`：
  - 「自动化边界」中移除「不自动 `openspec archive`」，改为「门禁通过后可自动归档 OpenSpec」。
  - 「当前不做」中移除「不自动执行 `openspec archive`」。
- `DESIGN-SUPPLEMENT.md`：同步更新流程描述和自动边界。
- `feishu-wiki-onion-sdd-usage.md`：
  - 移除「OpenSpec 未安装时，归档仍需你在终端执行」的说法，改为「CLI 不可用时 Agent 使用手工移动目录等效归档」。
  - 更新「收尾与归档」章节，说明 `/onsf-finish` 自动归档。
  - 更新对比表格中「OpenSpec 归档」一行。

**验证**：
- 文档中不再出现「归档仍需你在终端执行」或「不自动执行 `openspec archive`」。
- 使用文档的示例流程与改造后行为一致。

### 步骤 6：可选的外部 spec 技能检查

**目标文件**：
- `plugins/onion-sdd/skills/external-spec/SKILL.md`
- `plugins/onion-sdd/skills/pull-yapi/SKILL.md`

**改动内容**：
- 保留「冲突未裁决前不要进入归档」的约束。
- 如果文档中提到归档由用户执行，更新为「由 `/onsf-finish` 自动执行」。

**验证**：
- 没有冲突未裁决却自动归档的 loophole。

### 步骤 7：质量检查

- 运行 `rg -n "不自动执行 openspec archive|只提示.*归档|归档仍需" plugins/onion-sdd` 确保没有遗漏。
- 运行 `rg -n "openspec archive" plugins/onion-sdd` 检查所有出现位置的语义一致性。
- 校验文档语言规范（中文正文，代码/命令保留英文）。
- 检查是否有互相矛盾的描述。

## 回滚点

- 如果在任何步骤发现文档互相矛盾，暂停并回滚该文件到改动前，重新统一表述。
- 如果用户中途改变主意（恢复手动归档），保留所有改动为一次 revertable commit。

## 完成验证

1. 所有目标文件中关于自动归档的表述一致。
2. 自动归档的门禁条件、CLI 调用、降级路径、失败处理、状态同步都已在文档中定义。
3. 没有遗留「不自动执行 `openspec archive`」或「只提示归档」的旧描述。
4. 文档通过中文语言规范检查。
