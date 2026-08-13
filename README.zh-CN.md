# Engineering Figure GPT

面向科研论文配图的 Codex Skill，重点支持工程、计算机、AI、数据科学与数学建模。

## 三种模式

- `image`：系统架构图、算法流程图、Graphical Abstract、数学建模框架图、机制图、重绘与编辑。
- `plot`：对数值真实性要求严格的柱状图、折线图、散点图、热力图、消融实验图与 benchmark 图。
- `mixed`：定量 panel 本地精确绘制，概念 panel 使用 Codex 内置 GPT 图像生成能力。

## 核心原则

定量真实性优先。精确数值、坐标轴、误差棒和 benchmark 几何关系不交给图像模型重画。

概念图优先采用白底、简洁标签、清晰箭头、明确阅读顺序和论文风格排版。

数学建模与中文科研图是本项目的一等场景。

## 当前结构

- `SKILL.md`：Codex Skill 核心工作流
- `agents/openai.yaml`：Codex 元数据
- `assets/prompt-templates/`：中英文科研图提示模板
- `references/`：Figure Brief、论文配图规范与 OpenAI 图像工作流

当前版本优先使用 Codex 自带的 GPT 图像生成能力，而不是自行封装 Gemini / Nano Banana provider。
