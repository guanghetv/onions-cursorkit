# 需求目录模板

## metadata.yaml

```yaml
name: <中文显示名>
id: <english-keyword-slug>   # 稳定英文 kebab-case，创建后不变；供 openspec/脚本引用
module: <业务模块>
feishu_doc: <飞书文档链接>
figma: null
created_at: <YYYY-MM-DD>

prd:
  stage: v5_pending          # v5_pending | v5_confirmed | v9_pending | confirmed
  status: pending            # 仅 9稿 confirmed 后 = confirmed
  confirmed_at: null
  v5:
    status: pending
    confirmed_at: null
    snapshot: null
  v9:
    status: pending
    confirmed_at: null
    snapshot: null

test_spec:
  status: pending
  confirmed_at: null
```

## prd.md（飞书七章空骨架）

Agent 在 `/req-new` 时从飞书标题或用户输入补齐占位。对齐模板：https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg

```markdown
# 【功能名称】PRD

## 一、需求概述

| 项目 | 内容 |
|------|------|
| 当前阶段 | 5稿 |
| 需求类型 |  |
| 影响范围 |  |
| 原型情况 |  |
| 建议阅读顺序 |  |

用一段话讲清楚：本次需求做什么、给谁用、在哪个场景使用、解决什么问题、上线后希望达到什么效果。

> 示例：本需求在【系统/页面】新增【功能名称】，用于【目标用户】在【业务场景】下完成【核心动作】，解决当前【痛点问题】，提升【效率/体验/转化/管理能力】。

## 二、版本及进度跟踪

| 日期 | 版本号 | PM | 变更内容 | 对应 spec / demo |
|------|--------|-----|----------|------------------|
|  |  |  |  |  |

## 三、背景和价值

### 3.1 背景

- 当前现状：
- 当前问题：
- 影响范围：

### 3.2 价值

- 对用户的价值：
- 对业务的价值：
- 对内部协作/运营/交付的价值：

### 3.3 关键关注

> [!IMPORTANT]
> - 

### 3.4 回归范围

> [!NOTE]
> - **需回归**：
> - **不纳入本次回归**：

## 四、需求 Feature List

| Feature | 功能点 | 需求说明 | 优先级 | MODULE | 备注 |
|---------|--------|----------|--------|--------|------|
| Feature 1 |  |  | P0 | MODULE-1 |  |

## 五、需求详情说明

### MODULE-1: <待定> [新增]

| 模块/页面 | 图示 | 说明 |
|-----------|------|------|
|  |  | 1. 【功能说明】<br/>a. <br/>2. 【交互说明】<br/>a. <br/>3. 【补充规则】<br/>a.  |

## 六、设计图地址

| 类型 | 地址 | 说明 |
|------|------|------|
| 设计稿 |  |  |
| 原型/demo |  |  |
| 评审截图/录屏 |  |  |

## 七、埋点需求

本需求无埋点需求

### 7.1 核心指标

- 

### 7.2 事件埋点

| 事件名 | 触发时机 | 参数 | 备注 |
|--------|----------|------|------|
|  |  |  |  |

### 7.3 漏斗/分析口径

1. 
```

## test/test-spec.md（空模板）

```markdown
# 测试用例：<需求标题>

> 来源产品 spec: requirements/<中文目录名>/prd.md
> 确认时间: YYYY-MM-DD

## MODULE-1: <待定>

### 场景 1.1: <待定>
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
