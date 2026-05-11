## Context

CursorKit 当前维护 `onions-plugins` 私有插件市场，插件以 `plugins/<name>/` 目录发布，并通过 `.cursor-plugin/marketplace.json` 注册。已有 `go-cutover-suite` 这类业务工作流插件，采用 `commands + skills + scripts + references` 的独立套件结构。

`tls-route-traffic-compare` 当前位于个人 skills 目录，已经具备以下能力：

- 使用 Python 标准库直接调用火山 TLS API，并实现 SigV4 签名。
- 按 `{namespace}-{service}` 规则发现 topic。
- 按 route/method 查询生产流量，并对比两个服务。
- 对 route 做确定性归一化：去 `/teacher-school` 前缀、统一 `:id` / `{id}` 为 `{param}`。
- 生成 assisted candidate report，由主 Agent 启动只读 subagent 分析候选，再把显式规则传回脚本应用。
- 输出动态六列：`路由地址`、`method`、`<A服务名>流量`、`<B服务名>流量`、`<A服务名>有流量`、`<B服务名>有流量`。
- 可选写入飞书 Base，但依赖外部 `lark-cli` 和 lark base 操作能力。

本变更要把该能力从个人 skill 迁移为团队可安装插件，而不是重新设计 TLS 对比算法。

## Goals / Non-Goals

**Goals:**

- 新增独立插件 `tls-traffic-suite`，并注册到 CursorKit 插件市场。
- 迁移 `tls-route-traffic-compare` skill 的可复用源码、文档、脚本和测试。
- 新增 `/tls-route-traffic-compare` 命令入口，作为用户使用该工作流的统一触发方式。
- 更新根 README 和插件 README，使团队成员知道如何安装、配置环境变量、运行对比和写入飞书。
- 保持脚本无第三方 Python 依赖，继续使用标准库调用火山 TLS。
- 保留 assisted 聚合的人机边界：脚本只生成候选和应用显式规则，Agent/subagent 负责判断规则。

**Non-Goals:**

- 不把该能力并入 `common` 或 `go-cutover-suite`。
- 不复制或内嵌 `lark-base`、`lark-shared`、`lark-cli` 能力。
- 不迁移个人运行产物，如 `tmp/*.json`、临时 CSV、飞书写入批次文件。
- 不新增自动创建飞书 Base 表的完整建表工作流；本次只要求字段检查和兼容写入说明。
- 不改变火山 TLS 查询 SQL、route 归一化算法或 assisted candidate 算法的语义。

## Decisions

### Decision 1: 使用独立插件 `tls-traffic-suite`

把 TLS 流量对比做成 `plugins/tls-traffic-suite/`，结构参考 `go-cutover-suite`：

```text
plugins/tls-traffic-suite/
├── .cursor-plugin/plugin.json
├── README.md
├── commands/
│   └── tls-route-traffic-compare.md
└── skills/
    └── tls-route-traffic-compare/
        ├── SKILL.md
        ├── references/
        └── scripts/
```

理由：

- TLS 流量对比是完整业务工作流，不是通用规则或单个小工具。
- 独立插件便于后续扩展 `tls-traffic-audit`、`cutover-traffic-verify` 等能力。
- `go-cutover-suite` 可以在未来依赖或提示安装该插件，但两者不应强耦合。

备选方案：

- 放进 `common`：安装覆盖面大，但会让通用插件变重，并把火山 TLS 业务依赖带给不需要的人。
- 放进 `go-cutover-suite`：当前用例来自 Go 迁移，但 TLS 对比本身可用于任意两个服务，不应绑定 Go 切流。

### Decision 2: 迁移源码但排除运行产物

从个人 skill 迁移：

- `SKILL.md`
- `references/input-format.md`
- `references/tls-query.md`
- `references/merge-and-preview.md`
- `references/base-output.md`
- `scripts/tls_route_traffic.py`
- `scripts/test_tls_route_traffic.py`

不迁移：

- `tmp/`
- 临时 JSON / CSV / 飞书批量写入文件
- 本地环境变量或任何凭证

理由：插件包应只包含可复用能力，不能携带某次生产查询结果或用户私有数据。

### Decision 3: 命令入口只编排，不复制算法

`commands/tls-route-traffic-compare.md` 只负责：

- 触发时要求 Agent 读取 `skills/tls-route-traffic-compare/SKILL.md`。
- 收集环境、A/B 服务、时间范围、输出目标。
- 强调写入飞书前必须预览和确认。

所有算法、脚本命令和失败处理仍由 skill 文档和 Python 脚本承载。

理由：避免命令和 skill 之间出现两套流程描述，降低后续维护成本。

### Decision 4: 飞书能力保持外部依赖

`base-output.md` 需要从个人目录相对路径表述改成插件环境下的外部依赖表述：

- 写入飞书 Base 前，Agent 必须使用已安装的 lark-base / lark-shared 能力或 `lark-cli base +...` reference。
- 插件不打包 lark skills。
- 文档必须说明 `lark-cli` 授权、字段检查、批量写入上限和安全约束。

理由：CursorKit 里已有飞书相关能力，TLS 插件只消费它，不复制它。

### Decision 5: 验证分两层

实现后必须运行：

- `python3 plugins/tls-traffic-suite/skills/tls-route-traffic-compare/scripts/test_tls_route_traffic.py`
- `node scripts/validate-template.mjs`

必要时再补充一次命令/文档路径检查，确认 `SKILL.md` 示例里的脚本路径已从个人 `.agents/skills/...` 改成插件相对路径或说明清楚。

理由：Python 测试保证迁移后核心能力不坏，模板校验保证插件能被市场识别。

## Risks / Trade-offs

- [Risk] 文档中保留个人目录路径，安装后用户按示例执行会失败。  
  Mitigation: 迁移时统一检查 `SKILL.md` 和 references 中的脚本路径，改成插件内相对路径或命令入口表达。

- [Risk] 飞书 Base 依赖描述不清，用户以为安装 TLS 插件就自带 lark 能力。  
  Mitigation: 在 plugin README 和 `base-output.md` 明确 `lark-cli` / lark-base 是外部依赖。

- [Risk] 误把 `tmp/` 运行结果打包进插件，泄露生产流量样本。  
  Mitigation: tasks 中明确排除 `tmp/`，实现后用文件列表检查。

- [Risk] 根 README 与 marketplace 清单继续不一致。  
  Mitigation: 本变更同时更新 README 当前插件列表，并以 marketplace 为准补齐已有插件描述。

- [Risk] 独立插件增加一个安装项，用户可能不知道与 `go-cutover-suite` 的关系。  
  Mitigation: README 中说明 TLS 插件可独立使用，也可作为切流验收辅助能力与 Go cutover 配合。

## Migration Plan

1. 创建 `plugins/tls-traffic-suite/` 插件目录和 `.cursor-plugin/plugin.json`。
2. 迁移 skill 文件，排除 `tmp/`。
3. 新增 `/tls-route-traffic-compare` command。
4. 修正插件内文档路径和外部依赖描述。
5. 更新 `.cursor-plugin/marketplace.json` 和根 README。
6. 运行 Python 单测和插件模板校验。

Rollback strategy: 如果插件校验或迁移测试失败，删除 `plugins/tls-traffic-suite/`，移除 marketplace 和 README 中的新条目，即可回到当前状态；个人 skill 不受影响。

## Open Questions

- 是否需要给 `tls-traffic-suite` 增加专属 logo。第一版可以不加，沿用无 logo 插件模式；后续如果市场展示需要再补。
