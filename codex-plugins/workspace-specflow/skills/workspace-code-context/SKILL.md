---
name: workspace-code-context
description: 在 Codex 的 specs 仓会话中解析 workspace-repos.json，并优先通过 CodeWiki/GitNexus 查询关联代码仓。用于任何跨仓代码扫描、现状核验、页面复用或测试行为识别。
compatibility: Requires CodeWiki MCP for preferred search; local registered repositories are an explicit fallback.
---

# Workspace Code Context

Codex 不依赖 Cursor 多根工作区。需要代码证据时，按以下顺序建立上下文。

## 1. 定位 registry

从当前工作目录向上确认 specs 仓根，依次检查：

1. `<specs-root>/workspace-repos.json`
2. `<specs-root>/scripts/workspace-repos.json`

文件必须包含 `repos` 数组；每项按需读取 `name`、`path`、`remote`。找不到或解析失败时，不得编造关联仓。

## 2. 优先使用 CodeWiki

1. 未知仓库或跨仓问题先使用 CodeWiki 的业务知识搜索。
2. 调用 GitNexus 仓库清单，取得后续代码图谱工具要求的规范 `repo` 名。
3. 将 registry 的 Git remote 归一化为仓库 path：
   - `git@gitlab.yc345.tv:backend/teacher-desk.git` → `backend/teacher-desk`
   - `https://gitlab.yc345.tv/teacher/fe/padh5.git` → `teacher/fe/padh5`
4. 用归一化 remote path 与清单中的规范仓名精确匹配。
5. 仅当 remote 缺失且仓库 basename 在清单中唯一时，才允许按 `name` 兜底。
6. 命中后使用 CodeWiki/GitNexus 代码搜索；不要把 registry 逻辑名直接作为 `repo` 参数。

多个候选、无候选或权限清单缺失时，报告证据缺口，不选择“看起来最像”的仓库。

## 3. 本地只读降级

CodeWiki 不可用或目标仓未建索引时：

1. 解析 registry `path`，相对路径以 specs 根为基准。
2. 确认目录存在且可读。
3. 只读、按需求范围扫描相关文件；禁止修改代码仓。
4. 明确告知用户已降级为本地扫描，并说明实际扫描了哪些仓库。

## 4. 双重失败

CodeWiki 与本地目录都不可用时：

- 只阻断当前依赖代码上下文的步骤。
- 纯 PRD 编辑、飞书同步、需求状态读取等不依赖代码证据的步骤继续执行。
- 输出未验证事实和恢复方式，例如补充 CodeWiki 权限、索引或本地仓路径。
