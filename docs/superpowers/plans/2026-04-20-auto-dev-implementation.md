# /auto-dev 小需求自动开发技能 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `plugins/common/skills/` 下新增 `/auto-dev` 技能，支持“强制工作区扫描 -> 一次人工确认 -> 后台 Agent 全自动执行 -> AI CodeReview 自动修复 -> 自动创建到 develop 的 MR”的小需求流水线规范。

**Architecture:** 采用“主技能 + 参考文档”结构。`SKILL.md` 负责入口、门禁和状态机，`references/*.md` 负责细化执行步骤、示例、故障排查与 MR 描述模板。通过复用已有 `create-feature-branch` 与 `aicr-local` 约束，减少重复定义并保证行为一致。

**Tech Stack:** Markdown 技能文档、Cursor Skill Frontmatter、Git、Node 校验脚本（`scripts/validate-template.mjs`）、ripgrep 文本断言。

---

## 文件结构与职责映射

- `plugins/common/skills/auto-dev/SKILL.md`：技能入口、适用场景、状态机、关键 MUST/MUST NOT。
- `plugins/common/skills/auto-dev/references/DETAILED_STEPS.md`：阶段化执行细则（扫描、确认、后台执行、CR 循环、MR）。
- `plugins/common/skills/auto-dev/references/EXAMPLES.md`：单项目/多项目/零命中/阻断恢复示例。
- `plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md`：常见失败场景、排障命令、恢复动作。
- `plugins/common/skills/auto-dev/references/MR_TEMPLATE.md`：MR 描述结构模板与字段解释。
- `plugins/common/.cursor-plugin/plugin.json`：更新描述，纳入 `/auto-dev` 能力说明。

---

### Task 1: 搭建 auto-dev 技能骨架

**Files:**
- Create: `plugins/common/skills/auto-dev/SKILL.md`
- Create: `plugins/common/skills/auto-dev/references/DETAILED_STEPS.md`
- Create: `plugins/common/skills/auto-dev/references/EXAMPLES.md`
- Create: `plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md`
- Create: `plugins/common/skills/auto-dev/references/MR_TEMPLATE.md`
- Test: `plugins/common/skills/auto-dev/SKILL.md`

- [ ] **Step 1: 写最小失败断言（目录与文件应不存在）**

Run:
```bash
test ! -f plugins/common/skills/auto-dev/SKILL.md
```
Expected: exit code `0`（表示当前文件不存在）。

- [ ] **Step 2: 创建目录与占位文件（最小实现）**

```bash
mkdir -p plugins/common/skills/auto-dev/references
cat > plugins/common/skills/auto-dev/SKILL.md <<'EOF'
---
name: auto-dev
description: 小需求自动开发技能。触发后强制扫描工作区并确认范围，确认后后台自动执行开发、CR、自修与MR创建。
---

# /auto-dev

详见 references 文档。
EOF

cat > plugins/common/skills/auto-dev/references/DETAILED_STEPS.md <<'EOF'
# 详细步骤（占位）
EOF

cat > plugins/common/skills/auto-dev/references/EXAMPLES.md <<'EOF'
# 示例（占位）
EOF

cat > plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md <<'EOF'
# 故障排查（占位）
EOF

cat > plugins/common/skills/auto-dev/references/MR_TEMPLATE.md <<'EOF'
# MR 模板（占位）
EOF
```

- [ ] **Step 3: 运行存在性校验（让“失败断言”转为通过）**

Run:
```bash
test -f plugins/common/skills/auto-dev/SKILL.md && \
test -f plugins/common/skills/auto-dev/references/DETAILED_STEPS.md && \
test -f plugins/common/skills/auto-dev/references/EXAMPLES.md && \
test -f plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md && \
test -f plugins/common/skills/auto-dev/references/MR_TEMPLATE.md
```
Expected: exit code `0`。

- [ ] **Step 4: Commit**

```bash
git add plugins/common/skills/auto-dev
git commit -m "feat: scaffold auto-dev skill structure"
```

---

### Task 2: 完成 SKILL.md 主流程与门禁约束

**Files:**
- Modify: `plugins/common/skills/auto-dev/SKILL.md`
- Test: `plugins/common/skills/auto-dev/SKILL.md`

- [ ] **Step 1: 写失败断言（关键语句尚不存在）**

