## ADDED Requirements

### Requirement: key 命名规范
Redis key SHALL 以业务名/数据库名为前缀，用冒号分隔（如 `teacher:room:id`）；key SHALL 在保证语义的前提下尽量简短；key SHALL 不包含空格、换行、单双引号等特殊字符。

#### Scenario: key 无业务前缀
- **WHEN** 出现 `SET userId:123 value` 无服务/业务前缀
- **THEN** 应提示改为 `SET <service>:user:123 value` 格式

#### Scenario: key 含特殊字符
- **WHEN** key 中包含空格或换行符
- **THEN** 应提示移除特殊字符

---

### Requirement: 禁止 bigkey
String 类型 value SHALL 控制在 10KB 以内；hash、list、set、zset 元素数 SHALL 不超过 5000；删除大 key SHALL 使用渐进式删除（`hscan`/`sscan`/`zscan`），不得直接 `del`。

#### Scenario: 存储超大 value
- **WHEN** 代码向 Redis 写入超过 10KB 的 string 或超 5000 元素的集合
- **THEN** 应提示拆分数据或改用其他存储方案

---

### Requirement: 所有 key 必须设置过期时间
每个 Redis key SHALL 设置合理的过期时间（`EXPIRE`）；不过期的数据 SHALL 特别关注 `idletime`。

#### Scenario: 写入 key 未设置过期时间
- **WHEN** `SET key value` 后无 `EXPIRE key seconds`
- **THEN** 应提示添加过期时间，避免 Redis 成为"垃圾桶"

---

### Requirement: 禁止在线上使用危险命令
生产环境 SHALL 禁止使用 `KEYS`、`FLUSHALL`、`FLUSHDB` 等全量/清空命令；遍历需求 SHALL 使用 `SCAN`/`HSCAN`/`SSCAN`/`ZSCAN` 渐进式处理。

#### Scenario: 使用 KEYS * 遍历
- **WHEN** 代码中出现 `KEYS *` 或 `KEYS pattern`
- **THEN** 应提示改为 `SCAN` 游标方式遍历

---

### Requirement: O(N) 命令需明确 N 的量级
`HGETALL`、`LRANGE`、`SMEMBERS`、`ZRANGE` 等 O(N) 命令 SHALL 在使用前明确 N 的数量级，超过阈值时 SHALL 改用对应的渐进式命令。

#### Scenario: 无限制使用 SMEMBERS
- **WHEN** 对可能包含大量元素的 set 直接调用 `SMEMBERS`
- **THEN** 应提示改用 `SSCAN` 并限制每次返回数量

---

### Requirement: 使用批量操作提升效率
多次读写 Redis 时 SHALL 优先使用批量命令（`MGET`/`MSET`）或 pipeline，单次批量操作元素数 SHALL 控制在 500 以内。

#### Scenario: 循环逐条写入
- **WHEN** for 循环中每次迭代单独调用 `SET`/`GET`
- **THEN** 应提示改用 `MSET`/`MGET` 或 pipeline 批量操作

---

### Requirement: 缓存与数据库操作顺序
更新数据时 SHALL 先操作数据库，再删除缓存（非高并发场景）；高并发强一致场景 SHALL 采用延迟双删方案；缓存删除失败时 SHALL 有重试机制（如写入 MQ 异步重试）。

#### Scenario: 先更新缓存再写数据库
- **WHEN** 代码中先 `SET cache` 再 `UPDATE db`
- **THEN** 应提示改为先 `UPDATE db` 再 `DEL cache`

---

### Requirement: 使用连接池访问 Redis
应用 SHALL 使用带连接池的 Redis 客户端；不同应用 SHALL 避免共用同一 Redis 实例；Redis 连接 SHALL 配置密码认证。

#### Scenario: 未使用连接池
- **WHEN** 每次操作都新建 Redis 连接
- **THEN** 应提示改为连接池模式

---

### Requirement: 冷热数据分离
Redis SHALL 仅存储高频热数据（QPS > 5000）；低频冷数据 SHALL 使用 MySQL/ES/MongoDB 等磁盘存储；超过 500 字节的大文本 SHALL 压缩后再存入 Redis。

#### Scenario: 将全量数据放入 Redis
- **WHEN** 将全量历史数据或低频访问数据缓存到 Redis
- **THEN** 应提示只缓存热点数据，冷数据使用磁盘存储
