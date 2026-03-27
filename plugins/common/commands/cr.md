---
name: /cr
id: cr
category: Code Review
description: 执行AI代码审查，调用aicr-local技能分析Git暂存区变更
---

# 代码审查 (/cr)

触发 AI 代码审查。

## 使用方法

```bash
# 1. 添加文件到暂存区
git add <files>

# 2. 执行审查
/cr
```

## 说明

本命令调用 `aicr-local` 技能执行代码审查。
