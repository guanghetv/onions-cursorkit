---
name: onsf-fix
description: 针对已确认、低风险的小修复启动 Onion SDD mini change 流程。
---

# /onsf-fix

用于处理 Tier 0+ 小修复：文案、样式、常量、低风险配置、局部兜底逻辑等已经明确且影响很小的变更。若请求命中线上 P0/P1 紧急故障、修复明确且预计 30 分钟内完成，可标记为 Tier 0++，走先修后补。

## 执行顺序

1. 读取 `skills/tier-triage/SKILL.md`，确认请求仍属于 Tier 0+ 或 Tier 0++。
2. **运行态 / 0++ 逾期扫描**：`python3 <onion-sdd>/scripts/onion_state.py --repo-root . get`。若发现其它 change 的 `tier0pp_openspec_pending` 已逾期，输出硬提示（补档或 `## 带债项`），再继续本请求。
3. 若发现升级红线，停止 fix 流程，并建议用户改用 `/onsf-plan`。
4. Tier 0++：先完成修复与验证；**必须**调用：
   ```bash
   python3 <onion-sdd>/scripts/onion_state.py --repo-root . mark-tier0pp --change-id <id>
   ```
   再在 24 小时内补齐 mini OpenSpec，然后 `clear-tier0pp-pending`。
5. 读取 `skills/mini-change/SKILL.md`，按 mini change 模板产出或更新 `openspec/changes/<change-id>/`。
6. 阶段切换（openspec / implement / verify）后**必须** `onion_state.py set --change-id --tier --phase --last-action`。
7. 只读取和变更直接相关的文件、规格、测试与上下文。
8. 完成实现后执行定向验证，并把验证命令、结果和未覆盖风险写回产物或最终回复。

## 约束

- 以 slash command 显式触发；不做完整 brainstorming，不默认进入完整 SDD 路径。
- 不要求全仓上下文，按需读取即可。
- 阶段切换必须调用 `onion_state.py`；输出核对 `primary_write`。
- 完成并验证通过后调用 `/onsf-finish`（其内先跑 `finish_check.py`）自动归档；不自动提交 git commit。
