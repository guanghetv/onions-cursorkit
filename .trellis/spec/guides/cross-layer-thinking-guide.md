# 跨层思考指南（Cross-Layer Thinking Guide）

> **目的**：在实现之前先想清楚跨层的数据流。

---

## 问题所在

**大多数 bug 发生在层边界**，而不是层内部。

常见跨层 bug：

- API 返回格式 A，前端期望格式 B
- 数据库存 X，service 转成 Y，但丢了数据
- 多层以不同方式实现同一逻辑

---

## 实现跨层功能之前

### 步骤 1：画出数据流

画出数据如何流动：

```
Source → Transform → Store → Retrieve → Transform → Display
```

对每个箭头，问：

- 数据处于什么格式？
- 可能出什么问题？
- 谁负责校验？

### 步骤 2：识别边界

| 边界 | 常见问题 |
| ---- | -------- |
| API ↔ Service | 类型不匹配、字段缺失 |
| Service ↔ Database | 格式转换、null 处理 |
| Backend ↔ Frontend | 序列化、日期格式 |
| Component ↔ Component | Props 形状变化 |

### 步骤 3：定义契约

对每个边界：

- 精确的输入格式是什么？
- 精确的输出格式是什么？
- 可能出现哪些错误？

---

## 常见跨层错误

### 错误 1：隐式格式假设

**不好**：不检查就假设日期格式

**好**：在边界处显式做格式转换

### 错误 2：校验散落各处

**不好**：在多层重复校验同一件事

**好**：在入口处校验一次

### 错误 3：泄漏的抽象

**不好**：组件知道数据库 schema

**好**：每层只了解相邻层

### 错误 4：每个消费者都解析同一份 payload

**不好**：命令读取 JSONL 事件并在行内 cast 字段：

```typescript
const thread = (ev as { thread?: string }).thread;
const labels = (ev as { labels?: string[] }).labels;
```

这看起来是局部的，但意味着每个消费者都拥有一份私有的事件契约。下次字段变更会更新一个命令而漏掉另一个。

**好**：在事件边界解码一次，然后导出类型化的 projection：

```typescript
if (!isThreadEvent(ev)) return false;
return ev.thread === filter.thread;
```

**规则**：对于 append-only 日志、JSON 流、RPC payload 或配置文件，为以下内容创建唯一所有者：

- event / payload 类型定义
- 从 `unknown` 出发的 type guard 与规范化
- UI 命令使用的 metadata projection
- 从真相源回放状态的 reducer

渲染代码可以格式化字段，但不得重新定义 payload 契约。

---

## 跨层功能检查清单

实现前：

- [ ] 已画出完整数据流
- [ ] 已识别所有层边界
- [ ] 已定义每个边界的格式
- [ ] 已决定校验发生在何处

实现后：

- [ ] 用边界情况测试过（null、空、非法）
- [ ] 验证了每个边界的错误处理
- [ ] 检查数据能否往返存活
- [ ] 检查消费者是否 import 共享 decoder / projection，而不是在本地 cast payload 字段
- [ ] 检查派生状态是否回指源事件标识符（`seq`、`id`、`version`），而不是发明第二个游标

---

## 跨平台模板一致性

在 Trellis 中，命令模板（例如 `record-session.md`）存在于**多个平台**，内容相同或近乎相同。这是一个跨层边界。

### 检查清单：修改任一命令模板之后

