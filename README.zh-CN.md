# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

一个面向 **Codex + GPT** 的科研配图 Skill，重点覆盖工程、计算机、AI、数据科学、电子信息和数学建模论文。

它把科研配图拆成三种模式：

- `image`：系统架构、算法流程、图形摘要、数学建模框架、机制图、重绘与图片编辑；
- `plot`：精确柱状图、趋势图、热力图、散点图、敏感性/稳健性、消融实验、benchmark、多面板定量图；
- `mixed`：定量部分本地精确绘制，概念部分使用 GPT 图像生成。

核心原则：**数值、坐标轴、误差、公式和 benchmark 几何关系不能为了“好看”被生图模型改写。**

[English](README.en.md) · [安装说明](INSTALL.md) · [Showcase](docs/showcase.md)

## Image Mode：现在支持一条命令完成 Prompt → Image

在 Codex 内优先使用已经安装的内置 GPT 图像能力。为了可复现和便携运行，仓库同时提供 GPT Image-compatible CLI。

默认使用：

```text
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_IMAGE_MODEL=gpt-image-2
```

现在不再要求用户先手动生成 Prompt、再复制给 Image CLI。可以直接：

```bash
python scripts/efg.py image \
  "一个包含 OCR、Embedding、向量检索、Rerank 和答案生成的 RAG 系统" \
  --figure-template system-architecture \
  --lang zh \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

去掉 `--dry-run` 才会真正发起图片请求。

## 自定义中转站

支持 OpenAI-compatible 中转站 Base URL，但必须显式确认信任：

```powershell
$env:OPENAI_BASE_URL = "https://你的中转站/v1"
$env:OPENAI_ALLOW_THIRD_PARTY = "1"
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_API_KEY_FILE = "$HOME/.codex/secrets/openai_api_key.txt"
```

也可以直接：

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template system-architecture \
  --base-url https://你的中转站/v1 \
  --allow-third-party
```

这样设计是为了防止环境变量被误改后，把 API Key 或编辑图片静默发送给陌生服务。

### 中转站兼容检查

现在新增不生成图片的兼容探测：

```bash
python scripts/efg.py provider-check \
  --base-url https://你的中转站/v1 \
  --allow-third-party
```

它会检查基础 URL、模型列表端点和 `/images/generations`、`/images/edits` 的可达性信号。它不会产生图片费用，但也不能保证所有中转站都完全实现每个 OpenAI Images 参数。

## Final / High-resolution 路由

普通生图使用：

```text
OPENAI_IMAGE_MODEL
```

最终稿/高分辨率使用：

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

示例：

```powershell
$env:OPENAI_IMAGE_MODEL = "gpt-image-2"
$env:OPENAI_IMAGE_HIGHRES_MODEL = "<你的官方或中转站实际提供的最终质量模型>"
```

调用：

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template graphical-abstract \
  --final
```

如果用户要求 `--final` / `--highres`，但没有配置最终质量模型，也没有显式传 `--model`，CLI 会直接停止，**不会偷偷降级模型、画质、尺寸或 Provider**。

详见 [High-resolution Policy](references/highres-policy.md)。

## Plot Mode：一条命令完成 Request → Spec → Figure

用户面对的是自然语言，JSON 只是内部执行契约。

Plot Engine 支持：

- grouped bar / error bar / 数值标注
- trend curve / uncertainty shadow
- heatmap
- scatter
- legend-only panel
- empty panel
- multi-panel layout

现在推荐直接：

```bash
python scripts/efg.py plot request.json \
  --spec-out output/spec.json \
  --out-path output/figure \
  --formats png pdf svg
```

内部自动完成：

```text
Plot Request (`kind`)
      ↓
build_plot_spec.py
      ↓
Normalized Plot Spec (`type`)
      ↓
plot_publication_figure.py
      ↓
