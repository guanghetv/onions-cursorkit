# 需求目录模板

## metadata.yaml

```yaml
name: <中文显示名>
id: <kebab-case-id>
module: <业务模块>
feishu_doc: <飞书文档链接>
figma: null
created_at: <YYYY-MM-DD>

prd:
  status: pending
  confirmed_at: null

test_spec:
  status: pending
  confirmed_at: null
```

## prd.md（空模板）

```markdown
# <需求标题>

> 来源: <飞书文档链接>

## 需求背景

（待撰写）

## 功能描述

（待撰写）
```

## test/test-spec.md（空模板）

```markdown
# 测试用例：<需求标题>

> 来源产品 spec: requirements/<requirement-id>/prd.md
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
requirements/<requirement-id>/
  ├─ prd.md
  ├─ metadata.yaml
  ├─ prototypes/          （含 .gitkeep）
  └─ test/
       └─ test-spec.md
```
