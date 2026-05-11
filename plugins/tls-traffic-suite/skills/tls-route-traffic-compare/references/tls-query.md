# TLS 查询

## 凭证

从环境变量读取：

```text
VOLCENGINE_ACCESS_KEY_ID
VOLCENGINE_SECRET_ACCESS_KEY
VOLCENGINE_REGION
VOLCENGINE_ENDPOINT
```

`VOLCENGINE_ENDPOINT` 可选，默认按 region 生成公网地址 `tls-{region}.volces.com`。如果运行环境能访问火山私网，也可以显式设置为 `https://tls-{region}.ivolces.com`。只检查变量是否存在，不打印变量值。

如果 AK/SK 曾经出现在聊天、日志、截图或提交记录中，应在火山控制台轮换密钥。生产环境建议通过 1Password、Vault 或 CI secrets 注入，不要把真实值写入仓库。

## Python 依赖

脚本只使用 Python 标准库，不需要 `pip install volcengine`。TLS API 调用通过 `urllib.request` 发起，火山 OpenAPI SigV4 签名通过 `hmac`、`hashlib` 实现。

执行前可先检查环境变量：

```bash
python3 scripts/tls_route_traffic.py validate-env
```

## 环境映射

```text
prod  -> prod-vke
stage -> stage-vke
```

## topic 发现

1. 根据 `{namespace}-{service}` 构造 topic 名。
2. 使用火山 TLS `DescribeTopics` 在目标 project 中查找 topic。
3. 精确命中时返回 topic ID。
4. namespace 缺失时搜索 `*-{service}`，展示候选并等待用户确认。

## 默认查询

```sql
status:>=200 | SELECT route,method,count(*) pv GROUP BY route,method ORDER BY pv DESC LIMIT 999
```

每个服务输出统一规整为：

```json
[
  {"route": "/rooms/:roomid/students", "method": "get", "pv": 123}
]
```

## route 字段约束

第一版要求日志中存在结构化 `route` 字段。如果只有 `path` 或 `uri`，不要自动归一化，应提示用户补充 route mapping 或调整采集字段。
