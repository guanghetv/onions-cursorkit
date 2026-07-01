# onion-sdd 技术方案补充与完善

> 本文档是对 Onion SDD Phase 0 命令壳方案的补充。
> 聚焦 Phase 0 命令壳阶段需要进一步澄清的设计细节。
> Phase 1/2 相关内容仅给设计方向，不要求 Phase 0 实现。

---

## 一、Tier 边界判定清单（替代直觉判定）

当前基础方案中 Tier 0 vs 0+ vs 1 的判定容易依赖"影响用户行为""小交互"等模糊描述。以下给出可操作的判定清单。

### Tier 判定决策树（从 Tier 0 开始逐级判定）

```
Q1: 这个变更是否需要修改代码/配置/文档？
    否 → Tier 0（纯问答/排查/审阅）
    是 → 继续 Q2

Q2: 变更是否影响用户可感知的行为、产品语义、接口契约或数据结果？
    否 → 继续 Q2a
    是 → 继续 Q3

Q2a: 变更是否属于以下纯内部修正？
  - 类型标注修正（不影响运行时行为）
  - lint/格式化
  - 非用户可见的注释/日志格式
  - 纯重构（行为不变，有现有测试覆盖）
    是 → Tier 0（内部修正，不落 OpenSpec，commit message 说明验证即可）
    否 → 继续 Q2b

Q2b: 变更是否属于以下纯配置/文档变更？
  - CI/CD 配置
  - 环境变量（非用户可见）
  - README / 内部文档
  - .gitignore / .editorconfig
  - 依赖版本升级（无 breaking change）
    是 → Tier 0（同内部修正处理）
    否 → 继续 Q3（此时已确定至少影响用户行为）

Q3: 变更是否涉及任一升级红线？
  - 接口字段/错误码/数据模型变更
  - 状态机/权限/安全/支付/资金/审计
  - 跨模块（>1 个独立模块）或跨仓
  - 需求或验收标准不清晰，且不能通过一次简短确认解决
    是 → Tier 2+
    否 → 继续 Q4

Q4: 变更是否属于明确且低风险的修复？
  特征：问题已定位、修复方案唯一且确定、验证路径清晰、预计改动 ≤3 个文件
    是 → Tier 0+（fix / mini change）
    否 → 继续 Q5

Q5: 变更是否属于单模块内的小范围行为/体验调整？
  特征：1 个页面/组件、有限产品语义、无新接口、可定向验证 + 小范围回归覆盖
    是 → Tier 1（tweak / light change）
    否 → Tier 2+（标准 SDD）
```

### 具体示例

#### Tier 0 示例

| 场景 | 判定 | 处理 |
|------|------|------|
| "这段代码是什么意思？" | 纯问答 | 不创建 OpenSpec |
| 修复一个 TS 类型标注，不影响运行时 | 纯内部修正 | commit message 说明 + lint 通过 |
| 更新 `.prettierrc` 的 printWidth | 纯配置 | 同上 |
| 升级 `lodash` 补丁版本（无 breaking） | 纯配置 | 同上 |
| 重构一个 util 函数，行为不变，现有测试全绿 | 纯重构 | 同上 |

#### Tier 0+ 示例

| 场景 | 判定 | 处理 |
|------|------|------|
| 支付按钮点击无响应，原因是事件绑定拼写错误 | 明确修复，1 文件 | mini change |
| 用户头像在某些情况下显示裂图，原因是 URL 拼接缺少默认值 | 明确修复，1 文件 | mini change |
| 表单提交报错文案有错别字（用户可见） | 明确修复，1 文件 | mini change |
| 列表页在空数据时应该显示空状态而非空白，忘记加了 | 明确小改动 | mini change |

#### Tier 1 示例

| 场景 | 判定 | 处理 |
|------|------|------|
| 搜索框增加防抖（之前每次键入都触发请求） | 单组件行为调整 | light change |
| 下拉选择器增加"最近使用"分组 | 单组件体验调整 | light change |
| 表单增加一个"全选"复选框，不涉及新接口 | 轻量交互 | light change |
| Toast 提示从顶部改到底部 | 单点体验 | light change |

#### Tier 2+ 示例

| 场景 | 判定 | 处理 |
|------|------|------|
| 用户角色从 2 种扩展到 3 种，涉及权限判断 | 权限红线 | 完整 SDD |
| 新增登录方式（微信扫码），涉及新接口和状态流 | 接口+状态流 | 完整 SDD |
| 支付流程增加优惠券选择步骤 | 支付红线 | 完整 SDD |
| 列表页从客户端分页改为服务端分页 | 接口契约变更 | 完整 SDD |

---

