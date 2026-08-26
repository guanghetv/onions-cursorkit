# Onion Systematic Debugging 使用指南

`onion-systematic-debugging` 是洋葱技术栈专用的全链路排查 skill。核心通过 GitNexus 定位仓库、路由、handler 与调用链；只有需要验证现网行为时，才按需查询 metrics、trace、logs 或 Archery。

## 适用范围

适用：

- 洋葱前后端接口超时、5xx、空数据、字段不一致等问题
- 已知服务名、仓库、页面入口、HTTP path、gRPC operation 或错误文案
- 需要定位维护仓库及相关代码逻辑

不适用：

- 非洋葱项目、个人项目、开源项目或其他公司的技术栈
- 本地单测、编译错误等通用代码问题
- 直接修改代码或提交 Archery 工单

## 前置条件

### 必需：GitNexus MCP

GitNexus 是主路径，至少需要以下只读工具：

- `list_repos`
- `query`
- `context`
- `route_map`

目标仓库必须已被 GitNexus 索引。仓库未索引或索引过期时，skill 会明确报告能力缺口，不会假装已经定位。

### 可选：运行时 MCP

仅在需要验证某环境实际发生了什么时使用：

- `mcp-metrics`
- `mcp-trace`
- `mcp-logs`
- `mcp-archery`

调用任何运行时 MCP 前必须由用户明确唯一 `env`。同一证据包禁止混用不同环境的数据。

## 快速使用

在 Cursor Chat 输入：

```text
/onion-systematic-debugging 服务 teacher-desk 的 /api/lesson 接口返回空数据，请定位仓库和代码调用链
```

默认流程：

1. 判断是否为洋葱技术栈问题。
2. 用 GitNexus 找到维护仓库。
3. 根据路由、错误文案或服务名定位 handler、业务函数和下游调用。
4. 代码证据写完后给出置信度（`high`/`medium`/`low`）和代码侧初步结论；`high` + `stop` 时可直接收束。
5. 评估为需要现网验证时，再询问 `env` 和时间窗，并只加载必要的运行时域。

需要运行时证据时可直接提供环境：

```text
/onion-systematic-debugging 服务 order-api 的下单接口间歇性超时；先定位代码，如果需要运行时证据，只查询 prod 最近 15 分钟
```

不要这样使用：

```text
/onion-systematic-debugging 对比 prod 和 stage 的日志并综合判断
```

跨环境必须拆成两个独立证据包，不能聚合为同一次事故证据。

## 建议提供的信息

至少提供一项代码入口：

- 服务名或 GitLab 仓库路径
- HTTP path / gRPC operation
- 页面入口或前端组件
- 错误文案、错误码或日志关键词

如需运行时，再补充：

- 唯一 `env`
- 绝对时间窗，或可转换为绝对时间的相对时间
- `trace_id` / `request_id`（如有）
- `namespace`、topic 或数据库资源（对应域确实需要时）

## 安装 Command

### 方式一：在本仓库使用

本仓库已经包含：

```text
.cursor/commands/onion-systematic-debugging.md
```

用 Cursor 打开本仓库后，在 Chat 中输入 `/onion-systematic-debugging` 即可。若命令未出现，执行一次 **Developer: Reload Window** 或重启 Cursor。

### 方式二：安装到个人 Cursor（推荐）

在本仓库根目录执行。场景 skill 会引用三个已落地 domain skill，因此必须安装这个依赖闭包；`mcp-trace` 暂无独立 skill，只要求客户端已注册对应 tools。

```bash
mkdir -p "$HOME/.cursor/skills" "$HOME/.cursor/commands"
for name in onion-systematic-debugging metrics-query logs-query archery-query; do
  ln -sfn "$PWD/skills/$name" "$HOME/.cursor/skills/$name"
done
ln -sfn "$PWD/skills/onion-systematic-debugging/commands/onion-systematic-debugging.md" \
  "$HOME/.cursor/commands/onion-systematic-debugging.md"
```

然后重新加载 Cursor。该命令可在其他洋葱项目中使用；非洋葱项目仍会被 skill 门禁拒绝。

升级时更新本仓库即可；符号链接会继续指向单一源。若仓库移动，重新执行上述命令。

### 方式三：只安装到某个项目

在本仓库根目录执行，将 `<target-repo>` 替换为目标洋葱项目的绝对路径。项目级安装同样复制完整依赖闭包：

```bash
mkdir -p "<target-repo>/.cursor/skills" "<target-repo>/.cursor/commands"
for name in onion-systematic-debugging metrics-query logs-query archery-query; do
  mkdir -p "<target-repo>/.cursor/skills/$name"
  cp -R "skills/$name/." "<target-repo>/.cursor/skills/$name/"
done
cp "skills/onion-systematic-debugging/commands/onion-systematic-debugging.md" \
  "<target-repo>/.cursor/commands/onion-systematic-debugging.md"
```

项目级安装应提交到目标仓库前先遵循该仓库的代码审查与配置管理规则。

`skills/onion-systematic-debugging/commands/onion-systematic-debugging.md` 是 command 唯一编辑源；仓库 `.cursor/commands/` 下的同名文件只是受测试约束的项目适配副本。

## 输出内容

回复包含：

1. GitNexus 定位到的仓库、路由、符号、文件和调用链（`GN-*` 证据卡）
2. 静态代码逻辑对齐
3. 代码侧置信度与初步结论（不是现网「根因是」）
4. 运行时证据（仅实际加载时）
5. 单一可证伪假设与下一步
6. 未索引、MCP 不可用等能力缺口

该 skill 在 GitNexus 证据后给出代码侧评估；不修改代码，也不把静态判断写成现网根因。
