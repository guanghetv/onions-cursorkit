# 实施计划

## 清单

- [x] 新增 `skills/full-change/SKILL.md`，沉淀 Tier 2+ 完整流程编排。
- [x] 新增 `skills/openspec-change/SKILL.md`，沉淀完整 OpenSpec 落盘模板。
- [x] 新增 `skills/external-spec/SKILL.md`，沉淀后端/QA/外部 spec 接入与差异分析。
- [x] 新增 `skills/verify-change/SKILL.md`，沉淀 E2E/验收报告门禁。
- [x] 更新 `commands/onion-plan.md`，让 Tier 2+ 明确调用 onion 自有完整流程 skills。
- [x] 更新 `commands/onion-continue.md`，补齐完整流程阶段恢复规则。
- [x] 更新 `commands/onion-finish.md`，补齐 Tier 2+ E2E/验收门禁。
- [x] 更新 `rules/onion-sdd.mdc`，同时覆盖轻量路径与完整路径门禁。
- [x] 更新 `README.md` 和 `DESIGN-SUPPLEMENT.md`，说明基座能力已补齐以及 Trellis adapter 后续接入边界。
- [x] 运行验证命令，记录偏离项。

## 验证结果

- `find plugins/onion-sdd -type f | sort`：通过，新增 4 个完整流程 skill。
- `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json`：通过。
- frontmatter 抽检：通过，commands / skills / rules 均有必需字段。
- `rg -n "full-change|openspec-change|external-spec|verify-change" plugins/onion-sdd`：通过，命令、README、规则、补充设计均引用新 skill。
- `rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd`：无命中。
- `rg -n "/fe-sdd|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd`：无命中。
- `node scripts/validate-template.mjs`：通过；仅输出既有插件未配置 hooks/mcp 的非阻塞 warnings。

## 文件责任

| 文件 | 责任 |
| --- | --- |
| `skills/full-change/SKILL.md` | 完整流程总编排、阶段推断、需求接入、tasks/TDD 纪律 |
| `skills/openspec-change/SKILL.md` | proposal/specs/tasks 模板与写入流程 |
| `skills/external-spec/SKILL.md` | 外部后端/QA/spec 文档读取、落盘、差异分析 |
| `skills/verify-change/SKILL.md` | 验证清单、浏览器自动化确认、`e2e-report.md` 结构与结论 |
| `commands/onion-plan.md` | Tier 路由入口 |
| `commands/onion-continue.md` | 恢复入口 |
| `commands/onion-finish.md` | 收束入口 |
| `rules/onion-sdd.mdc` | 写入与阶段门禁 |
| `README.md` | 用户理解入口 |
| `DESIGN-SUPPLEMENT.md` | 技术补充与后续 adapter 衔接 |

## 验证命令

```bash
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
rg -n "name:|description:" plugins/onion-sdd/commands plugins/onion-sdd/skills plugins/onion-sdd/rules
rg -n "full-change|openspec-change|external-spec|verify-change" plugins/onion-sdd
rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd && echo "FAIL: heavy scan constraint found" || echo "OK: no hard full-scan constraint"
rg -n "/fe-sdd|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd && echo "FAIL: legacy runtime dependency found" || echo "OK: no legacy runtime dependency"
git diff -- plugins/onion-sdd
```

## Review Gate

开始实现前，需要用户确认：

- 本子任务先补齐 `onion-sdd` 基座能力。
- Trellis adapter 不在本子任务内实现。
- 新增 skill 名称采用 `full-change`、`openspec-change`、`external-spec`、`verify-change`。
