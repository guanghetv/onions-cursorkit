# Tasks

- [x] 确认 Tier 1 范围与升级红线
- [x] 写入 proposal/spec/tasks
- [x] 更新 `SKILL.md`：步骤 4/5、快速清单、注意事项中的查询通道（CLI 优先、MCP 备选）
- [x] 同步 `references/DETAILED_STEPS.md` 查询示例与失败回退说明
- [x] 必要时更新 `references/EXAMPLES.md`、`references/TROUBLESHOOTING.md`
- [x] 定向验证：文档一致性 +（有 CLI 时）help/查询路径核对
- [x] 小范围回归：基线门禁与多链接拼接描述未被破坏
- [x] 本机工具校验（2026-07-23）：
  - Meegle CLI：`@lark-project/meegle@1.0.16` 已安装；`workitem get` / `url decode` 与技能一致；`workitem get --dry-run` 映射后端工具 `get_workitem_brief`
  - Meegle auth：当前未登录（`AUTH_REQUIRED`），符合技能「先 auth，失败回退 MCP」路径
  - 飞书项目 MCP：`FeishuProjectMcp` / `get_workitem_brief` 可用（实测工作项 `7056666842`）
  - 字段：`名称`→`name`，`规划迭代`→`planning_sprint`（field_name 可查）；技能示例可用中文名或 field_key
- [x] 更新任务状态与验证记录；收尾走 `/onsf-finish`
