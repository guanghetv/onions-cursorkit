## 安装脚本说明

此目录用于存放可扩展的安装脚本。每个脚本提供一致的命令行接口与日志输出，便于按需将 CursorKit 的配置同步到目标项目。

### 当前脚本

- `install/cursor`：同步 `.cursor` 下的 `commands`、`rules`、`skills` 到目标项目

### 通用参数

- `--target <path>`：目标项目路径（默认当前目录）
- `--only <scope>`：仅同步指定范围（`commands`、`rules`、`skills`，可用逗号分隔）
- `--dry-run`：仅输出操作，不写入文件
- `--force`：冲突时直接覆盖
- `--backup`：冲突时备份原文件再写入
- `--help`：显示帮助信息

### 冲突处理策略

- 默认不覆盖已有文件，若内容一致则跳过
- 若内容不同且未指定 `--force` / `--backup`，脚本会退出并提示冲突
- `--force` 会直接覆盖目标文件
- `--backup` 会先备份旧文件，再写入新文件

备份目录位于目标路径下，命名为 `.cursor-backup-<timestamp>`，并保留原始目录结构。

### 示例

```bash
# 通过 wget 下载并执行（默认当前目录）
wget -qO- https://gitlab.yc345.tv/backend/cursorkit/-/raw/master/install/cursor | bash

# 通过 wget 下载并执行（指定目标目录）
wget -qO- https://gitlab.yc345.tv/backend/cursorkit/-/raw/master/install/cursor | bash -s -- --target /path/to/project

# 同步全部 Cursor 配置（默认当前目录）
install/cursor

# 同步全部 Cursor 配置到指定目录
install/cursor --target /path/to/project

# 仅同步 rules
install/cursor --target /path/to/project --only rules

# 预览将要执行的操作
install/cursor --target /path/to/project --dry-run
```
