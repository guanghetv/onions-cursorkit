---
name: sourcegraph-api-search
description: >-
  Searches Sourcegraph for all repositories and call sites that use a given API
  or code string. By default save results as a Markdown file (--md). Outputs
  repo list, file path, line number, and code snippet. Also helps construct or
  explain Sourcegraph search query syntax (patternType, repo, file, lang,
  count, etc.). Use when the user wants to find where an API is used, list
  projects using an endpoint, generate an API usage report, or build/correct a
  Sourcegraph query. Trigger: Sourcegraph, API 搜索, 接口使用,
  哪些项目/仓库用了某接口, 查询语法, 怎么写 Sourcegraph 搜索.
---

# Sourcegraph API 使用搜索

在 Sourcegraph 上按「接口/API 字符串」搜索，列出所有使用该接口的**仓库**和**调用详情**（文件路径、行号、代码行）。支持自建 Sourcegraph 与 sourcegraph.com。

**默认交付物：** 由助手执行本 skill 时，**默认将结果写入 Markdown 文件**（使用 `--md`，落盘到用户指定路径，文件名建议 `api-usage-<接口路径摘要>.md`，若用户没有指定路径，则不落盘，直接打印结果，并告知用户“由于没有指定路径所以没有生成文件”）。若用户明确要求仅控制台、JSON 或其它格式，再改用对应选项。

## 何时使用

- 用户要查「哪些项目用了某个 API/接口」
- 需要生成接口调用清单或 Markdown 报告
- 用户提到 Sourcegraph、API 搜索、接口使用、调用方统计
- 用户需要**构造或理解 Sourcegraph 查询语法**（怎么写/改一条搜索、加 repo/file 过滤等）
- 当用户提到查询，但是没有提供明确的查询语法时，需要根据用户描述，先构造查询语句，可以参考"构造 Sourcegraph 查询语法"

## 执行脚本

脚本路径：本 skill 下的 `scripts/searchApi.js`。需 Node.js 18 及以上（内置 `fetch`，建议 18+ 版本）。

**基本用法：**（默认使用内置 Sourcegraph 地址，无需配置环境变量）

助手代跑时**推荐**（结果写入 `.md` 文件）：

```bash
node <skill路径>/scripts/searchApi.js "<API 或代码字符串>" --md > <用户指定路径>/api-usage-<摘要>.md
```

仅看终端、不落盘时（脚本默认 stdout 为文本）：

```bash
node <skill路径>/scripts/searchApi.js "<API 或代码字符串>"
```

**常用选项：**

| 选项 | 说明 |
| --- | --- |
| `--json` | 输出 JSON：`{ repos: string[], details: Array<{ repository, path, lineNumber, line, contextSnippet, commit? }> }` |
| `--md` | 输出 Markdown 文档：表格（含服务名/团队等列时以脚本为准），代码用 HTML 代码块渲染；**执行本 skill 时默认应使用并写入 `.md` 文件** |
| `--regex` | 按正则匹配（默认按字面量） |
| `--limit N` | 最多返回 N 条匹配（默认 3000） |

**环境变量（可选）：**

默认无需设置即可使用，脚本内置 Sourcegraph 地址。仅在使用自建/私有等**特殊地址**时再通过环境变量覆盖。

| 变量 | 说明 |
| --- | --- |
| `SOURCEGRAPH_URL` | 覆盖 Sourcegraph 地址；不设置时使用脚本内置默认值 |
| `SOURCEGRAPH_ACCESS_TOKEN` | 访问令牌，见下方「访问令牌」说明 |

### 访问令牌（Token）——交互说明

脚本**必须**有有效 token 才会请求 Sourcegraph。按场景友好处理：

**1. 助手（Agent）代跑脚本时**

