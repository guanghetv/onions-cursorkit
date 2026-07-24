# onion-sdd monorepo repo-root 解析与规范交付物门禁

## Goal

为 onion-sdd 补齐 monorepo repo-root 解析与规范类交付物门禁，防止两类回归：
1. 子包 cwd 看不到外层 `.trellis/`，导致 onion-sdd 误判「无 Trellis」、状态/产物落错位置。
2. 编码规范被当成 change 产品交付物落进子包 `docs/`，绕过 Phase 3.3 spec 积累。

## Background

在 onion-monitor（pnpm monorepo，`.trellis/` 与 `openspec/` 在外层根，子包 `onion-monitor-view` 无独立 `.trellis`）中跑 Onion SDD Tier 2 change 时，AI 工作目录在子包，`onion_state.py --repo-root .` 默认取子包为根，看不到外层 `.trellis/`，于是把「落规范」写进 `onion-monitor-view/docs/frontend-module-conventions.md`，而非外层 `.trellis/spec/onion-monitor-view/frontend/`。根因：流程模型正确（trellis-update-spec 路由「Established a convention → spec」），但 monorepo repo-root 解析无规则、规范路由只在 finish 期 skill 而规划期无门禁。

## Requirements

### R1: repo-root 自动解析（向后兼容）
- onion_state.py 在未显式传 `--repo-root` 且无 `ONION_SDD_ROOT` 时，从 cwd 向上查找最近的含 `.trellis/` 的目录作为 repo-root；找不到则回退 cwd（保持现行独立模式）。
- 显式 `--repo-root` 与 `ONION_SDD_ROOT` 优先级不变。
- `.onion-sdd/current.json` 与 `.gitignore` 更新随 repo-root 落到含 `.trellis/` 的外层根，而非子包目录。

### R2: 规范类交付物门禁（WARN + 规划期硬规则）
- openspec-change 编写 tasks.md 时，硬规则：tasks.md 只装产品/验收交付物；编码约定/规范属 Phase 3.3 spec 积累，目标 `.trellis/spec/<package>/<layer>/`，禁止落 `docs/`。
- finish_check.py 归档预检新增 WARN（非 fatal）：若 change 在 `docs/**` 下新建/改了名字形如 convention/guideline/standard/规范/约定 的文件，提示应迁入 `.trellis/spec/`。WARN 不改变 exit code。

### R3: 发版 0.1.2
- CHANGELOG 新增 `[0.1.2]` 小节；plugin.json version 0.1.1 → 0.1.2。

## Acceptance Criteria

- [ ] 从子包 cwd（本地无 `.trellis/`、外层有）跑 `onion_state.py get`，repo-root 解析到外层根，读到外层 `.onion-sdd/current.json`（而非子包不存在的 current.json 的 idle 兜底）。
- [ ] 从子包 cwd 跑 `onion_state.py set --idle`，写入外层 `.onion-sdd/current.json` 且 `.gitignore` 更新落在外层根。
- [ ] `.trellis/` 在 cwd 的仓库：行为不变（现有用法/测试通过）。
- [ ] 无 `.trellis/` 的仓库：行为不变（回退 cwd，独立模式）。
- [ ] finish_check.py 对创建了 `docs/frontend-conventions.md` 的 change 输出 WARN 并点名 `.trellis/spec/`，exit code 不变。
- [ ] finish_check.py 对无此类文件的 change 不产生新 WARN。
- [ ] openspec-change/SKILL.md 含「规范属 Phase 3.3、落 `.trellis/spec/`、不进 tasks.md/docs」规则。
- [ ] CHANGELOG 与 plugin.json 版本一致为 0.1.2。

## Out of Scope

- 不改 Trellis 源码或 `.trellis/scripts/**`。
- 不把 finish_check 的 WARN 升级为 HARD FAIL（留待后续视误报率再定）。
- 不改 onion-sdd 之外插件的代码。
