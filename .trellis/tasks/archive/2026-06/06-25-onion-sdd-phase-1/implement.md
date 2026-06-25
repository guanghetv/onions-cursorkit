# 实施计划

## 总体顺序

- [x] 创建 Phase 1 父任务。
- [x] 确认技术方案意图：`onion-sdd` 以 `fe-specflow` 基座能力为基础，再接 Trellis runtime。
- [x] 创建子任务：补齐 fe-specflow 基座能力。
- [x] 创建子任务：Trellis adapter 状态同步。
- [ ] 完成基座能力子任务的 PRD / design / implement，并请用户 review。
- [ ] 用户确认后启动基座能力子任务进入 Phase 2。
- [ ] 基座能力完成并通过检查后，回到 adapter 子任务规划。
- [ ] Adapter 子任务完成后，做父任务最终集成验收。

## 子任务启动规则

- 不启动父任务执行实现；父任务只用于总控和最终验收。
- 第一个可启动的实现任务是 `.trellis/tasks/06-25-onion-sdd-base-capabilities`。
- `.trellis/tasks/06-25-onion-sdd-trellis-adapter` 必须等待基座能力的阶段模型和 onion 自有产物清单稳定后再启动。

## 父任务验证

完成两个子任务后执行：

```bash
python3 ./.trellis/scripts/task.py list
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
rg -n "fe-specflow|fe-sdd|dev-workflow|design-to-opsx|pull-spec|e2e-verify" plugins/onion-sdd
rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd
```

期望：

- 子任务已完成或归档。
- `onion-sdd` 文件结构完整。
- 不存在要求用户调用 `fe-specflow` 的运行时依赖措辞；如提及这些词，只能出现在迁移说明或历史对比中。
- 不重新引入全仓扫描硬约束。