- 先向用户说明：接下来需要 Sourcegraph 访问令牌，用于本次搜索。
- **优先**：请用户在对话里提供 token（或确认已在本机终端 `export SOURCEGRAPH_ACCESS_TOKEN=...`），再由助手用环境变量执行脚本，避免用户找不到终端提示。
- **默认**：优先用 `--md` 产出；**具体落盘规则**（用户指定路径 / 未指定路径 / 仅摘要）见下方「场景示例与处理方式（助手）」表格第一行；除非用户只要终端输出或 JSON。
- 若用户在终端自己运行脚本：说明会出现**交互式提示**，按提示粘贴 token 后回车即可；**直接回车（留空）** 表示取消，脚本会友好退出、**不会**发起搜索。

**2. 用户本机终端直接运行**

- 未设置 `SOURCEGRAPH_ACCESS_TOKEN` 时，脚本会先打印简短说明（当前实例地址、为何需要 token），再提示粘贴 token。
- 不想交互时，可一次性传入环境变量：  
  `SOURCEGRAPH_ACCESS_TOKEN=你的令牌 node ...`
- 令牌一般在 Sourcegraph 网页：**用户设置 → Access tokens** 中创建；请妥善保管，勿提交到仓库或截图泄露。

**3. 无 token 时**

- 脚本**不会**执行搜索；退出前会提示如何设置环境变量或重新运行并输入。

**示例：**

```bash
# 使用前设置 skill 目录变量（或写死路径）
SKILL_DIR=~/.cursor/skills/sourcegraph-api-search

# 默认推荐：Markdown 落盘（助手执行时优先采用）
SOURCEGRAPH_ACCESS_TOKEN=xxx node "$SKILL_DIR/scripts/searchApi.js" "/go-revenue/good/info" --md > "$用户指定路径/api-usage-go-revenue-good-info.md"
node "$SKILL_DIR/scripts/searchApi.js" "/api/user/list" --md > "$用户指定路径/api-usage-api-user-list.md"

# 限制条数、仍输出为 md
node "$SKILL_DIR/scripts/searchApi.js" "/go-revenue/good/info" --limit 50 --md > "$用户指定路径/api-usage-go-revenue-good-info.md"

# 仅需要机器可读时用 JSON
SOURCEGRAPH_ACCESS_TOKEN=xxx node "$SKILL_DIR/scripts/searchApi.js" "getUserInfo" --json
```

## 输出说明

- **本 skill 约定（助手）**：接口使用类查询的**默认产出**为 **Markdown 文件**（`--md` + 重定向或写入文件），便于留存与分享。
- **脚本 stdout 默认（无 `--md`/`--json`）**：纯文本——先列仓库列表，再列调用详情（仓库、路径、行号、代码行）。
- **`--json`**：便于下游处理或导入其他工具（用户或助手明确要求时使用）。
- **`--md`**：表格 + 表格内 HTML 代码块；**默认应保存为 `.md` 文件**，而非仅打印在对话里（除非用户只要摘要）。

脚本会过滤掉 `*.pb.go`、`*.swagger.json`、`openapi.yaml`、`*.md` 等生成/文档类文件。

## 场景示例与处理方式（助手）

下列为常见用户说法与推荐处理；执行前仍需满足「访问令牌」一节的要求。

