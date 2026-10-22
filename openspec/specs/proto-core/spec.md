# proto-core Specification

## Purpose
TBD - created by archiving change workspace-specflow-prd-flow-upgrade. Update Purpose after archive.
## Requirements
### Requirement: 去掉占位和引导

`/pm-proto` MUST 生成只含核心页面流程和交互的原型，不包含占位文案和给产品看的操作引导。

#### Scenario: 新生成原型

- **WHEN** 产品用 `/pm-proto` 生成页面
- **THEN** 页面不出现占位说明、填写提示和操作引导
- **AND** 主流程页面和交互仍可走通

#### Scenario: 迭代已有原型

- **WHEN** 产品要求迭代已有原型
- **THEN** 新改的页面同样不增加占位文案和引导
- **AND** 不因去掉引导而删掉完成主流程所需的控件

