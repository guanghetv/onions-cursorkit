## Why

当前安装流程支持多种方式，维护成本高且用户路径分散。希望明确支持面向稳定交付的主流程，只保留 SSH 一键安装与 git remote 备选方式，并新增将 `.cursor` 下 `commands`、`rules`、`skills` 同步到目标项目标准目录的能力，提升落地一致性。

## What Changes

- 仅保留通过 SSH 一键安装方式，并提供 git remote 作为备选路径。其他安装方式移除或不再支持（**BREAKING**）。
- 新增将 `.cursor` 下 `commands`、`rules`、`skills` 同步到目标项目 cursor 标准目录的能力。

## Capabilities

### New Capabilities
- `cursor-config-copy`: 将 `.cursor/commands`、`.cursor/rules`、`.cursor/skills` 同步到目标项目 cursor 标准目录的能力。
- `install-methods-restrict`: 仅支持 SSH 一键安装与 git remote 备选方式的安装流程与约束。

### Modified Capabilities
<!-- 无现有 specs，可留空 -->

## Impact

- 影响安装脚本与参数解析（`install/cursor`, `install/lib/common.sh`）。
- 影响项目文档与使用说明（`README.md`）。
- 可能影响现有使用其他安装方式的用户流程（需要迁移说明）。
