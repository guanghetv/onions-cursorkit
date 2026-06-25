---
name: onion-tweak
description: 针对单点轻量体验或行为调整启动 Onion SDD light change 流程。
---

# /onion-tweak

用于处理 Tier 1 轻量调整：单页面、单组件、单流程中的小范围行为或体验变化。允许有少量设计判断，但不应跨多个模块或改变核心契约。

## 执行顺序

1. 读取 `skills/tier-triage/SKILL.md`，判断是否属于 Tier 1。
2. 如只缺一个范围信息，可向用户做一次简短确认；确认后继续。
3. 若出现跨模块、接口契约、权限、安全、资金、复杂状态流等红线，升级到 `/onion-plan`。
4. 读取 `skills/light-change/SKILL.md`，按 light change 模板产出或更新 `openspec/changes/<change-id>/`。
5. 完成实现后执行定向验证，必要时补充小范围回归点。

## 约束

- Phase 0 只承诺 slash command 触发。
- 不照搬其他插件的完整流程；如需升级，进入 onion 自有完整 SDD 路径。
- 不设置全仓扫描硬约束，优先读取直接相关的规格、代码、测试和运行证据。
- 不自动执行 `openspec archive`，不自动提交 git commit。
