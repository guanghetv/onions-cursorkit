# workspace-specflow-codex-distribution Specification

## Purpose

为 Codex 提供可独立安装、与 Cursor 隔离并支持 CodeWiki 跨仓检索的 workspace-specflow 能力。

## Requirements

### Requirement: 标准且隔离的 Codex 插件包

系统 MUST 生成符合 OpenAI Codex 官方插件格式的自包含包，并保持 Cursor marketplace 不发现该 Codex 专属包。

#### Scenario: 构建可安装包

- **WHEN** 维护者执行 Codex 插件构建
- **THEN** ZIP 的唯一插件根包含有效 `.codex-plugin/plugin.json` 和 `skills/`
- **AND** 每个技能满足 Agent Skills 的目录与 frontmatter 约束
- **AND** 包不要求运行时访问 cursorkit 源仓
- **AND** 打包、同步与校验脚本位于 Codex 插件目录内，不新增仓库根 `scripts/` 入口

#### Scenario: Cursor 隔离

- **WHEN** Codex 插件源和构建能力加入 cursorkit
- **THEN** `.cursor-plugin/marketplace.json` 不增加该 Codex 包
- **AND** 现有 workspace-specflow Cursor 插件 manifest 与发现路径保持不变

### Requirement: 单一源与漂移检测

系统 MUST 以 `plugins/workspace-specflow/skills/` 为业务正文唯一源，通过构建生成 Codex 包内容。

#### Scenario: 源技能更新

- **WHEN** 任一源 skill、reference、script 或 asset 发生变化
- **THEN** 未同步的 check 必须失败并指出漂移
- **AND** 重新构建后包内容与源内容一致

#### Scenario: 打包入口隔离

- **WHEN** 维护者查看仓库根 `scripts/` 与 Codex 插件目录
- **THEN** 同步、校验和 ZIP 入口只出现在 Codex 插件目录内
- **AND** 仓库根 `scripts/` 不新增 Codex 打包入口

#### Scenario: 重复构建

- **WHEN** 输入未变化并连续构建两次
- **THEN** 两次包内容清单与摘要一致

### Requirement: CodeWiki 优先的跨仓代码上下文

系统 MUST 从 specs 仓的 `workspace-repos.json` 解析关联仓，并以 CodeWiki/GitNexus 作为首选代码检索渠道。

#### Scenario: remote 精确映射

- **WHEN** registry 项含 GitLab remote 且 GitNexus 清单含对应规范仓名
- **THEN** 系统按归一化 remote path 选择唯一仓库
- **AND** 不把 registry 逻辑名直接假设为规范仓名

#### Scenario: CodeWiki 不可用

- **WHEN** 当前代码检索步骤无法调用 CodeWiki
- **THEN** 系统检查 registry 的本地 path 并尝试只读扫描
- **AND** 明确提示用户已降级及证据范围

#### Scenario: 双重不可用

- **WHEN** CodeWiki 和本地仓库均不可用
- **THEN** 系统只阻断当前依赖代码上下文的步骤
- **AND** 不阻断纯 PRD、同步或状态查询步骤
- **AND** 不猜测代码事实或仓库映射

### Requirement: 可复现验证与运维说明

系统 MUST 提供静态校验、安装、升级、卸载和故障排查说明。

#### Scenario: 缺少 Codex CLI

- **WHEN** 验收环境没有 Codex CLI
- **THEN** 静态结构、漂移、ZIP 和映射测试仍可执行
- **AND** 真实安装发现测试被明确标记为待补，而不是虚构成功
