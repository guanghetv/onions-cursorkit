# 质量规范

## 校验入口

本仓库没有统一包管理脚本。按改动选择校验：

```bash
node scripts/validate-template.mjs
python3 -m json.tool plugins/<plugin>/.cursor-plugin/plugin.json
python3 ./.trellis/scripts/get_context.py --mode record
python3 ./.trellis/scripts/task.py list
```

如果修改了同步脚本，至少做 dry-run 或局部阅读确认：

```bash
node scripts/sync-guardrails.mjs --dry-run
```

## 插件资产质量

正式插件必须满足 `scripts/validate-template.mjs`：

- marketplace entry 的 `name` 与插件 `plugin.json.name` 一致。
- `plugin.json` 的 `rules`、`skills`、`commands` 等路径必须存在且不能越界。
- rule frontmatter 必须有 `description`。
- skill/agent/command frontmatter 必须有 `name` 和 `description`。

试点插件如果暂不注册 marketplace，也要局部验证 JSON 和 frontmatter。

## Trellis Git 安全

涉及 `.trellis/` 自动提交时，遵守 `.trellis/scripts/common/safe_commit.py`：

- 只 stage 明确产品路径：任务目录、archive 目录、developer journal、index。
- 不要 `git add .trellis/`。
- 不要 `git add -f .trellis/`。
- 如果脚本已移动文件但自动提交失败，先 `git status`，再只补提交实际移动的任务路径。

## 同步产物

部分插件内容同步自上游 guardrails，例如 `plugins/frontend/`、`plugins/fe-figma-flow/`、`plugins/fe-onion-stack/` 的描述中明确写了“内容同步自 ai-guardrails，请勿手改”。

修改这类内容前先判断：

- 是否应该改 `scripts/sync-guardrails.mjs` 的映射或修补表。
- 是否应该回上游仓库改源文件。
- 本仓库临时修补是否会被下次同步覆盖。

## 提交范围

提交时按逻辑分组：

- 插件功能/文档提交：只包含对应 `plugins/<name>/` 和必要任务文件。
- Trellis archive/journal 提交：由脚本或手动补交 `.trellis/tasks` / `.trellis/workspace`。
- 不要把 `.agents/`、`.cursor/`、`.codex/`、`.gitignore` 等初始化变更混入无关插件提交。

## 常见错误

- 注册 marketplace 后不跑 `node scripts/validate-template.mjs`。
- command/skill 缺 frontmatter。
- JSON 示例带注释导致 `json.tool` 失败。
- 试点文档引用外部旧流程，让插件看起来存在运行时依赖。
