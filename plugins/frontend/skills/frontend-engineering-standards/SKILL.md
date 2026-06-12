---
name: frontend-engineering-standards
description: Use when working on frontend code, naming variables or types, writing git commit messages, adding comments or JSDoc, configuring ESLint, Prettier, stylelint, Husky, lint-staged, or commitlint, or when the user mentions code standards, commit rules, formatting, logging, or console.log.
---

# Frontend Engineering Standards

## Overview

This skill captures the project's frontend engineering standards.

Use it when the task touches:

- commit message writing
- naming symbols and types
- comments or JSDoc
- lint and format toolchains
- debug logging conventions

默认使用中文说明，保留常用英文术语与配置名，避免把规则解释得过长。

## When to Use

Use this skill when the user asks to:

- 写 `git commit message`
- 命名变量、方法、泛型、接口、类、弹窗、工具类
- 补充注释、JSDoc、`@link`
- 配置或解释 `ESLint`、`stylelint`、`Prettier`
- 配置 `lint-staged`、`Husky`、`commitlint`
- 讨论 `console.log`、调试日志、logger 方案
- 对齐前端代码规范、提交规范、格式规范

Do not use this skill for backend-only conventions that are unrelated to frontend engineering standards.

## Commit Message Rules

提交信息遵循 Angular-style format:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### Required Rules

- 每个 commit message 可包含 `subject`、`body`、`footer`
- 各部分之间使用空行分隔
- 任意一行不超过 100 个字符
- `scope` 写影响范围，尽量具体

### Allowed `type`

- `feat`: 一个新特性
- `fix`: 修复 bug
- `docs`: 文档修改
- `style`: 不影响代码含义的更改，如空格、格式化、缺少分号
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试用例修改
- `chore`: 构建过程、辅助工具或依赖调整

### `subject` Rules

- 使用陈述语句
- 首字母不要大写
- 末尾不要加 `.`
- 保持简洁，优先写清楚 why 或主要变化点

### Example

```text
feat(auth): add login request validation

Validate request payload before calling the login API and align the
error path with the existing auth flow.
```

### Guidance for Agent

When drafting a commit message:

- 先判断主要变更属于哪一种 `type`
- 如果能看出影响范围，就补上 `scope`
- 不要输出只含 `type: subject` 且没有 `scope` 的格式，除非用户明确要求省略
- 如果一次提交混合多种改动，优先围绕“最主要的业务变化”命名

## Naming Rules

### Core Principle

命名要 `readable` 且 `searchable`。

Avoid:

- 生僻、难发音、随意拼接的单词
- 过度缩写
- 无法通过 IDE 联想触发补全的命名

### General Naming

- 优先使用能表达业务含义的完整单词
- 命名要让人能通过关键词联想到相关方法或字段
- 看到名字就应该大致知道职责，不要依赖注释补义

### Camel Case and Acronyms

缩写按普通单词处理，不要全大写连写。

Good:

- `loadHttpUrl`
- `parseJsonValue`

Avoid:

- `loadHTTPURL`
- `parseJSONVALUE`

Exception:

- 平台约定名可保留，例如 `XMLHttpRequest`

### Generic Type Parameters

泛型参数尽量语义化，不要默认只写单个大写字母。

Good:

```ts
type RequestParams<
  Page extends PageType = 'Home',
  Tab extends TabType = 'DailyTab',
>
```

Avoid:

```ts
type RequestParams<T, U>
```

### `_` Prefix

标识符可以使用 `_` 前缀表示“当前未使用”，但不要把未使用变量带到最终产物中。

If skipping tuple items, prefer destructuring holes instead of fake names:

```ts
const [a, , b] = [1, 5, 10]
```

### Constants

不可变值使用 `CONSTANT_CASE`。

```ts
const UNIT_SUFFIXES = {
  milliseconds: 'ms',
  seconds: 's',
}
```

类中的 `static readonly` 常量也遵循同样思路：

```ts
class InteractiveCourseApplication {
  private static readonly DESIGN_WIDTH = 667
}
```

### Industry Conventions

- 接口前缀使用 `I`，例如 `IUserService`
- 弹窗后缀使用 `Dialog`，例如 `AppUpdateDialog`
- 工具类后缀使用 `Utils` 或 `Helper`，例如 `TrackUtils`、`VoiceHelper`

### Guidance for Agent

When naming symbols:

- 接口优先考虑 `I` 前缀
- 如果用户明确说是“工具类”，优先使用 `Utils` 或 `Helper`，不要随意改成 `Service`
- 如果是弹窗组件，优先补 `Dialog`
- 泛型名优先表达角色，例如 `Page`、`Tab`、`Filters`、`ResponseData`

