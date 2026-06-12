---
name: interceptors
description: 请求/响应拦截器，用于认证和错误处理
---

# 拦截器

使用拦截器全局处理认证、错误处理和请求转换。

## 请求拦截器

```ts
// src/api/instance.ts
import type { InternalAxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'

instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)
```

## 响应拦截器

```ts
import type { AxiosResponse, AxiosError } from 'axios'
import type { ApiResponse } from './types'

instance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response

    if (!data.success) {
      handleBusinessError(data)
      return Promise.reject(new Error(data.message))
    }

    return response
  },
  (error: AxiosError<ApiResponse>) => {
    handleHttpError(error)
    return Promise.reject(error)
  },
)
```

---

## HTTP 状态码规范

> 参考：[HTTP 状态码规范](https://guanghe.feishu.cn/wiki/LFIXw0Xz8i7H0fkU2dLc5moNnAd)

### 常用状态码

| 状态码 | 含义 | 前端处理策略 |
|--------|------|-------------|
| 200 | 请求成功且有数据返回 | 正常处理 |
| 204 | 请求成功但无数据返回 | 正常处理，不读取 body |
| 400 | 参数错误（类型错误、缺少必填项） | 提示用户修正输入 |
| 401 | 登录凭证不存在或失效 | 清除凭证，跳转登录页 |
| 403 | 没有访问资源的权限 | 提示无权限，可跳转至无权限页 |
| 409 | 状态冲突（业务限制、重复请求） | 根据 `reason` 字段做定制化处理 |
| 500 | 服务器内部错误 | 提示系统异常，可触发重试 |
| 502 | 网关错误 | 提示服务暂不可用，触发重试 |
| 503 | 服务不可用 | 提示服务暂不可用，触发重试 |
| 504 | 网关超时 | 提示请求超时，触发重试 |

### 错误响应格式

后端返回的错误响应应遵循统一格式：

```ts
// src/api/types/common.ts

interface ErrorResponse {
  code: number
  message: string
  /** 业务错误标识，用于前端定制化处理 */
  reason: string
  metadata: Record<string, unknown>
}
```

示例：

```json
{
  "code": 409,
  "message": "书桌已经被抢占",
  "reason": "DESKTOP_HAS_CONFLICT",
  "metadata": {}
}
```

---

## 错误处理

```ts
import router from '@/router'

type ErrorHandler = (error: AxiosError<ApiResponse>) => void

const HttpErrorMessages: Record<number, string> = {
  400: '请求参数错误',
  401: '登录凭证已失效',
  403: '没有访问权限',
  409: '操作冲突，请稍后重试',
  500: '服务器内部错误',
  502: '网关错误，服务暂不可用',
  503: '服务暂不可用',
  504: '网关超时，请稍后重试',
}

const httpErrorHandlers: Partial<Record<number, ErrorHandler>> = {
  401: () => {
    const userStore = useUserStore()
    userStore.logout()
    router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } })
  },
  403: () => {
    router.push({ name: 'Forbidden' })
  },
}

function handleHttpError(error: AxiosError<ApiResponse>) {
  const status = error.response?.status

  if (!status) {
    // 无响应：网络断开或请求被取消
    if (error.code === 'ERR_CANCELED') return
    console.error('网络连接失败，请检查网络')
    return
  }

  const handler = httpErrorHandlers[status]
  if (handler) {
    handler(error)
    return
  }

  const message = HttpErrorMessages[status] || `请求失败 (${status})`
  console.error(message)
}

function handleBusinessError(data: ApiResponse) {
  // 409 冲突错误：可根据 reason 字段定制处理
  // if (data.reason === 'DESKTOP_HAS_CONFLICT') { ... }

  console.error(`[${data.code}] ${data.message}`)
}
```

