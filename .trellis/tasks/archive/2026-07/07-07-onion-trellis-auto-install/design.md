# Design: onion-sdd 检测缺失 Trellis 时交互式安装初始化

## 触发与检测

新增位置：`plugins/onion-sdd/skills/full-change/SKILL.md`「需求接入」章节之前，插入新小节「Trellis 使用检查」，只在本技能（Tier 2+/3）被触发时执行一次：

```
1. 检测 `.trellis/scripts/add_session.py` 是否存在。
   - 存在 → Trellis 可用，维持现状（不改动本次任务范围外的"是否创建 task"逻辑）。
   - 不存在 → 进入安装询问。
2. 安装询问（仅手动入口；/onsf-auto 不触发，见下方「auto 边界」）：
   向用户说明"当前项目未安装 Trellis，其 journal/spec 积累/task 能力可增强 onion-sdd 记忆"，
   询问是否现在安装并初始化。
3. 用户同意：
   a. 询问或确认开发者标识 `-u <name>`（优先复用 git 全局 `user.name`/已知身份，找不到则问用户）。
   b. 确定平台：默认只用当前 Agent 所在平台（如当前会话运行在 Cursor 中就是 `--cursor`），
      追加一句"是否要顺带初始化 Claude / Codex 等其它平台"，用户可多选或跳过。
   c. 先探测 `trellis --version`：
      - 成功（CLI 已全局安装，只是本项目未 `trellis init`）→ 跳过安装，直接进入 `trellis init`
      - 失败/命令不存在 → `npm install -g @mindfoldhq/trellis`（需要 full_network 权限）→ `trellis --version` 确认安装成功
      - 最后执行 `trellis init -u <name> <平台 flag 组合>`
   d. 执行 gitignore 更新（见下节）。
   e. 完成后继续原 Tier 2+/3 流程（相当于 Trellis 从「不可用」变为「可用」，后续步骤按现状协议走）。
4. 用户拒绝，或安装/初始化失败：
   - 报告失败原因（网络、权限、CLI 报错内容）。
   - 不阻塞：按现有「Trellis 不可用」降级路径继续 Tier 2+/3（`full-change/SKILL.md` 中各阶段已有的
     "如果 Trellis 不可用，回退到 XXX" 分支，本次不改）。
```

## auto 边界

`plugins/onion-sdd/commands/onsf-auto.md` 的「Trellis 边界」小节追加一句：

> 本次新增的"Trellis 缺失时询问是否安装"仅适用于手动入口（`/onsf-plan` 等触发的 `full-change`）；`/onsf-auto` 无交互场景不触发该询问，Trellis 不可用时继续按现状静默降级（不在停止条件中新增"是否安装 Trellis"）。

不修改 auto-flow 的停止条件列表本身（“需要创建/启动/归档 Trellis task”已经涵盖“需要用户交互决定 Trellis 相关事项”这一类，无需为“安装”单列一条）。

## gitignore 更新范围（已按用户反馈简化为整目录忽略）

> 决策变更记录：最初设计过"只忽略 Trellis 生成子路径、不整目录忽略"的精确方案，动机是本仓库 `.cursor/commands/opsx-*.md`（第三方 OpenSpec 插件的手写文件，没有独立源头，直接放在共享目录下）需要 `git add -f` 才能追踪的问题。但该混用场景是本仓库特有的（第三方插件把手写文件直接放进平台共享目录），不是通用新项目会遇到的情况；且 gitignore 规则本身不会取消已追踪文件的追踪，不存在"误伤"风险。综合考虑简单性和本仓库已验证可行的现状写法，改回整目录忽略。

为**本次实际初始化的平台**追加整目录忽略：

| 平台 | 追加到 `.gitignore` 的条目 |
|------|---------------------------|
| `--cursor` | `.cursor/` |
| `--claude` | `.claude/` |
| `--codex` | `.codex/` |

规则：
- 每条追加前检查 `.gitignore` 是否已存在等价条目，已存在则跳过，不重复添加。
- 只追加"本次实际执行 `trellis init` 时所选平台"对应的条目；未选中的平台不动。
- 不删除、不重写用户已有的 `.gitignore` 内容；只在文件末尾追加新增部分，追加前加一行注释 `# Trellis / AI 平台生成文件（本地初始化产物，无需同步到仓库）`。
- 不处理 `.agents/skills/`（始终追踪，跨平台真相源，不在忽略范围）。
- 如果该平台目录下已存在被 git 追踪的文件（例如其它插件手写并直接提交在同一目录下的文件），忽略规则不会取消其追踪，但提示用户后续该目录下新文件需要 `git add -f` 才能追踪。

## 文档同步范围

- `plugins/onion-sdd/USAGE.md`、`plugins/onion-sdd/docs/feishu-wiki-onion-sdd-usage.md`：8.2 节后补充"Tier 2+/3 首次触发且 Trellis 未安装时，Agent 会主动询问是否安装并初始化"的说明，以及 gitignore 整目录追加行为。
- `plugins/onion-sdd/README.md`：如含相同能力对照表，同步补充一行。
- `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`：如有「Trellis 可用性检测」相关描述，补充"检测到不可用时的交互式安装"分支。

## 兼容性与回滚

- 新增内容集中在 `full-change/SKILL.md` 一个新小节 + `onsf-auto.md` 一句边界说明 + 文档；不改动 `.trellis/scripts/**`、Trellis CLI、`.trellis/.runtime/**`。
- 回滚：`git revert` 对应 commit 即可，不涉及数据迁移。
- 已经装好 Trellis 的项目（如本仓库）不会触发新逻辑（第 1 步检测到可用直接跳过），因此本次改动对当前仓库运行时行为无影响，纯粹是面向"尚未安装 Trellis 的新项目"的能力。
