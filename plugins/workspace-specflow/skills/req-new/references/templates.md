# 需求目录模板

## metadata.yaml

```yaml
name: <中文显示名>
id: <english-keyword-slug>   # 稳定英文 kebab-case，创建后不变；供 openspec/脚本引用
module: <业务模块>
feishu_doc: <飞书文档链接>   # 兼容旧字段；与 feishu.doc_url 保持同步
figma: null
created_at: <YYYY-MM-DD>

# 飞书绑定与同步状态（/prd-feishu-sync 维护）
feishu:
  doc_url: null              # 与 feishu_doc 同步
  doc_token: null
  created_at: null
  last_synced_at: null
  last_synced_stage: null    # skeleton | current | reconcile；旧值 v5/v9 只作历史
  last_synced_commit: null
  feishu_revision: null      # 最近一次同步读到的飞书 revision_id，不是基线
  v9_synced: false           # 旧字段。true 只表示曾经按 9 稿同步过，不再阻止 push

# /prd-check 的结论。字段名保持 consistency，供已有目录和 /qa-spec 读取；不要另写 prd.check
# create 后 status=unknown。飞书文末只有一块「文档状态」，其中 prd-sync:check:v1 显示「未校验」；检查后覆盖为 pass|warn|fail
consistency:
  status: unknown            # unknown | pass | warn | fail
  checked_at: null
  report_path: null          # 如 prototypes/prd-check-YYYY-MM-DD.md
  source_commit: null


prd:
  status: pending            # 第一次 /prd-publish 成功后改为 confirmed，之后保持 confirmed
  confirmed_at: null
  baseline:                  # 只由成功的 /prd-publish 前进
    revision_id: null        # 发布最后一次写完飞书后的回读序号，不是版本表里的发布序号
    version: null            # 版本表里的发布序号，第一次成功发布为 1，之后每次 +1
    row_revision_id: null    # 追加版本行之前的飞书 revision_id，不写入版本表，不拿来显示
    snapshot: null           # snapshots/prd-baseline-YYYY-MM-DD.md
    published_at: null
  risk_precheck:             # /prd-risk 维护；报告正文不写这些字段
    last_result: null        # 规则预检通过 | 待补信息 | 需调整
    last_checked_at: null
    report: null             # prototypes/prd-risk-precheck.md

test_spec:
  status: pending
  confirmed_at: null
```

## 旧稿次怎么读

新建需求不再写 `prd.stage`、`prd.v5`、`prd.v9`。读到旧目录时：

- 已确认：`prd.status=confirmed`，或 `prd.stage=confirmed`，或 `prd.v9.status=confirmed`
- 基线快照：`prd.baseline.snapshot`，否则 `prd.v9.snapshot`，否则 `snapshots/` 里最新的 `prd-v9-*.md`，再否则最新的 `prd-v5-*.md`
- 基线 revision：`prd.baseline.revision_id`。旧目录没有该字段时，不把当前飞书正文当成已发布基线


## prd.md（空骨架）

`/req-new` 只写下面这一版。飞书标题和 `metadata.name` 用同一句需求名。目录名从这句按 `SKILL.md` Step 2 清洗，最长 30 字，可以比 name 短。概述用用户原话写成一段，不写成待确认清单。

不要在骨架里预置关键关注、回归范围、Feature List、关联材料、数据观察与发布约束，也不要预置 `MODULE-N`。这些等 `/pm-spec` 确认有内容再加。背景、目标、本次范围只留标题，不写 `-`。不要把版本号、`R1` / `R2` 或技能说明写进正文。飞书文末的「文档状态」只在 `/prd-feishu-sync create` 写入，不放进 `prd.md`。create 成功后把文档地址追加到 `prd.md` 末尾的「飞书文档」，这一节不上传。

```markdown
# <需求名称>

## 需求概述

| 项目 | 内容 |
|------|------|
| 需求类型 |  |
| 影响范围 |  |

<谁在什么场景遇到什么问题，本次要改变什么。用用户原话写一段。>

## 版本及进度跟踪

| 日期 | 版本号 | PM | 变更内容 | 对应 spec / demo |
|------|--------|-----|----------|------------------|
|  |  |  |  |  |

## 背景与目标

### 背景

### 目标

### 本次范围

## 需求详情

| 功能模块 | 图示 | 详细说明 |
|-----------|------|------|
|  |  |  |
```

## test/test-spec.md（空模板）

```markdown
# 测试用例：<需求标题>

> 来源产品 spec: requirements/<中文目录名>/prd.md
> 确认时间: YYYY-MM-DD

## MODULE-1: <待定>

### 场景: <描述性标题>
**测试类型**: 功能测试
**覆盖端**: 待定
**前置条件**:
- 待定
**操作步骤**:
1. 待定
**预期结果**:
- 待定

## 兼容性 & 回归

（待填写）
```

## 目录结构

```
requirements/<中文目录名>/
  ├─ prd.md
  ├─ metadata.yaml
  ├─ snapshots/           （含 .gitkeep）
  ├─ prototypes/          （含 .gitkeep）
  └─ test/
       └─ test-spec.md
```

**命名规则**：目录名为清洗后中文；`metadata.id` 为英文关键词 slug（创建后不变）。重名消歧：`-2`、`-3`… 或 `-MMDD`。
