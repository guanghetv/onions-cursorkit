## ADDED Requirements

### Requirement: 减少代码嵌套
代码 SHALL 尽早处理错误/特殊情况并 `return` 或 `continue`，避免多层嵌套。

#### Scenario: 深层嵌套替代早返回
- **WHEN** 循环内正常逻辑嵌套在 `if condition == true { ... }` 中
- **THEN** 应提示反转条件，用 `if condition != true { continue }` 提前结束

---

### Requirement: 缩小变量作用域
变量 SHALL 在尽可能小的作用域内声明，除非与减少嵌套的规则冲突。

#### Scenario: 变量声明作用域过大
- **WHEN** 变量在 `if` 块外声明但仅在 `if` 块内使用
- **THEN** 应提示使用短变量声明 `if err := ...; err != nil {}`

---

### Requirement: if / switch 语句缩进规范
`if` 语句 SHALL 不跨行；`switch` 和 `case` SHALL 始终在一行；大括号的闭合 `}` SHALL 与开头大括号保持相同缩进层级。

#### Scenario: if 条件跨行
- **WHEN** `if db.CurrentStatusIs(...) &&\n    db.ValuesEqual(...)` 跨行
- **THEN** 应提示将条件提取为命名变量后合并为单行

#### Scenario: case 跨行
- **WHEN** `case db.TransactionStarting,\n    db.TransactionActive:` 跨行
- **THEN** 应提示改为单行 `case db.TransactionStarting, db.TransactionActive:`

---

### Requirement: 零值变量初始化
声明值为零值的变量时 SHALL 使用 `var` 而非 `:=`；结构体初始化 SHALL 使用字段名，不得按位置初始化。

#### Scenario: 零值变量使用 :=
- **WHEN** 出现 `s := ""` 或 `i := 0`
- **THEN** 应提示改为 `var s string` / `var i int`

#### Scenario: 结构体按位置初始化
- **WHEN** 出现 `Point{1, 2}` 形式
- **THEN** 应提示改为 `Point{X: 1, Y: 2}`

---

### Requirement: 切片声明与初始化规范
非空切片 SHALL 使用字面量初始化；需要预分配大小时 SHALL 使用 `make`；不得用 `append` 一次追加单个元素替代批量初始化；`nil` 切片与空切片语义不同，需明确区分。

#### Scenario: 空切片用 nil 声明却期望 JSON 为 []
- **WHEN** 代码将 `var s []string`（nil）序列化后期望输出 `[]`
- **THEN** 应提示使用 `s := []string{}` 或 `s := make([]string, 0)`

---

### Requirement: map 使用规范
map SHALL 使用 `make` 初始化后再写入；直接对 nil map 赋值 SHALL 不允许；从 map 中读取不存在的 key 时 SHALL 使用双值赋值检查存在性。

#### Scenario: 向 nil map 写入
- **WHEN** 出现 `var m map[string]int; m["key"] = 1`
- **THEN** 应提示改为 `m := make(map[string]int); m["key"] = 1`

---

### Requirement: channel 使用规范
channel SHALL 在明确生产者/消费者模型后使用；不得在未知容量的情况下使用无缓冲 channel 做异步通信；使用 channel 时 SHALL 考虑 goroutine 泄漏风险。

#### Scenario: 忘记关闭 channel 导致 goroutine 泄漏
- **WHEN** 生产者 goroutine 写完数据后未关闭 channel，消费者持续阻塞
- **THEN** 应提示在生产者完成后 `close(ch)`，或使用 `context` 控制退出

---

### Requirement: 并发编程规范
共享变量的并发访问 SHALL 使用 `sync.Mutex` 或 channel 保护；不得在不同 goroutine 间通过裸变量共享状态；goroutine 启动时 SHALL 能通过 `context` 或 channel 退出。

#### Scenario: 并发访问未加锁
- **WHEN** 多个 goroutine 无保护地读写同一变量
- **THEN** 应提示加 `sync.Mutex` 或改用 channel 传递数据

---

### Requirement: 接口设计规范
接口 SHALL 在使用方（消费者）定义，而非在实现方定义；接口 SHALL 尽量小（单方法优先）；不得为了"以后可能有多个实现"而提前定义接口。

#### Scenario: 接口在实现包中定义
- **WHEN** 实现包中定义了自身实现的接口
- **THEN** 应提示将接口移至调用方包，或作为独立 package 存放

---

### Requirement: 泛型使用规范
泛型 SHALL 在类型参数能带来明显复用价值时使用；不得为了"看起来通用"而引入泛型增加复杂度；类型约束 SHALL 尽量精确。

#### Scenario: 不必要的泛型引入
- **WHEN** 泛型函数实际只有一种具体类型的调用
- **THEN** 应提示移除泛型，使用具体类型

---

### Requirement: 字符串拼接使用 strings.Builder
频繁拼接字符串 SHALL 使用 `strings.Builder`，不得在循环中使用 `+` 拼接。

#### Scenario: 循环中用 + 拼接字符串
- **WHEN** 出现 `for _, s := range list { result += s }`
- **THEN** 应提示改为 `var b strings.Builder; for _, s := range list { b.WriteString(s) }`
