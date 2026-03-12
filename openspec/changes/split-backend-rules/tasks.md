## 1. 准备工作

- [x] 1.1 确认 `.cursor/rules/` 目录存在（已有 `doc-writing-zh.mdc` 作为参考格式）
- [x] 1.2 阅读现有 `doc-writing-zh.mdc` 确认 frontmatter 格式（description / globs / alwaysApply）

## 2. Go 编程规范 rule 文件

- [x] 2.1 创建 `.cursor/rules/go-coding-style.mdc`，frontmatter `globs: **/*.go`，内容提炼自 `洋葱开发规范.md` 章节 2.1–2.4（格式化、命名、注释、导入）
- [x] 2.2 创建 `.cursor/rules/go-error-handling.mdc`，frontmatter `globs: **/*.go`，内容提炼自章节 2.5（panic 限制、错误返回、调用方处理策略）
- [x] 2.3 创建 `.cursor/rules/go-language-features.mdc`，frontmatter `globs: **/*.go`，内容提炼自章节 2.6.1–2.6.6（嵌套/作用域/变量/切片/map/channel/并发/接口/泛型/字符串拼接）
- [x] 2.4 创建 `.cursor/rules/go-http-api.mdc`，frontmatter `globs: **/*.go`，内容提炼自章节 2.6.7（HTTP 状态码规范）

## 3. 数据库规范 rule 文件

- [x] 3.1 创建 `.cursor/rules/database-pg.mdc`，frontmatter `globs: "**/*.go, **/migrations/**"`，内容提炼自章节 3（建表、索引、SQL、事务规范）
- [x] 3.2 创建 `.cursor/rules/database-redis.mdc`，frontmatter `globs: **/*.go`，内容提炼自章节 5（key 设计、bigkey、过期、命令规范、缓存一致性）
- [x] 3.3 创建 `.cursor/rules/database-mongo.mdc`，frontmatter `globs: **/*.go`，内容注明"待团队补充 MongoDB 规范"

## 4. 工程规范 rule 文件

- [x] 4.1 创建 `.cursor/rules/engineering-conventions.mdc`，frontmatter `globs: "**/*.go, **/Makefile, **/.gitlab-ci.yaml"`，内容提炼自章节 7（分层、日志、链路、CI/CD、版本锁定）

## 5. 安全合规规范 rule 文件

- [x] 5.1 创建 `.cursor/rules/security-compliance.mdc`，frontmatter `alwaysApply: true`，内容提炼自章节 8（设备脱敏、敏感信息加密、视频加密、接口签名）

## 6. 验收

- [x] 6.1 逐一打开每个 `.mdc` 文件，确认 frontmatter 格式正确（YAML 合法，字段完整）
- [x] 6.2 确认每个 rule 文件的【强制】条目全部保留，关键代码示例至少保留一个 Good/Bad 对比
- [ ] 6.3 在 Cursor 中打开一个 `.go` 文件，验证 Go 相关 rule 在 `@Rules` 中可见
- [x] 6.4 确认 `security-compliance.mdc` 的 `alwaysApply: true` 已正确设置
- [ ] 6.5 更新 `洋葱开发规范.md` 文件头注释或 README，说明各章节对应的 `.cursor/rules` 文件（可选）
