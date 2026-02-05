## Why

CursorKit 项目维护内部的 Cursor commands、rules 和 agent skills，但目前缺少 Anthropic 官方提供的通用技能。Anthropic 在 GitHub 仓库 (https://github.com/anthropics/skills) 中开源了大量高质量的 agent skills，涵盖创意设计、技术开发、企业通信等多个领域。将这些官方技能同步到 CursorKit 中，可以让团队成员在项目中直接使用这些经过验证的技能模板，提升开发效率。

## What Changes

- 从 `https://github.com/anthropics/skills` 仓库同步官方技能到 CursorKit 的 `.cursor/skills/` 目录
- 保留项目现有的自定义技能（openspec-* 系列和 create-feature-branch）
- 添加同步脚本或机制，支持选择性同步和持续更新
- 更新 `.cursor/skills/README.md` 以区分官方技能和自定义技能

## Capabilities

### New Capabilities

- `anthropic-skills-sync`: 从 Anthropic GitHub 仓库同步官方技能的能力，包括 Git 克隆、选择性同步、冲突处理和更新机制

### Modified Capabilities

<!-- 无现有 capability 的需求变更 -->

## Impact

- `.cursor/skills/` 目录将从 `https://github.com/anthropics/skills` 同步官方技能
- 同步的技能包括但不限于：
  - 创意与设计类：art、music、design 等
  - 开发与技术类：testing、MCP server generation 等
  - 企业与通信类：communications、branding 等
  - 文档处理类：docx、pdf、pptx、xlsx（source-available，仅供参考）
- 需要处理与现有自定义技能的共存问题（保留 openspec-* 和 create-feature-branch）
- `.cursor/skills/README.md` 需要更新以说明技能来源和分类
- 可能需要添加 `.gitignore` 规则或同步脚本到 `install/` 目录
