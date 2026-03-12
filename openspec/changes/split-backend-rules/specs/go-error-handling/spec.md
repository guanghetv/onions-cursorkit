## ADDED Requirements

### Requirement: 禁止用 panic 做常规错误处理
正常错误处理 SHALL 通过返回 `error` 实现，不得使用 `panic`。允许 panic 的两个例外：（1）程序启动时依赖异常；（2）表示"不可能"出现的条件错误。

#### Scenario: 用 panic 处理业务错误
- **WHEN** 代码中出现 `panic("an argument is required")` 用于处理常规输入验证
- **THEN** 应提示改为 `return errors.New("an argument is required")`

---

### Requirement: error 作为最后一个返回参数
函数返回 error 时，`error` SHALL 是最后一个返回参数。

#### Scenario: error 不在最后
- **WHEN** 函数签名为 `func Foo() (error, int)`
- **THEN** 应提示改为 `func Foo() (int, error)`

---

### Requirement: 返回 error 接口类型
返回错误的函数 SHALL 使用 `error` 接口类型作为返回值，不得返回具体错误类型指针。

#### Scenario: 返回具体错误类型
- **WHEN** 函数签名为 `func ReturnErr() *MyError`
- **THEN** 应提示改为 `func ReturnErr() error`（`MyError` 实现 `error` 接口）

---

### Requirement: 导出函数使用 error 类型而非 nil 判断
返回错误的导出函数 SHALL 使用 `error` 类型，调用方 SHALL 通过 `err != nil` 判断，而非判断返回值是否为 nil。

#### Scenario: 通过返回值 nil 判断错误
- **WHEN** `func Lookup() *Result {}` 且调用方用 `if r != nil {}` 判断
- **THEN** 应提示改为 `func Lookup() (*Result, error)` 并用 `err != nil` 判断

---

### Requirement: 错误变量与类型命名规范
全局错误变量 SHALL 使用 `Err` 前缀（导出）或 `err` 前缀（不导出）；自定义错误类型 SHALL 使用 `Error` 后缀。

#### Scenario: 全局错误变量缺少 Err 前缀
- **WHEN** 出现 `BrokenLink = errors.New("link is broken")`
- **THEN** 应提示改为 `ErrBrokenLink = errors.New("link is broken")`

#### Scenario: 自定义错误类型缺少 Error 后缀
- **WHEN** 出现 `type NotFound struct {}`
- **THEN** 应提示改为 `type NotFoundError struct {}`

---

### Requirement: 使用 errors.Is / errors.As 处理错误类型
判断特定错误或转换错误类型 SHALL 使用 `errors.Is` / `errors.As`，不得使用字符串比较或直接类型断言。

#### Scenario: 字符串比较错误
- **WHEN** 出现 `if err.Error() == "file does not exist"`
- **THEN** 应提示改为 `if errors.Is(err, targetErr)`

#### Scenario: 直接类型断言错误
- **WHEN** 出现 `if pathErr, ok := err.(*os.PathError); ok {}`
- **THEN** 应提示改为 `var pathErr *os.PathError; if errors.As(err, &pathErr) {}`

---

### Requirement: 错误处理后正常逻辑不进 else
处理错误后，正常逻辑代码 SHALL 出现在 `if` 块之后，不得缩进在 `else` 子句中（早返回模式）。

#### Scenario: 正常代码在 else 中
- **WHEN** 代码结构为 `if err != nil { ... } else { // 正常代码 }`
- **THEN** 应提示改为 `if err != nil { return }` 后紧跟正常代码

---

### Requirement: 错误只处理一次
调用方 SHALL 选择「处理错误」或「向上透传错误」之一，不得同时打印日志又返回错误（会产生重复日志）。

#### Scenario: 同时打印并返回错误
- **WHEN** 出现 `log.Printf(..., err); return err`
- **THEN** 应提示选择其一：仅 `return err`，或仅 `log.Printf` 并降级处理
