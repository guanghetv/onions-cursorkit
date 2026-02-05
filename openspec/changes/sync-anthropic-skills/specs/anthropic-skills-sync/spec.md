# Anthropic Skills Sync

## 概述

本规格定义从 Anthropic 官方 GitHub 仓库 (https://github.com/anthropics/skills) 同步 agent skills 到 CursorKit 项目的能力。

## ADDED Requirements

### Requirement: 克隆 Anthropic Skills 仓库

系统 SHALL 能够从 GitHub 克隆或更新 Anthropic skills 仓库到临时目录。

#### Scenario: 首次克隆仓库

- **WHEN** 用户执行同步命令且本地无缓存
- **THEN** 系统克隆 `https://github.com/anthropics/skills` 到临时目录（如 `/tmp/anthropic-skills-xxx`）

#### Scenario: 更新已存在的克隆

- **WHEN** 用户执行同步命令且临时目录存在旧克隆
- **THEN** 系统执行 `git pull` 更新到最新版本

#### Scenario: 克隆失败处理

- **WHEN** 网络错误或仓库不可访问
- **THEN** 系统显示错误信息并提示检查网络连接，退出码非零

### Requirement: 识别并过滤技能文件

系统 SHALL 能够识别 Anthropic 仓库中的有效技能文件，并过滤出需要同步的内容。

#### Scenario: 识别有效技能

- **WHEN** 扫描克隆的仓库目录
- **THEN** 系统识别所有包含 `SKILL.md` 文件的目录作为有效技能

#### Scenario: 排除特定类型技能

- **WHEN** 识别到文档处理类技能（docx、pdf、pptx、xlsx）
- **THEN** 系统可选择性地跳过这些技能（因为它们是 source-available 而非 open source）

#### Scenario: 排除元数据文件

- **WHEN** 遍历技能目录
- **THEN** 系统排除 `.git`、`README.md`、`spec/`、`template/` 等非技能目录

### Requirement: 保护现有自定义技能

系统 SHALL 保护项目中已存在的自定义技能，避免被官方技能覆盖。

#### Scenario: 检测自定义技能

- **WHEN** 执行同步前检查目标目录
- **THEN** 系统识别所有 `openspec-*` 前缀的技能和 `create-feature-branch` 技能为自定义技能

#### Scenario: 跳过自定义技能覆盖

- **WHEN** 官方仓库包含与自定义技能同名的技能
- **THEN** 系统保留本地自定义技能，不进行覆盖

#### Scenario: 警告名称冲突

- **WHEN** 发现官方技能与自定义技能名称冲突
- **THEN** 系统输出警告信息，说明跳过了哪些技能

### Requirement: 复制技能到目标目录

系统 SHALL 将筛选后的官方技能复制到 `.cursor/skills/` 目录。

#### Scenario: 复制新技能

- **WHEN** 官方技能在本地不存在
- **THEN** 系统复制整个技能目录（包括 `SKILL.md` 和所有附加文件）到 `.cursor/skills/<skill-name>/`

#### Scenario: 更新已存在的技能

- **WHEN** 官方技能在本地已存在且版本不同
- **THEN** 系统覆盖本地技能文件（但保留备份选项）

#### Scenario: 保持目录结构

- **WHEN** 官方技能包含子目录（如 `references/`）
- **THEN** 系统保持完整的目录结构复制

### Requirement: 提供选择性同步选项

系统 SHALL 支持用户选择性地同步特定类别或特定技能。

#### Scenario: 同步所有技能

- **WHEN** 用户未指定过滤条件
- **THEN** 系统同步所有开源技能（排除 source-available 的文档处理类）

#### Scenario: 按类别同步

- **WHEN** 用户指定类别（如 `--category development`）
- **THEN** 系统仅同步该类别下的技能

#### Scenario: 同步特定技能

- **WHEN** 用户指定技能名称列表（如 `--skills create-rule,create-skill`）
- **THEN** 系统仅同步指定的技能

### Requirement: 生成同步报告

系统 SHALL 在同步完成后生成详细报告，说明同步了哪些技能及其状态。

#### Scenario: 显示同步摘要

- **WHEN** 同步完成
- **THEN** 系统显示新增、更新、跳过的技能数量统计

#### Scenario: 列出所有操作

- **WHEN** 使用 verbose 模式（如 `--verbose`）
- **THEN** 系统详细列出每个技能的操作（新增/更新/跳过）及原因

#### Scenario: 标识技能来源

- **WHEN** 同步完成
- **THEN** 系统在报告中标明技能来源为 Anthropic 官方仓库及 commit hash

### Requirement: 更新技能文档

系统 SHALL 更新 `.cursor/skills/README.md` 以反映官方技能和自定义技能的分类。

#### Scenario: 添加技能分类说明

- **WHEN** 同步完成
- **THEN** 系统在 README 中添加或更新章节，说明哪些是 Anthropic 官方技能，哪些是项目自定义技能

#### Scenario: 添加同步信息

- **WHEN** 同步完成
- **THEN** 系统在 README 中记录同步时间、源仓库版本（commit hash）

#### Scenario: 保留原有自定义内容

- **WHEN** README 中存在其他自定义内容
- **THEN** 系统仅更新技能列表部分，保留其他内容

### Requirement: 支持干运行模式

系统 SHALL 支持 dry-run 模式，允许用户预览同步操作而不实际修改文件。

#### Scenario: 预览同步操作

- **WHEN** 用户使用 `--dry-run` 参数
- **THEN** 系统显示将要执行的所有操作，但不实际修改任何文件

#### Scenario: 显示潜在冲突

- **WHEN** dry-run 模式检测到名称冲突或覆盖
- **THEN** 系统警告用户并说明哪些文件会被影响

### Requirement: 错误处理和回滚

系统 SHALL 在同步过程中处理错误，并提供回滚能力。

#### Scenario: 同步失败回滚

- **WHEN** 同步过程中发生错误（如磁盘空间不足）
- **THEN** 系统恢复同步前的状态，删除部分复制的文件

#### Scenario: 备份现有技能

- **WHEN** 使用 `--backup` 参数
- **THEN** 系统在同步前备份现有的官方技能到 `.cursor/skills/.backup-<timestamp>/`

#### Scenario: 验证技能完整性

- **WHEN** 复制技能后
- **THEN** 系统验证 `SKILL.md` 文件存在且格式正确（包含必需的 YAML frontmatter）
