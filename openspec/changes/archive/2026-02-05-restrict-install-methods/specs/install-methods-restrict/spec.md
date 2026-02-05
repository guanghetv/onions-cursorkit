## ADDED Requirements

### Requirement: 仅支持 SSH 一键安装
安装脚本 MUST 仅支持使用 SSH 方式拉取安装源，并在默认情况下使用 SSH 仓库地址。

#### Scenario: 未指定仓库地址
- **WHEN** 用户未传入 `--repo`
- **THEN** 系统 MUST 使用 SSH 形式的默认仓库地址

### Requirement: 拒绝非 SSH 仓库地址
当用户通过 `--repo` 指定安装源时，系统 MUST 校验其为 SSH 形式，非 SSH 地址 MUST 被拒绝并提示原因。

#### Scenario: 使用 HTTPS 仓库地址
- **WHEN** 用户传入 `--repo https://example.com/repo.git`
- **THEN** 系统 MUST 拒绝执行并提示仅支持 SSH 安装方式

### Requirement: 提供 git remote 备选指引
当安装方式受限或用户需要备选路径时，系统 MUST 在文档中提供 git remote 备选流程的说明。

#### Scenario: 阅读安装文档
- **WHEN** 用户查看安装说明
- **THEN** 文档 MUST 仅展示 SSH 一键安装与 git remote 备选方式
