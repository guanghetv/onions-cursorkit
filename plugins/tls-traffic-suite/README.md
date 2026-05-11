# tls-traffic-suite

面向火山 TLS 生产流量对比的插件化工作流套件。当前包含 `tls-route-traffic-compare`，用于对比任意两个服务按 `route + method` 聚合后的流量，并输出适合 CSV 或飞书 Base 的六列结果。

## 包含的 Skills

- `tls-route-traffic-compare`: 查询两个服务的 TLS route/method 流量，执行 route 归一化、assisted 候选聚合分析，并生成预览、CSV 或飞书 Base 写入数据。

## 包含的 Commands

- `/tls-route-traffic-compare`: TLS 路由流量对比统一入口，转入 `tls-route-traffic-compare` skill。

## 输出列

默认输出：

```text
路由地址
method
<A服务名>流量
<B服务名>流量
<A服务名>有流量
<B服务名>有流量
```

例如：

```text
路由地址
method
teacherschool/teacher流量
teacherschool/teacher-school流量
teacherschool/teacher有流量
teacherschool/teacher-school有流量
```

## 外部依赖

- `python3`
- 火山 TLS 环境变量：
  - `VOLCENGINE_ACCESS_KEY_ID`
  - `VOLCENGINE_SECRET_ACCESS_KEY`
  - `VOLCENGINE_REGION`
  - `VOLCENGINE_ENDPOINT`（可选，默认 `tls-{region}.volces.com`）
- 写入飞书 Base 时还需要：
  - `lark-cli`
  - 已授权的 `lark-cli auth login --domain base`
  - 已安装的 `lark-base` / `lark-shared` 能力，或等价的 `lark-cli base +...` 命令参考

脚本只使用 Python 标准库访问火山 TLS API，不需要安装 Volcengine SDK。

## 使用示例

对话内执行：

```text
/tls-route-traffic-compare prod teacherschool/teacher vs teacherschool/teacher-school 最近24小时
```

也可以直接进入 skill：

```text
对比 prod teacherschool/teacher 和 teacherschool/teacher-school 最近 24 小时 TLS 流量，导出 CSV
```

脚本调试时进入 skill 目录运行：

```bash
python3 scripts/tls_route_traffic.py validate-env
python3 scripts/tls_route_traffic.py discover-topic --env prod --service teacherschool/teacher-school
python3 scripts/tls_route_traffic.py compare --a a.json --b b.json --a-name teacherschool/teacher --b-name teacherschool/teacher-school
```

## 安全约束

- 不要在聊天、终端输出、文档或飞书 Base 中打印火山 AK/SK。
- 不要把个人运行产物、生产查询结果、临时 CSV 或批量写入 JSON 放进插件目录。
- 写入飞书 Base 前必须先预览结果并获得用户确认。
- assisted 聚合只接受显式 rules JSON；脚本不直接进行模型推理。

## 目录结构

```text
plugins/tls-traffic-suite/
├── .cursor-plugin/plugin.json
├── README.md
├── commands/
│   └── tls-route-traffic-compare.md
└── skills/
    └── tls-route-traffic-compare/
        ├── SKILL.md
        ├── references/
        └── scripts/
```
