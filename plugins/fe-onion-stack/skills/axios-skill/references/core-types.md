---
name: types
description: API 请求和响应的 TypeScript 类型定义
---

# 类型定义

为 API 响应、请求参数和数据模型定义一致的类型。

## 响应类型

```ts
// src/api/types/common.ts

/** 标准 API 响应包装 */
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

/** 分页参数 */
export interface PageParams {
  pageIndex: number
  pageSize: number
}

/** 分页数据 */
export interface PageData<T> {
  list: T[]
  total: number
}

export type PageResponse<T> = ApiResponse<PageData<T>>
```

---

## 模型类型

```ts
// src/api/types/user.ts

export type UserStatus = 'active' | 'inactive' | 'banned'
export type UserRole = 'admin' | 'user' | 'guest'

export interface UserInfo {
  id: string
  username: string
  email: string
  avatar?: string
  status: UserStatus
  role: UserRole
  createdAt: number
  updatedAt: number
}

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  refreshToken: string
  expiresIn: number
  user: UserInfo
}
```

---

## 类型工具

```ts
// src/api/types/utils.ts

/** 从 ApiResponse 中提取 data 类型 */
export type ExtractData<T> = T extends ApiResponse<infer D> ? D : never

/** 创建参数类型（排除 id 和时间戳） */
export type CreateParams<T> = Omit<T, 'id' | 'createdAt' | 'updatedAt'>

/** 更新参数类型 */
export type UpdateParams<T> = Partial<CreateParams<T>> & { id: string }
```

---

## 类型导出

```ts
// src/api/types/index.ts
export * from './common'
export * from './user'
export * from './utils'
```

## 命名规范

| 类型 | 后缀 | 示例 |
|------|------|------|
| 请求参数 | `Params` | `LoginParams`、`UserListParams` |
| 响应数据 | 实体名或 `Result` | `UserInfo`、`LoginResult` |
| 列表查询 | `ListParams` | `UserListParams` |

## 使用示例

```ts
import { instance } from '../instance'
import type { ApiResponse } from '../types/common'
import type { UserInfo } from '../types/user'

// ✅ 始终指定泛型类型
const res = await instance.get<ApiResponse<UserInfo>>('/user/info')

// ❌ 避免无类型请求
const res = await instance.get('/user/info')
```
