# 代码安全规范（前端）

> **定位**：前端代码层面的安全约束——XSS/注入、CSRF 配合方式、开放重定向、`postMessage`、CSP 等。与**数据安全**的边界：存储/日志/脱敏/密钥管理见 [data-security.md](./data-security.md)；本文聚焦**渲染、跳转、跨窗口通信与安全头**。  
> 技术栈以 **Vue 2 / Vue 3** 为主，规则需可判定、可审查。

---

## 原则

1. **默认转义、显式放行**：框架默认转义（如 Vue 的 `{{ }}`）不绕过；只有确需 HTML 时再经白名单/消毒后使用（如 `v-html` + 消毒库）。
2. **不信任输入**：URL 参数、`postMessage` 载荷、第三方脚本返回内容均视为不可信，使用前校验来源与格式。
3. **纵深防御**：XSS 防护依赖输出编码/消毒 + CSP 等；CSRF 依赖后端校验，前端正确携带 token 不替代服务端验证。

---

## 1. XSS（跨站脚本）

**依据**：[OWASP Cross-Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)、[DOM based XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)、[Vue - Security](https://v3.vuejs.org/guide/security.html)（Vue 3）、[Vue 2 - Security](https://v2.vuejs.org/v2/guide/security.html)（Vue 2）。

| 场景 | 要点 |
|------|------|
| **模板插值** | Vue 的 `{{ data }}` 会转义，**禁止**为绕过转义而把未消毒内容交给可执行上下文。 |
| **v-html** | 仅用于**可信或已消毒**的 HTML；用户输入、URL 参数、接口返回的 HTML 必须经消毒（如 DOMPurify 或团队认可的库）后再用 `v-html`。 |
| **危险 Sink** | 避免把不可信数据写入 `innerHTML`、`document.write`、`eval`、`setTimeout(string)`、`location.href`/`location` 等；若框架外有原生 DOM 操作，须按上下文做编码或消毒。 |
| **DOM XSS 源** | 不可信数据常来自 `location.hash`、`location.search`、`postMessage`、`window.name`、部分 Storage；流入上述 Sink 前必须校验或编码。 |

### MUST

- 使用 `v-html` 时，**必须**对不可信内容先做 HTML 消毒（白名单标签/属性），再渲染。
- 禁止将**用户可控或接口未消毒**的字符串直接赋给 `innerHTML`、`eval` 或作为脚本 URL（如 `script.src`、`a.href` 的 `javascript:`）。

### MUST NOT

- 禁止为「方便渲染」而对用户输入、URL 或第三方数据使用 `v-html` 且不做消毒。
- 禁止在富文本、Markdown 渲染管线中跳过消毒步骤（若使用 Markdown，需使用安全配置/插件，避免产出可执行脚本）。

### SHOULD

- 优先用文本展示或组件化结构替代原始 HTML；确需富文本时采用成熟消毒库（如 DOMPurify）并限定允许的标签/属性。
- Vue 项目可考虑 `vue-dompurify-html`（Vue 3）等插件，在统一指令层做消毒，避免散落 `v-html`。

---

## 2. CSRF（跨站请求伪造）

**依据**：[OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)。

- **前端职责**：对状态变更请求（POST/PUT/DELETE 等）按后端要求携带 CSRF token（如自定义 Header、或表单隐藏域）；token 的生成与校验在**服务端**。
- **MUST**：若后端采用 CSRF token 方案，前端**必须**在所有会改变状态的请求中携带（通常不用于只读 GET）。
- **MUST NOT**：禁止在 GET 或可被缓存的请求 URL 中放置 CSRF token（易泄露）；token 的存储与生命周期见 [data-security.md - 存储与 Cookie](./data-security.md#1-浏览器存储web-storage--indexeddb)。
- **注意**：XSS 可窃取或伪造 token，因此 XSS 防护是 CSRF 有效的前提。

---

## 3. 开放重定向与不可信 URL 跳转

**依据**：[OWASP Unvalidated Redirects and Forwards](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)、[CWE-601: Open Redirect](https://cwe.mitre.org/data/definitions/601.html)。

- 跳转目标**不得**仅依赖用户输入（如 `?redirect=`、`?url=`）且未校验即用于 `window.location`、`location.href` 或服务端 302 Location。
- **MUST**：重定向目标应为**白名单**（相对路径或允许的域名列表）；若必须接受 URL 参数，则解析后与白名单比对，禁止使用「黑名单」或仅校验协议。
- **MUST NOT**：禁止 `window.location = userInput` 或 `router.push(userInput)` 且 `userInput` 未做白名单校验。

---

## 4. postMessage

**依据**：[MDN Window.postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)、[MDN message 事件](https://developer.mozilla.org/en-US/docs/Web/API/Window/message_event)、[OWASP WSTG - Web Messaging](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/11-Testing_Web_Messaging)。

| 角色 | 要求 |
|------|------|
| **发送方** | 使用具体 `targetOrigin`，禁止对含敏感信息的消息使用 `*`。 |
| **接收方** | **必须**校验 `event.origin` 是否在预期域名列表内；将 `event.data` 视为不可信，校验数据形状与类型后再使用，避免注入或非法结构导致异常。 |

### MUST

- 在 `message` 监听器中**必须**判断 `event.origin`，仅处理来自受信任源的报文。
- 对 `event.data` 做结构/类型校验后再参与业务逻辑或写入 DOM。

### MUST NOT

- 禁止在未校验 `origin` 的情况下根据 `event.data` 执行跳转、写 `innerHTML` 或执行脚本。

---

## 5. 敏感信息与源码/构建物

**依据**：[OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)；与 [data-security.md - 密钥与配置](./data-security.md#2-密钥与配置secrets) 对齐。

- **MUST NOT**：禁止在源码或仓库中提交**私密 API Key、数据库连接串、签名密钥**等；禁止在生产 client bundle 中打包上述密钥。
- 构建时注入的环境变量（如 `VITE_*`、`VUE_APP_*`）会进入前端包，**仅允许公开配置**；私有凭证须走后端或 BFF 签发短时 token，详见 data-security。

---

## 6. CSP 与安全头

**依据**：[MDN Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)、[CSP script-src](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src)。

- CSP 通常由**服务端/网关**或构建部署环节下发（如 `Content-Security-Policy` 响应头）；前端可参与**策略建议**与**自检**（避免内联脚本、未授权域名等）。
- **SHOULD**：与运维/后端约定至少包含 `script-src`、`default-src` 等，限制脚本与资源来源，降低 XSS 影响面；若使用非内联脚本且无 `eval`，在策略中显式限制。
- 前端不单独「实现」CSP，但代码层面应避免依赖内联事件（如 `onclick="..."`）或未受控的 `eval`/`new Function`，以便与严格 CSP 兼容。

---

## 检查方式（CR / 自检）

- [ ] 是否对用户输入、URL 或接口返回使用了 `v-html` 且未消毒？
- [ ] 是否存在 `innerHTML`、`document.write`、`eval(unknown)` 且输入不可信？
- [ ] 重定向是否仅依赖用户可控参数且无白名单校验？
- [ ] `postMessage` 监听是否校验 `event.origin` 并对 `event.data` 做形状校验？
- [ ] 状态变更请求是否按后端要求携带 CSRF token？
- [ ] 源码或构建产物中是否出现私密密钥或不应公开的配置？（可与 data-security 检查合并）

---

## 例外与审批

- 必须使用未消毒 HTML 或放宽 CSP 的：**安全/架构**评审并记录原因与缓解措施。
- 临时开放重定向白名单或 postMessage 新来源：需**代码评审**并注明允许的域名/路径。

---

## 参考链接汇总

| 主题 | 链接 |
|------|------|
| XSS 防护（通用） | [OWASP Cross-Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) |
| DOM XSS | [OWASP DOM based XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html) |
| Vue 3 安全 | [Vue 3 - Security](https://v3.vuejs.org/guide/security.html) |
| Vue 2 安全 | [Vue 2 - Security](https://v2.vuejs.org/v2/guide/security.html) |
| CSRF 防护 | [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) |
| 开放重定向 | [OWASP Unvalidated Redirects and Forwards](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) |
| 开放重定向（CWE） | [CWE-601: URL Redirection to Untrusted Site](https://cwe.mitre.org/data/definitions/601.html) |
| postMessage 发送 | [MDN Window.postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) |
| postMessage 接收 | [MDN Window: message event](https://developer.mozilla.org/en-US/docs/Web/API/Window/message_event) |
| Web Messaging 测试 | [OWASP WSTG - Testing Web Messaging](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/11-Testing_Web_Messaging) |
| CSP 总览 | [MDN Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) |
| CSP script-src | [MDN CSP script-src](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src) |
| 密钥管理（与 data-security 共用） | [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) |