## 二、Tier 0++ 紧急 Fix：先修后补

### 问题

普通 fix (Tier 0+) 仍要求先写 `proposal.md` + `tasks.md` 再修。对于需要 15 分钟内上线的 P0 级别修复，这是不现实的。

### 设计

新增 Tier 0++ 路径：**先修后补**。

```
Tier 0++ 触发条件（全部满足）：
  1. 线上 P0/P1 级别故障（用户核心路径不可用或数据错误）
  2. 修复方案明确且经过快速验证可以回滚
  3. 预计修复时间 < 30 分钟

流程：
  修复 + 验证 → commit + deploy
                    ↓
              24 小时内补 mini OpenSpec

特殊规则：
  - Tier 0++ 的 OpenSpec 不需要写「为什么做」和「影响范围」（修复完成后这些是已知事实）
  - 只需记录：根因、修复内容、验证结果、回滚方案
  - 超过 24 小时未补 → 自动从 Tier 0++ 降级为流程违规，需要事后评审
  - 同一周内同一开发者使用 Tier 0++ 超过 2 次 → 触发流程审计
```

### tier-triage 输出中增加

```markdown
- 紧急 fix 候选: <是/否>
- 原因: <如果候选 Tier 0++，说明为什么>
```

**Phase 0 实现建议**：tier-triage 中增加一个"紧急 fix 候选"判断逻辑。如果用户描述中包含 "P0" "线上挂了" "紧急" 等信号，且修复符合 Tier 0+ 条件，则标记为 Tier 0++ 候选并提示用户可以走先修后补路径。

---

## 三、Phase 0 最小状态文件

### 问题

如果 Phase 0 的 /onsf-continue 只扫描 `openspec/changes/` 推算状态，恢复体验会不稳定。不做 Trellis 不代表不能有轻量状态。

### 设计：`.onion-sdd/current.json`

```jsonc
{
  "version": 1,
  "active_change_id": "2025-06-25-fix-payment-button",
  "tier": "0+",
  "phase": "implement",     // triage | plan | implement | verify | finish
  "last_action": "tasks.md 第 3 项已勾选完成，定向验证通过",
  "last_action_at": "2025-06-25T15:30:00+08:00",
  "upgrade_risk": false,    // 实现中是否发现了升级红线的苗头
  "notes": "用户提醒注意兼容 IE11"
}
```

**写入时机（协议目标）**：阶段切换时**建议**更新；当前由 Agent 按 `trellis-adapter` 手动写入，**尚无专用 CLI / Hook 保证每次 `/onsf-*` 后自动落盘**。
**读取时机**：`/onsf-continue` 在 Trellis `meta.onion` 之后读取 `current.json`；缺失或 `idle` 时 fallback 扫描 OpenSpec。
**Phase 0 成本**：读写一个 JSON 文件，无需任何依赖；自动写入能力待后续补齐。

### README 中增加

```markdown
## 运行时状态

Phase 0 使用 `.onion-sdd/current.json` 作为可选轻量恢复 hint。
该文件**当前不保证自动维护**；无该文件时 `/onsf-continue` 仍可通过 OpenSpec fallback 恢复。
接入 Trellis 后，优先用 `meta.onion`；`current.json` 作为无 Trellis 时的 fallback hint。
```

---

## 四、Mini/Light OpenSpec 质量门禁

### 问题

如果 mini proposal 只写了"修了支付按钮。验证通过。"，它在形式上满足了要求但实质上毫无审计价值。

### 最低质量标准

#### Mini Change (Tier 0+)

| 字段 | 最低要求 | 不合格示例 | 合格示例 |
|------|----------|------------|----------|
| 背景 | 必须描述复现步骤或触发条件 | "修 BUG" | "用户在 Safari 17 点击支付按钮无响应，控制台无报错" |
| 变更 | 必须描述根因，不只描述现象 | "让按钮可以点" | "事件绑定使用了不兼容的语法，改为 addEventListener" |
| 影响范围 | 至少列出文件路径 | "改了点东西" | "src/payment/Button.tsx L42-L48" |
| 验证 | 必须包含可复现的验证命令/步骤 | "测过了" | "Safari 17 下点击支付按钮 → 跳转收银台；Chrome/Firefox 回归通过" |

#### Light Change (Tier 1)

除上述 mini 要求外，额外要求：

| 字段 | 最低要求 |
|------|----------|
| 不做范围 | 必须有至少一条明确排除项 |
| spec.md | 至少 1 个 Requirement + 1 个主场景 + 1 个边界场景 |
| 验证计划 | 至少列出具体验证工具/命令（不只是"手动测试"） |

### 门禁实现方式