Run:
```bash
rg "/auto-dev" plugins/common/skills/auto-dev/SKILL.md && \
rg "目标分支固定为 `develop`" plugins/common/skills/auto-dev/SKILL.md
```
Expected: 第二个 `rg` 失败（exit code 非 0）。

- [ ] **Step 2: 写入完整主技能内容（最小满足 spec）**

```markdown
---
name: auto-dev
description: 小需求自动开发技能。强制扫描工作区并一次确认范围，随后后台 Agent 自动完成开发、AI CodeReview、自动修复、提交与创建 MR（target=develop）。
---

# /auto-dev 小需求自动开发

## 何时使用
- 文案改动、新增提示、轻逻辑调整等小需求
- 单项目或多项目（2-3 项）联动小改

## 强约束（MUST）
- 必须先执行工作区扫描，再允许改动
- 命中项目为 0 时必须阻断，不允许硬改
- 仅允许一次人工确认（确认命中范围）
- 确认后必须切换后台 Agent 执行，不占用当前编辑器
- 每个项目必须独立创建 MR，目标分支固定为 `develop`
- AI CodeReview 严重问题必须自动修复并复审，最多 3 轮

## 主状态机
`SCANNED -> CONFIRMED -> BRANCH_CREATED -> CHANGES_APPLIED -> LOCAL_VERIFY_PASSED -> CR_LOOP_PASSED -> COMMITTED -> MR_CREATED -> DONE`

## 执行入口
1. 解析输入（飞书链接/文本）
2. 强制扫描工作区并产生命中证据
3. 展示命中项目并等待一次确认
4. 生成 run-id，转后台执行
5. 聚合输出 MR 结果

## 参考文档
- `references/DETAILED_STEPS.md`
- `references/EXAMPLES.md`
- `references/TROUBLESHOOTING.md`
- `references/MR_TEMPLATE.md`
```

- [ ] **Step 3: 校验关键门禁文案存在**

Run:
```bash
rg "命中项目为 0 时必须阻断" plugins/common/skills/auto-dev/SKILL.md && \
rg "确认后必须切换后台 Agent 执行" plugins/common/skills/auto-dev/SKILL.md && \
rg "目标分支固定为 `develop`" plugins/common/skills/auto-dev/SKILL.md && \
rg "最多 3 轮" plugins/common/skills/auto-dev/SKILL.md
```
Expected: 所有 `rg` 命中并返回 exit code `0`。

- [ ] **Step 4: Commit**

```bash
git add plugins/common/skills/auto-dev/SKILL.md
git commit -m "feat: define auto-dev workflow and hard gates"
```

---

### Task 3: 编写 DETAILED_STEPS.md（阶段化执行细则）

**Files:**
- Modify: `plugins/common/skills/auto-dev/references/DETAILED_STEPS.md`
- Test: `plugins/common/skills/auto-dev/references/DETAILED_STEPS.md`

- [ ] **Step 1: 写失败断言（阶段标题尚不完整）**

Run:
```bash
rg "^## 步骤1：强制扫描当前工作区" plugins/common/skills/auto-dev/references/DETAILED_STEPS.md
```
Expected: 未命中（exit code 非 0）。

- [ ] **Step 2: 写入详细步骤**

```markdown
# 详细步骤说明

## 步骤1：强制扫描当前工作区
- 扫描工作区所有注册项目
- 输出命中项目与证据
- 若命中数为 0：立即阻断并提示补充需求信息

## 步骤2：一次人工确认范围
- 展示命中项目列表
- 支持“确认全部”或“排除部分后确认”
- 确认后冻结项目范围

## 步骤3：后台任务接管
- 生成 run-id
- 切换至 Cursor CLI Agent/云 Agent 执行
- 前台仅保留状态查询能力

## 步骤4：每项目自动执行
- 复用 create-feature-branch 建分支规则
- 执行小需求改动与最小验证集
- 调用 aicr-local 做 CR

## 步骤5：CR 自动修复闭环
- Critical 必须修复并复审
- 最多 3 轮 review->fix->verify->re-review
- 超过 3 轮仍失败则 BLOCKED 并通知人工

## 步骤6：自动创建 MR
- 每项目创建 1 个 MR
- target branch 必须为 develop
- 使用 MR_TEMPLATE.md 生成结构化描述

## 步骤7：收尾与汇总
- 输出项目级 MR 链接与摘要
- 输出失败项目阻断点与建议动作
```