## Comment Rules

### Principle

- As short as possible
- As long as necessary

优先提升代码本身的可读性；只有当代码本身难以直接表达意图时，再补充注释。

### JSDoc

Basic format:

```ts
/**
 * 进行截图
 * @param options 截图选项
 */
const screenShot = (options: ScreenshotOptions) => {}
```

Single-line form is also acceptable:

```ts
/** 进行截图，返回 blob */
const screenShot = (options: ScreenshotOptions) => {}
```

Guidance:

- 在 TypeScript 中，通常不必重复写 `@param` 或 `@returns` 的类型
- 参数说明仍然有价值，尤其是业务含义不直观时
- 注释应解释意图、限制、前后行为差异，而不是重述代码

### Markdown in JSDoc

`JSDoc` 支持 Markdown，必要时优先使用列表，而不是靠纯文本缩进表达层级。

Good:

```ts
/**
 * 连线题匹配
 *
 * - FixedEffect: 连线固定，代表连对
 * - BounceEffect: 连线回弹，代表连错
 */
connectionEffect?: 'FixedEffect' | 'BounceEffect'
```

### `@link`

Use `@link` to connect related logic:

```ts
/**
 * 自适应停止，先停止录音
 *
 * 当 {@link onResult} 监听到 isLast 时再停止监听回调
 */
function stop() {}
```

### Guidance for Agent

When adding comments:

- 没有必要时不要加注释
- 需要说明业务意图、边界条件、调用时机时再加
- 如果是对外 API、复杂行为或跨模块关联，优先补 `JSDoc`
- 如果要列举枚举含义，优先使用 Markdown list

## Formatting and Toolchain

该项目的格式与质量保障依赖如下工具链：

- `ESLint`: 检查 `ts`、`js`、`vue2`、`vue3` 的语法问题与潜在风险
- `stylelint`: 检查 `CSS`、`SCSS`、`Less`
- `Prettier`: 统一代码格式
- `lint-staged`: 只在 Git 暂存区文件上运行检查
- `Husky`: 在 Git hooks 中执行校验流程
- `commitlint`: 校验提交信息是否符合规范
- `VSCode`: 保存时按项目规则自动格式化

### Prettier Preferences

When asked to align formatting, prefer these key settings:

```json
{
  "printWidth": 80,
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "endOfLine": "lf"
}
```

If the user asks for a full formatter setup, keep consistency with the project's existing formatter config rather than inventing a new style.

### Guidance for Agent

- 涉及代码风格时，优先提 `ESLint + Prettier + stylelint`
- 涉及提交前校验时，优先提 `lint-staged + Husky`
- 涉及提交信息规范时，优先提 `commitlint`
- 不要把这些工具说成可选装饰；它们是工程约束的一部分

## Logging Rules

### Principle

- 不建议线上代码直接使用 `console.log`
- 开发环境需要输出调试信息时，优先使用 `utils` 库提供的 `createLogger`
- `createLogger` 需要带项目分区名

Example:

```ts
const CustomLogger = createLogger('ai-summarize-custom')
```

### Guidance for Agent

When the user asks how to add logs:

- 不要先推荐直接写 `console.log`
- 优先说明开发环境使用 `createLogger('project-zone')`
- 如果用户只是临时排查，也要提醒避免把临时日志带到线上

## Quick Reference

### Commit

- Format: `<type>(<scope>): <subject>`
- Subject: 小写开头、陈述语句、无句号
- Line length: under 100 chars

### Naming

- readable + searchable
- acronym as word: `loadHttpUrl`
- interface: `IUserService`
- dialog: `AppUpdateDialog`
- utility class: `TrackUtils` / `VoiceHelper`
- constants: `CONSTANT_CASE`

### Comments

- no comment if code is already obvious
- use `JSDoc` for external API or complex behavior
- use Markdown list inside JSDoc when listing options
- use `@link` for related logic

### Toolchain

- quality: `ESLint`, `stylelint`
- formatting: `Prettier`
- staged checks: `lint-staged`
- hooks: `Husky`
- commit validation: `commitlint`

### Logging

- avoid production `console.log`
- prefer `createLogger('project-zone')`

## Common Mistakes

- 把 commit message 写成 `feat: xxx`，却缺少 `scope`
- `subject` 首字母大写或结尾带 `.`
- 把工具类命名成 `SomethingService`
- 泛型参数命名成没有业务意义的 `T`、`U`
- 给明显代码补废话注释
- 在正式代码中直接建议 `console.log`
- 只谈 `Prettier`，忽略 `ESLint`、`stylelint`、`Husky`、`commitlint`
