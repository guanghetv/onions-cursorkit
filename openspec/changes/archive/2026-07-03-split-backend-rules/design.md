## Context

项目已有一个 `.cursor/rules/doc-writing-zh.mdc`，格式为标准 Cursor Rule 结构：YAML frontmatter（`description`、`globs`、`alwaysApply`）+ Markdown 正文。`洋葱开发规范.md` 当前是一份 2000+ 行的单体文档，AI 无法按场景选择性加载。

## Goals / Non-Goals

**Goals:**
- 将规范拆分为 9 个独立 `.mdc` 文件，每个聚焦单一领域
- 每个 rule 配置合理的 `globs`，使 Cursor 在对应文件类型中自动激活
- 内容精炼：保留【强制】/【推荐】条目和核心代码示例，去除大段叙述性内容
- 与现有 `doc-writing-zh.mdc` 保持一致的格式

**Non-Goals:**
- 不修改或删除 `洋葱开发规范.md` 原文
- 不做内容的重新诠释，仅做提炼与格式转换
- 不涉及任何业务代码变更

## Decisions

### 1. 文件命名：与 capability 名称一致
使用 `<capability>.mdc`，例如 `go-coding-style.mdc`。
备选：按章节编号命名（`ch2-1.mdc`）。选择语义化名称，可读性更强，与 proposal 的 capability 定义保持一致。

### 2. `globs` 配置策略
- Go 规范（go-coding-style、go-error-handling、go-language-features、go-http-api）：`globs: **/*.go`
- 数据库规范（database-pg、database-redis、database-mongo）：`globs: **/*.go, **/migrations/**`（在 Go 代码和迁移脚本中触发）
- 工程规范（engineering-conventions）：`globs: **/*.go, **/Makefile, **/.github/**`
- 安全合规（security-compliance）：`alwaysApply: true`（安全规范全局生效）

### 3. `alwaysApply` 策略
- 默认 `alwaysApply: false`，依靠 `globs` 按需激活，避免 token 浪费
- 仅 `security-compliance` 设为 `alwaysApply: true`，因安全规范不受文件类型限制

### 4. 内容精炼原则
- 保留所有【强制】条目（完整保留）
- 保留【推荐】条目（可适当精简描述）
- 代码示例：每条规则保留 Good/Bad 示例各一个最典型的
- 去除：图片链接（均为 CDN 截图）、冗长的背景叙述、修订历史
- 格式：使用 Markdown 列表 + 代码块，不使用 HTML 表格

### 5. 章节对应关系

| 文件 | 原文章节 |
|---|---|
| `go-coding-style.mdc` | 2.1, 2.2, 2.3, 2.4 |
| `go-error-handling.mdc` | 2.5 |
| `go-language-features.mdc` | 2.6.1–2.6.6 |
| `go-http-api.mdc` | 2.6.7 |
| `database-pg.mdc` | 3 |
| `database-redis.mdc` | 5 |
| `database-mongo.mdc` | 6 |
| `engineering-conventions.mdc` | 7 |
| `security-compliance.mdc` | 8 |

## Risks / Trade-offs

- **内容遗漏风险** → 原文存在大量 CDN 图片（代码截图），部分示例无法从文本中提取；缓解：直接用文字描述规则，不依赖图片内容
- **rule 文件过长** → 部分章节内容较多（如 2.6 语言特性），文件可能偏长影响 token 效率；缓解：go-language-features 可进一步拆分（并发单独一个文件），但首期保持 9 个文件的简洁结构
- **globs 覆盖不全** → 不同项目目录结构不同；缓解：使用 `**/*.go` 宽泛匹配，降低漏触发风险
