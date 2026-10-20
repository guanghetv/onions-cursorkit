---
name: pm-spec
description: >-
  Use when user mentions: 写需求文档/pm-spec/产品spec/转换需求/增强prd/spec转换/PRD评审。
  也兼容旧说法 5稿、9稿、pm-spec-5、定稿。稿次已取消，统一走本技能。
  多轮只改本地 prd.md。不在本技能里自动预检、校验或推飞书。
  工作区改完需求后停住，二次确认后再引导 /prd-publish。同一句话里说发布也不立刻进入发布。
---

# /pm-spec — 编写并更新需求文档

<HARD-GATE>
在 Step 3 Brainstorming 完成且用户**明确确认**之前，**禁止**：

- 写入或大幅改写 `prd.md`
- 把差异写回飞书或原型
- 以「prd 已有内容 / 飞书已拉取」为由跳过澄清

必须 **Read 并遵循** `superpowers:brainstorming` 的 SKILL.md 全流程。
</HARD-GATE>

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- 目标目录存在 `prd.md` 与 `metadata.yaml`
- 主路径是先有 `/pm-proto` 的核心流程。没有原型时可以继续，并在文档里写明无原型的原因。

## 核心原则

本技能是多轮改稿循环，每一轮默认只改本地 `prd.md`。

同一份飞书需求文档持续更新，但同步不在每一轮末尾自动发生。`prd.status=confirmed` 只由第一次成功的 `/prd-publish` 写入。本技能不把状态改成 `confirmed`，也不前进基线。

- 飞书正文以 `../../references/产品组PRD写作规范.md` 为准（来源 [产品组 PRD 写作规范 V1.0](https://guanghe.feishu.cn/docx/Cqtqd9BxJoUYAFxbXFocp2qYnWd)）
- Agent 禁令以 `../../rules/agent-hard-rules.mdc` 为准
- 三端对齐先 Read `../../references/three-way-sync.md`。每一轮先提示另外两端，用户确认前不写
- 模板见 `references/prd-template.md`。详细说明写规则、状态和异常，不单设验收章，不把同一规则再写成验收清单
- 飞书读取用 `lark-cli`。文档已有内容时禁止整篇覆盖
- 写正文或扫描工作区之前，先调用 `user-codewiki-mcp` 的 `search_wiki`。`query` 写本轮功能或页面。全新功能也先查一次
- 内容质量、两端对齐和可读性告警由 `/prd-check` 在 `/prd-publish` 时执行。本技能不自动调用它，也不自动调用 `/prd-risk`

## 流程

### Step 0: 先查现有实现

按 `rules/agent-hard-rules.mdc` 调用 `user-codewiki-mcp` 的 `search_wiki`。`query` 写本轮要写的功能或页面。仓库不明时不要先猜 `scope`。不确定用哪个工具时，先调用 `get_codewiki_mcp_guidance`，然后必须再调用 `search_wiki`。调用失败时写出原因，再进入 Step 1。禁止把失败说成「没有这个功能」。工作区代码不能代替这次调用。

### Step 1: 定位并对比三端

读取原型、`prd.md` 和飞书文档。已确认的需求也可以继续改，不要因为 `prd.status=confirmed` 而停止。

按 `three-way-sync.md` 给出差异判断：哪一端更新、影响哪些模块、建议如何写回另外两端。用户确认前不写另外两端。

飞书和原型都没有当前 `prd.md` 里没有的内容时，本地只是草稿超前。用一句话说明飞书仍是旧的，继续改本地，不阻断。

飞书或原型有当前 `prd.md` 没有的内容时，必须写明「本轮不会纳入这些手改」，并建议先 `/prd-feishu-sync reconcile` 或 `/pm-proto`。用户未明确接受丢弃或延后纳入前，不要覆盖那些差异点。

历史快照 `snapshots/prd-v5-*.md`、`snapshots/prd-v9-*.md` 只作对照，不再代表稿次。

### Step 2: 读取原型

若 `prototypes/`、`assets/` 存在，作为正文输入。原型锚点写入对应模块。用户要改原型时，停在本技能，改走 `/pm-proto`。

### Step 3: Brainstorming【阻断】

**REQUIRED SUB-SKILL:** `superpowers:brainstorming`（一次一问）

澄清：未确认项、MODULE 拆分、规则/状态/异常是否可判断、本轮变更的 MODULE、回归范围。

同一会话里的后续轮次：只澄清这一轮相对上一轮的变化，不必重开整份需求。

### Step 4: 只写本地 `prd.md`

按写作规范和 `references/prd-template.md` 更新正文。

- 保留仍然有效的规则
- 背景与目标是正文的一部分，不因旧的 9 稿瘦身规则删除
- 需求详情不写独立验收清单
- 本步不跑 `/prd-risk`，不跑 `/prd-check`，不 push，不追加基线版本行，不改 `prd.status`

### Step 5: 本轮收尾

本地 `prd.md` 写完后停住，按 `three-way-sync.md` 的「文档更新后的二次确认」再问一次是否现在发布，并说明下一步是 `/prd-publish`。也可以继续改本地。第二次明确同意之前，不进入发布，不预检，不校验，不 push。空骨架还没有需求规则时，只提示继续 `/pm-spec`，不要问是否发布。

用户是在上一轮已经写完之后，再说「同步到飞书」「推到飞书」或「发布」：结束本技能，改走 `/prd-publish`。同一轮里既改内容又说发布，仍然先写完再问一次。不要在这里 push，也不要在这里跑 `/prd-risk` 或 `/prd-check`。

用户贴了绑定文档，并说更新需求、改范围或这条先不做了：第一次确认后只把决定写入本地 `prd.md`，然后停住做二次确认。不要先改飞书正文，不要在这里追加版本表。

用户要改原型：执行 `/pm-proto`，由该技能按三端协议处理。

「同步回来 / 按飞书改本地」不是发布，走 `/prd-feishu-sync reconcile`。

## 约束

- 不编造未确认方案
- MODULE ID 保持稳定
- 版本表的基线行只在 `/prd-publish` 成功后追加
