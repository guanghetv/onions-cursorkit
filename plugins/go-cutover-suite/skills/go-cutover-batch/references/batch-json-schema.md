# 批次 JSON Schema

## 顶层 Batch

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["batchId", "tasks", "feishuAlertOpenId"],
  "properties": {
    "batchId": {
      "type": "string",
      "description": "批次唯一ID，格式: batch-YYYYMMDD-NNN",
      "example": "batch-20260403-001"
    },
    "description": {
      "type": "string",
      "description": "批次描述"
    },
    "feishuAlertOpenId": {
      "type": "string",
      "description": "告警目标用户的飞书 open_id（ou_ 开头）"
    },
    "SOURCEGRAPH_URL": {
      "type": "string",
      "default": "https://sourcegraph.yc345.tv"
    },
    "SOURCEGRAPH_TOKEN": {
      "type": "string",
      "description": "兼容字段；通常不需要手工填写。优先从环境变量获取，若缺失或失效，执行器会在批次开始前自动刷新"
    },
    "GITLAB_URL": {
      "type": "string",
      "default": "https://gitlab.yc345.tv"
    },
    "GITLAB_TOKEN": {
      "type": "string",
      "description": "可选；用于 GitLab API 查询/创建 Merge Request，如省略则优先尝试 git push options"
    },
    "workspaceRoot": {
      "type": "string",
      "default": "~/work"
    },
    "oldServiceName": {
      "type": "string",
      "description": "批次级默认老服务名；任务未单独填写时继承"
    },
    "newServiceName": {
      "type": "string",
      "description": "批次级默认新服务名；任务未单独填写时继承"
    },
    "oldNamespace": {
      "type": "string",
      "description": "批次级默认老 namespace；任务未单独填写时继承"
    },
    "newNamespace": {
      "type": "string",
      "description": "批次级默认新 namespace；任务未单独填写时继承"
    },
    "oldServiceHint": {
      "type": "string",
      "description": "批次级默认老服务 hint；任务未单独填写时继承"
    },
    "newServiceHint": {
      "type": "string",
      "description": "批次级默认新服务 hint；任务未单独填写时继承"
    },
    "maxConcurrent": {
      "type": "integer",
      "default": 1,
      "description": "当前实现仅支持 1，始终顺序执行"
    },
    "defaultTimeout": {
      "type": "integer",
      "default": 1800,
      "description": "单任务超时秒数"
    },
    "retryLimit": {
      "type": "integer",
      "default": 2
    },
    "tasks": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/definitions/Task" }
    }
  }
}
```

## Task 定义

```json
{
  "definitions": {
    "Task": {
      "type": "object",
      "required": ["oldRoute", "newRoute", "method", "branch"],
      "properties": {
        "taskId": {
          "type": "string",
          "description": "任务唯一ID；如省略，由执行器自动生成",
          "example": "route-cutover-20260403-0001"
        },
        "oldRoute": {
          "type": "string",
          "description": "老路由路径",
          "example": "/admin-room/list"
        },
        "newRoute": {
          "type": "string",
          "description": "新路由路径",
          "example": "/teacher-school/admin-room/list"
        },
        "method": {
          "type": "string",
          "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
          "example": "GET"
        },
        "branch": {
          "type": "string",
          "description": "目标 Git 分支",
          "example": "feat/m-6920925476"
        },
        "oldServiceName": {
          "type": "string",
          "description": "任务级覆盖老服务名；如省略，继承批次级默认值",
          "example": "teacher"
        },
        "newServiceName": {
          "type": "string",
          "description": "任务级覆盖新服务名；如省略，继承批次级默认值",
          "example": "teacher-school"
        },
        "oldNamespace": {
          "type": "string",
          "description": "任务级覆盖老 namespace；如省略，继承批次级默认值",
          "example": "teacherschool"
        },
        "newNamespace": {
          "type": "string",
          "description": "任务级覆盖新 namespace；如省略，继承批次级默认值",
          "example": "teacherschool"
        },
        "oldServiceHint": {
          "type": "string",
          "description": "任务级覆盖老服务 hint；如省略，继承批次级默认值，通常可由 serviceName.namespace 生成",
          "example": "teacher.teacherschool"
        },
        "newServiceHint": {
          "type": "string",
          "description": "任务级覆盖新服务 hint；如省略，继承批次级默认值，通常可由 serviceName.namespace 生成",
          "example": "teacher-school.teacherschool"
        },
        "workspaceRoot": {
          "type": "string",
          "description": "覆盖批次级 workspaceRoot"
        },
        "targetRepos": {
          "type": "array",
          "items": { "type": "string" },
          "description": "兼容旧格式保留；新批次不再推荐手填"
        },
        "gatewayRepos": {
          "type": "array",
          "items": { "type": "string" },
          "description": "高优先级网关仓库；默认 `onions-school`, `channel-platform-server`, `channel`, `teacher-tenant`"
        },
        "apisixAdminURL": {
          "type": "string",
          "description": "单个 APISIX Admin API routes 地址"
        },
        "apisixAdminURLs": {
          "type": "array",
          "items": { "type": "string" },
          "description": "多个 APISIX Admin API routes 地址"
        },
        "apisixAdminKeyEnvVar": {
          "type": "string",
          "description": "APISIX X-API-KEY 所在环境变量名，不是 key 值本身",
          "default": "APISIX_ADMIN_KEY"
        },
        "timeout": {
          "type": "integer",
          "description": "覆盖批次级 timeout"
        },
        "retryLimit": {
          "type": "integer",
          "description": "覆盖批次级 retryLimit"
        }
      }
    }
  }
}
```

## 完整示例

```json
{
  "batchId": "batch-20260403-001",
  "description": "行政班接口批量切换 v2",
  "feishuAlertOpenId": "ou_xxx",
  "SOURCEGRAPH_URL": "https://sourcegraph.yc345.tv",
  "GITLAB_URL": "https://gitlab.yc345.tv",
  "GITLAB_TOKEN": "xxx",
  "workspaceRoot": "~/work",
  "oldServiceName": "teacher",
  "newServiceName": "teacher-school",
  "oldNamespace": "teacherschool",
  "newNamespace": "teacherschool",
  "oldServiceHint": "teacher.teacherschool",
  "newServiceHint": "teacher-school.teacherschool",
  "maxConcurrent": 2,
  "defaultTimeout": 1800,
  "retryLimit": 2,
  "tasks": [
    {
      "taskId": "route-cutover-20260403-0001",
      "oldRoute": "/admin-room/list",
      "newRoute": "/teacher-school/admin-room/list",
      "method": "GET",
      "branch": "feat/m-6920925476",
      "gatewayRepos": ["onions-school", "channel-platform-server", "channel", "teacher-tenant"],
      "apisixAdminURLs": ["https://school-test.example.com/apisix/admin/routes"]
    },
    {
      "taskId": "route-cutover-20260403-0002",
      "oldRoute": "/admin-room/{ref}/detail",
      "newRoute": "/teacher-school/admin-room/{ref}/detail",
      "method": "GET",
      "branch": "feat/m-6920925476",
      "oldServiceName": "teacher",
      "newServiceName": "teacher-school",
      "oldServiceHint": "teacher.teacherschool",
      "newServiceHint": "teacher-school.teacherschool",
      "gatewayRepos": ["onions-school", "channel-platform-server", "channel", "teacher-tenant"],
      "apisixAdminURLs": ["https://school-test.example.com/apisix/admin/routes"]
    }
  ]
}
```
