---
name: "/onion-systematic-debugging"
id: "onion-systematic-debugging"
category: "Onion"
description: "洋葱全链路排查。核心 GitNexus 定位仓库与代码；运行时 MCP 按需加载且须唯一 env。"
---

# /onion-systematic-debugging

显式启动洋葱全链路排查。加载并严格遵循 `onion-systematic-debugging` skill：

- 项目内源：`skills/onion-systematic-debugging/SKILL.md`
- 个人安装：`~/.cursor/skills/onion-systematic-debugging/SKILL.md`
- 必读 `references/gitnexus.md`；按需 `onion-gate.md`、`intake.md`、`symptom-routes.md`、`layers.md`

**输入**：事故描述（服务、接口、现象）。env 可后补。无参数先问服务/路由/现象，禁止为代码检索猜 env。

```
$ARGUMENTS
```

## 必须执行

1. 洋葱门禁：非洋葱则结束，禁止公司 MCP。
2. **代码优先**：GitNexus `list_repos` → `query` / `context` / `route_map`；按 `GN-*` 证据卡交付。证据后给出代码侧置信度与初步结论。`high` + `stop` 即可收束。
3. **运行时按需**：仅当评估为 `need_runtime` 或用户要现网数据时钉死唯一 `env`，只开需要的 metrics/trace/logs/archery；禁止跨 env 聚合、禁止四域空扫。
4. 交付：代码证据 + 代码侧评估为主；运行时表仅已加载时出现。
5. 不写「根因是」、不改代码、不走 Archery 工单、不 `curl` 平台、不 `rename`/`group_sync`。
