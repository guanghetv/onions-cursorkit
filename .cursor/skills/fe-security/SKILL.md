---
name: fe-security
description: >-
  前端安全规范：代码安全、数据安全、依赖安全、域名安全。用于安全审查、实现自检、PR
  检查。在用户提及前端安全、域名规范、存储桶、k8s 命名空间、XSS、CSRF、Cookie、CORS、npm 审计等时启用。
---

# 前端安全规范（fe-security）

团队前端侧安全要求的入口技能。细则在 `references/` 下分文件维护，按需 Read 对应文档。

## 资源路径（技能目录）

| 文档 | 内容 |
|------|------|
| `references/code-security.md` | 代码安全规范（XSS、重定向、`postMessage`、CSP 等） |
| `references/data-security.md` | 数据安全规范（存储、日志、埋点、脱敏等） |
| `references/dependency-security.md` | 依赖安全规范（lockfile、审计、供应链等） |
| `references/domain-security.md` | 域名安全（场景选域、Path 规范、k8s 命名空间、对象存储桶、Cookie/CORS 要点） |

## 何时使用

- 前端安全审查、安全相关 CR、实现前的安全自检
- 用户明确提到：XSS、注入、开放重定向、敏感信息泄露、token 存哪、CORS、Cookie、`npm audit`、依赖升级、第三方脚本域名等

## 使用方式

1. 按议题打开上表对应 `references/*.md`（不要臆造团队细则；缺项标注「待团队补充」）。
2. 输出对照 **MUST / MUST NOT / SHOULD** 与可执行的检查项。
3. 与后端/网关/运维重叠的条目在 reference 内用「见基础设施文档」一句话收口，避免重复堆砌。

## 维护说明

- 新增规范：写入对应 reference 文件，保持 MUST 可判定。
- 版本迭代：在 reference 文末可追加变更记录（可选）。
