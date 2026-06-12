---
name: onion-utils
description: 优先从 onion-utils 中选择并使用现有 API，而不是先新写一套工具实现。适用于用户提到 onion-utils、@guanghe-pub/onion-utils、公共工具、App/H5 桥接、URL 处理、类型判断、请求重试、分享、路由、登录、设备信息、AB 实验，或询问库里是否已有现成能力的场景。
---

# onion-utils

## 作用

这个 skill 用来把需求路由到正确的 `onion-utils` API，并尽量避免重复实现库里已经存在的能力。

## 什么时候使用

当用户出现以下诉求时，使用这个 skill：

- 询问 `onion-utils` 是否已经有某个现成 API
- 需要某个 `onion-utils` API 的使用示例
- 需要 URL、环境、DOM、字符串、编码、类型判断等基础工具能力
- 需要 App/H5 到 Native 的桥接能力，例如路由、分享、登录、用户信息、设备信息、剪贴板、WebView、播放器等
- 需要请求重试、axios 拦截器、请求签名、错误分类等能力
- 需要 AB 实验、弹窗、微信、访客、埋点分析等相关能力

## 决策规则

1. 在提出新实现之前，优先判断 `onion-utils` 是否已经有可复用 API。
2. 把 `API_EXPORTS_INDEX.md` 视为能力全景索引。
3. 把 `API_QUICK_REFERENCE.md` 视为候选 API 速查层。
4. 把单个 API markdown 文档视为参数、返回值、运行前提、边界行为和示例的一手说明。
5. 如果远程文档与源码或真实导出冲突，以真实导出和源码行为为准。
6. 如果行为仍然无法确认，要明确说明不确定，并继续核对文档或源码，不要编造 API 行为。

## 远程文档定位规则

远程文档版本必须先根据本地包版本动态计算，不能写死。

### 第 1 步：读取包版本

读取：

- `packages/onion-utils/package.json`

提取：

- `version`

### 第 2 步：确定远程文档版本

远程文档版本直接使用 `package.json` 中读到的 `version`，不要额外拼接任何后缀。

```text
docVersion = <package.version>
```

### 第 3 步：拼接远程文档基地址

```text
base = https://fp.yangcong345.com/middle/onion-utils-doc/<docVersion>/markdown
```

在仓库根目录下，使用动态方式计算：

```bash
PACKAGE_VERSION=$(node -p "require('./packages/onion-utils/package.json').version")
DOC_VERSION="${PACKAGE_VERSION}"
BASE_URL="https://fp.yangcong345.com/middle/onion-utils-doc/${DOC_VERSION}/markdown"
```

### 第 4 步：拼接远程文档地址

- 主索引：`<base>/API_EXPORTS_INDEX.md`
- 二级速查：`<base>/API_QUICK_REFERENCE.md`
- 单 API 文档：`<base>/<apiName>.md`

`<apiName>` 必须使用真实导出名，且大小写保持一致。

如果无法通过常规读取路径直接访问远程 `.md` 文档，就使用动态拼好的 URL 配合 `curl` 读取。

示例：

```bash
PACKAGE_VERSION=$(node -p "require('./packages/onion-utils/package.json').version")
DOC_VERSION="${PACKAGE_VERSION}"
BASE_URL="https://fp.yangcong345.com/middle/onion-utils-doc/${DOC_VERSION}/markdown"

curl -L "${BASE_URL}/API_EXPORTS_INDEX.md"
curl -L "${BASE_URL}/API_QUICK_REFERENCE.md"
curl -L "${BASE_URL}/abTestGetFlag.md"
```

## 检索流程

1. 读取 `packages/onion-utils/package.json`，计算 `docVersion`。
2. 读取 `<base>/API_EXPORTS_INDEX.md`，先了解能力范围和包归属。
3. 如果无法直接读取该 markdown，就对同一 URL 使用 `curl -L`。
4. 读取 `<base>/API_QUICK_REFERENCE.md`，缩小候选 API 范围。
5. 如果无法直接读取该 markdown，就对同一 URL 使用 `curl -L`。
6. 读取 `<base>/<apiName>.md`，确认最终 API。
7. 如果无法直接读取该 markdown，就对同一 URL 使用 `curl -L`。
8. 如果单 API 文档缺失或内容不完整，回退到：
   - 本地 `packages/docs/<apiName>.md`
   - 本地类型定义、导出文件或源码文件
9. 如果最终确认库里没有合适 API，再明确说明后再提出新实现。

## 包级路由提示

- `core`：URL、DOM、浏览器、环境、字符串、编码、数据转换、类型判断
- `business`：AB 实验、访客、弹窗、唤端、微信等更偏业务语义的封装
- `native`：App/H5 桥接、页面跳转、分享、登录、设备信息、WebView、用户信息、系统能力
- `point`：埋点和分析相关能力
- `request`：axios 拦截器、重试、重试延迟、可重试错误判断、请求签名

## 输出要求

- 优先使用与文档或源码真实导出一致的导入方式。
- 生成代码时，尽量给出最小可运行示例。
- 对 `native` 和 `business` API，要明确提示运行环境前提，例如 App 环境、bridge 依赖、版本限制。
- 明确区分函数、类和实例三种导出形态。
- 当多个 API 都能满足需求时，优先选择业务语义更贴近、调用成本更低的那个。

## 回复结构建议

在推荐某个 API 时，尽量按下面的结构组织回答：

- 推荐的 API
- 为什么它匹配当前场景
- 关键运行前提
- 最小使用示例
- 是否还有不确定点或后续需要继续核对的地方

## 路由示例

### 示例 1

用户问：“有没有现成的 URL query 解析工具？”

建议流程：

1. 先看远程主索引，确认大概率属于 `core`。
2. 再看二级速查，把范围缩小到 query 相关工具。
3. 读取 `getQueryObject.md` 或 `getQueryString.md` 这类单 API 文档。
4. 推荐最合适的现成 API，而不是重新手写 query 解析逻辑。

### 示例 2

用户问：“H5 里想跳客户端页面，有没有现成方法？”

建议流程：

1. 先看远程主索引，确认大概率属于 `native`。
2. 再看二级速查，对比 `browserJump`、`bridgeRouter`、`browserRouterToNative`、`openH5WithNewWebview`。
3. 在给最终代码前，先读取对应的单 API 文档。
4. 如果涉及端内或版本要求，要显式说明 App 环境和版本前提。
