# 飞书 Base 输出

## 前置读取

写入飞书 Base 前，必须先使用当前环境中已安装的飞书 Base 能力：

- 优先读取并遵循已安装的 `lark-shared` / `lark-base` skills。
- 如果没有对应 skills，使用 `lark-cli base +field-list`、`+record-list`、`+record-delete`、`+record-batch-create` 等命令前，先查看对应命令帮助或本地 reference。
- 本插件不内置 `lark-cli`、`lark-base` 或 `lark-shared`；它只定义 TLS 对比结果如何安全写入 Base。

## 目标字段

目标表需要存储字段：

```text
路由地址
method
<A服务名>流量
<B服务名>流量
<A服务名>有流量
<B服务名>有流量
```

例如 A 为 `teacherschool/teacher`，B 为 `teacherschool/teacher-school` 时：

```text
路由地址
method
teacherschool/teacher流量
teacherschool/teacher-school流量
teacherschool/teacher有流量
teacherschool/teacher-school有流量
```

写入前先 `+field-list` 确认字段存在且类型兼容。流量字段应为数字字段；`有流量` 字段应优先使用 checkbox / boolean 兼容字段，并写入 boolean 值，不要写本地化文本 `是` / `否`。

## 写入策略

默认策略：

1. 先生成预览。
2. 等用户明确确认写入目标 Base。
3. 优先写入新表，或在用户明确确认后清空目标表重写。
4. 第一版不默认做复杂 upsert。

如果目标表还是旧四列 `A服务流量` / `B服务流量`，需要先重建字段或新建表，再写入增强后的六列结果。不要把六列结果强行写入旧四列表。

## 批量约束

飞书 Base 批量写入单批不超过 200 条。大结果集要分批串行写入，批次间保留短暂间隔。

## 安全约束

不要把火山 AK/SK、完整错误堆栈或未脱敏调试信息写入 Base。
