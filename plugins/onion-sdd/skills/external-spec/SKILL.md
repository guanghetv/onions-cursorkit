---
name: external-spec
description: 将后端、QA、GitLab、workspace 文件或用户粘贴的外部 spec 接入 Onion SDD change，并做差异分析。
---

# External Spec

本技能用于完整流程中的外部 spec 接入。它把外部材料写入当前 `openspec/changes/<change-id>/`，并与 `proposal.md` / `specs/**/spec.md` 做差异分析。

YApi 结构化接口详情优先使用 `pull-yapi`，写入 `backend-yapi-*.md`；本技能仍负责 GitLab/后端叙事 spec、QA spec、workspace 文件和用户粘贴的外部材料。

## 触发

- “后端 spec 到了”
- “API 文档到了”
- “测试 spec 到了”
- “QA 文档到了”
- 用户提供 GitLab 文件 / MR 链接
- 用户粘贴接口、测试或验收文档
- 用户用工作区文件提供 spec 内容

## 定位 change

写入前必须先定位目标变更目录：

```bash
find openspec/changes -maxdepth 2 -name proposal.md 2>/dev/null
```

| 场景 | 处理 |
|------|------|
| 用户指定 change-id | 使用指定目录 |
| 只有一个候选 | 自动选定 |
| 多个候选 | 列出并请用户选择 |
| 无候选 | 停止，提示先用 `/onsf-plan` 创建完整 OpenSpec |

禁止写到变更目录以外的位置。

## 读取策略

| 优先级 | 策略 | 说明 |
|--------|------|------|
| 1 | 工作区文件 | 用户已提供或上下文已注入文件正文时直接使用 |
| 2 | workspace-native | 无显式链接时，若可解析 `workspace-repos.json` 且当前 proposal 有 `requirement_ref`，从工作区内 specs/API 仓库读取 |
| 3 | GitLab / 远程链接 | 使用可用 token 或工具读取；失败时明确说明原因 |
| 4 | 用户粘贴 | 作为兜底输入 |

远程读取失败不能静默跳过；必须说明是权限、认证、网络、路径还是 token 问题。

### Workspace-native 读取

workspace-native 是零手动输入的优先路径，适用于用户只说“后端 spec 到了”或“测试 spec 到了”且工作区已有配套 specs/API 仓库的场景。

前置条件：

- 仓库根或 `scripts/` 下存在可解析的 `workspace-repos.json`。
- 当前 `openspec/changes/<change-id>/proposal.md` frontmatter 含 `requirement_ref`；如有 `modules`，后续测试 spec 需要按 MODULE 切片。
- 目标仓库可在当前工作区中定位；读取远程分支时只用 `git fetch` / `git show` 一类非 checkout 操作。

处理规则：

- 测试/QA spec：优先从 specs 仓库读取，按 `modules` 保留相关 MODULE 与公共部分。
- 后端/API spec：优先从匹配仓库的约定分支或用户指定 ref 读取接口文档。
- 任一步骤无法定位、认证失败或内容不确定时，降级到 GitLab/远程链接或用户粘贴，并说明降级原因。
- 不把 workspace-native 失败当成流程失败；只要用户能提供正文，仍可继续落盘和差异分析。

## 命名

| 类型 | 文件名 |
|------|--------|
| 后端/API spec | `backend-<name>.md` |
| YApi 接口契约 | 交给 `pull-yapi` 写入 `backend-yapi-<name>.md` |
| 测试/QA spec | `qa-<name>.md` |
| 其它外部验收材料 | `external-<name>.md` |

写入路径固定为 `openspec/changes/<change-id>/`。

## 文件头

```markdown
<!-- external-spec metadata -->
<!-- source: <url / workspace-native / workspace-file:path / user-paste> -->
<!-- ref: <branch/ref/path 或 N/A> -->
<!-- commit: <hash 或 N/A> -->
<!-- pulled_at: <YYYY-MM-DD HH:mm> -->
<!-- WARNING: 此文件为外部 spec 副本，实现以源材料为准 -->
```

## 差异分析

写入后必须读取：

- `proposal.md`
- `specs/**/spec.md`
- 新写入的 `backend-*.md` / `qa-*.md` / `external-*.md`

输出：

| 类型 | 说明 |
|------|------|
| 一致 | 外部 spec 与当前方案一致 |
| 差异 | 字段、错误码、流程、文案、权限、验收口径不同 |
| 增量 | 外部 spec 有但当前 OpenSpec 未覆盖 |
| 冲突 | 需要用户或协作者裁决 |

有差异时，建议更新 `proposal.md`、`specs/**/spec.md`、mock、实现或验证清单。冲突未裁决前不要进入归档。

## 完成标准

- 外部 spec 已落在当前 change 目录。
- 差异分析已输出。
- 需要更新的 OpenSpec 或实现项已写入 `tasks.md` 或最终回复。
- QA spec 存在时，后续 `verify-change` 必须以 QA spec 为最高优先级。
