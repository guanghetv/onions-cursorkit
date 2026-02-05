## Context

当前 `install/cursor` 通过 `git clone` 拉取安装源并同步 `.cursor/commands`、`.cursor/rules`、`.cursor/skills` 到目标项目。默认使用 HTTPS 源地址，且文档中存在多种安装方式描述。需求希望收敛安装路径，仅保留 SSH 一键安装与 git remote 备选方式，同时将 cursor 相关目录同步能力作为显式保障能力。

## Goals / Non-Goals

**Goals:**
- 明确并强制只支持 SSH 一键安装与 git remote 备选路径。
- 保证 `.cursor/commands`、`.cursor/rules`、`.cursor/skills` 能稳定同步到目标项目标准目录，且支持只同步指定范围与冲突处理。
- 更新安装文档与提示，降低用户误用其他安装方式的概率。

**Non-Goals:**
- 不引入新的安装协议或包管理方式（如 npm、brew）。
- 不改变 `.cursor` 内容结构或其内部文件格式。
- 不引入复杂的远程配置同步或增量更新机制。

## Decisions

- **安装源协议限制为 SSH**：`install/cursor` 默认使用 SSH 形式的仓库地址，并在用户通过 `--repo` 覆盖时校验必须为 SSH。选择此方案是为了与“仅支持 SSH 一键安装”保持一致，并避免 HTTPS 带来的认证与交互问题。替代方案是继续支持 HTTPS 并只在文档层面提示，但这与“仅保留”目标不一致。
- **git remote 作为备选路径**：为已有仓库的用户提供“设置 git remote 为 SSH → 本地运行安装脚本”的文档化路径。相比继续提供其他下载或复制方式，这种方式成本低、可追溯且与 SSH 限制一致。
- **同步能力以脚本为唯一入口**：继续通过 `install/cursor` 完成 `.cursor` 目录下 `commands`、`rules`、`skills` 的同步，支持 `--only`、`--force`、`--backup`，并在冲突时给出明确指引。替代方案是提供额外独立脚本，但会增加维护成本和用户路径分散。

## Risks / Trade-offs

- **破坏现有 HTTPS 或其他安装方式用户** → 在脚本中给出清晰错误信息，并在 README 中提供迁移与 git remote 备选指引。
- **严格限制导致内部环境无法访问 SSH** → 明确以 git remote 方式作为备选，并在文档中标注网络/权限要求。
- **同步冲突导致覆盖风险** → 继续支持 `--backup` 与 `--force`，默认在冲突时中止并提示可选策略。

## Migration Plan

- 更新 README 与安装说明，移除其他安装方式，新增 SSH 一键安装与 git remote 备选流程。
- 在脚本中加入 SSH 地址校验与错误提示，说明可选的 git remote 备选方式。
- 发布后收集用户反馈，必要时补充常见问题说明。

## Open Questions

- git remote 备选方式的具体命令流程是否需要固定模板（例如 remote 名称与分支约定）？
- 是否需要为企业内网或 SSH 受限场景提供额外说明或已知限制列表？