在 mini-change 和 light-change 的 SKILL.md 中增加「质量自检」步骤：Agent 在写完 OpenSpec 后自问 3 个问题：

1. 如果 3 个月后有人看这个 change，能理解为什么改吗？
2. 如果这个修改引入了回归，能从 proposal 中定位根因吗？
3. 验证步骤别人能复现吗？

3 个都是"否"→ 不满足最低标准，重写。

---

## 五、活跃变更冲突检测

### 问题

两个开发者同时改同一文件，或一个 fix 和一个 Tier 2 需求重叠时，需要最小协调机制。

### 设计

在 tier-triage 阶段增加一步：

```
5. 冲突检测：
   - 扫描 openspec/changes/ 下所有活跃（未归档）change
   - 如果本次变更涉及的文件与任一活跃 change 重叠 → 输出警告
   - 不阻断，但要求用户确认知晓冲突
```

**Phase 0 实现**：在 tier-triage SKILL.md 的"输入"和"纪律"中增加冲突扫描步骤。

**输出格式补充**：

```markdown
- 活跃冲突: <无 / change-id-A（共享文件: xxx.ts）/ ...>
- 建议: <无 / 联系对方协调 / 考虑合并到一个 change>
```

---

## 六、"带债归档"定义

### 问题

"带债归档"必须先定义什么是"债"，否则 finish 门禁无法稳定判断。

### 定义

"债"指在归档时已明确知晓但未解决的风险或未完成项。

#### 债的分类

| 类别 | 示例 | 可带债归档？ | 条件 |
|------|------|:---:|------|
| 未完成任务 | tasks.md 中勾选"不做"的项 | ✅ | 在 proposal 的不做范围中已声明 |
| 部分验证 | 只在 Chrome 验证，未回归 Safari | ✅ | Tier 0+/1 允许；需在验证结果中注明 |
| 已知兼容性问题 | IE11 下样式错位，确认暂不处理 | ✅ | 创建单独的 follow-up issue/task |
| 未完成的 E2E | Tier 2+ 变更跳过了 E2E | ❌ | 不能带债归档，必须先升级或补 E2E |
| 接口契约未同步 | 改了接口字段但没通知后端 | ❌ | 涉及 Tier 2 红线，不可带债 |

#### 带债归档流程

1. 在 proposal.md 增加 `## 带债项` 章节，逐条列明
2. 为每条债创建 follow-up issue 或 Trello/Linear card
3. /onsf-finish 输出中标注"带债归档，债项 N 条，见 proposal.md"

---

## 七、Rollback/Revert 路径

### 问题

整个 Tier 体系是单向的（创建→实现→验证→归档），没有"撤销一个 change"。

### 设计

Revert 不创建新 Tier。处理规则：

| Revert 场景 | 处理方式 |
|-------------|----------|
| 未归档的 change 需要回退 | 在 tasks.md 追加 revert 任务 + 验证；还原后正常 finish |
| 已归档的 change 需要回退 | 创建新 change（建议 change-id 包含 "revert-<原id>"），Tier 按回退内容重新判定 |
| Tier 0++ 的修复上线后引发新问题需要 revert | 使用 Tier 0++ 再次紧急回退；两个 Tier 0++ 触发流程审计 |

---

## 八、Tier 3 大型任务设计占位

### 问题

Tier 3（多仓/长周期）是最复杂场景，Phase 0 至少需要给出设计占位。

### Phase 0 定位

Phase 0 不实现 Tier 3 完整支持，但需要在设计中预留接口：

```
Tier 3 不阻塞 Phase 0：
  - /onsf-plan 在判定 Tier 3 时输出提示："建议拆分为 N 个子任务，当前仅支持手动拆分"
  - Phase 0 不做 parent/child task 自动化
  - Phase 1 通过 `trellis-adapter` 利用 Trellis 现有 parent/child task 树承载运行时关系
```

### 后续设计的预留项

以下内容在 Phase 2+ 再细化，但目录结构需在 Phase 1 预留：

```text
openspec/changes/<parent-id>/
  ├── proposal.md           # 总览：背景、目标、子任务清单、跨 child 验收标准
  ├── CHILDREN.md           # 子 change 列表 + 依赖关系声明
  └── archive-order.md      # 归档顺序（哪些 child 必须等另一些 child 先归档）

openspec/changes/<child-id-1>/
  └── ...（独立 Tier 2/3 流程）

openspec/changes/<child-id-2>/
  ├── CHARTER.md            # 声明 parent + 依赖的 child + 独立可归档声明
  └── ...
```

---

## 九、向前兼容 /onsf-auto

### 问题

