---
name: fe-security
description: >-
  团队前端安全与供应链对照技能：从 references 拉取细则，输出 MUST/MUST NOT/SHOULD 与可执行检查项。
  覆盖代码安全（XSS、v-html 消毒、DOM sink、开放重定向、postMessage origin、CSRF 配合、CSP 兼容、密钥不进 client bundle）、
  数据安全（localStorage/sessionStorage/IndexedDB、HttpOnly Cookie、环境变量公开性、日志/埋点/上报脱敏、URL 与剪贴板、上传前端职责、Web Crypto 边界）、
  依赖安全（lockfile、pnpm/npm audit、飞书《现有技术选型》白名单与禁止包表、内部 @guanghe-pub 包优先）、
  域名安全（场景主域名、Path 优于子域、k8s 命名空间 7to12/teacherschool/wuhan、对象存储桶按类型、Cookie Domain/CORS/第三方脚本域）。
  在用户做前端安全审查、安全向 Code Review/PR、实现前自检，或提到 XSS、注入、敏感信息泄露、token 存哪、Pinia/Vuex 持久化敏感数据、
  Sentry/监控字段、npm audit、供应链、postMessage、重定向参数、域名/存储桶/Ingress/命名空间 时启用。
---

# 前端安全规范（fe-security）

团队前端侧安全要求的入口。**细则只在 `references/`**；按需 Read，禁止臆造团队域名/桶名/选型结论。

## 按议题选文件

| 文档 | 何时 Read |
|------|-----------|
| `references/code-security.md` | XSS、`v-html`/innerHTML、开放重定向、`postMessage`、CSRF 前端配合、CSP、源码/构建物密钥 |
| `references/data-security.md` | Storage/Cookie、环境变量、日志与埋点、URL/剪贴板、上传前端校验、前端加密边界 |
| `references/dependency-security.md` | 新增依赖、lockfile、audit、选型表、禁止包与组件库场景 |
| `references/domain-security.md` | 页面/活动域名、Path、命名空间、OSS 桶类型、Cookie/CORS/第三方脚本（与网关文档冲突时以后者为准） |

## 执行步骤

1. 根据用户议题或改动面，Read 上表中**必要**的 reference（可多篇，不要全文堆砌到回复里）。
2. 对照文中 **MUST / MUST NOT / SHOULD** 与文末检查清单，输出：**结论**（通过/风险/需确认）+ **条目化依据** + **建议改法**；缺团队明文规定的写「待团队补充」，不编造。
3. 与后端/网关/运维重叠处：reference 内已用「见基础设施文档」收口的，不重复展开。

## 维护

新增或变更规范：写入对应 `references/*.md`，保持 MUST 可判定；与飞书选型表/域名规范冲突时**以飞书最新版为准**，并同步更新本 skill 引用段落。
