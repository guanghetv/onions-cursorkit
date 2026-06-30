# 技术设计

## 架构

在 `plugins/onion-sdd/` 内补齐 onion 自有完整流程层：

```text
plugins/onion-sdd/
  commands/
    onion-plan.md          # Tier 路由 + 完整流程入口
    onion-continue.md      # 阶段恢复
    onion-finish.md        # 验收与归档判断
  skills/
    tier-triage/           # 既有：分级
    mini-change/           # 既有：Tier 0+
    light-change/          # 既有：Tier 1
    full-change/           # 新增：Tier 2+ 完整流程编排
    openspec-change/       # 新增：完整 OpenSpec 落盘
    external-spec/         # 新增：后端/QA/外部 spec 接入
    verify-change/         # 新增：E2E / 验收报告
  rules/
    onion-sdd.mdc          # 轻量 + 完整流程门禁
```

## 能力映射

| 原 fe-specflow 能力 | onion-sdd 目标能力 | 说明 |
| --- | --- | --- |
| `dev-workflow` | `full-change` | 通用化阶段编排，不再绑定前端专用命名 |
| `design-to-opsx` | `openspec-change` | 完整 OpenSpec 产物落盘 |
| `pull-spec` | `external-spec` | 后端、QA、GitLab、workspace 文件和粘贴内容接入 |
| `e2e-verify` | `verify-change` | E2E 清单、浏览器验证、`e2e-report.md` 门禁 |

## 流程

### Tier 0+/1

保持 Phase 0 轻量路径：

```text
/onion-hotfix → tier-triage → mini-change → 定向验证 → onion-finish
/onion-tweak  → tier-triage → light-change → 定向验证 → onion-finish
```

### Tier 2+

补齐完整路径：

```text
/onion-plan
  → tier-triage
  → full-change
  → openspec-change
  → tasks.md / TDD 任务规划
  → external-spec（按事件触发）
  → verify-change
  → onion-finish
```

## 状态恢复

`/onion-continue` 继续遵循 Phase 0 的读取优先级：

1. `.onion-sdd/current.json`
2. 用户指定 change-id
3. `openspec/changes/**` 产物推断

推断规则：

| 产物 | 阶段 |
| --- | --- |
| 无变更目录 | triage / plan |
| `proposal.md` + `specs/`，无 `tasks.md` | tasks |
| `tasks.md` 有未完成项 | implement |
| `tasks.md` 全部完成，无 `e2e-report.md` | verify 或等待外部 spec |
| 有 `backend-*.md` / `qa-*.md` | integration / verify |
| `e2e-report.md` 有通过结论 | finish |

## 文案与依赖

- 新增文档可以在迁移说明中提到 `fe-specflow`，但用户执行路径必须使用 onion 自有 skill 名称。
- 不复制 `fe-specflow` 的“全局扫描当前仓库”硬约束；改为“按需读取需求来源、OpenSpec 产物、用户指定范围、必要邻近代码和验证入口”。
- 保留“用户在终端执行 OpenSpec CLI，Agent 写 Markdown 内容”的分工。

## 验证设计

本子任务主要修改插件 Markdown/规则/JSON 示例，验证以结构和文本规则为主：

```bash
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
rg -n "name:|description:" plugins/onion-sdd/commands plugins/onion-sdd/skills plugins/onion-sdd/rules
rg -n "full-change|openspec-change|external-spec|verify-change" plugins/onion-sdd
rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd
rg -n "/fe-sdd|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd
```

## 回滚

本子任务只修改 `plugins/onion-sdd/` 与任务文档。回滚时恢复该目录相关文件即可；不影响 `.trellis/scripts/**`。
