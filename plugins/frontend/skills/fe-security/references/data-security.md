# 数据安全规范（前端）

> **定位**：浏览器侧数据的存储、传输展示、日志与上传等环节的约束。会话与鉴权细节以**后端 Set-Cookie 策略**为准；本文对齐 [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) 等与前端相关的共识，**落地以公司内部数据分级与合规要求为准**。
>
> **与 code-security 的边界**：XSS/CSRF、开放重定向、`postMessage`、CSP、以及「禁止在源码/构建物中提交密钥」的代码层面检查见 [code-security.md](./code-security.md)。本文聚焦**数据存哪、记什么、传什么**（存储、日志/埋点、URL/剪贴板、上传、密钥配置），不重复代码安全细则。

---

## 目录

- [原则](#原则)
- [1. 浏览器存储（Web Storage / IndexedDB）](#1-浏览器存储web-storage--indexeddb)
- [2. 密钥与配置（Secrets）](#2-密钥与配置secrets)
- [3. 日志、错误上报与埋点](#3-日志错误上报与埋点)
- [4. 展示、剪贴板与 URL](#4-展示剪贴板与-url)
- [5. 文件上传（前端职责）](#5-文件上传前端职责)
- [6. Web Crypto 与「前端加密」](#6-web-crypto-与前端加密)
- [检查清单（CR / 自检）](#检查清单cr--自检)
- [例外与审批](#例外与审批)
- [参考地址（数据安全规则）](#参考地址数据安全规则)

---

## 原则

1. **最小暴露**：前端只保留完成功能所必需的数据；能放服务端/HttpOnly Cookie 的凭证不要放进 JS 可读存储。
2. **不信任客户端**：展示层校验不能替代服务端；上传的 MIME/扩展名可被伪造，**安全判定在后端**。
3. **可观测但不泄密**：监控、埋点、错误上报要稳定，但**不得**写入密码、token、完整证件号等（见下文 OWASP Logging「不得记录」清单）。

---

## 1. 浏览器存储（Web Storage / IndexedDB）

**依据**：[OWASP Session Management - HTML5 Web Storage](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#html5-web-storage-api)、[WHATWG Web Storage](https://html.spec.whatwg.org/multipage/webstorage.html#webstorage)。

| 机制 | 要点（前端须知晓） |
|------|-------------------|
| **同源** | `localStorage` / `sessionStorage` 仅同 scheme + host + port 可读；与 Cookie `Secure` 类似，HTTPS 存的数据不会被 HTTP 页直接读。 |
| **持久化** | `localStorage` **跨会话持久化**，设备/配置变更前长期可读，**不适合存会话令牌或高敏感数据**（任意 XSS 可读）。 |
| **sessionStorage** | 随**标签页/窗口**隔离，关闭标签后不可再取；仍**非加密落盘**，且 XSS 可读。 |
| **IndexedDB** | 容量大、可结构化；同样受同源与 XSS 影响，敏感数据需业务加密时**密钥不能长期放前端**。 |

### MUST

- **会话标识 / 访问令牌**：优先由后端通过 **HttpOnly + Secure + SameSite** 的 Cookie 下发（见 [Session Management - Cookies](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#cookies)）；**禁止**将长期 refresh token、主站 session id 写入 `localStorage` 作为默认方案（除非安全已评估且配合短寿命与轮换）。
- **禁止**在 Storage / IndexedDB 存：**数据库连接串、服务端 API 密钥、加密主密钥**（与 [Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) 一致：密钥不进仓库与客户端长期驻留）。

### MUST NOT

- 把 **密码明文、完整银行卡号、完整身份证号** 等写入 Storage 仅图省事。
- 在 **生产构建** 中把第三方密钥硬编码进 bundle（可被任意用户解压查看）。

### SHOULD

- 非敏感 UI 状态（主题、草稿、非身份类偏好）可用 `sessionStorage` / `localStorage`；跨标签共享且可丢则用 `sessionStorage` 降低暴露窗口。
- 若业务必须用内存持短期 token，考虑**短 TTL + 登出清空**；更高要求时由架构评估 **Web Worker 内持有 secret** 等模式（仍无法防 XSS 诱导 Worker 代劳，见 OWASP Session Management *Web Workers* 一节）。
- **Vue 2 / Vue 3** 项目：Vuex、Pinia 等状态若需持久化（如 `localStorage` 插件），**不得**持久化 token、密码、完整证件号等敏感数据；会话与鉴权以 HttpOnly Cookie 或后端控制为准。

---

## 2. 密钥与配置（Secrets）

**依据**：[OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)。代码层面禁止在源码/构建物中提交密钥的检查见 [code-security.md - 敏感信息与源码/构建物](./code-security.md#5-敏感信息与源码构建物)。

- **MUST**：构建时注入的 `VITE_*` / `VUE_APP_*` / `REACT_APP_*` 等会进客户端包，**仅允许公开配置**（如公开 analytics id）；**私有 API Key、OSS 签名密钥**等须走**后端签发临时凭证**或 BFF，不得写进前端环境变量长期分发。
- **SHOULD**：密钥集中管理、轮换与最小权限在服务端/DevOps 完成；前端只消费**短时、scoped** 的 token。

---

## 3. 日志、错误上报与埋点

**依据**：[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)（*Data to exclude*、*Event collection*）。

### 通常不得明文写入日志/上报体（应脱敏、哈希或省略）

- 用户未同意或法律禁止采集的数据  
- 支付卡号、完整银行账号  
- **加密主密钥、数据库连接串、登录密码**  
- **访问令牌、Session ID**（如需关联会话可用**哈希**或内部匿名 id）  
- 高敏感 PII（健康、政务标识等，按法务定义）  
- 应用源码片段（易泄密且难控）

### 需谨慎处理后再记录

- 姓名、电话、邮箱、内部 IP、文件路径等 —— 按需 **脱敏 / 假名化**；遵守隐私政策与留存周期。

### MUST

- 上报前对字符串做 **sanitize**，避免 **log injection**（换行符、分隔符破坏下游解析或伪造条目）。  
- **不得**在 `console.log`、前端异常栈、第三方监控自定义字段中输出 **token、密码、完整请求体中的敏感字段**（生产环境应关闭或过滤调试输出）。

### SHOULD

- 埋点字段**白名单**；与产品/数据团队对齐 **PII 分级**。  
- 错误上报带 **交互 id**、版本、路由等便于排障，而非用户密码。

---

## 4. 展示、剪贴板与 URL

- **MUST NOT**：在 URL query/hash 中传递 **密码、长期 token**（Referer、历史、分享链接易泄露）。  
- **SHOULD**：列表中的手机号、证件号、邮箱等按规范 **掩码**；导出/复制敏感内容需二次确认或权限控制。  
- 使用 [Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API) 时仅复制必要字段，不扩大敏感面。

---

## 5. 文件上传（前端职责）

**依据**：[OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)。

**攻击面简述**：恶意内容（XSS/HTML）、ZIP bomb、超大文件 DoS、解析器漏洞等；**Content-Type 由客户端指定，不可信**。

| 层级 | 要求 |
|------|------|
| **前端 MUST** | **大小上限**、**扩展名/业务允许类型**提示；禁止仅依赖 `input.accept` 或 MIME 作为安全边界。 |
| **前端 SHOULD** | 分片/断点与后端约定；敏感文件走**鉴权上传**与**私有桶**（与 `domain-security` 存储桶规范一致）。 |
| **后端 MUST** | 白名单扩展、内容校验、存储路径与权限；前端**不能替代**上述控制。 |

---

## 6. Web Crypto 与「前端加密」

**依据**：[MDN Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)。

- 浏览器可提供哈希、对称/非对称运算；**密钥若放在 JS/Storage，XSS 即可窃取**。  
- **MUST NOT** 用「前端藏密钥」代替 HTTPS 与服务端保护。  
- 合规传输依赖 **TLS**；端到端场景由**专门方案**设计，不在此 skill 臆造。

---

## 检查清单（CR / 自检）

- [ ] 是否在 `localStorage` 长期放了可冒充用户的 token？能否改为 HttpOnly Cookie 或缩短寿命？  
- [ ] 环境变量、构建产物中是否出现 **私有 API Key**？  
- [ ] 监控/日志/埋点是否含 **密码、token、完整证件号、卡号**？  
- [ ] 生产是否仍向控制台打印敏感对象？  
- [ ] 上传是否仅有前端校验、无后端类型/大小/内容策略？  
- [ ] 分享链接是否夹带 **session 或 refresh token**？

---

## 例外与审批

- 新业务必须在 Storage 存 token、或埋点必须采某类 PII：**安全/架构 + 合规**书面或流程审批，并写明留存与脱敏策略。

---

## 参考地址（数据安全规则）

以下为数据安全规则相关权威参考，便于延伸阅读与审计对照。**XSS/CSRF/CSP/postMessage 等代码安全参考见 [code-security.md](./code-security.md)**。

### OWASP Cheat Sheets（存储、会话、密钥、日志、上传）

| 主题 | 链接 | 说明 |
|------|------|------|
| 会话与 Cookie、Web Storage 使用约束 | [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) | 同源、HttpOnly/Secure/SameSite、HTML5 Storage 注意点 |
| 密钥与配置（不进仓库与客户端长期驻留） | [Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) | 与本文「密钥与配置」一节对齐 |
| 日志与脱敏（不得记录项、Data to exclude） | [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) | 敏感数据不写日志、log injection 防范 |
| 文件上传（前端职责与后端必须校验） | [File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) | 类型/大小/内容校验、存储路径与权限 |

### OWASP 测试指南（浏览器存储）

| 主题 | 链接 | 说明 |
|------|------|------|
| 浏览器存储安全测试 | [WSTG - Testing Browser Storage (WSTG-CLNT-12)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/12-Testing_Browser_Storage) | 客户端存储敏感数据与注入测试要点 |

### 标准与规范（Web Storage、隐私、Crypto）

| 主题 | 链接 | 说明 |
|------|------|------|
| Web Storage 标准 | [WHATWG HTML - Web Storage](https://html.spec.whatwg.org/multipage/webstorage.html#webstorage) | localStorage / sessionStorage 同源与持久化语义 |
| Web Storage（W3C 第二版） | [W3C Web Storage, 2nd ed](https://www.w3.org/TR/2021/SPSD-webstorage-20210128/) | 规范参考 |
| 安全与隐私自评问卷 | [W3C Self-Review Questionnaire: Security and Privacy](https://www.w3.org/TR/security-privacy-questionnaire/) | 新特性/存储类能力评估用 |
| 隐私原则（产品对齐） | [W3C Privacy Principles](https://www.w3.org/TR/privacy-principles/) | 隐私设计原则 |
| Storage 访问与分区 | [Storage Access (Privacy CG)](https://privacycg.github.io/storage-access-headers) | 跨站存储访问策略 |
| Web Crypto API | [MDN Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API) | 浏览器加密能力与密钥不可长期放前端 |

### MDN（存储与 Cookie）

| 主题 | 链接 | 说明 |
|------|------|------|
| Web Storage API | [MDN Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API) | localStorage / sessionStorage 用法与限制 |
| HTTP Cookie | [MDN Using HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) | Cookie 属性与安全相关行为 |
| Clipboard API | [MDN Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API) | 剪贴板与敏感内容复制 |

### Vue 2 / Vue 3（数据安全相关）

| 主题 | 链接 | 说明 |
|------|------|------|
| Vue 3 安全实践 | [Vue 3 - Security](https://vuejs.org/guide/best-practices/security.html) | 官方安全说明；数据存储与敏感信息见本文，XSS 等见 code-security |
| Vue 2 安全实践 | [Vue 2 - Security](https://v2.vuejs.org/v2/guide/security.html) | 同上，Vue 2 项目 |

说明：Vue 官方安全页以 XSS、模板信任、依赖更新为主，**敏感数据不存客户端、会话用 HttpOnly Cookie** 等数据安全规则以本文与 OWASP Session/Secrets/Logging 为准；Vue 技术栈下 Pinia/Vuex 等状态库同样不应持久化 token/密码等敏感数据到 Storage。
