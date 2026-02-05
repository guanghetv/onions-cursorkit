# CursorKit

此项目用于维护洋葱内部自建或从第三方收集的`cursor command` `cursor rules` `agent skills`

- [cursor command](.cursor/commands/README.md)
- [cursor rules](.cursor/rules/README.md)
- [agent skills](.cursor/skills/README.md)

## 项目中快速集成

### 脚本安装（推荐）

1. 通过脚本安装（推荐）：
   - wget 执行（默认当前目录）：`wget -qO- https://gitlab.yc345.tv/backend/cursorkit/-/raw/master/install/cursor | bash`
   - wget 执行（指定目标目录）：`wget -qO- https://gitlab.yc345.tv/backend/cursorkit/-/raw/master/install/cursor | bash -s -- --target /path/to/project`
   - 本地执行（默认当前目录）：`bash install/cursor`
   - 本地执行（指定目标目录）：`bash install/cursor --target /path/to/project`
2. 可选参数示例：
   - 仅同步规则：`bash install/cursor --target /path/to/project --only rules`
   - 预览操作：`bash install/cursor --target /path/to/project --dry-run`

### git remote 方式（备选）

1. `git remote add cursorkit git@gitlab.yc345.tv:backend/cursorkit`
2. `git pull cursorkit master --allow-unrelated-histories`