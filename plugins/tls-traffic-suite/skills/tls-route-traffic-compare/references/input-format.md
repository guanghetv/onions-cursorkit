# 输入格式

## 推荐格式

```text
<env> <namespace-a>/<service-a> vs <namespace-b>/<service-b> <time-range> [写入 <base-url>]
```

示例：

```text
prod teacherschool/teacher-school vs xxxx/teacher-school-go 最近24小时
```

## 字段含义

- `env`：环境。第一版支持 `prod`、`stage`。
- `namespace`：TLS topic 前缀，例如 `teacherschool`、`7to12`、`xxxx`。
- `service`：服务名，例如 `teacher-school`。
- `time-range`：查询时间范围，例如 `最近15分钟`、`最近24小时`、固定起止时间。

## topic 规则

精确 topic 名：

```text
{namespace}-{service}
```

示例：

```text
teacherschool/teacher-school -> teacherschool-teacher-school
```

如果用户只给 service，不给 namespace，只能做 `*-{service}` 候选搜索，并要求用户确认后继续。
