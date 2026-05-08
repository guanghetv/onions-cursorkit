# Cursor CLI 接手协议（第二阶段）

第一阶段（IDE 内 Cursor Agent）完成后，各目标仓库已存在**已推送的 feature 分支**。  
第二阶段由本机 **Cursor CLI Agent** 以 **Headless / Print 模式**执行，避免 IDE 内终端命令反复「Run / Allowlist」打断流程。

官方说明：[使用 Headless CLI](https://cursor.com/cn/docs/cli/headless)（`agent -p`，配合 `--force` 实际写文件）。

---

## IDE Agent 必须亲自启动 CLI（MUST）

- 写入上下文文件后，**必须由当前 IDE Agent 使用终端工具（Shell）执行**下列启动命令（或等价单行），**不得**把「仅可复制脚本」作为阶段B 的唯一完成标准。
- 执行成功后须在回复中写明：**CLI 日志路径**、**PID 文件路径**（若写入）、以及 `tail -f` 查看方式。
- 若 IDE 弹出终端执行授权（Run / Allowlist），Agent **仍应先发起命令**；用户点击允许后即视为符合本协议，不得因「怕弹窗」改为只发脚本不修文档规定的流程。
- 仅当 `which agent` 失败或 Shell 返回非零且已明确 **BLOCKED** 时，才可停止自动启动并给出安装/配置指引。

---

## 前置条件

```bash
which agent    # Cursor CLI 已安装且在 PATH 中
```

按需配置（脚本/自动化场景）：

```bash
export CURSOR_API_KEY=...   # 见官方安装与鉴权文档
```

GitLab MR：`GITLAB_TOKEN` 或 `GITLAB_PRIVATE_TOKEN`（与 SKILL 一致）。

---

## 任务上下文文件（IDE Agent 在启动 CLI 前写入）

路径建议：`/tmp/auto-dev-<run-id>.context.md`（也可用用户指定目录，但须为**绝对路径**）。

建议字段：

```markdown
# auto-dev CLI context

run_id: <run-id>
branch_name: <已在远端存在的分支名>

## 需求详情
<全文>

## 仓库列表
- name: <逻辑名>
  path: <仓库绝对路径>

## 技能绝对路径（供 CLI 内 Read）
aicr_local_skill: <.../aicr-local/SKILL.md>
mr_template: <.../auto-dev/references/MR_TEMPLATE.md>
```

---

## 启动命令（IDE Agent 用 Shell 执行；以下为示例）

由 **IDE Agent** 调用 Shell，在**任意 cwd** 均可执行（提示词内须含 `${CONTEXT}` 绝对路径）。**提示词中必须包含上下文文件路径**，使 CLI 能读到需求与仓库列表：

```bash
CONTEXT="/tmp/auto-dev-<run-id>.context.md"
LOG="/tmp/auto-dev-<run-id>.cli.log"

nohup agent -p --force --output-format text \
  "你是 auto-dev 第二阶段执行器。请读取文件：${CONTEXT}。
  然后对每个仓库 path：
  1) cd 到该 path，git fetch origin && git checkout <branch_name>（分支已由第一阶段推送）
  2) 按需求详情完成小需求改动；范围边界与 SKILL 一致（文件数等）
  3) 运行项目 lint（如 npm run lint），失败则自修至多 1 轮
  4) git add . 后按 aicr_local_skill 路径读取 aicr-local，以暂存区模式执行 CR；Critical 自修至多 3 轮
  5) git commit / git push
  6) 按 mr_template 生成描述，glab 或 curl 创建 MR，target=develop，使用环境变量 GITLAB_TOKEN
  逐仓库顺序执行；任一仓库 BLOCKED 则记录原因并继续下一仓库。
  全部结束后在输出中给出 MR 链接汇总。" \
  >> "${LOG}" 2>&1 &

echo $! > "/tmp/auto-dev-<run-id>.cli.pid"
echo "CLI 日志: tail -f ${LOG}"
```

说明：

- **`--force`**：允许在无交互下修改文件（见 Headless 文档）。
- **多仓库**：提示词中明确「顺序执行」；若需并行，可用多个 `nohup`（注意资源与锁）。
- CLI 权限与 IDE **相互独立**，见 [permissions.json](https://cursor.com/docs/reference/permissions) 中「CLI permissions are separate」。

---

## IDE Agent 在 Shell 成功启动 CLI 后的职责

1. 再次向用户输出：`run-id`、已启动的 **PID**（若已写入 `.pid` 文件则一并说明）、CLI **日志路径**、`tail -f` 命令。
2. **不再**在 IDE 会话内执行 `npm run lint`、批量改业务代码（避免终端审批风暴）。
3. 可选：轮询或等待 CLI 日志中出现 `[MR_CREATED]` / 汇总段落后，读取日志并向用户输出「完成通知」；若异步仅告知查看日志也可，但**不得**省略「已由 Shell 启动 CLI」这一事实。

---

## 失败处理

| 现象 | 处理 |
|------|------|
| `which agent` 为空 | BLOCKED：提示安装 Cursor CLI 后重试 |
| CLI 日志中报 Critical 3 轮未过 | BLOCKED：按 SKILL 人工接管 |
| Token 缺失 | BLOCKED：配置 GITLAB_TOKEN |
