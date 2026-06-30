# 质量规范

## 基础校验

正式插件改动后运行：

```bash
node scripts/validate-template.mjs
```

未注册的试点插件至少运行：

```bash
find plugins/<plugin> -type f | sort
python3 -m json.tool plugins/<plugin>/.cursor-plugin/plugin.json
rg -n "name:|description:" plugins/<plugin>/commands plugins/<plugin>/skills plugins/<plugin>/rules
```

修改 `.trellis/spec/` 后检查是否还存在模板占位语、空章节或不符合本仓库实际结构的泛化说明。

## 文档质量

好的插件文档应该：

- 面向使用者，而不是只记录开发过程。
- 明确触发方式、适用范围、不做范围。
- 给出具体路径和命令。
- 不暗示不存在的运行时依赖。

### 迁移/抽象旧插件能力

当从一个既有插件抽象出新插件或通用流程时：

- 可以在设计文档中说明能力来源和历史背景。
- 用户可见的 README、command、skill、rule 必须给出新插件自有入口和自有 skill 名称。
- 不要让新插件的运行路径要求用户调用旧命令、安装旧插件或读取旧插件目录。
- 验证时增加负向搜索，确认没有旧入口运行时依赖措辞，例如：
  ```bash
  rg -n "/old-command|调用 old-plugin|依赖 old-plugin" plugins/<new-plugin>
  ```

这样可以保留成熟流程经验，同时避免新插件成为旧插件的隐式包装层。

参考：
- `plugins/onion-sdd/README.md`
- `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`
- `docs/add-a-plugin.md`

## 规则质量

规则文件应尽量小而明确：

- `globs` 不要过宽，避免和其他插件冲突。
- `alwaysApply: true` 只用于真正全局规则，例如提交规范或文档语言规范。
- rule 中的 MUST/MUST NOT 要可执行，不要写抽象价值观。

参考：
- `plugins/common/rules/doc-writing-zh.mdc`
- `plugins/frontend/rules/commit-rule.mdc`
- `plugins/onion-sdd/rules/onion-sdd.mdc`

## 技能质量

Skill 必须让 AI 知道下一步怎么做：

- 入口条件。
- 输入。
- 步骤。
- 输出格式。
- 何时停止或升级。

避免只写“要认真分析”这类无法执行的建议。

## 提交质量

提交信息使用中文 Conventional Commits，参考 `plugins/frontend/rules/commit-rule.mdc`：

```text
feat(onion-sdd): 初始化独立 SDD 插件流程
docs(trellis): 填充项目开发规范
chore(task): archive ...
```

不要把不相关初始化文件混入插件功能提交。

## 常见错误

- README、command、skill 之间口径不一致。
- 文档中还残留模板占位。
- 未注册试点插件误跑全量 marketplace 校验后忽略失败原因。
- 同步产物被手工改动，下一次同步被覆盖。
