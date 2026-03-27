## ADDED Requirements

### Requirement: 连接池参数合理配置
数据库连接池 SHALL 配置合理的 `MaxIdleConns`、`MaxOpenConns`、`ConnMaxLifeTime`；连接数 SHALL 参考 `(核心数 * 2) + 有效磁盘数` 估算，不得无限制开放。

#### Scenario: 连接池未配置最大连接数
- **WHEN** 代码中 `MaxOpenConns` 未设置或设置为 0（无限制）
- **THEN** 应提示根据实例规格设置合理上限

---

### Requirement: 建表必须有主键且字符编码为 UTF8
每张表 SHALL 有主键；字符编码 SHALL 为 UTF8，禁止其他编码。

#### Scenario: 建表缺少主键
- **WHEN** `CREATE TABLE` 语句中无 PRIMARY KEY 声明
- **THEN** 应提示添加主键列

#### Scenario: 字符编码非 UTF8
- **WHEN** 建表语句中指定了非 UTF8 编码
- **THEN** 应提示改为 UTF8

---

### Requirement: 查询/排序字段必须有索引
作为 `WHERE` 条件或 `ORDER BY` 的字段 SHALL 建立索引；组合查询字段 SHALL 建立复合索引，将单独查询最多的字段放在前面。

#### Scenario: 高频查询字段无索引
- **WHEN** 接口 WHERE 条件字段在表定义中无对应索引
- **THEN** 应提示创建索引，如 `CREATE INDEX ON table_name (uid)`

---

### Requirement: 唯一约束由数据库保证
唯一列或组合唯一列 SHALL 在数据库层面添加唯一约束，不得仅依赖应用层逻辑保证唯一性。

#### Scenario: 唯一字段缺少约束
- **WHEN** 代码注释说明某字段唯一，但 DDL 中无 UNIQUE 约束
- **THEN** 应提示在 DDL 中添加 `UNIQUE` 约束

---

### Requirement: NOT NULL 约束与默认值
语义上无零值/空值区分的字段 SHALL 添加 `NOT NULL` 约束；有默认值的列 SHALL 添加 `DEFAULT` 子句。

#### Scenario: 可为 NULL 的必填字段
- **WHEN** 业务上必填的字段 DDL 中未声明 NOT NULL
- **THEN** 应提示添加 NOT NULL 约束

---

### Requirement: 对象命名使用 snake_case 小写
表名、列名、函数名等数据库对象 SHALL 只使用小写字母、下划线、数字；名称 SHALL 与业务一致，长度不超过 63 字符；不得使用保留字、中文、美元符号、pg_ 前缀。

#### Scenario: 对象名含大写或驼峰
- **WHEN** 出现 `orderDeductibleInfo` 作为表名
- **THEN** 应提示改为 `order_deductible_info`

---

### Requirement: 主键类型选择规范
主键 SHALL 优先使用 `BIGSERIAL` 或 `IDENTITY` 列；有分片需求时 SHALL 使用 UUID v7；禁止使用无序 UUID（v4 等）作为主键。

#### Scenario: 使用无序 UUID 作为主键
- **WHEN** 主键类型为 `uuid` 且使用 `uuid_generate_v4()`
- **THEN** 应提示改为 UUID v7 或 BIGSERIAL，避免索引碎片化

---

### Requirement: 在线业务使用 CONCURRENTLY 创建/删除索引
在线业务新建或删除索引 SHALL 使用 `CREATE INDEX CONCURRENTLY` / `DROP INDEX CONCURRENTLY`，避免锁表；在 archery 平台外单独由运维执行。

#### Scenario: 直接创建索引未使用 CONCURRENTLY
- **WHEN** 线上表执行 `CREATE INDEX` 不加 CONCURRENTLY
- **THEN** 应提示改为 `CREATE INDEX CONCURRENTLY`，并由运维操作

---

### Requirement: 禁止在 archery 平台修改或删除索引
修改或删除索引 SHALL 提运维工单处理，不得在 archery SQL 上线平台直接执行。

#### Scenario: 在 archery 提交 DROP INDEX
- **WHEN** 通过 archery 平台提交 DROP INDEX 语句
- **THEN** 应提示转为运维工单，使用 CONCURRENTLY 方式夜间执行

---

### Requirement: 事务快速提交，优先使用基础库事务管理
事务 SHALL 开启后尽快提交或回滚；SHALL 优先使用 ORM 框架提供的事务方法（如 `db.Transaction`），不得手动 BEGIN/COMMIT 长事务。

#### Scenario: 手动控制长事务
- **WHEN** 代码中手动 BEGIN 事务后在事务内有长耗时操作（如 HTTP 调用）
- **THEN** 应提示将耗时操作移出事务，或使用框架事务管理保证快速提交

---

### Requirement: 禁止全表扫描（在线业务）
在线业务 SHALL 避免全表扫描；禁止在首层过滤条件中使用 `!=`、`<>`、NULL 判断；禁止不加 WHERE 条件的 SELECT * 查询（常量极小表、低频后台操作除外）。

#### Scenario: WHERE 条件使用否定操作符
- **WHEN** 首层过滤条件出现 `WHERE status != 'active'`
- **THEN** 应提示改用正向条件或添加覆盖索引

---

### Requirement: 游标使用后必须及时关闭
使用游标（`rows`）后 SHALL 使用 `defer rows.Close()` 确保关闭，防止连接泄漏。

#### Scenario: 游标未关闭
- **WHEN** 代码中 `rows, err := db.Query(...)` 后无 `rows.Close()` 调用
- **THEN** 应提示添加 `defer rows.Close()`

---

### Requirement: 避免在数据库中执行复杂计算
复杂业务计算逻辑 SHALL 在应用层实现，不得下推到数据库执行；禁止使用数据库触发器。

#### Scenario: 使用触发器实现业务逻辑
- **WHEN** DDL 中出现 `CREATE TRIGGER` 用于业务数据处理
- **THEN** 应提示将逻辑迁移到应用层