- [ ] **Step 3: 校验阶段完整性**

Run:
```bash
rg "^## 步骤[1-7]：" plugins/common/skills/auto-dev/references/DETAILED_STEPS.md -c
```
Expected: 输出 `7`。

- [ ] **Step 4: Commit**

```bash
git add plugins/common/skills/auto-dev/references/DETAILED_STEPS.md
git commit -m "docs: add auto-dev detailed execution steps"
```

---

### Task 4: 编写 EXAMPLES 与 TROUBLESHOOTING 文档

**Files:**
- Modify: `plugins/common/skills/auto-dev/references/EXAMPLES.md`
- Modify: `plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md`
- Test: `plugins/common/skills/auto-dev/references/EXAMPLES.md`
- Test: `plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md`

- [ ] **Step 1: 写失败断言（示例类别尚不完整）**

Run:
```bash
rg "单项目命中示例" plugins/common/skills/auto-dev/references/EXAMPLES.md && \
rg "零命中阻断示例" plugins/common/skills/auto-dev/references/EXAMPLES.md
```
Expected: 至少一个未命中（exit code 非 0）。

- [ ] **Step 2: 写入 EXAMPLES.md**

```markdown
# 使用示例

## 单项目命中示例
输入：`/auto-dev 修复登录页提示文案`
输出：命中 1 个项目 -> 人工确认 -> 后台执行 -> 返回 1 个 MR

## 多项目命中示例
输入：`/auto-dev 更新活动弹窗提示语（飞书链接）`
输出：命中 3 个项目 -> 人工确认 -> 并行后台执行 -> 返回 3 个 MR

## 零命中阻断示例
输入：`/auto-dev 优化某未知模块`
输出：命中 0 项目 -> 阻断 -> 要求补充关键词或手动指定项目

## CR 3 轮失败示例
输出：第 3 轮后仍有 Critical -> BLOCKED -> 通知人工接管
```

- [ ] **Step 3: 写入 TROUBLESHOOTING.md**

```markdown
# 故障排查

## 问题1：未扫描到匹配项目
- 检查需求关键词是否过于抽象
- 建议补充页面名/模块名/文案片段

## 问题2：后台任务无法启动
- 检查 Agent 凭证与运行权限
- 检查 run-id 是否正确生成

## 问题3：MR 创建失败（target 非 develop）
- 检查 MR API 参数
- 强制修正目标分支为 develop 后重试

## 问题4：CR 自动修复超过 3 轮
- 查看事件日志定位未收敛原因
- 人工接管后使用 resume 从 checkpoint 续跑
```

- [ ] **Step 4: 校验四类示例与四类故障都存在**

Run:
```bash
rg "^## " plugins/common/skills/auto-dev/references/EXAMPLES.md -c && \
rg "^## 问题[1-4]：" plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md -c
```
Expected: 第一条命令输出 `4`，第二条命令输出 `4`。

- [ ] **Step 5: Commit**

```bash
git add plugins/common/skills/auto-dev/references/EXAMPLES.md plugins/common/skills/auto-dev/references/TROUBLESHOOTING.md
git commit -m "docs: add auto-dev examples and troubleshooting"
```

---

### Task 5: 编写 MR_TEMPLATE 并接入主技能引用

**Files:**
- Modify: `plugins/common/skills/auto-dev/references/MR_TEMPLATE.md`
- Modify: `plugins/common/skills/auto-dev/SKILL.md`
- Test: `plugins/common/skills/auto-dev/references/MR_TEMPLATE.md`

- [ ] **Step 1: 写失败断言（MR 模板关键章节不存在）**

Run:
```bash
rg "## 需求背景" plugins/common/skills/auto-dev/references/MR_TEMPLATE.md && \
rg "## AI CodeReview 结果" plugins/common/skills/auto-dev/references/MR_TEMPLATE.md
```
Expected: 至少一个未命中（exit code 非 0）。

- [ ] **Step 2: 写入 MR_TEMPLATE.md（结构化描述模板）**

```markdown
# MR 描述模板

## 需求背景
- 来源：
- 目标：
- 约束：

## 改动内容
- 模块/文件：
- 改动说明：
- 改动原因：

## 影响范围
- 页面/接口/配置：

## 验证结果
- lint：
- typecheck：
- test：

## AI CodeReview 结果
- 轮次：
- 自动修复摘要：
- 遗留 Minor：

## 风险与回滚
- 风险：
- 回滚方案：

## 关联信息
- 需求 ID：
- run-id：
- 关联 MR：
```

