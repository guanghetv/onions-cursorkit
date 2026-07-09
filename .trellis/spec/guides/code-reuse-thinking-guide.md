# 代码复用思考指南（Code Reuse Thinking Guide）

> **目的**：在创建新代码之前停下来想一想——它是否已经存在？

---

## 问题所在

**重复代码是不一致类 bug 的头号来源。**

当你复制粘贴或重写已有逻辑时：
- Bug 修复无法传播
- 行为会随时间分叉
- 代码库更难理解

---

## 写新代码之前

### 步骤 1：先搜索

```bash
# Search for similar function names
grep -r "functionName" .

# Search for similar logic
grep -r "keyword" .
```

### 步骤 2：问自己这些问题

| 问题 | 如果是…… |
|------|----------|
| 是否已有类似函数？ | 使用或扩展它 |
| 这个模式是否在别处用过？ | 遵循已有模式 |
| 这能否做成共享工具？ | 在正确位置创建它 |
| 我是否在从另一个文件复制代码？ | **停下**——提取为共享代码 |

---

## 常见重复模式

### 模式 1：复制粘贴函数

**不好**：把校验函数复制到另一个文件

**好**：提取到共享 utilities，在需要处 import

### 模式 2：相似组件

**不好**：新建一个与现有组件 80% 相似的组件

**好**：用 props/variants 扩展现有组件

### 模式 3：重复常量

**不好**：在多个文件中定义同一个常量

**好**：单一真相源，到处 import

### 模式 4：重复的 payload 字段提取

**不好**：多个消费者在本地对同一组 JSON/event 字段做 cast：

```typescript
const description = (ev as { description?: string }).description;
const context = (ev as { context?: ContextEntry[] }).context;
```

即便只有两行，这也是重复的契约逻辑。每个消费者现在各自定义了「合法 payload」的含义。

**好**：把 decoder、type guard 或 projection 放在数据所有者旁边：

```typescript
if (isThreadEvent(ev)) {
  renderThreadEvent(ev);
}
```

**规则**：如果同一未类型化的 payload 字段在 2+ 处被读取，在增加第三个读取者之前，先创建共享的 type guard / normalizer / projection。

---

## 何时抽象

**应当抽象当**：
- 相同代码出现 3+ 次
- 逻辑复杂到足以产生 bug
- 可能有多人需要这段逻辑

**不要抽象当**：
- 只用一次
- 平凡的一行代码
- 抽象会比重复更复杂

---

## 批量修改之后

当你对多个文件做了类似修改时：

1. **复查**：是否覆盖了所有实例？
2. **搜索**：跑 grep 查找遗漏
3. **考虑**：是否应当抽象？

### Reducer 应使用穷尽式结构

当状态由类似 action 的值（`action`、`kind`、`status`、`phase`）推导时，优先用带一个 `switch` 的 reducer，而不是散落的 `if/else` 更新。

```typescript
// BAD - action-specific state transitions are hard to audit
if (action === "opened") { ... }
else if (action === "comment") { ... }
else if (action === "status") { ... }

// GOOD - one reducer owns the transition table
switch (event.action) {
  case "opened":
    ...
    return;
  case "comment":
    ...
    return;
}
```

当 event log 是真相源时，这一点尤为重要。Reducer 是文档化的回放模型；展示代码与命令不应复制该回放模型的片段。

---

## 提交前检查清单

- [ ] 已搜索现有相似代码
- [ ] 没有本应共享却被复制粘贴的逻辑
- [ ] 没有在共享 decoder 之外重复提取未类型化的 payload 字段
- [ ] 常量只在一处定义
- [ ] 相似模式遵循同一结构
- [ ] Reducer/action 转换集中在一个 reducer 或 command dispatcher 中

---

## 陷阱：Python if/elif/else 穷尽检查

**问题**：Python 的 if/elif/else 链没有编译期穷尽检查。当你向 `Literal` 类型（例如 `Platform`）新增一个值时，现有的 if/elif/else 链会静默落入 `else`，并带上错误的默认值。

**症状**：新平台只部分生效——部分方法返回 Claude 默认值而非平台特定值。不会抛出错误。

**示例**（`cli_adapter.py`）：
```python
# BAD: "gemini" falls through to else, returns "claude"
@property
def cli_name(self) -> str:
    if self.platform == "opencode":
        return "opencode"
    else:
        return "claude"  # gemini silently gets "claude"!

# GOOD: explicit branch for every platform
@property
def cli_name(self) -> str:
    if self.platform == "opencode":
        return "opencode"
    elif self.platform == "gemini":
        return "gemini"
    else:
        return "claude"
```

**预防**：向 Python `Literal` 类型新增值时，搜索所有按该类型分支的 if/elif/else 链并补上显式分支。不要依赖 `else` 对新值仍然正确。

---

## 陷阱：不对称机制产出相同结果

**问题**：当两种不同机制必须产出同一组文件时（例如 init 用递归目录复制，update 用手动 `files.set()`），结构变更（重命名、移动、新增子目录）只会通过自动机制传播。手动机制会静默漂移。

**症状**：Init 完美工作，但 update 把文件写到错误路径或完全漏掉文件。

**预防**：
- **最佳**：消除不对称——让手动路径调用自动路径（例如 `collectTemplateFiles()` 调用 `getAllScripts()`，而不是维护自己的列表）
- **若无法避免不对称**：增加回归测试，比较两种机制的输出
- 迁移目录结构时，搜索所有引用旧结构的代码路径

**真实案例**：`trellis update` 曾有一份手动 `files.set()` 列表，列出 11 个脚本，而这些脚本 `getAllScripts()` 已经在跟踪。修复：用 `for..of getAllScripts()` 循环替换手动列表。见 v0.4.0-beta.3 中的 `update.ts` 重构。

---

## 模板文件注册（Trellis 专用）

向 `src/templates/trellis/scripts/` 添加新文件时：

**唯一注册点**：`src/templates/trellis/index.ts`

1. 添加 `export const xxxScript = readTemplate("scripts/path/file.py");`
2. 加入 `getAllScripts()` Map

就这些。`commands/update.ts` 直接使用 `getAllScripts()`——无需手动同步。

**为何重要**：若不在 `getAllScripts()` 中注册，`trellis update` 不会把该文件同步到用户项目。Bug 修复与功能无法传播。

**历史**：在 v0.4.0-beta.3 之前，`update.ts` 有自己手维护的文件列表，经常与 `getAllScripts()` 不同步。这导致 11 个 Python 文件在 `trellis update` 时被静默跳过。修复是消除重复列表，以 `getAllScripts()` 作为唯一真相源。

### 新脚本快速检查清单

```bash
# After adding a new .py file, verify it's in getAllScripts():
grep -l "newFileName" src/templates/trellis/index.ts  # Should match
```

### 模板同步约定

`.trellis/scripts/`（dogfood）与 `packages/cli/src/templates/trellis/scripts/`（模板）必须保持一致。编辑 `.trellis/scripts/` 后，务必同步：

```bash
rsync -av --delete --exclude='__pycache__' .trellis/scripts/ packages/cli/src/templates/trellis/scripts/
```

**陷阱**：rsync 的源/目标路径写反会创建嵌套垃圾目录（例如 `.trellis/scripts/packages/cli/...`）。运行前务必再核对路径。
