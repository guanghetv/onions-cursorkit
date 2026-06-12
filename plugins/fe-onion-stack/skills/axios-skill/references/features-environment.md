---
name: environment
description: API 地址的环境配置
---

# 环境配置

使用 Vite 环境变量配置不同环境的 API 地址。

## 环境与分支对应

| 分支 | 环境 | mode | 说明 |
|------|------|------|------|
| `dev` | 开发环境 | `dev` | 日常开发调试 |
| `test` | 测试环境 | `test` | QA 验证 |
| `stage` | 预发环境 | `stage` | 上线前验收 |
| `master` | 生产环境 | `master` | 正式线上 |

## 环境文件

```
project/
├── .env                  # 共享配置（提交到仓库）
├── .env.local            # 本地覆盖（git 忽略）
├── .env.dev              # 开发环境 (dev 分支)
├── .env.test             # 测试环境 (test 分支)
├── .env.stage            # 预发环境 (stage 分支)
├── .env.master           # 生产环境 (master 分支)
```

## 变量定义

只有 `VITE_` 前缀的变量会暴露给客户端：

```bash
# .env.dev (dev)
VITE_API_BASE_URL=http://localhost:3000/api
VITE_UPLOAD_URL=http://localhost:3000/upload

# .env.test (test)
VITE_API_BASE_URL=https://test-api.example.com
VITE_UPLOAD_URL=https://test-upload.example.com

# .env.stage (stage)
VITE_API_BASE_URL=https://stage-api.example.com
VITE_UPLOAD_URL=https://stage-upload.example.com

# .env.master (master)
VITE_API_BASE_URL=https://api.example.com
VITE_UPLOAD_URL=https://upload.example.com
```

---

## 类型声明

```ts
// src/env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_UPLOAD_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## 使用方式

```ts
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// 环境判断
if (import.meta.env.DEV) {
  console.log('开发环境')
}
```

---

## 代理配置

```ts
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})
```

## 构建命令

```json
{
  "scripts": {
    "dev": "vite",
    "build:test": "vite build --mode test",
    "build:stage": "vite build --mode stage",
    "build:master": "vite build --mode master"
  }
}
```