| 用户意图（示例） | 如何处理 |
| --- | --- |
| 「哪些项目用了 `/api/foo/bar`」或贴了完整 path | 将 path **原样**作为第一个参数（字面量，默认不加 `--regex`）。用户指定了保存路径则 `--md` 重定向到 `api-usage-<路径摘要>.md`；**未指定路径**时不在仓库内擅自写文件：终端跑一遍拿结果，在回复里给摘要，并说明「未指定保存路径故未生成 Markdown 文件」；若用户明确表示要留存，可写入本 skill 目录下 `api-usage-*.md` 并告知绝对路径。 |
| 「只要前端 / 只要某团队仓库」 | `searchApi.js` **不会**把 `repo:`、`lang:` 等拼进请求，结果是全实例匹配。处理方式二选一：**(A)** 仍用脚本跑全量，`--md` 或 `--json` 产出后在表格「所属团队」或仓库名中筛 `frontend` 等；**(B)** 给用户一条可在 Sourcegraph 网页搜索框使用的完整查询（见下文「网页端限定范围」）。 |
| 「只要控制台 / 不要文件」 | 不传 `--md`，用默认文本输出；或用户自跑脚本只看 stdout。 |
| 「要 JSON 做二次处理」 | 使用 `--json`，由助手或用户用 `jq`/脚本过滤 `details[].repository`、`path` 等。 |
| 「可能是正则 / 多种写法」 | 使用 `--regex`，并提醒 RE2 语法与转义；复杂需求优先在网页用 `patternType:regexp` 试搜再固化字符串。 |
| 「结果太多、先抽样」 | 加 `--limit N`（控制 API `display` 上限，默认 3000）。 |
| 「查函数名或常量，不是 URL」 | 同样把标识符作为第一个参数；若含空格，在 shell 里用引号包住整段。 |
| 「解释/改一条 Sourcegraph 查询」 | 不强制跑脚本；按「构造 Sourcegraph 查询语法」帮用户写或改 `patternType`、`repo`、`file`、`lang`、`count`。 |

**网页端限定范围（脚本做不到时的补充）：** 当用户必须限定 `repo:frontend`、`lang:typescript` 等时，在 Sourcegraph 搜索框使用**完整**查询，例如：

```
patternType:literal "/your/api/path" repo:frontend lang:typescript count:all
```

脚本侧传入的 `api字符串` 若需与网页一致，应仅为其中的**搜索词**部分；过滤条件目前在网页或后续扩展脚本前由用户手写。

## 构造 Sourcegraph 查询语法

当用户需要**手写、修改或理解** Sourcegraph 搜索表达式时，按以下语法帮助构造。

**基本形式：** `[过滤与参数] 搜索词`（空格分隔）

### 模式类型 `patternType`

| 值 | 含义 |
| --- | --- |
| `literal` | 字面匹配（默认），精确字符串 |
| `regexp` | 正则（RE2 语法） |
| `structural` | 结构化匹配，适合多行/代码块 |

示例：`patternType:literal "/api/user"`、`patternType:regexp "func\s+\w+\s*\("`

### 常用过滤与参数

| 过滤 | 说明 | 示例 |
| --- | --- | --- |
| `repo:<正则>` | 限定仓库 | `repo:^gitlab\.yc345\.tv/backend/`、`repo:go-revenue` |
| `-repo:<正则>` | 排除仓库 | `-repo:.*-test` |
| `file:<正则>` | 限定文件路径/后缀 | `file:\.go$`、`file:src/.*\.ts` |
| `-file:<正则>` | 排除文件 | `-file:\.test\.` |
| `lang:<语言>` | 按语言 | `lang:go`、`lang:typescript` |
| `count:N` / `count:all` | 结果数量；全量用 `count:all` | `count:500`、`count:all` |

### 搜索词写法

- 无空格、无特殊字符：直接写，如 `GetUserInfo`
- 有空格或需精确短语：用双引号，如 `"get: \"/api/info\""`
- 正则：配合 `patternType:regexp`，注意转义

### 组合示例

```
# 某接口在后端仓库、字面匹配、要全部结果
patternType:literal "/go-revenue/good/info" repo:backend count:all

# 仅 Go 文件
patternType:literal "uuid_generate_v1mc()" lang:go count:500

# 正则、仅前端、排除测试文件
patternType:regexp "axios\.(get|post)" repo:frontend -file:\.test\. count:all
```

脚本 `searchApi.js` 内部会为传入的字符串加上 `patternType:literal`（或 `--regex` 时为 `regexp`）和 `count:all`；若用户需要在 Sourcegraph 网页或 API 中手写查询，可按上表自行组合。

## 帮助

运行 `node scripts/searchApi.js --help` 可查看完整用法。