- [ ] **Step 3: 在 SKILL.md 增加模板强制引用语句**

```markdown
## MR 描述要求（MUST）
- 创建 MR 时必须按 `references/MR_TEMPLATE.md` 生成完整描述
```

- [ ] **Step 4: 校验模板与引用生效**

Run:
```bash
rg "^## " plugins/common/skills/auto-dev/references/MR_TEMPLATE.md -c && \
rg "MR_TEMPLATE.md" plugins/common/skills/auto-dev/SKILL.md
```
Expected: 第一条命令输出 `7`，第二条命令命中并返回 exit code `0`。

- [ ] **Step 5: Commit**

```bash
git add plugins/common/skills/auto-dev/references/MR_TEMPLATE.md plugins/common/skills/auto-dev/SKILL.md
git commit -m "docs: define auto-dev MR description template"
```

---

### Task 6: 更新 common 插件描述并做仓库校验

**Files:**
- Modify: `plugins/common/.cursor-plugin/plugin.json`
- Test: `plugins/common/.cursor-plugin/plugin.json`

- [ ] **Step 1: 写失败断言（描述中无 auto-dev 关键词）**

Run:
```bash
rg "auto-dev" plugins/common/.cursor-plugin/plugin.json
```
Expected: 未命中（exit code 非 0）。

- [ ] **Step 2: 修改插件描述（最小改动）**

```json
{
  "description": "文档语言规则、/cr 代码审查命令，以及本地 AI 审查、飞书分支创建与 /auto-dev 小需求自动开发等通用技能。"
}
```

- [ ] **Step 3: 运行结构与模板校验**

Run:
```bash
node scripts/validate-template.mjs
```
Expected: exit code `0`，无错误输出。

- [ ] **Step 4: 运行关键文本断言**

Run:
```bash
rg "^name: auto-dev" plugins/common/skills/auto-dev/SKILL.md && \
rg "目标分支固定为 `develop`" plugins/common/skills/auto-dev/SKILL.md && \
rg "最多 3 轮" plugins/common/skills/auto-dev/SKILL.md && \
rg "auto-dev" plugins/common/.cursor-plugin/plugin.json
```
Expected: 所有命中，exit code `0`。

- [ ] **Step 5: Commit**

```bash
git add plugins/common/.cursor-plugin/plugin.json plugins/common/skills/auto-dev
git commit -m "feat: add auto-dev skill docs and plugin metadata"
```

---

### Task 7: 回归验证与交付说明

**Files:**
- Modify: `docs/superpowers/specs/2026-04-20-auto-dev-design.md`（仅在需要补充引用时）
- Test: `plugins/common/skills/auto-dev/SKILL.md`

- [ ] **Step 1: 端到端演练清单（文本级）**

Run:
```bash
rg "强制扫描" plugins/common/skills/auto-dev/SKILL.md && \
rg "命中项目为 0 时必须阻断" plugins/common/skills/auto-dev/SKILL.md && \
rg "后台 Agent" plugins/common/skills/auto-dev/SKILL.md && \
rg "MR_TEMPLATE.md" plugins/common/skills/auto-dev/SKILL.md
```
Expected: 全部命中。

- [ ] **Step 2: 变更摘要检查**

Run:
```bash
git status --short && git diff -- plugins/common/skills/auto-dev plugins/common/.cursor-plugin/plugin.json
```
Expected: 仅出现本计划定义的文件改动。

- [ ] **Step 3: 最终 Commit（如 Task1-6 已各自提交则跳过）**

```bash
git add plugins/common/skills/auto-dev plugins/common/.cursor-plugin/plugin.json
git commit -m "docs: finalize auto-dev skill for background automation workflow"
```

---

## Self-Review Checklist（执行前再次核对）

1. **Spec coverage:** 已覆盖扫描门禁、一次确认、后台执行、CR 3 轮自修、develop MR、结构化 MR 描述。
2. **Placeholder scan:** 全文禁止 `TODO`/`TBD`/“后续补充”。
3. **Type consistency:** 术语统一使用 `/auto-dev`、`run-id`、`BLOCKED`、`develop`、`Critical/Major/Minor`。

