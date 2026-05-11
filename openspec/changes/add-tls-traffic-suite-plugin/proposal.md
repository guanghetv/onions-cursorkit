## Why

`tls-route-traffic-compare` 已经在个人 skills 目录中验证可用，但目前还不是 CursorKit 插件市场的一部分，团队成员无法通过 `onions-plugins` 统一安装和复用。

将它封装为独立插件可以沉淀 TLS 流量对比、路由归一化、assisted 聚合和飞书 Base 输出能力，并为后续迁移验收、切流前后流量校验等场景留下扩展空间。

## What Changes

- 新增 `tls-traffic-suite` 插件，作为独立的 Cursor 插件市场条目发布。
- 将现有 `tls-route-traffic-compare` skill 迁入插件目录，保留 `SKILL.md`、`references/`、核心脚本和测试。
- 新增 `/tls-route-traffic-compare` 命令作为对话入口，避免用户记忆底层 skill 名称和脚本路径。
- 更新插件市场清单和根 README，使 `tls-traffic-suite` 出现在可安装插件列表中。
- 明确只迁移可复用源码与文档，不迁移个人运行产生的 `tmp/` 结果文件。
- 明确外部依赖：Python 3、火山 TLS 环境变量、可选的 `lark-cli` / lark-base 能力用于写入飞书 Base。

## Capabilities

### New Capabilities

- `tls-traffic-suite-plugin`: 发布 TLS 流量对比插件，包含插件清单、命令入口、skill 迁移、脚本测试、市场注册和 README 文档要求。

### Modified Capabilities

- None.

## Impact

- 新增 `plugins/tls-traffic-suite/` 插件目录。
- 修改 `.cursor-plugin/marketplace.json` 注册新插件。
- 修改根 `README.md` 的当前插件列表和推荐安装说明。
- 复用来自个人 skill 的 `tls-route-traffic-compare` 文档、脚本与测试。
- 不引入新的 Python 第三方依赖；脚本继续仅使用标准库访问火山 TLS API。
