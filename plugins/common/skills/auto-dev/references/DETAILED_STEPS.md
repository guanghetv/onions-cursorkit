# 详细步骤说明

## 步骤0：输入门禁校验

- 必须收到"需求详情描述"。
- 必须收到"飞书卡片链接"或"明确开发分支名"之一。
- 若飞书卡片链接与明确分支名都缺失：立即中断并提示开发者补充后再继续。

## 步骤1：拉取飞书卡片详情（可用时）

- 若输入包含飞书卡片链接，优先查询卡片详情。
- 查询成功时：以飞书卡片内容优先推断需求详情，补全需求上下文。
- 查询失败时：回退到开发者提供的需求详情继续执行，并在输出中记录"卡片详情获取失败"。

## 步骤2：强制扫描当前工作区

- 扫描工作区内所有注册项目（workspace 模式）。
- 通过需求关键词、模块名、页面名、文案片段进行命中判定。
- 输出命中项目及证据（文件路径、关键词命中、模块映射）。
- 若命中数为 0：立即阻断，提示补充需求信息或手动指定项目后重试。
- 若"当前项目"未命中：明确提示"当前项目与需求不匹配"，禁止在当前项目硬改。

## 步骤3：一次人工确认范围

- 展示命中项目列表（单项目/多项目）及命中证据。
- 展示将使用的分支名。
- 支持确认全部或排除部分项目后确认。
- 确认后冻结项目范围，本次执行不再自动新增项目。
- 确认卡片必须包含"当前项目命中状态"和"证据摘要"。

> ⚠️ **这是全流程唯一的人工操作节点。**

## 步骤4：生成 run-id 并进入阶段A

用户确认后，在 **IDE 内 Agent** 立即：

1. 生成 `run-id`（格式：`auto-dev-YYYYMMDD-HHmm-<首个仓库名缩写>`）
2. 输出执行计划（run-id、目标仓库、分支名、**两阶段说明**）

```
✅ 已确认 → 阶段A：各仓库创建并推送分支
→ 阶段B：本机 Cursor CLI 无头改码 / lint / CR / MR
run-id  : auto-dev-20260420-1523-branstark
```

---

## 阶段A（IDE）：仅建分支

对每个目标仓库**顺序**执行。**本阶段不写业务代码、不跑 npm lint。**

### A-1 路径与技能

切换到仓库根目录：

```bash
cd <repo绝对路径>
git remote get-url origin   # 校验仓库
```

读取 **相对于 auto-dev 技能目录**的 `../create-feature-branch/SKILL.md`（或使用你在上下文里记录的该文件**绝对路径**），严格按其「快速执行清单」执行：

```bash
git status --porcelain       # 必须为空，否则 BLOCKED
git fetch origin
git checkout master && git pull origin master
git branch --show-current    # 须为 master（或技能允许的显式基线例外）
git checkout -b <branch_name>
git push -u origin <branch_name>
```

分支名须在步骤 1～3 已对齐，不在本步骤重新发明名称。

全部仓库完成后：

```
[阶段A 完成] run-id=... 已推送分支=<branch_name> 仓库=<...>
```

---

## 阶段B（本机 Cursor CLI）：改动 / lint / CR / MR

### B-1 校验 CLI

```bash
which agent || { echo BLOCKED: 请安装 Cursor CLI; exit 1; }
```

### B-2 写入上下文文件

路径：`/tmp/auto-dev-<run-id>.context.md`（文件名可自定，须与启动命令一致）。

上下文须包含：**run_id**、**branch_name**、需求全文、每个仓库 **path（绝对路径）**、`aicr-local/SKILL.md` 与 **`references/MR_TEMPLATE.md` 的绝对路径**（指向本仓库 `plugins/common/skills/auto-dev/references/MR_TEMPLATE.md`）。

字段说明见 `references/CLI_HANDOFF.md`。

### B-3 启动 Headless Agent（必须由 IDE Agent 调 Shell）

- **必须使用 Cursor 内置终端能力（Shell）执行启动命令**，启动本机 `agent -p --force`，**禁止**仅以聊天粘贴「请复制运行」脚本作为阶段B 的唯一交付。
- 提示词须使 CLI **读取上下文文件**，并在各仓库完成：**checkout 已存在分支 → 改动 → lint → git add → 按 aicr-local 做 CR 循环 → commit/push → 按 MR_TEMPLATE 创建 MR（target=`develop`，Token 优先读环境变量）**。
- Shell 成功后：将 **CLI 日志路径**、子进程 **PID**（若已写入 pid 文件）写入对用户回复。

命令骨架见 **`references/CLI_HANDOFF.md`**。

### B-4 IDE Agent 收尾

本阶段**不要在 IDE 里再跑** `npm run lint` / 大批量改文件。仅需：

- 输出：`run-id`、CLI 日志路径、`tail -f …`（及已确认的 CLI 已启动说明）；
- 若同步等待 CLI 结束，则读取日志中的 MR URL 写入完成通知。

---

## 步骤5（别名）：阶段B 完成通知

CLI 全流程结束后输出（或由 IDE Agent 在读日志后代为输出）：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ auto-dev 完成 | run-id: ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 MR 待 Review：
  • <仓库名> → develop
    <MR链接>

⚠️ BLOCKED …（若有）

请对 MR 进行 Code Review。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
