## Purpose

（TBD）

## Requirements

### Requirement: Script entry and CLI parity
安装脚本框架 MUST 提供统一的命令行接口与帮助信息，并确保各脚本的参数行为一致。

#### Scenario: Show help
- **WHEN** 用户执行 `install/<tool> --help`
- **THEN** 系统展示统一格式的用法说明与参数列表

### Requirement: Target path validation
框架 SHALL 支持 `--target <path>` 参数，并在写入前验证目标路径存在且可写。

#### Scenario: Invalid target path
- **WHEN** `--target` 指向不存在或不可写的路径
- **THEN** 系统以非零退出并输出明确错误信息

### Requirement: Logging and error handling
框架 MUST 提供标准日志输出（info/warn/error）并在失败时返回非零退出码。

#### Scenario: Command fails
- **WHEN** 安装流程中出现不可恢复错误
- **THEN** 系统输出 error 日志并以非零退出码结束

### Requirement: Dry-run behavior
框架 SHALL 支持 `--dry-run`，在该模式下不写入任何文件且仍输出将要执行的操作。

#### Scenario: Dry-run copy
- **WHEN** 用户执行 `install/<tool> --dry-run`
- **THEN** 系统仅输出拟执行的复制与冲突检查结果，不修改目标目录

### Requirement: Git source retrieval
框架 MUST 使用 git 协议从 `git@gitlab.yc345.tv/backend/cursorkit.git` 获取安装源文件。

#### Scenario: Fetch source via git
- **WHEN** 脚本需要获取安装源文件
- **THEN** 系统使用 `git` 从 `git@gitlab.yc345.tv/backend/cursorkit.git` 拉取所需内容

### Requirement: Backup and force behavior
框架 MUST 支持 `--backup` 与 `--force` 的冲突处理策略。

#### Scenario: Conflict with backup
- **WHEN** 目标文件已存在且内容不同，并且指定 `--backup`
- **THEN** 系统先备份旧文件，再写入新文件