PNG / PDF / SVG
```

如果已经有 normalized spec：

```bash
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg
```

复杂图参见 [Publication Plot API](references/publication-plot-api.md) 和 [Chart Patterns](references/publication-chart-patterns.md)。

## 数学建模已经升级为独立 Domain Pack

现在不是只在 `SKILL.md` 里写“支持数学建模”，而是新增独立模板包：

```text
assets/prompt-templates/mathematical-modeling-templates.json
```

覆盖：

- `problem-analysis`
- `q1-q2-q3-dependency`
- `data-preprocessing`
- `forecasting-workflow`
- `classification-workflow`
- `clustering-workflow`
- `optimization-model`
- `multi-objective-pareto`
- `spatial-model`
- `network-model`
- `evaluation-system`
- `sensitivity-analysis`
- `robustness-analysis`
- `decision-framework`
- `full-modeling-pipeline`

加上原来的工程模板后，可以直接查看全部模板：

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

数学建模规则也已经扩充到独立的 [Mathematical Modeling Guidance](references/mathematical-modeling.md)，重点约束：

- Q1/Q2/Q3 信息传递不能乱画；
- 模型名称、变量、符号、单位、约束必须忠实；
- 长公式不要交给生图模型硬写；
- 预测曲线、Pareto 前沿、敏感性指数、稳健性曲线、混淆矩阵、benchmark 等全部保持本地精确绘制；
- 不得虚构权重、系数、最优值、敏感性排名和评价结果。

## Editable Figure Handoff

科研图最终常常还需要一次人工可编辑排版。

现在增加 [Editable Figure Handoff](references/editable-figure-handoff.md)，推荐保留：

```text
brief.md
prompt.txt
output.png
verification.md
editable-handoff.md
```

定量图则额外保留：

```text
request.json
plot-spec.json
output.svg
output.pdf
```

这样后续可以在 PowerPoint / Illustrator / Inkscape / Figma 中统一中文字体、公式、箭头和版面，而不会破坏精确数据图。

## 安装

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

Runtime 安装到：

```text
~/.codex/skills/engineering-figure-gpt
```

仓库中的 `docs/`、`examples/`、`tests/`、GitHub CI 不会全部塞进 Codex Runtime。

安装检查：

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

交互式 Wizard：

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

Wizard 现在支持：

- 查看全部工程/数学建模模板；
- 一步完成 Prompt → Image；
- 官方 OpenAI / 自定义可信中转站；
- Provider compatibility probe；
- `--final` 高质量路由；
- 一步完成 Plot Request → Spec → Figure。

## Unified CLI

```bash
# 仅生成 Prompt
python scripts/efg.py prompt --figure-template problem-analysis --lang zh "建模背景"

# Prompt + 生图一步完成
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run

# 检查中转站兼容性，不生成图片
python scripts/efg.py provider-check --base-url https://你的中转站/v1 --allow-third-party

# Plot Request -> Spec -> Figure 一步完成
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg

# 已有 Spec 时直接渲染
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg

# 离线 Runtime 检查
python scripts/efg.py check
```

## 安装后的真实验收

默认 `install_and_test.ps1` 会真实执行本地 Plot E2E：

```text
request → normalized spec → renderer → non-empty PNG
```

这一步不会产生图片 API 费用。真正的 GPT Image 请求仍然是显式 opt-in。

## CI 与质量检查

GitHub Actions 当前检查：

- Python 编译
- Skill 元数据和 Runtime 必需文件
- UTF-8 / 中文乱码
- 工程 + 数学建模 Prompt Pack
- Markdown 链接和图片路径
- Figure Brief / Plot Request / Plot Spec 数据契约
- GPT Image generation/edit 请求构造
- 官方地址和第三方中转站显式信任规则
- malformed URL / embedded credential / model safety
- final/high-resolution fail-closed 路由
- HTTP error / timeout / malformed response / empty output
- 本地 Plot E2E
- Runtime pruning
- Runtime token budget
- 离线 CLI smoke test

## Showcase 状态

当前 [Showcase](docs/showcase.md) 中的概念 SVG 仍然明确标注为 **layout preview**，不会假装成真实 GPT 输出。

真正的 Showcase 必须保存完整证据链：

```text
Figure Brief
    ↓
Final Prompt
    ↓
Real GPT Output
    ↓
Verification
```

定量图则保存：

```text
Plot Request
    ↓
Normalized Plot Spec
    ↓
Renderer
    ↓
Real Output
    ↓
Verification
```

## 设计原则

1. 科研真实性优先于装饰。
2. 数值图保持本地、精确、确定性。
3. 自然语言是用户入口，JSON 是内部契约。
4. GPT 只用在真正需要语义构图的地方。
5. 中文科研和数学建模是一等场景。
6. 自定义中转站必须显式信任。
7. 最终质量请求不得静默降级。
8. Runtime 必须精简、可检查。
9. 最终输出尽量保留可复现证据链和可编辑 handoff。

## License

见 [LICENSE](LICENSE)。
