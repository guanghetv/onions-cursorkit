# 前端代码规范（精简版）

## 1. 命名规范

- **变量/函数**: `camelCase` (例: `userName`, `fetchData`)
- **常量**: `UPPER_SNAKE_CASE` (例: `API_URL`, `MAX_RETRIES`)
- **类型/接口**: `PascalCase` (例: `User`, `ApiResponse`)
- **组件**: `PascalCase` (例: `UserTable`, `LoginModal`)
- **文件夹**: `camelCase` (例: `userManagement`)
- **文件**: `camelCase` (例: `userManagement`)
- **布尔值**: 使用 `is`, `has`, `can` 开头 (例: `isVisible`, `hasPermission`)
- **事件处理函数**: 使用 `handle` 或 `on` 开头 (例: `handleClick`, `onSubmit`)

## 2. 组件设计

- **高内聚、低耦合**: 组件内部逻辑紧密，对外依赖最小。
- **通信**: 
    - **父传子**: 使用 `props`。
    - **子传父**: 使用回调函数。
    - **跨层级**: 谨慎使用 `Context` 或状态管理库。
- **接口(Props)**: 组件 `Props` 定义应清晰、类型化，非必需属性使用 `?` 标记。


## 3. TypeScript

- **禁止 `any`**: 避免使用 `any`，优先使用具体类型、`unknown` 或泛型。
- **类型定义**: 优先使用具体类型，其次是联合类型，必要时使用泛型。

## 4. 安全校验规范

### 🚨 高危安全关键词检测
以下关键词出现时需要**严厉警示**并重点审查：

#### 🔴 XSS风险关键词
- `innerHTML`、`outerHTML`
- `document.write`、`document.writeln`
- `eval()`、`Function()`
- `setTimeout(string)`、`setInterval(string)`
- `v-html` (Vue.js)
- `dangerouslySetInnerHTML` (React)

#### 🔴 敏感关键词
- **根域名直接使用**: 检测直接使用 `yangcong345.com` 根域名的情况
  - ⚠️ **需要告警的情况**: `https://yangcong345.com/`、`http://yangcong345.com/`、`yangcong345.com/api` 等直接使用根域名的URL
  - ✅ **无需告警的情况**: `https://fp.yangcong345.com/`、`https://api.yangcong345.com/`、`https://cdn.yangcong345.com/` 等子域名使用

**⚠️ 安全审查要求：**
- 发现需要告警的情况时，必须使用 🚨 图标进行严厉警示，并在Review结果中回显关键词
- **根域名检测规则**: 只有当代码中出现直接使用 `yangcong345.com` 根域名的URL时才告警，子域名使用（如 `*.yangcong345.com`）无需告警


