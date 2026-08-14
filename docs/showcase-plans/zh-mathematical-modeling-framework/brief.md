# Figure Brief — Chinese Mathematical-Modeling Framework

- **slug:** `zh-mathematical-modeling-framework`
- **figure_goal:** create a strong Chinese overview figure that demonstrates the skill's mathematical-modeling specialization.
- **paper_claim:** the workflow integrates data preparation, forecasting, optimization, validation, sensitivity/robustness analysis, and final decision support; it does not claim any numerical result.
- **figure_type:** end-to-end mathematical-modeling framework.
- **mode:** image.
- **language:** Chinese, while preserving standard English abbreviations when useful.
- **orientation:** landscape, strong left-to-right reading order with one clearly subordinate validation loop.

## Intended structure

Primary chain:

```text
问题分析
  ↓
数据预处理
  ↓
特征构建与探索分析
  ↓
预测模型
  ↓
多目标优化
  ↓
模型检验
  ↓
敏感性 / 稳健性分析
  ↓
决策输出
```

Supporting relationships:

- validation may feed back to model selection/parameter adjustment;
- sensitivity and robustness analysis evaluate the already-built model rather than replace it;
- no exact curve, coefficient, weight, Pareto point, or optimal value appears in the conceptual image.

## Must-keep labels

- 问题分析
- 数据预处理
- 特征构建
- 探索分析
- 预测模型
- 多目标优化
- 模型检验
- 敏感性分析
- 稳健性分析
- 决策输出

## Style constraints

- clean white background;
- competition-paper / journal-quality hierarchy, not a business infographic;
- restrained blue/teal/neutral palette;
- concise Chinese labels with enough whitespace;
- consistent rounded modules and thin directional arrows;
- no decorative 3D objects, glowing UI, gradients that reduce legibility, or stock-photo elements;
- leave formulas and exact numeric results out of the image.

## Verification targets

- Chinese labels are legible and not malformed;
- workflow direction is scientifically coherent;
- sensitivity/robustness appears after the core model stage;
- validation loop does not imply unsupported data flow;
- no fabricated data, performance numbers, model coefficients, or optimization result is added.