/onsf-auto 被推迟了至少 6 次但完全没设计。Phase 0 的命令和模板完全以人工交互为前提，后续加 auto 可能返工。

### 最小向前兼容

在现有模板中为 `auto_mode` 预留语义，不要求 Phase 0 实现：

#### proposal.md 增加可选的自动化标记

```markdown
## 背景
- <为什么要做这个小修复>

<!-- AUTO_MODE: 上述内容由 AI 根据需求源自动生成，人工确认后去除此行 -->
```

#### tier-triage 输出增加 auto 预留字段（不实现，但文档中标明）

```markdown
- auto 模式判定: <人工 / 半自动 / 全自动>  # Phase 0 固定为"人工"，后续阶段扩展
- auto 置信度: N/A                          # 后续阶段：0.0-1.0
- auto 阻断原因: N/A                        # 后续阶段：如不能全自动，为什么不
```

此字段 Phase 0 固定输出 `人工`，不影响现有逻辑。后续实现 /onsf-auto 时可以直接读取并替换。

---

## 十、基线度量收集（Phase 0 轻量方案）

### 问题

Phase 2 承诺 ROI 度量但没有 Phase 0 基线。

### 最小方案

在 `.onion-sdd/current.json` 中被动记录时间戳，不需要主动分析：

```jsonc
{
  // ... 现有字段 ...
  "metrics": {
    "created_at": "2025-06-25T14:00:00+08:00",
    "triage_completed_at": "2025-06-25T14:05:00+08:00",
    "tasks_completed_at": null,
    "verified_at": null,
    "finished_at": null
  }
}
```

每个阶段完成时打时间戳。Phase 2 只需扫描 `openspec/changes/*/metrics.json` 聚合分析即可。

**Phase 0 成本**：每个阶段结束时多写一行 time 字段，几乎零成本。

---

## 十一、自然语言弱触发路由规则（Phase 0 参考）

### 问题

自然语言弱触发如果后续要做，需要先保留可演进的匹配规则。

### 规则（可选的 mdc 补充）

```
用户表达路径 → Tier 判定辅助信号：

"修/改/bug/报错/挂了/线上/紧急/P0/P1"
  → 倾向于 Tier 0+（fix），检查是否命中紧急标志 → Tier 0++

"加/新增/优化/调整/改一下" + "这个小/这个简单/这个快的"
  → 倾向于 Tier 1（tweak），但先穿过 Tier 0+ 判定排除 bug 修复

"这个需求/这个功能/评审/设计/方案"
  → 倾向于 Tier 2+（plan）

"继续/接着/刚才/上次的"
  → /onsf-continue

"好了/做完了/归档/可以上线/收尾"
  → /onsf-finish
```

**Phase 0 不强依赖此规则**。自然语言路由放到 Phase 1 与 Trellis workflow-state 结合后再正式实现。

---

## 十二、总结：Phase 0 补丁清单

| 编号 | 补丁项 | 影响文件 | Phase 0 是否必做 |
|------|--------|----------|:---:|
| S1 | Tier 判定决策树 + 示例 | tier-triage/SKILL.md | ✅ |
| S2 | Tier 0++ 紧急 fix（先修后补） | tier-triage/SKILL.md | ✅ |
| S3 | `.onion-sdd/current.json` 最小状态 | README.md + 新文件 | ✅ |
| S4 | Mini/Light OpenSpec 质量门禁 | mini-change/SKILL.md, light-change/SKILL.md | ✅ |
| S5 | 活跃变更冲突检测 | tier-triage/SKILL.md | ✅ |
| S6 | "带债归档"定义 | onsf-finish.md + README | ✅ |
| S7 | Rollback/Revert 路径 | README（文档） | 可选 |
| S8 | Tier 3 设计占位 | README（文档） | 可选 |
| S9 | /onsf-auto 向前兼容字段 | tier-triage/SKILL.md | 推荐 |
| S10 | 基线度量时间戳 | current.json 设计 | 推荐 |

**Phase 0 最小必做**：S1～S6。这 6 项补丁的成本全部在修改 markdown 文档和技能文件，不涉及任何运行时代码。

---

## 十三、Phase 1 基座能力补齐

Phase 1 先补齐 Onion SDD 的完整基座能力，再接入 Trellis runtime。补齐后的插件不再只用命令文档描述 Tier 2+，而是用 onion 自有 skills 承载完整流程：

