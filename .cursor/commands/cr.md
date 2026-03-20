---
name: /cr
id: cr
category: Code Review
description: 执行AI代码审查，支持暂存区变更或GitLab MR链接
---

# 代码审查 (/cr)

触发 AI 代码审查，支持两种输入形式。

## 使用方法

**暂存区模式**（开发自审）：
```bash
git add <files>
/cr
```

**MR 模式**（审查 GitLab MR）：
```
/cr https://gitlab.yc345.tv/backend/foo/-/merge_requests/123
```

## 说明

本命令调用 `aicr-local` 技能执行代码审查。无参数时从 Git 暂存区获取变更；传入 GitLab MR 链接时从 MR 获取变更。
