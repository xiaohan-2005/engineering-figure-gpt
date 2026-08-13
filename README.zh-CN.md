# Engineering Figure GPT 中文说明

Engineering Figure GPT 是一个面向 Codex 的科研配图 Skill，重点服务工程、计算机、AI、数据科学和数学建模。

它不把所有图片都交给生图模型，而是将任务拆成三种模式：

| 需求 | 模式 |
|---|---|
| 系统架构、算法流程、Graphical Abstract、数学建模框架、重绘/编辑 | `image` |
| 柱状图、趋势图、热力图、散点图、消融实验、benchmark | `plot` |
| 概念 panel + 精确定量 panel | `mixed` |

## 核心原则

**定量真实性优先。**

精确数值、坐标轴、误差棒、置信区间、benchmark 几何关系和必须逐字符准确的长公式，不交给图像模型重新绘制。

概念图可以使用 GPT 图像生成；定量图由本地 Python/Matplotlib 精确绘制。

## Image Mode

在 Codex 中，优先使用已经安装的内置图像生成能力。

仓库同时提供一个可复现的 GPT-only CLI fallback：

```bash
python scripts/generate_image.py "生成一张论文级系统架构图……" --dry-run
```

确认配置 OpenAI API Key 后，再去掉 `--dry-run`。

CLI 默认使用 `gpt-image-2`，并且：

- 默认只允许 OpenAI 官方接口
- 不自动切换到 Gemini / Banana
- 不静默降级到其他图像模型
- 支持生成与图片编辑

## Plot Mode

用户不需要手写 JSON。

正确交互是：

```text
自然语言需求
   ↓
Codex 提取数据、panel、标签、单位、误差等
   ↓
内部 concise request
   ↓
build_plot_spec.py
   ↓
normalized spec
   ↓
plot_publication_figure.py
   ↓
PNG / PDF / SVG
```

当前精确绘图支持：

- grouped bar
- error bars
- value annotations
- trend curves
- uncertainty shadows
- heatmap
- scatter
- 多 panel
- 独立 legend panel
- width / height ratio
- PNG / PDF / SVG / EPS / JPEG / TIFF

示例：

```bash
python scripts/build_plot_spec.py examples/multi-panel-plot-request.json --out output/spec.json
python scripts/plot_publication_figure.py output/spec.json --out-path output/figure --formats png pdf svg
```

## 数学建模方向

数学建模是本 Skill 的一等场景，重点包括：

- 问题分析图
- 总体模型框架
- Q1/Q2/Q3 依赖关系
- 数据预处理
- 时间序列/预测流程
- 优化求解流程
- 空间或网络模型示意
- 模型评价
- 敏感性分析
- 稳健性分析
- 最终决策框架

对公式、变量、模型名称、单位和约束必须严格保真。

## 中文科研图

中文标签需要额外检查：

- 中文乱码
- 字体 fallback
- 标签过长
- 箭头与文字重叠
- 数学符号
- 负号
- 单位
- 中英混排
- 图例裁切

详细规范见 `references/chinese-labels.md`。

## 安装

推荐把 GitHub 仓库作为源码目录，再同步精简版 Runtime Skill：

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

Runtime 会被安装到：

```text
~/.codex/skills/engineering-figure-gpt
```

安装器会刻意排除：

```text
docs/
examples/
tests/
.github/
README*
```

避免把 GitHub 展示文件全部塞进 Codex 上下文。

检查环境：

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

## CLI

```bash
python scripts/efg.py prompt --figure-template mathematical-model-framework --lang zh "论文背景"
python scripts/efg.py image "科研配图提示词" --dry-run
python scripts/efg.py build-plot request.json --out spec.json
python scripts/efg.py plot spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py check
```

## Showcase 说明

当前仓库中的概念 SVG 是 **layout preview**，不是伪装成 GPT 实际输出的图片。

后续真实 GPT 生成案例应按照下面的证据链提交：

```text
Figure Brief → Prompt → Output
```

精确定量图则使用：

```text
Plot Request → Spec → Output
```

这样每一个案例都可以复现和审查。