| 能力 | Onion skill | 说明 |
|------|-------------|------|
| 完整流程编排 | `full-change` | 需求接入、澄清、阶段推断、任务规划、事件路由 |
| OpenSpec 落盘 | `openspec-change` | `proposal.md`、`specs/**/spec.md`、`tasks.md` 模板与质量自检 |
| 外部 spec 接入 | `external-spec` | 后端/API/QA/外部文档写入当前 change 并做差异分析 |
| E2E / 验收 | `verify-change` | 验证清单、浏览器或等价验收、`e2e-report.md` 门禁 |

这四个 skill 是 `onion-sdd` 的自有能力，不要求用户调用其它 SDD 插件。Tier 0+/1 仍保持 mini/light 路径，跳过完整 brainstorming 和默认 E2E；Tier 2+ 才进入完整基座流程。

完整流程仍遵循 Single Source of Truth：OpenSpec change 目录保存正文，`.onion-sdd/current.json` 保存轻量运行态。Trellis adapter 只同步 metadata、phase、hash、path、journal 和 parent/child 关系，不复制 OpenSpec 正文。

## 十四、Phase 1 Trellis Adapter

Phase 1 的 Trellis adapter 采用 **onion 插件内 skill + 文档协议**，不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。如果后续发现必须改 Trellis 才能继续，需要先停止实现并与用户确认。

### 数据边界

| 资产 | 角色 | 写入内容 |
|------|------|----------|
| `openspec/changes/<change-id>/` | 唯一变更正文 | proposal、specs、tasks、backend/qa/e2e |
| `.onion-sdd/current.json` | 轻量本地状态 | 当前 change、tier、phase、last_action、metrics、trellis_task |
| `.trellis/tasks/<task>/task.json` | 运行时 metadata | `meta.onion`、status、parent/children |
| `.trellis/workspace/<developer>/journal-*.md` | 会话记忆 | last_action 摘要、提交、恢复提示 |

### 字段映射

`task.json.meta.onion`：

```json
{
  "version": 1,
  "change_id": "add-invoice-export",
  "change_path": "openspec/changes/add-invoice-export",
  "tier": "2",
  "phase": "verify",
  "last_action": "qa spec 已接入，待执行 verify-change",
  "last_action_at": "2026-06-25T18:30:00+08:00",
  "upgrade_risk": false,
  "source_hashes": {
    "proposal": "sha256:...",
    "tasks": "sha256:...",
    "specs": "sha256:...",
    "backend": "sha256:...",
    "qa": "sha256:...",
    "e2e": "sha256:..."
  }
}
```

`.onion-sdd/current.json` 追加 `trellis_task`：

```json
{
  "trellis_task": {
    "task_dir": ".trellis/tasks/06-25-add-invoice-export",
    "status": "in_progress"
  }
}
```

### 同步时机

| Onion 事件 | OpenSpec | Trellis |
|------------|----------|---------|
| Tier 判断完成 | change 策略确定 | 写 `meta.onion.tier` |
| OpenSpec 落盘 | proposal/specs/tasks | 写 `change_id`、`change_path`、phase |
| tasks 更新 | `tasks.md` | 更新 phase / last_action |
| 外部 spec 接入 | `backend-*.md` / `qa-*.md` | 更新 `source_hashes` |
| 验证完成 | `e2e-report.md` | phase = finish / verified |
| finish | 归档判断 | `add_session.py` 写 journal 摘要 |

### 恢复优先级

`/onsf-continue` 的恢复顺序：

1. Trellis active task：若 `task.json.meta.onion.change_id` 指向存在的 OpenSpec change，则使用它。
2. `.onion-sdd/current.json`：若 task 不存在或 stale，使用轻量状态。
3. OpenSpec fallback：扫描 `openspec/changes/**`，按产物推断阶段。

冲突处理：

- Trellis 与 current 指向不同 change：提示冲突，默认以 Trellis active task 为准；用户可指定 change-id 覆盖。
- Trellis 指向的 change 不存在：标记 stale，fallback 到 current/OpenSpec。
- current 指向的 task 不存在：忽略 `trellis_task`，但保留 change 恢复。
- `source_hashes` 与实际文件不一致：提示 stale，不自动覆盖正文。

### Tier 3

Tier 3 使用 Trellis parent/child task tree：

- parent task 对应 parent OpenSpec change 或总览 change。
- 每个 child task 对应一个独立可归档 OpenSpec child change。
- child 的 `meta.onion.parent_change_id` 指回 parent。
- child 的 `CHARTER.md` 或 proposal 中说明依赖关系和独立归档条件。

### 回滚

- Adapter 协议失败时，删除或忽略 `meta.onion`，回到 `.onion-sdd/current.json` + OpenSpec fallback。
- 不修改 Trellis 核心脚本，因此不会影响普通 Trellis task 流。
- `source_hashes` 只用于提示 stale，不作为阻塞性真相源。