- [ ] 找出所有拥有同一命令的平台：`find src/templates/*/commands/trellis/ -name "<command>.*"`
- [ ] 更新所有平台副本（Markdown `.md` 与 TOML `.toml`）
- [ ] 对 Gemini TOML：适配行续写（`\\` vs `\`）与三引号字符串
- [ ] 运行 `/trellis:check-cross-layer` 确认没有遗漏

**真实案例**：在 Claude 中把 `record-session.md` 更新为使用 `--mode record`，但忘了 iFlow、Kilo、OpenCode 和 Gemini——被跨层检查抓住。

---

## 生成式运行时模板升级一致性

有些生成文件既是文档也是运行时输入。在 Trellis 中，`.trellis/workflow.md` 会被 `get_context.py`、`workflow_phase.py`、SessionStart 过滤器以及每轮 hook 解析。模板变更必须同时针对全新 init 与升级路径做校验。

### 检查清单：修改运行时解析的模板之后

- [ ] 识别每一个读取该模板的运行时解析器，而不只是安装它的文件写入器
- [ ] 检查相关语法是否落在明显托管区域（如 tag 块）之外
- [ ] 验证全新 `init` 输出，以及写入较旧 `.trellis/.version` 的版本化 `update` 场景
- [ ] 用较旧的原始模板 fixture 增加升级回归，然后断言已安装文件达到当前打包形态
- [ ] 更新拥有该运行时契约的 backend spec

---

## 版本化文档边界

版本化文档是一个跨层边界：源路径、`docs.json` 版本路由，以及渲染出的版本选择器，都必须描述同一条发布线。

### 检查清单：编辑版本化文档之前

- [ ] 识别目标发布线：stable、beta 或 RC
- [ ] 确认编辑的 MDX 路径与该发布线匹配：
  - stable：`docs-site/{start,advanced,...}` 与 `docs-site/zh/{start,advanced,...}`
  - beta：`docs-site/beta/**` 与 `docs-site/zh/beta/**`
  - RC：`docs-site/rc/**` 与 `docs-site/zh/rc/**`
- [ ] 确认 `docs.json` 导航把版本标签指向相同路径
- [ ] 提交前在对面树中 grep 发布线特定术语
- [ ] 把出现在根发布路径下的 beta 内容视为源路径 bug，而不是渲染 bug

**真实案例**：一项仅 beta 的任务工作流变更，把 `prd.md` + `design.md` + `implement.md`、任务创建同意，以及 Codex 模式横幅文档写在了根路径 `start/` 与 `advanced/` 下。文档站随后在 Release 选择器下提供了 0.6 beta 行为。修复是恢复根发布文档，把 0.6 内容移到 `beta/` 与 `zh/beta/`，并增加对根发布树的 beta 标记 grep 审计。

**真实案例**：Codex inline 模式把工作流平台标记从 `[Codex]` / `[Kilo, Antigravity, Windsurf]` 改为 `[codex-sub-agent]` / `[codex-inline, Kilo, Antigravity, Windsurf]`。全新 init 正确，但 `trellis update` 只合并 `[workflow-state:*]` 块，并保留这些块之外的陈旧标记。结果：升级后的项目拿到了新的 hook 脚本，但工作流路由仍是旧的，因此 `get_context.py --mode phase --platform codex` 可能返回空的 Phase 2.1 详情。

---

## 模式探测 Probe 检查清单

当 CLI 通过探测远程资源自动检测模式时（例如检查 `index.json` 是否存在，以决定 marketplace 还是直接下载）：

### 实现前：

- [ ] Probe 在**所有**使用其结果的代码路径中运行（interactive、`-y`、`--flag` 组合）
- [ ] 区分 404 与瞬时错误——不要把两者都当成「未找到」
- [ ] 瞬时错误应**中止或重试**，绝不能静默切换模式
- [ ] 上下文变化时（例如用户切换源）必须**重置**共享状态（缓存、预取数据）
- [ ] **快捷路径**（例如 `--template` 跳过选择器）必须与探测路径有同等的错误处理质量——检查下游函数是否调用了 catch-all 包装器

### 实现后：

- [ ] 追踪从 probe 结果到模式决策分支的每条路径——无 fallthrough
- [ ] 外部格式契约（giget URI、原始 URL）已测试，或至少以注释文档化
- [ ] 元数据读取消费完整响应或使用流式解析器——绝不要把固定大小前缀当完整 JSON 解析
- [ ] 从解析出的部分重建复合标识符时，确认**所有**字段都包含且位置**正确**（例如 `provider:repo/path#ref`，而不是 `provider:repo#ref/path`）
- [ ] 确认快捷路径之后调用的**动作函数**内部没有使用旧的 catch-all fetch——在需要区分错误时，必须使用 probe 质量的变体

**真实案例**：自定义 registry 流程在 3 轮评审中出现 8 个 bug：（1）probe 只在 interactive 模式运行；（2）瞬时错误落入错误模式；（3）giget URI 的 `#ref` 位置错误；（4）预取模板在源切换时泄漏；（5）`--template` 快捷路径绕过了 probe，但 `downloadTemplateById` 内部使用 catch-all `fetchTemplateIndex`，把超时变成了「Template not found」。

**真实案例**：Agent 会话更新提示用 `response.read(4096)` 拉取 npm `latest` 元数据，然后当完整 JSON 解析。`@mindfoldhq/trellis` 包元数据超过 4 KB，JSON 被截断，解析静默失败，首次会话注入没有显示更新提示。修复：解析前读取完整响应，并增加回归：`version` 后面跟 8 KB 元数据尾巴。

---

## 跨平台模板一致性

在 Trellis 中，命令模板（例如 `record-session.md`）存在于**多个平台**，内容相同或近乎相同。这是一个跨层边界。

### 检查清单：修改任一命令模板之后

- [ ] 找出所有拥有同一命令的平台：`find src/templates/*/commands/trellis/ -name "<command>.*"`
- [ ] 更新所有平台副本（Markdown `.md` 与 TOML `.toml`）
- [ ] 对 Gemini TOML：适配行续写（`\\` vs `\`）与三引号字符串
- [ ] 运行 `/trellis:check-cross-layer` 确认没有遗漏

**真实案例**：在 Claude 中把 `record-session.md` 更新为使用 `--mode record`，但忘了 iFlow、Kilo、OpenCode 和 Gemini——被跨层检查抓住。

---

## 生成式运行时模板升级一致性

有些生成文件既是文档也是运行时输入。在 Trellis 中，`.trellis/workflow.md` 会被 `get_context.py`、`workflow_phase.py`、SessionStart 过滤器以及每轮 hook 解析。模板变更必须同时针对全新 init 与升级路径做校验。

### 检查清单：修改运行时解析的模板之后

- [ ] 识别每一个读取该模板的运行时解析器，而不只是安装它的文件写入器
- [ ] 检查相关语法是否落在明显托管区域（如 tag 块）之外
- [ ] 验证全新 `init` 输出，以及写入较旧 `.trellis/.version` 的版本化 `update` 场景
- [ ] 用较旧的原始模板 fixture 增加升级回归，然后断言已安装文件达到当前打包形态
- [ ] 更新拥有该运行时契约的 backend spec

**真实案例**：Codex inline 模式把工作流平台标记从 `[Codex]` / `[Kilo, Antigravity, Windsurf]` 改为 `[codex-sub-agent]` / `[codex-inline, Kilo, Antigravity, Windsurf]`。全新 init 正确，但 `trellis update` 只合并 `[workflow-state:*]` 块，并保留这些块之外的陈旧标记。结果：升级后的项目拿到了新的 hook 脚本，但工作流路由仍是旧的，因此 `get_context.py --mode phase --platform codex` 可能返回空的 Phase 2.1 详情。

---

## 模式探测 Probe 检查清单

当 CLI 通过探测远程资源自动检测模式时（例如检查 `index.json` 是否存在，以决定 marketplace 还是直接下载）：

### 实现前：
- [ ] Probe 在**所有**使用其结果的代码路径中运行（interactive、`-y`、`--flag` 组合）
- [ ] 区分 404 与瞬时错误——不要把两者都当成「未找到」
- [ ] 瞬时错误应**中止或重试**，绝不能静默切换模式
- [ ] 上下文变化时（例如用户切换源）必须**重置**共享状态（缓存、预取数据）
- [ ] **快捷路径**（例如 `--template` 跳过选择器）必须与探测路径有同等的错误处理质量——检查下游函数是否调用了 catch-all 包装器

### 实现后：
- [ ] 追踪从 probe 结果到模式决策分支的每条路径——无 fallthrough
- [ ] 外部格式契约（giget URI、原始 URL）已测试，或至少以注释文档化
- [ ] 元数据读取消费完整响应或使用流式解析器——绝不要把固定大小前缀当完整 JSON 解析
- [ ] 从解析出的部分重建复合标识符时，确认**所有**字段都包含且位置**正确**（例如 `provider:repo/path#ref`，而不是 `provider:repo#ref/path`）
- [ ] 确认快捷路径之后调用的**动作函数**内部没有使用旧的 catch-all fetch——在需要区分错误时，必须使用 probe 质量的变体

