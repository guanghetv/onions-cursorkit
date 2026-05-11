## 1. 插件骨架与市场注册

- [x] 1.1 创建 `plugins/tls-traffic-suite/` 目录结构，包含 `.cursor-plugin/`、`commands/`、`skills/` 子目录。
- [x] 1.2 新增 `plugins/tls-traffic-suite/.cursor-plugin/plugin.json`，声明 `name`、`displayName`、`version`、`description`、`author`、`keywords`、`skills` 和 `commands`。
- [x] 1.3 在 `.cursor-plugin/marketplace.json` 注册 `tls-traffic-suite`，`source` 使用 `tls-traffic-suite`。

## 2. Skill 迁移

- [x] 2.1 创建 `plugins/tls-traffic-suite/skills/tls-route-traffic-compare/` 目录。
- [x] 2.2 从个人 skill 迁移 `SKILL.md` 到插件 skill 目录。
- [x] 2.3 从个人 skill 迁移 `references/input-format.md`、`references/tls-query.md`、`references/merge-and-preview.md`、`references/base-output.md`。
- [x] 2.4 从个人 skill 迁移 `scripts/tls_route_traffic.py` 和 `scripts/test_tls_route_traffic.py`。
- [x] 2.5 确认未迁移个人运行产物：`tmp/`、临时 JSON、CSV、飞书批量写入文件、任何凭证。

## 3. 插件内文档适配

- [x] 3.1 更新插件内 `SKILL.md` 的脚本路径示例，避免继续引用个人 `.agents/skills/...` 路径。
- [x] 3.2 更新 `references/tls-query.md`，确保环境变量、公共 endpoint、无 SDK 依赖说明适用于插件安装环境。
- [x] 3.3 更新 `references/merge-and-preview.md`，确认六列输出、确定性归一化和 assisted subagent 边界描述完整。
- [x] 3.4 更新 `references/base-output.md`，将 `lark-base` / `lark-shared` 描述为外部已安装能力或 `lark-cli` 依赖，不使用个人目录相对路径。

## 4. 命令入口与 README

- [x] 4.1 新增 `plugins/tls-traffic-suite/commands/tls-route-traffic-compare.md`，命令触发后要求读取并遵循插件内 skill。
- [x] 4.2 命令文档说明必须收集环境、A/B 服务、时间范围、输出目标，并在写入飞书前预览确认。
- [x] 4.3 新增 `plugins/tls-traffic-suite/README.md`，说明包含的 skill、command、依赖、环境变量、安全约束和使用示例。
- [x] 4.4 更新根 `README.md` 当前插件列表，新增 `tls-traffic-suite`，并补齐 marketplace 中已有但 README 缺失的插件条目。

## 5. 验证

- [x] 5.1 运行 `python3 plugins/tls-traffic-suite/skills/tls-route-traffic-compare/scripts/test_tls_route_traffic.py`，确认迁移后的脚本测试通过。
- [x] 5.2 运行 `node scripts/validate-template.mjs`，确认插件清单和市场注册通过校验。
- [x] 5.3 搜索 `plugins/tls-traffic-suite/`，确认不存在 `tmp/`、生产查询结果文件、凭证或个人绝对路径。
- [x] 5.4 复核 `openspec/changes/add-tls-traffic-suite-plugin/specs/tls-traffic-suite-plugin/spec.md` 的每条 Requirement 都有对应完成任务。
