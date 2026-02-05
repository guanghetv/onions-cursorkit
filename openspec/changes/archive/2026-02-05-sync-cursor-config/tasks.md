## 1. 安装脚本框架

- [x] 1.1 创建 `install/` 目录与基础脚手架（含 `install/README.md`）
- [x] 1.2 新增 `install/lib/` 通用库：参数解析、日志、错误处理
- [x] 1.3 实现 `--target` 校验与路径可写检查
- [x] 1.4 实现 `--dry-run` 行为与统一输出
- [x] 1.5 实现 git 协议获取源文件（`git@gitlab.yc345.tv/backend/cursorkit.git`）
- [x] 1.6 实现冲突检测与 `--force` / `--backup` 策略

## 2. Cursor 配置同步脚本

- [x] 2.1 实现 `install/cursor` 脚本入口与 `--help` 输出
- [x] 2.2 实现 `.cursor/commands`、`.cursor/rules`、`.cursor/skills` 同步逻辑
- [x] 2.3 支持 `--only` 选择性同步并验证范围
- [x] 2.4 实现内容一致时跳过写入与日志输出
- [x] 2.5 实现目标目录不存在时的自动创建

## 3. 文档与说明

- [x] 3.1 更新根目录 `README.md`，加入脚本安装说明与示例
- [x] 3.2 编写 `install/README.md`，说明参数、示例与冲突处理
