## ADDED Requirements

### Requirement: Sync cursor config directories
`install/cursor` 脚本 MUST 将 `.cursor` 下的 `commands`、`rules`、`skills` 同步到目标项目的 `.cursor` 目录。

#### Scenario: Default sync all
- **WHEN** 用户执行 `install/cursor --target <path>`
- **THEN** 系统在目标路径生成或更新 `.cursor/commands`、`.cursor/rules`、`.cursor/skills`

### Requirement: Selective sync by scope
脚本 SHALL 支持选择性安装 `commands`、`rules`、`skills`，并仅同步被选择的目录。

#### Scenario: Only sync rules
- **WHEN** 用户执行 `install/cursor --only rules`
- **THEN** 系统仅同步 `.cursor/rules`，不处理 `commands` 与 `skills`

### Requirement: Skip identical files
脚本 MUST 对目标文件进行内容比对，若内容一致则跳过写入。

#### Scenario: File already up to date
- **WHEN** 目标文件存在且内容与源文件一致
- **THEN** 系统不覆盖该文件并记录跳过信息

### Requirement: Conflict handling
脚本 MUST 在目标文件存在且内容不同的情况下按框架策略处理冲突（默认报错，`--force` 覆盖，`--backup` 备份）。

#### Scenario: Conflict without force
- **WHEN** 目标文件存在且内容不同，且未指定 `--force` 或 `--backup`
- **THEN** 系统以非零退出并输出冲突提示

### Requirement: Create target directories
脚本 SHALL 在目标目录缺少 `.cursor` 或子目录时自动创建所需目录。

#### Scenario: Missing cursor directory
- **WHEN** 目标路径不存在 `.cursor` 目录
- **THEN** 系统创建 `.cursor` 与必要子目录后再进行同步
