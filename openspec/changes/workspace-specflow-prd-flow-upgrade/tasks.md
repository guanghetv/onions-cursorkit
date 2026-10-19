# Tasks: workspace-specflow-prd-flow-upgrade

> 执行约束
> - 每个任务必须有验证点。
> - 插件技能以人工按场景走读为主，不要求为 Markdown 技能单写单元测试。
> - 不在本任务中归档遗留 OpenSpec，不推送远端，不执行 Multica `sync --execute`。
> - 写作规范正文已在 `6702435`，不要把它和本变更打进同一次提交。

## 1. 取消稿次与基线

- [x] 1.1 需求创建和状态读取不再进入 v5/v9 阶段；历史 v9 已确认映射为 `confirmed` 加最近快照。
      验证点: 走读 `/req-new` 与状态过滤；用一份带旧 `prd.stage` 的 metadata 确认映射结果。
- [x] 1.2 第一次 `/prd-publish` 成功写入 `prd.status=confirmed`、基线快照、版本表行，以及最后一次飞书写入之后回读的 `revision_id`；再次发布只前进基线。
      验证点: 对照 `specs/prd-baseline/spec.md` 的首次发布与再次发布场景。发布结束后当前序号等于 `prd.baseline.revision_id`。
- [x] 1.3 除 `/qa-spec` 外，飞书序号不等于基线，或本地 `prd.md` 正文偏离快照时，下游读取上一版快照。
      验证点: 走读开发消费入口，确认不读当前未发布正文。

## 2. 三端对齐

- [x] 2.1 主路径文档写明先原型，再写 `prd.md` 和飞书文档。
      验证点: `/pm-proto` 之后的写文档技能不再要求先完成 5 稿。
- [x] 2.2 任一端先改时，先展示差异，用户确认后才写另外两端。
      验证点: 对照 `specs/three-way-sync/spec.md` 的先改飞书、先改原型两个场景。
- [x] 2.3 飞书文档已有内容时，同步路径不提供整篇覆盖。
      验证点: `prd-feishu-sync` 的命令清单规则和失败分支中不存在「确认后 overwrite」。

## 3. 写作规范落地

- [x] 3.1 模板、一致性检查和 AI Review 不再要求独立验收章；可测规则在需求详情。
      验证点: 一份只有需求详情、没有验收 checklist 的文档不被 AI Review 判失败。
- [x] 3.2 `/qa-spec` 可从 `prd.md` 或飞书 CLI 链接提取规则。已发布且未漂移时读当前正文；有快照且漂移时读快照并提示。比较对象是 `prd.baseline.revision_id`。
      验证点: 对照 `specs/writing-and-qa/spec.md` 的输入场景。已发布未漂移且只给本地目录时读 `prd.md`。
- [x] 3.3 `/qa-spec` 在未确认、一致性失败或无基线时仍生成用例，并写明风险。只有来源已发布、未漂移且 `consistency.status` 为 `pass` 或 `warn` 时，`test_spec.status=confirmed`。缺失和 `unknown` 保持 `pending`。其他下游仍等待首次发布。
      验证点: 走读 `/qa-spec` 前置条件与 Step 8。一致性技能不再写「阻断 qa-spec」。

## 4. 产品变更技能

- [x] 4.1 发布成功后由 `/prd-publish` 用当前登录账号 `im +messages-send --as user` 发短消息。群来自项目卡 `group_type.group_id`。无卡、多卡或无 `oc_` 群则跳过且发布仍成功。不建群，不用 bot，不调用 Multica 或 `notify_spec_published`。
      验证点: 对照 `specs/prd-change-notify/spec.md` 的有群、无群、发送身份、不调用 Multica。
- [x] 4.2 群内查询由 `prd-change` 按 `chat_id` 反查项目卡。有工作项链接时用该链接的 `project_key` 核对 `group_id`；没有链接时只在 `ruxiao` / `tec_prd` 查一次。0 张、多张或查询失败时不翻全空间。其后用版本表 `R1` 和历史序号判断。旧稿次编号无法判断。多次序号确认不了时不断言。该技能不发布基线，也不注册产品斜杠命令。
      验证点: 走读查询分支的找卡、仅回写、同一次拆号、无法确认、超前、旧编号和无法匹配。
- [x] 4.3 `/prd-publish` 成功后引导产品提交代码，引导失败不回滚基线。
      验证点: 发布结果文本包含提交引导，且基线字段已经写好。

## 5. 原型只留核心流程

- [x] 5.1 `/pm-proto` 新页面和迭代页面不生成占位文案与操作引导，主流程控件仍在。
      验证点: 对照 `specs/proto-core/spec.md`，抽一页原型检查文案和主流程。

## 6. Agent 禁令

- [x] 6.1 `rules/agent-hard-rules.mdc` 保持 `alwaysApply`，并覆盖写作禁令、评论二次确认、禁止整篇覆盖、先调用 `search_wiki`。`/pm-proto` 与 `/pm-spec` 扫描工作区或写正文前也要调用。
      验证点: 对照 `specs/agent-hard-rules/spec.md` 通读规则文件和 `/prd-feishu-sync` 安全约束，确认没有相反例外。
