## 1. 创建独立同步脚本

- [x] 1.1 创建 `install/sync-skills` 脚本文件，设置执行权限和 shebang
- [x] 1.2 添加脚本头部：source `install/lib/common.sh` 工具函数，设置 `set -euo pipefail`
- [x] 1.3 定义常量：Anthropic 仓库 URL、自定义技能白名单、排除技能列表
- [x] 1.4 实现参数解析：支持 `--dry-run`、`--force`、`--backup`、`--help` 参数
- [x] 1.5 实现 `show_usage()` 函数，显示脚本使用说明

## 2. 实现仓库克隆逻辑

- [x] 2.1 实现 `clone_anthropic_repo()` 函数：创建临时目录，克隆 Anthropic skills 仓库（使用 `--depth 1`）
- [x] 2.2 添加 `trap` 处理：确保脚本退出时清理临时目录
- [x] 2.3 添加错误处理：检测 git 命令失败，输出网络问题提示
- [x] 2.4 记录克隆的 commit hash 用于后续追溯

## 3. 实现技能识别和过滤

- [x] 3.1 实现 `list_valid_skills()` 函数：扫描临时目录，识别所有包含 `SKILL.md` 的技能目录
- [x] 3.2 实现 `is_custom_skill()` 函数：检查技能名称是否匹配自定义技能白名单（openspec-* 或 create-feature-branch）
- [x] 3.3 实现 `is_excluded_skill()` 函数：检查技能名称是否在排除列表中（docx、pdf、pptx、xlsx）
- [x] 3.4 实现 `filter_skills()` 函数：过滤出需要同步的技能列表，跳过自定义和排除的技能

## 4. 实现技能复制逻辑

- [x] 4.1 实现 `sync_skill()` 函数：复制单个技能目录到 `.cursor/skills/`，保持完整目录结构
- [x] 4.2 集成 `install/lib/common.sh` 的 `sync_file()` 函数处理文件冲突和备份
- [x] 4.3 添加技能验证：复制后检查目标目录中 `SKILL.md` 文件是否存在且格式正确
- [x] 4.4 实现同步统计：记录新增、更新、跳过的技能数量

## 5. 实现 README 更新

- [x] 5.1 读取 `.cursor/skills/README.md` 的现有内容（如果存在）
- [x] 5.2 生成技能分类段落：列出自定义技能和官方技能
- [x] 5.3 添加同步信息段落：记录同步时间、源仓库 commit hash、Anthropic 仓库链接
- [x] 5.4 将更新后的内容写回 `.cursor/skills/README.md`（或创建新文件）

## 6. 实现主流程和输出

- [x] 6.1 实现 `main()` 函数：串联克隆、过滤、复制、README 更新流程
- [x] 6.2 添加详细的日志输出：每个阶段显示进度信息（使用 `log_info`、`log_warn`）
- [x] 6.3 生成同步报告：输出新增、更新、跳过的技能统计和列表
- [x] 6.4 支持 `--dry-run` 模式：显示将要执行的操作但不实际修改文件

## 7. 测试和验证

- [x] 7.1 在干净的测试环境中运行 `install/sync-skills --dry-run`，验证预览输出正确
- [x] 7.2 运行 `install/sync-skills`（不带参数），验证首次同步：检查官方技能被复制、自定义技能未被修改
- [x] 7.3 再次运行 `install/sync-skills`，验证更新场景：检查已存在的官方技能被正确覆盖
- [x] 7.4 测试 `--backup` 参数：验证备份目录被创建，旧文件被保存
- [x] 7.5 验证 `.cursor/skills/README.md` 被正确更新，包含技能分类和同步信息
- [x] 7.6 验证自定义技能保护：检查 openspec-* 和 create-feature-branch 技能未被覆盖

## 8. 文档更新

- [x] 8.1 在项目根目录 `README.md` 中添加"技能同步"章节，说明如何使用 `install/sync-skills`
- [x] 8.2 说明脚本职责：仅负责将 Anthropic 官方技能同步到 CursorKit 本地仓库，不涉及其他项目
- [x] 8.3 添加示例命令：展示常见的同步场景（首次同步、更新、dry-run、backup）
- [x] 8.4 说明自定义技能保护机制和官方技能来源
