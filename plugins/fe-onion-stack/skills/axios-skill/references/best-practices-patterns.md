---
name: patterns
description: API 模块组织、Mock 和组合式函数的常用模式
---

# 常用模式

API 模块组织、MSW Mock 和组合式函数的最佳实践。

## 目录结构

```
src/api/
├── instance.ts       # Axios 实例与拦截器
├── types/            # 类型定义
│   ├── index.ts      # 统一导出
│   ├── common.ts     # 通用类型（ApiResponse、PageData）
│   └── user.ts       # 用户模块类型
└── modules/          # API 模块
    ├── user.ts       # 用户模块
    └── product.ts    # 商品模块
```

**按模块导入（推荐）：**

```ts
import { getUserInfo, login } from '@/api/modules/user'
import { getProductList } from '@/api/modules/product'

import type { UserInfo, LoginParams } from '@/api/types/user'
import type { PageData, ApiResponse } from '@/api/types/common'
```

---

## Axios 实例

```ts
// src/api/instance.ts
import axios from 'axios'

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export { instance }
```

---

## API 模块定义

```ts
// src/api/modules/user.ts
import { instance } from '../instance'
import type { UserInfo, LoginParams, LoginResult } from '../types/user'
import type { ApiResponse, PageData } from '../types/common'

export function getUserInfo() {
  return instance.get<ApiResponse<UserInfo>>('/user/info')
}

export function login(data: LoginParams) {
  return instance.post<ApiResponse<LoginResult>>('/auth/login', data)
}

export function getUserList(params: { page: number; pageSize: number }) {
  return instance.get<ApiResponse<PageData<UserInfo>>>('/user/list', { params })
}
```

---

## 文件上传

```ts
// src/api/modules/upload.ts
import { instance } from '../instance'
import type { ApiResponse } from '../types/common'

export function uploadFile<T>(
  url: string,
  file: File,
  onProgress?: (percent: number) => void,
) {
  const formData = new FormData()
  formData.append('file', file)

  return instance.post<ApiResponse<T>>(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
}
```

## 文件下载

```ts
export async function downloadFile(url: string, filename?: string) {
  const res = await instance.get(url, { responseType: 'blob' })
  const blob = new Blob([res.data])
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename || 'download'
  link.click()
  URL.revokeObjectURL(link.href)
}
```

---

## 组件中调用 API

### 基础用法

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUserInfo } from '@/api/modules/user'
import type { UserInfo } from '@/api/types/user'

const userInfo = ref<UserInfo>()
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    userInfo.value = await getUserInfo()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="userInfo">
    <h1>{{ userInfo.username }}</h1>
    <p>{{ userInfo.email }}</p>
  </div>
</template>
```

### 搜索防抖

```vue
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { searchUser } from '@/api/modules/user'
import type { UserInfo } from '@/api/types/user'

const keyword = ref('')
const results = ref<UserInfo[]>([])
const loading = ref(false)

const doSearch = useDebounceFn(async (value: string) => {
  if (!value.trim()) {
    results.value = []
    return
  }
  loading.value = true
  try {
    const data = await searchUser({ keyword: value })
    results.value = data.list
  } finally {
    loading.value = false
  }
}, 300)

watch(keyword, doSearch)
</script>

<template>
  <input v-model="keyword" placeholder="搜索用户" />
  <div v-if="loading">搜索中...</div>
  <ul v-else>
    <li v-for="user in results" :key="user.id">{{ user.username }}</li>
  </ul>
</template>
```

---

## MSW Mock

```ts
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/user/info', () => {
    return HttpResponse.json({
      code: 0,
      success: true,
      data: { id: '1', username: 'admin' },
    })
  }),

  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json()
    if (body.password === '123456') {
      return HttpResponse.json({
        code: 0,
        success: true,
        data: { token: 'mock-token' },
      })
    }
    return HttpResponse.json({ code: 2003, success: false })
  }),
]

// src/mocks/browser.ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)

// main.ts
if (import.meta.env.DEV) {
  const { worker } = await import('./mocks/browser')
  worker.start({ onUnhandledRequest: 'bypass' })
}
```

---

## 组合式函数

```ts
import { ref, shallowRef } from 'vue'

export function useRequest<T, P extends unknown[]>(
  fetcher: (...args: P) => Promise<T>,
) {
  const data = shallowRef<T>()
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute(...args: P) {
    loading.value = true
    error.value = null
    try {
      data.value = await fetcher(...args)
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, execute }
}

// 使用示例
const { data, loading, execute } = useRequest(getUserInfo)
await execute()
```
