## ADDED Requirements

### Requirement: Go 代码格式化
Go 源码在保存时 SHALL 使用 `gofmt` 和 `goimports` 进行格式化，导入分组 SHALL 分为标准库与非标准库两组，由 `goimports` 自动维护。

#### Scenario: 代码保存时未格式化
- **WHEN** 提交或保存包含未格式化 Go 代码的文件
- **THEN** 应提示使用 `gofmt` / `goimports` 格式化，不允许合入未格式化代码

#### Scenario: 导入分组混乱
- **WHEN** import 块中标准库与第三方库未分组
- **THEN** 应提示按「标准库 / 第三方库」两组排列，中间保留空行

---

### Requirement: 多词命名使用驼峰
Go 标识符包含多个词时 SHALL 使用 `MixedCaps` 或 `mixedCaps`，不得使用下划线（蛇形命名）。

#### Scenario: 使用下划线命名
- **WHEN** 代码中出现 `MIXED_CAPS` 或 `mixed_caps` 形式的标识符
- **THEN** 应提示改为驼峰形式 `MixedCaps` / `mixedCaps`

---

### Requirement: 包命名规范
包名 SHALL 简短且全部小写；多词包名 SHALL 全部小写不加分隔符；包名 SHALL 避免与常用局部变量同名；包名 SHALL 语义明确，避免 `util`、`common`、`helper` 等无意义名称（老服务已有的 common 包除外）。

#### Scenario: 包名含大写或下划线
- **WHEN** 声明 `package TabWriter` 或 `package tab_writer`
- **THEN** 应提示改为 `package tabwriter`

#### Scenario: 包名与常用变量冲突
- **WHEN** 包名为 `count`、`user` 等极易被局部变量覆盖的词
- **THEN** 应提示使用更具体的名称，如 `usercount`

---

### Requirement: 接收者变量命名
接收者变量 SHALL 为类型名的一到两个字母缩写，且同一类型的所有方法接收者名称 SHALL 保持一致；类型方法 SHALL 全部使用指针接收者。

#### Scenario: 接收者命名不一致
- **WHEN** 同一类型的两个方法中接收者名称不同（如 `s` 和 `n`）
- **THEN** 应提示统一为同一名称

#### Scenario: 使用值接收者
- **WHEN** 方法声明为 `func (t Tray) Method()`
- **THEN** 应提示改为指针接收者 `func (t *Tray) Method()`

---

### Requirement: 常量命名规范
常量 SHALL 按角色而非值命名；常量 SHALL 遵循驼峰命名，不得使用全大写加下划线形式。

#### Scenario: 常量按值命名
- **WHEN** 出现 `const Ten = 10`
- **THEN** 应提示按业务角色命名，如 `const ScrumSprintCycle = 10`

#### Scenario: 常量使用全大写下划线
- **WHEN** 出现 `const MAX_PACKET_SIZE = 512`
- **THEN** 应提示改为 `const MaxPacketSize = 512`

---

### Requirement: 缩写词大小写一致性
缩写词 SHALL 与实际使用保持大小写一致（全大写或全小写），根据是否需要导出决定：导出时全大写，不导出时全小写。

#### Scenario: 缩写词大小写不规范
- **WHEN** 出现 `XmlApi`、`xmlapi`、`Grpc`、`Id` 等不规范写法
- **THEN** 应提示：导出用 `XMLAPI`/`GRPC`/`ID`，不导出用 `xmlAPI`/`gRPC`/`id`

---

### Requirement: 函数返回值命名
同类型多返回值 SHALL 使用命名参数加以区分；调用方需执行特定操作的返回值 SHALL 命名；中等以上长度函数 SHALL 不使用裸 return；不得为了减少 `var` 声明而使用命名返回值。

#### Scenario: 同类型多返回值未命名
- **WHEN** 函数签名为 `func (n *Node) Children() (*Node, *Node, error)`
- **THEN** 应提示改为 `func (n *Node) Children() (left, right *Node, err error)`

#### Scenario: 中等函数使用裸返回
- **WHEN** 函数体超过几行且末尾使用 `return`（无显式参数）
- **THEN** 应提示显式写出返回值

---

### Requirement: 命名避免冗余
导出方法/函数名 SHALL 不包含包名；变量名 SHALL 不含类型信息（除非同作用域内存在同类型多个变量）；命名 SHALL 不重复来自周围上下文（包名、方法名、类型名）的信息。

#### Scenario: 方法名含包名
- **WHEN** `package widget` 中出现 `func NewWidget()`
- **THEN** 应提示改为 `func New()`

---

### Requirement: 导出符号必须有文档注释
所有导出的名称（函数、类型、常量、变量）SHALL 有文档注释，注释 SHALL 以被注释的导出名称开头。

#### Scenario: 导出类型缺少注释
- **WHEN** `type Request struct { ... }` 无注释
- **THEN** 应提示添加 `// Request ...` 形式的文档注释

---

### Requirement: 包注释
每个包 SHALL 有一个包注释；多文件包中注释 SHALL 出现在其中一个文件中；注释与 `package` 语句之间 SHALL 无空行。

#### Scenario: 包缺少注释
- **WHEN** `package math` 上方无注释
- **THEN** 应提示添加 `// Package math provides ...`

---

### Requirement: 导入别名规范
仅在避免名称冲突时 SHALL 使用导入别名；别名 SHALL 遵循包命名规则；无语义的版本包（如 `v1`）SHALL 重命名以包含路径组件；proto 生成文件 SHALL 重命名以去除下划线。

#### Scenario: 无冲突时使用别名
- **WHEN** 在无命名冲突的情况下对标准库或常规包使用别名
- **THEN** 应提示移除多余别名

#### Scenario: 版本包未重命名
- **WHEN** 导入 `"github.com/kubernetes/api/core/v1"` 未设置别名
- **THEN** 应提示添加别名如 `core "github.com/kubernetes/api/core/v1"`
