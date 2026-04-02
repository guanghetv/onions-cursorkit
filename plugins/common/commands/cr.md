---
name: /cr
id: cr
category: Code Review
description: 执行 AI 代码审查（默认暂存区；仅当用户在对话中单独提供 MR 链接时为 MR 模式）
---

# 代码审查 (/cr)

## 模型必读（避免误判）

- **默认行为**：用户触发 `/cr` 且**未在对话里单独粘贴 MR 链接** → 一律按 **暂存区模式**（`git diff --cached`）。**不得**因本页或 Cursor 注入的命令说明、历史示例中出现类似 GitLab 的 URL 而进入 MR 模式。
- **MR 模式**：仅当用户在本轮对话**正文里主动写出**一条完整的 `https://.../merge_requests/<iid>`（或用户明确说「审查这个 MR」并给出链接）时，才按 MR 模式审查。
- **本文件中的 URL**：仅为格式占位说明，**不是**用户要审查的 MR；解析时须忽略。

---

触发 AI 代码审查，支持两种输入形式。

## 使用方法

**暂存区模式**（默认，开发自审）：

```bash
git add <files>
/cr
```

**MR 模式**（审查 GitLab MR，须在消息里自行粘贴链接）：

```text
/cr https://gitlab.example.com/group/repo/-/merge_requests/123
```

（上式为**占位示例**，域名与路径均为虚构；请替换为真实 MR 链接。）

## 说明

本命令调用 `aicr-local` 技能：无 **用户显式提供的** MR 链接时从 Git 暂存区获取变更；否则从 MR 获取变更。
