## ADDED Requirements

### Requirement: 同步 cursor 标准目录
安装脚本 MUST 将安装源中 `.cursor/commands`、`.cursor/rules`、`.cursor/skills` 同步到目标项目的 `.cursor` 标准目录。

#### Scenario: 全量同步
- **WHEN** 用户未指定 `--only`
- **THEN** 系统 MUST 同步 `commands`、`rules`、`skills` 三个目录到目标项目

### Requirement: 支持指定同步范围
安装脚本 MUST 支持通过 `--only` 限定同步范围，范围仅允许 `commands`、`rules`、`skills`。

#### Scenario: 仅同步规则
- **WHEN** 用户执行 `install/cursor --only rules`
- **THEN** 系统 MUST 只同步 `.cursor/rules`，且不写入 `commands` 与 `skills`

### Requirement: 冲突处理策略
当目标文件已存在且内容不同，系统 MUST 按用户参数选择行为：`--force` 覆盖、`--backup` 备份后写入，否则终止并提示冲突。

#### Scenario: 未指定策略遇到冲突
- **WHEN** 目标文件存在且内容不同，且未指定 `--force` 或 `--backup`
- **THEN** 系统 MUST 终止并输出冲突提示

### Requirement: dry-run 不写入
当启用 `--dry-run` 时，系统 MUST 只输出将要执行的操作，不得写入任何文件或目录。

#### Scenario: dry-run 执行
- **WHEN** 用户执行 `install/cursor --dry-run`
- **THEN** 系统 MUST 不写入任何文件，并输出将要同步的路径信息
