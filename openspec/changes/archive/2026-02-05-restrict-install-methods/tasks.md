## 1. 安装方式限制

- [x] 1.1 将默认安装源改为 SSH 仓库地址，并在 `install/cursor` 中加入非 SSH 地址校验与错误提示
- [x] 1.2 明确 `--repo` 参数只接受 SSH 形式，新增示例与错误信息覆盖 HTTPS 场景

## 2. 文档与备选路径

- [x] 2.1 更新 `README.md`，仅保留 SSH 一键安装说明
- [x] 2.2 补充 git remote 备选流程说明（含步骤与注意事项）
- [x] 2.3 增加迁移提示：移除其他安装方式并说明影响范围

## 3. 同步能力校验

- [x] 3.1 核对 `install/cursor` 的同步逻辑覆盖 `commands`、`rules`、`skills` 及 `--only`
- [x] 3.2 验证 `--dry-run`、`--force`、`--backup` 的冲突处理与输出提示符合 specs
