# Frontend Entrypoint Report Format

报告开头先写中文的功能流程简述：

```markdown
## 功能流程简述

### `activityh5`
1. 进入家长绑定页 `/bind`
2. 如果页面带 `schoolId`，直接进入“按学校绑定”流程
3. 选择班级时会触发该接口
4. 如果没有 `schoolId`，先选地区和学校，再选班级时触发该接口

### `littlefinger`
1. 进入绑定页 `/bind`
2. 进入“按学校绑定”或“先选地区学校再绑定”流程
3. 当页面加载班级列表时会触发该接口
```

这段摘要要求：

- 只能用中文
- 按步骤写用户可见的功能流程
- 说明用户如何进入页面、哪一步会触发接口
- 避免文件路径、符号名和不必要的技术术语
- 面向测试同学，不面向开发同学
- 每个项目控制在 3-6 步
- 如果有多条真实路径，先写主路径，再写补充路径

然后，每个候选入口使用下面的中文结构：

```markdown
## 候选入口：<功能或页面名称>

- 项目：`<repo>`
- 文件：`<path>`
- 入口类型：`page|screen|modal|list-action|submit-flow|unknown`
- 置信度：`high|medium|low`
- 路由证据：`<来自本地代码的匹配路由或推导符号>`
- 路由来源类型：`code-gateway|apisix-admin-api|mixed-route-union|similar-route-fallback`
- 路由来源标识：`<gateway repo 或 APISIX sourceName>`
- 命中原因：<一句中文说明>
- 建议测试路径：<一段简短中文操作流>
```

如果项目是在本次分析时 clone 下来的，再补一行：

- 本地来源：`本次任务已 clone 到 <workspaceRoot>`

## 置信度规则

- `high`：API 层直接使用该路由，且能定位到真实页面或界面
- `medium`：通过间接 API 封装命中，但业务模块较明确
- `low`：只有文本、埋点或弱线索，没有直接路由证据

## 路由来源规则

- `code-gateway`：入口候选主要由代码网关确认的 outward route 支撑
- `apisix-admin-api`：入口候选主要由 APISIX 确认的 outward route 支撑
- `mixed-route-union`：代码网关与 APISIX 都给出了可用 outward route，当前候选建立在二者并集之上
- `similar-route-fallback`：没有 confirmed outward route，当前候选来自 fallback hypotheses

如果本次分析同时存在代码网关 confirmed route 和 APISIX confirmed route：

- 不要只保留其中一个来源
- 每个候选都要写清主要依据来自哪一类来源
- 如果同一候选同时受两类来源支持，优先标记为 `mixed-route-union`

## 结尾总结

最后补一个中文总结：

- 已确认入口
- 推测入口
- 代码网关确认入口
- APISIX 确认入口
- 缺失项目或访问阻塞
