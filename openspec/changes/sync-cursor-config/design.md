## Context

当前通过 git remote 集成 CursorKit 会引入不相关历史，并且无法选择性安装。需求是在仓库内新增统一的安装脚本体系，使用户可以按需将 `.cursor` 下的 commands、rules、skills 同步到目标项目，并为未来其他工具的安装脚本提供可扩展框架。

## Goals / Non-Goals

**Goals:**
- 定义统一的安装脚本框架与参数规范（日志、错误处理、目标路径、选择性安装）
- 提供 `install/cursor` 脚本，将 `.cursor` 配置同步到目标项目
- 支持增量更新与冲突处理，避免覆盖用户自定义内容

**Non-Goals:**
- 立即实现 `install/trae`、`install/claude` 等其他工具脚本
- 移除现有 git remote 安装方式
- 做复杂的交互式 UI 或跨平台安装器

## Decisions

- **使用 Bash 作为脚本入口**：仓库内已有脚本化需求，Bash 易于直接执行且无需额外依赖；未来如需更复杂逻辑，再引入 Node 作为可选实现。
- **安装脚本框架抽象为共享库**：在 `install/lib/` 提供通用函数（参数解析、日志、错误处理、路径校验、冲突检测），各工具脚本只关注自身安装逻辑，便于扩展。
- **安装源通过 git 协议获取**：脚本从 `git@gitlab.yc345.tv/backend/cursorkit.git` 拉取所需文件，确保来源一致且适配 GitLab 托管环境。
- **统一 CLI 规范**：约定 `--target`、`--only`、`--exclude`、`--dry-run`、`--force`、`--backup` 等参数，保持不同脚本一致的行为与输出。
- **冲突处理策略**：默认不覆盖已有文件；若内容一致则跳过，内容不一致则报错并提示使用 `--force` 或 `--backup`。使用备份目录保留旧文件，避免用户配置丢失。
- **同步范围按目录粒度控制**：`install/cursor` 支持按 `commands`、`rules`、`skills` 选择性安装，满足最常见场景且实现简单。

## Risks / Trade-offs

- **脚本可移植性差异** → 使用 POSIX 兼容写法，避免依赖不常见工具；对必须依赖的命令（如 `cp`、`mkdir`）做存在性检查。
- **冲突处理增加使用成本** → 默认安全策略并提供明确提示与 `--dry-run`，降低误用风险。
- **框架抽象过早** → 控制 `install/lib/` 规模，仅保留通用能力，避免过度工程化。

## Migration Plan

- 新增 `install/` 目录与脚本框架，不影响现有使用方式。
- 在根目录 `README.md` 中补充脚本安装方式，保留 git remote 作为备选。
- 若出现问题，用户可继续使用原有 git remote 方式作为回退路径。

## Open Questions

- 需要支持哪些默认参数组合（例如是否默认启用 `--backup`）？
- `install/cursor` 的目标路径是否允许非仓库根目录（例如 `--target` 指向子项目）？