**真实案例**：自定义 registry 流程在 3 轮评审中出现 8 个 bug：（1）probe 只在 interactive 模式运行；（2）瞬时错误落入错误模式；（3）giget URI 的 `#ref` 位置错误；（4）预取模板在源切换时泄漏；（5）`--template` 快捷路径绕过了 probe，但 `downloadTemplateById` 内部使用 catch-all `fetchTemplateIndex`，把超时变成了「Template not found」。

**真实案例**：Agent 会话更新提示用 `response.read(4096)` 拉取 npm `latest` 元数据，然后当完整 JSON 解析。`@mindfoldhq/trellis` 包元数据超过 4 KB，JSON 被截断，解析静默失败，首次会话注入没有显示更新提示。修复：解析前读取完整响应，并增加回归：`version` 后面跟 8 KB 元数据尾巴。

---

## 何时创建流程文档

在以下情况创建详细流程文档：

- 功能跨越 3+ 层
- 涉及多个团队
- 数据格式复杂
- 该功能以前出过 bug

---

## 事件日志 / Projection 边界

Append-only 日志是跨层契约。单个事件会经过：

```
CLI input → event writer → events.jsonl → reader → filter → reducer → display
```

### 检查清单：新增事件 kind 或字段之后

- [ ] 把事件 kind 加入中央事件分类法
- [ ] 在事件层添加类型化事件变体或 type guard
- [ ] 为来自用户输入或 JSON 的数组/对象字段添加规范化 helper
- [ ] 把 `seq` / `id` 赋值只放在 event writer 中
- [ ] 让 filter 与 reducer 消费类型化事件 guard，而不是本地 cast
- [ ] 让展示代码消费 reducer 输出或类型化事件，而不是原始 JSON
- [ ] 至少增加一个回归，证明历史回放与实时过滤使用同一 filter 模型

**真实案例**：Thread 频道增加了 `kind: "thread"`、`description`、`context`、labels 与 `lastSeq`。首次实现正确回放了 thread 状态，但若干命令仍用本地 cast 重新解析事件 payload 字段。修复是让核心事件层拥有 `ThreadChannelEvent` 与 `isThreadEvent`，让 `reduceChannelMetadata` 成为唯一的频道 metadata projection，让 `reduceThreads` 成为唯一的 thread 回放 reducer。
