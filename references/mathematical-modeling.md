# Mathematical Modeling Figures

Mathematical modeling is a first-class domain pack, not a side example.

Use the dedicated templates in:

```text
assets/prompt-templates/mathematical-modeling-templates.json
```

The domain pack covers problem analysis, Q1/Q2/Q3 dependency, preprocessing, forecasting, classification, clustering, optimization, Pareto workflows, spatial/network models, evaluation, sensitivity, robustness, decision frameworks, and full modeling pipelines.

## Core modeling chain

A complete paper often follows:

```text
problem understanding
      ↓
assumptions + data
      ↓
preprocessing / exploratory analysis
      ↓
submodel construction
      ↓
parameter estimation / prediction / optimization / evaluation
      ↓
validation
      ↓
sensitivity + robustness
      ↓
interpretation + decision
```

Do not force every project into this exact chain. Keep only steps supported by the paper/problem statement.

## Q1 / Q2 / Q3 dependency

For multi-question competition papers, show information handoffs explicitly:

```text
shared data preprocessing
        ↓
       Q1
        ↓ output / parameter / state
       Q2
        ↓ candidate / forecast / score
       Q3
```

If Q2 does not actually depend on Q1, draw parallel branches instead of inventing a dependency.

## Formula and symbol protection

Image mode must preserve:

- variable names;
- parameter symbols;
- units;
- constraint names;
- model names;
- standard abbreviations.

Long or exact formulas should not be trusted to image generation. Represent them as a clearly marked typesetting placeholder, then add the exact formula during editable handoff.

## What belongs in image mode

Good conceptual targets:

- problem-analysis map;
- overall framework;
- model dependency graph;
- optimization workflow;
- evaluation hierarchy;
- decision workflow;
- sensitivity/robustness procedure;
- spatial or network reasoning structure.

## What belongs in plot mode

Keep exact numeric results local and deterministic:

- prediction curves;
- residual plots;
- error metrics;
- sensitivity indices;
- Pareto fronts;
- robustness curves;
- heatmaps/correlation matrices;
- confusion matrices;
- ablation results;
- benchmark comparisons.

## Mixed-mode competition figure

A strong modeling paper may combine a conceptual framework with exact quantitative panels. Preferred workflow:

1. generate the conceptual framework independently;
2. render exact plots locally to SVG/PDF/PNG;
3. compose the final multi-panel figure outside the image model;
4. add panel labels and exact formulas during editable handoff;
5. verify that the image model never redrew the exact plot geometry.

## Chinese modeling-paper rules

For Chinese labels:

- prefer short noun phrases rather than full sentences;
- preserve standard English abbreviations such as ARIMA, LSTM, PCA, TOPSIS, NSGA-II, AHP, XGBoost when they are already used in the paper;
- avoid mechanically translating established model names;
- keep Q1/Q2/Q3 or “问题一/问题二/问题三” naming consistent;
- keep symbols such as $x_i$, $w_j$, $\lambda$, $\mu$ source-faithful;
- inspect exported figures for CJK font fallback and clipping.

## Template selection

Typical mapping:

| Need | Template |
|---|---|
| 赛题拆解 / 问题分析 | `problem-analysis` |
| 多问题依赖 | `q1-q2-q3-dependency` |
| 数据清洗 | `data-preprocessing` |
| 时间序列 / 预测 | `forecasting-workflow` |
| 分类 | `classification-workflow` |
| 聚类 | `clustering-workflow` |
| 单/多目标优化 | `optimization-model` / `multi-objective-pareto` |
| 空间问题 | `spatial-model` |
| 网络图问题 | `network-model` |
| 综合评价 | `evaluation-system` |
| 敏感性 | `sensitivity-analysis` |
| 稳健性 | `robustness-analysis` |
| 决策 | `decision-framework` |
| 全文总框架 | `full-modeling-pipeline` or `mathematical-model-framework` |

## Non-fabrication rule

Never invent:

- missing formulas;
- weights or coefficients;
- optimal values;
- forecast results;
- thresholds;
- sensitivity rankings;
- robustness conclusions;
- Pareto solutions;
- significance claims.

When evidence is missing, show the **workflow position** of the missing item, not a fabricated value.
