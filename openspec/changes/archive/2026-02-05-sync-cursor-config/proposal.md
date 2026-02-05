## Why

目前项目中集成 CursorKit 的方式是通过 git remote 拉取，这种方式存在以下问题：
1. 会引入不相关的 git 历史记录
2. 无法选择性地安装特定工具（如只安装 Cursor 配置，不安装其他工具）
3. 后续如果需要集成其他工具（如 trae、claude 等）缺乏统一的安装机制

需要提供一个更灵活、可扩展的安装脚本系统，让用户可以通过简单的命令将 CursorKit 的配置或其他工具安装到目标项目中。

## What Changes

- 新增 `install/` 目录，用于存放各种安装脚本
- 创建 `install/cursor` 脚本，用于将 `.cursor` 下的 commands、rules、skills 同步到目标项目
- 建立可扩展的安装脚本架构，支持后续添加其他工具的安装脚本（如 `install/trae`、`install/claude` 等）
- 提供统一的使用方式和参数规范

## Capabilities

### New Capabilities

- `install-script-framework`: 定义安装脚本的通用框架和规范，包括命令行参数、错误处理、日志输出等标准行为
- `cursor-config-sync`: 实现将 `.cursor` 配置（commands、rules、skills）同步到目标项目的功能，支持选择性安装和冲突处理

### Modified Capabilities

<!-- 无现有功能需要修改 -->

## Impact

**新增内容**:
- 新增 `install/` 目录
- 新增 `install/cursor` 脚本
- 新增 `install/README.md` 说明文档

**现有内容**:
- 更新根目录 `README.md`，添加新的安装方式说明
- 保留现有的 git remote 方式作为备选方案

**用户影响**:
- 提供更简洁的安装方式，用户可以直接运行脚本而不需要处理 git 历史
- 支持增量更新和选择性安装
