## Why

洋葱开发规范（`洋葱开发规范.md`）包含 2000+ 行的 Go 编程规范、数据库规范和工程规范，
以纯文档形式存放，AI 编码助手（Cursor）无法自动感知并应用这些规范。
将各章节拆分为独立的 `.cursor/rules/*.mdc` 文件后，AI 可在对应场景下自动获取相关规范上下文，从而减少违规代码的产生。

## What Changes

- 将 `洋葱开发规范.md` 中的后端规范按领域拆分为多个 `.cursor/rules/*.mdc` 文件
- 每个 rule 文件聚焦单一领域，包含强制/推荐级别标注，以及精简后的示例代码
- 原文档保留不变，rule 文件是其可机器消费的提炼版本

## Capabilities

### New Capabilities

- `go-coding-style`: Go 代码风格规范——格式化（gofmt/goimports）、命名（MixedCaps/包名/常量/变量/缩写词）、注释（导出符号/包注释）、包导入分组与别名（章节 2.1–2.4）
- `go-error-handling`: Go 错误处理规范——panic 使用限制、错误返回与包装、调用方处理策略（章节 2.5）
- `go-language-features`: Go 语言特性规范——减少嵌套/变量作用域/缩进、零值初始化、切片/map/channel 使用、并发编程、接口设计、泛型使用、字符串拼接（章节 2.6.1–2.6.6）
- `go-http-api`: HTTP 接口返回值规范——统一响应结构、状态码约定（章节 2.6.7）
- `database-pg`: PostgreSQL 数据库规范——命名、索引、查询、事务使用规范（章节 3）
- `database-redis`: Redis 使用规范——key 设计、value 设计、命令限制、缓存与数据库操作顺序（章节 5）
- `database-mongo`: MongoDB 使用规范（章节 6）
- `engineering-conventions`: 工程规范——分层架构、日志规范、链路追踪、CI/CD、版本管理、模块版本命名（章节 7）
- `security-compliance`: 安全合规规范——合规要求与安全编码规范（章节 8）

### Modified Capabilities

（无）

## Impact

- 新增文件：`.cursor/rules/` 目录下 9 个 `.mdc` 文件
- 不修改现有代码，不影响 CI/CD 流程
- 影响范围：Cursor AI 编码辅助行为，开发者使用 Cursor 时将自动受益
