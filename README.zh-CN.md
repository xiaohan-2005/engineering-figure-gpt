# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

一个面向 **Codex + GPT** 的科研配图 Skill，重点覆盖工程、计算机、AI、数据科学、电子信息和数学建模论文。

它不是把所有图都交给生图模型，而是把科研配图拆成三种模式：

- `image`：系统架构、算法流程、图形摘要、数学建模框架、机制图、重绘与图片编辑。
- `plot`：精确柱状图、趋势图、热力图、散点图、消融实验、benchmark、多面板定量图。
- `mixed`：定量部分本地精确绘制，概念部分使用 GPT 图像生成。

核心原则：**数值、坐标轴、误差、公式和 benchmark 几何关系不能为了“好看”被生图模型改写。**

[English](README.en.md) · [安装说明](INSTALL.md) · [Showcase](docs/showcase.md)

## 为什么需要这个 Skill

普通生图模型可以生成“像论文图”的图片，但科研图还要求：

- 术语不能乱改；
- 模块关系和箭头方向必须正确；
- 数值、误差棒、坐标轴必须精确；
- 公式和数学符号不能被 AI 篡改；
- 中文标签不能乱码、裁切或过长；
- 输出需要适合论文版面和后续复现。

因此，本 Skill 采用的是一条完整工作流：

```text
论文 / 方法 / 数据 / 参考图
          ↓
     Figure Brief
          ↓
  image / plot / mixed
     ↓      ↓      ↓
   GPT     本地    混合
  生图     绘图    工作流
      \      |      /
         验证
          ↓
      论文配图
```

## 核心能力

### Image Mode

适合：

- 系统架构图
- 算法流程图
- Graphical Abstract
- 数学建模总体框架图
- 数据分析 Pipeline
- 多目标优化 Workflow
- 评价体系图
- 电子系统示意图
- 重绘与图片编辑

在 Codex 内，优先使用已经安装的内置 GPT 图像生成能力。

为了可复现和便携运行，仓库同时提供 `scripts/generate_image.py`，默认使用 `gpt-image-2`，并且故意拒绝第三方 Base URL，只允许官方 OpenAI endpoint。

### Plot Mode

当“数值真实性”比视觉自由度更重要时使用。

当前 Plot Engine 支持：

- grouped bar
- error bar
- 数值标注
- trend curve
- uncertainty shadow
- heatmap
- scatter
- legend-only panel
- empty panel
- multi-panel layout

可输出 PNG / PDF / SVG / EPS / JPEG / TIFF 等 Matplotlib 支持格式。

### Mixed Mode

同一张图里如果既有实验曲线，又有概念机制图：

```text
精确数值 Panel → 本地绘制
概念 Panel     → GPT 生成
```

不要把已经精确绘制的图重新交给生图模型“美化重画”。

## 自然语言绘图

用户不应该手写复杂 JSON。

例如：

> 比较三个模型的 AUC、F1 和 Recall，带误差棒，把具体数值标在柱子上，图例放右侧。

Skill 应该先理解需求，再形成内部 Plot Request，然后：

```bash
python scripts/build_plot_spec.py request.json --out spec.json
python scripts/plot_publication_figure.py spec.json --out-path output/figure --formats png pdf svg
```

JSON 是内部执行格式，不是主要用户界面。详见 [Natural-language Plot Workflow](references/natural-language-plot-workflow.md)。

## 数学建模强化

这是本项目区别于普通工程图 Skill 的重点方向之一。

典型场景包括：

- 问题分析图
- 总体模型框架
- Q1 / Q2 / Q3 依赖关系
- 数据预处理流程
- 时间序列预测流程
- 多目标优化与 Pareto 流程
- 敏感性分析
- 稳健性分析
- 决策框架

同时专门考虑中文论文中的：

- 中文标签长度
- 中文字体 fallback
- 中英文混排
- 数学符号保护
- 公式不被 AI 改写
- 国赛论文式信息层级

详见 [数学建模说明](references/mathematical-modeling.md) 和 [中文标签规范](references/chinese-labels.md)。

## 安装

推荐先把源码仓库 clone 到普通目录，再由安装脚本同步精简后的 Runtime：

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

最终 Runtime 安装到：

```text
~/.codex/skills/engineering-figure-gpt
```

`docs/`、`examples/`、`tests/`、GitHub CI 等仓库文件不会全部塞进 Codex Runtime。

## 安装后的真实验收

默认的 `install_and_test.ps1` 现在不只是检查文件是否存在，它还会：

1. 检查 Python 和 Runtime 文件；
2. 运行离线 CLI smoke test；
3. 创建临时 Plot Spec；
4. 使用安装后的 Runtime **真实渲染一张 PNG**；
5. 检查 PNG 是否存在且非空；
6. 清理临时文件。

这一步完全本地执行，不产生 API 费用。

如果你还想显式测试一次真正 GPT Image 请求，可以使用：

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

这个选项会产生一次真实网络请求，因此默认关闭。

## Unified CLI

```bash
python scripts/efg.py prompt --figure-template mathematical-model-framework --lang zh "technical background"
python scripts/efg.py image "research figure prompt" --dry-run
python scripts/efg.py build-plot request.json --out spec.json
python scripts/efg.py plot spec.json --out-path output/figure --formats png pdf svg
python scripts/efg.py check
```

## Figure Brief

Figure Brief 是“论文想表达什么”和“最终怎么画”之间的中间契约，包含：

- figure goal
- paper claim
- figure type
- image / plot / mixed mode
- panel plan
- must-keep labels
- data / evidence
- style constraints
- output formats
- verification checklist

现在 `panels` 已使用更严格 Schema：每个 Panel 至少要包含 `name` 和 `content`，避免 Agent 产生无结构的垃圾 Panel 数据。

Schema： [schemas/figure-brief.schema.json](schemas/figure-brief.schema.json)

## GPT Image CLI fallback

生成：

```bash
python scripts/generate_image.py "Create a publication-quality architecture figure ..." --quality high --size 1536x1024
```

编辑：

```bash
python scripts/generate_image.py "Preserve structure and improve hierarchy" --input-image input.png --input-fidelity high
```

API Key 可以通过：

```text
OPENAI_API_KEY
OPENAI_API_KEY_FILE
~/.codex/secrets/openai_api_key.txt
```

提供。不要把真实 Key 提交到 GitHub。

## CI 与质量检查

GitHub Actions 当前检查：

- Python 编译
- Skill 元数据与目录结构
- UTF-8 与常见中文乱码
- 中英文 Prompt 模板
- 本地 Markdown 链接和图片路径
- 单元测试
- Runtime pruning
- Runtime token budget
- 离线 CLI smoke test

项目不追求“文件越多越专业”，而是让 GitHub 仓库可以丰富、Codex Runtime 保持精简。

## Showcase 状态

当前 [Showcase](docs/showcase.md) 中的概念 SVG 明确标注为 **layout preview**，不会伪装成 GPT 的真实输出。

下一阶段会逐步替换成完整证据链：

```text
Figure Brief
    ↓
Final Prompt
    ↓
Real GPT Output
```

定量图则保留 `Plot Request → Renderer → Real Output` 的可复现链路。

## 设计原则

1. 科研真实性优先于装饰。
2. 数值图保持本地、精确、确定性。
3. 自然语言是用户入口，JSON 是内部格式。
4. GPT 用在真正需要语义构图的地方。
5. 中文科研和数学建模是一等场景。
6. Runtime 必须精简、可检查。
7. 最终输出尽量保留可复现证据链。

## License

见 [LICENSE](LICENSE)。
