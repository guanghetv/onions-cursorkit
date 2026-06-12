---
name: api-convention
description: Vue/Vite 项目的 API 层规范，涵盖类型定义、拦截器、环境配置和模块组织。
---

# API Convention

Vue/Vite 项目中 API 层的规范与最佳实践，包括 TypeScript 类型定义、拦截器、环境配置和模块化组织。

## 参考

| 主题 | 描述 | 参考 |
|------|------|------|
| 类型定义 | 响应类型、请求参数、泛型、类型工具 | [core-types](references/core-types.md) |
| 拦截器 | 请求/响应拦截器、错误处理 | [features-interceptors](references/features-interceptors.md) |
| 环境配置 | .env 文件、代理配置、多环境设置 | [features-environment](references/features-environment.md) |
| 常用模式 | 目录结构、API 模块组织、Mock、组合式函数 | [best-practices-patterns](references/best-practices-patterns.md) |

## 关键建议

- **创建 axios 实例**：使用 `axios.create()` 而非全局 axios
- **使用 TypeScript 泛型**：类型安全的请求响应 `instance.get<ApiResponse<UserInfo>>('/user')`
- **集中错误处理**：在响应拦截器中统一处理，而非每个 API 调用
- **按模块组织**：每个业务域一个文件，直接导出函数 `getUserInfo()`、`login()`
- **使用 `import.meta.env`**：在 Vite 中配置环境相关的 API 地址
- **401 直接登出**：清除凭证并跳转登录页
