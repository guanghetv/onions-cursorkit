## ADDED Requirements

### Requirement: 独立插件发布
CursorKit SHALL publish TLS route traffic comparison as an independent plugin named `tls-traffic-suite`.

#### Scenario: 插件目录可被市场发现
- **WHEN** the plugin marketplace manifest is validated
- **THEN** `.cursor-plugin/marketplace.json` MUST contain a `tls-traffic-suite` entry whose `source` points to `tls-traffic-suite`

#### Scenario: 插件清单声明能力
- **WHEN** Cursor reads `plugins/tls-traffic-suite/.cursor-plugin/plugin.json`
- **THEN** the manifest MUST declare the plugin name, display name, version, description, author, keywords, skills path, and commands path

### Requirement: Skill 迁移
The plugin SHALL include the existing `tls-route-traffic-compare` skill as an installable Cursor skill.

#### Scenario: Skill 内容完整迁移
- **WHEN** the plugin is installed from CursorKit
- **THEN** the installed skill MUST include `SKILL.md`, `references/input-format.md`, `references/tls-query.md`, `references/merge-and-preview.md`, `references/base-output.md`, and `scripts/tls_route_traffic.py`

#### Scenario: 运行产物不进入插件
- **WHEN** the plugin directory is inspected
- **THEN** it MUST NOT include personal runtime result files from the source skill `tmp/` directory

#### Scenario: 脚本保持无第三方 Python 依赖
- **WHEN** `tls_route_traffic.py` runs in the plugin package
- **THEN** it MUST use Python standard library modules for Volcengine TLS HTTP calls and MUST NOT require installing the Volcengine SDK

### Requirement: 命令入口
The plugin SHALL provide a `/tls-route-traffic-compare` command as the user-facing entrypoint for the workflow.

#### Scenario: 命令触发 skill 工作流
- **WHEN** a user invokes `/tls-route-traffic-compare`
- **THEN** the command MUST instruct the Agent to read and follow `skills/tls-route-traffic-compare/SKILL.md`

#### Scenario: 命令收集必要输入
- **WHEN** the user has not provided environment, A service, B service, time range, or output target
- **THEN** the command MUST guide the Agent to infer safe defaults where possible and ask only for hard blockers

### Requirement: TLS 对比输出能力
The packaged skill SHALL preserve the latest TLS comparison behavior validated in the personal skill.

#### Scenario: 生成六列用户输出
- **WHEN** comparing two services with service names available
- **THEN** the output MUST include `路由地址`, `method`, `<A服务名>流量`, `<B服务名>流量`, `<A服务名>有流量`, and `<B服务名>有流量`

#### Scenario: 保留路由归一化
- **WHEN** raw routes contain `/teacher-school` prefixes, `:id` variables, or `{id}` variables
- **THEN** the comparison MUST normalize them before joining by route and method

#### Scenario: 保留 assisted 聚合边界
- **WHEN** candidate literal route groups are detected
- **THEN** the script MUST only generate candidate reports and apply explicit rules; the main Agent MUST remain responsible for launching read-only subagents and deciding which rules to pass back after user confirmation

### Requirement: 飞书 Base 输出依赖
The plugin SHALL document Feishu Base output as an optional integration that depends on existing lark capabilities.

#### Scenario: 写入前检查字段
- **WHEN** the user asks to write comparison results into Feishu Base
- **THEN** the workflow MUST check target Base fields before writing and MUST use number fields for traffic columns and checkbox-compatible fields for `有流量` columns

#### Scenario: 不复制 lark skills
- **WHEN** packaging `tls-traffic-suite`
- **THEN** the plugin MUST NOT duplicate `lark-base` or `lark-shared`; documentation MUST describe them as external installed capabilities or `lark-cli` dependencies

### Requirement: 文档和验证
The plugin SHALL include documentation and validation coverage sufficient for team installation.

#### Scenario: 根 README 列出插件
- **WHEN** a user reads the repository root `README.md`
- **THEN** the current plugin list MUST include `tls-traffic-suite` with a concise Chinese description

#### Scenario: 插件 README 说明使用方式
- **WHEN** a user opens `plugins/tls-traffic-suite/README.md`
- **THEN** it MUST describe included skills, commands, external dependencies, environment variables, and safe packaging boundaries

#### Scenario: 模板校验通过
- **WHEN** `node scripts/validate-template.mjs` is run
- **THEN** the new plugin and marketplace registration MUST pass validation

#### Scenario: Skill 脚本测试通过
- **WHEN** the plugin is implemented
- **THEN** the migrated `test_tls_route_traffic.py` test suite MUST pass against the plugin-local script
