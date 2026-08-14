# Figure Brief — Genetic Algorithm Workflow

- **slug:** `genetic-algorithm-workflow`
- **figure_goal:** demonstrate a loop-heavy algorithm workflow with a decision node and explicit termination path.
- **paper_claim:** the figure explains the canonical genetic-algorithm control flow only; it does not claim a specific encoding, population size, operator probability, or optimization result.
- **figure_type:** algorithm workflow.
- **mode:** image.
- **language:** Chinese with the standard English name “Genetic Algorithm (GA)” allowed in the title.
- **orientation:** landscape or compact wide flowchart.

## Intended structure

```text
参数与约束
   ↓
初始化种群
   ↓
适应度评价
   ↓
选择
   ↓
交叉
   ↓
变异
   ↓
新一代种群
   ↓
终止条件？
  ├─ 否 → 返回适应度评价
  └─ 是 → 输出最优解 / 最优候选
```

Elitism may appear only as a small optional preservation path if represented generically; do not imply that it is mandatory.

## Must-keep labels

- 参数与约束
- 初始化种群
- 适应度评价
- 选择
- 交叉
- 变异
- 新一代种群
- 终止条件？
- 否
- 是
- 输出最优候选

## Style constraints

- white background;
- strong loop readability;
- a clear diamond decision node for termination;
- consistent process modules;
- no fake equations or parameter values;
- restrained academic palette;
- small semantic icons are acceptable only if they do not replace readable labels.

## Verification targets

- loop returns from “否” to the next evaluation cycle;
- “是” exits to final output;
- selection precedes crossover and mutation;
- no population size, crossover probability, mutation probability, generation count, fitness value, or convergence result is invented;
- Chinese labels are legible and not malformed.
