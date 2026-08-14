# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

一个面向 **Codex + GPT** 的科研配图 Skill，重点覆盖工程、计算机、AI、数据科学、电子信息和数学建模论文。

它把科研配图拆成三种模式：

- `image`：系统架构、算法流程、图形摘要、数学建模框架、机制图、重绘与图片编辑；
- `plot`：精确柱状图、趋势图、热力图、散点图、敏感性/稳健性、消融实验、benchmark、多面板定量图；
- `mixed`：定量部分本地精确绘制，概念部分使用 GPT 图像生成。

核心原则：**数值、坐标轴、误差、公式和 benchmark 几何关系不能为了“好看”被生图模型改写。**

[English](README.en.md) · [安装说明](INSTALL.md) · [Showcase](docs/showcase.md)

## 适配你这种用法：CC Switch → 命令行 Codex → Skill

如果你使用 CC Switch 配好 API，然后在 PowerShell/终端里直接运行：

```powershell
codex
```

现在**不需要再给这个 Skill 配第二套 Base URL 和 API Key**。

运行链路是：

```text
CC Switch
   ↓
~/.codex/config.toml + ~/.codex/auth.json
   ↓
codex
   ↓
engineering-figure-gpt
```

Portable Image CLI 会优先读取当前 Codex live provider，包括常见的：

- `config.toml` 中的 `model_provider`、`base_url`、`env_key`、`experimental_bearer_token`；
- `auth.json` 中的 `OPENAI_API_KEY`。

连接解析顺序：

```text
显式 CLI 参数
    ↓
当前 Codex / CC Switch Provider
    ↓
OPENAI_* 环境变量兼容层
    ↓
OpenAI 官方默认值
```

查看当前 Skill 能识别到的 Codex Provider：

```powershell
python scripts/codex_provider_config.py
```

这里只显示 Provider、Base URL、wire API、是否找到 Key 等安全信息，**不会打印真实 Key**。

需要特别区分：**Codex 文本接口可用，不代表这个中转站一定支持图片接口。**

因此第一次建议运行：

```powershell
python scripts/efg.py provider-check
```

在 CC Switch 已选中 Provider 的情况下，这里不需要再写 `--base-url` 或 `--allow-third-party`。

详细说明见 [Codex CLI + CC Switch Integration](references/codex-cc-switch.md)。

## Image Mode：一条命令完成 Prompt → Image

在 Codex 内如果已有可用的内置 GPT 图像能力，可以直接使用。为了可复现和命令行运行，仓库同时提供 GPT Image-compatible CLI。

图片模型与 Codex 的文本/代码模型分开解析。也就是说，即使 `config.toml` 中 Codex 当前使用的是某个 coding model，图片模式也不会拿它去调用 Images API。

普通图片模型默认：

```text
OPENAI_IMAGE_MODEL → gpt-image-2
```

直接运行：

```bash
python scripts/efg.py image \
  "一个包含 OCR、Embedding、向量检索、Rerank 和答案生成的 RAG 系统" \
  --figure-template system-architecture \
  --lang zh \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

去掉 `--dry-run` 才会真正发起图片请求。

如果使用的是 CC Switch，dry-run 中应该能看到类似：

```text
connection_source: codex-config
codex_provider: <当前 Provider>
```

## 手动指定其他中转站

如果你不是复用 CC Switch 当前 Provider，而是**临时手动覆盖另一个 URL**，仍然要求显式确认信任：

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template system-architecture \
  --base-url https://你的另一个中转站/v1 \
  --allow-third-party
```

这条安全规则是为了防止 API Key 或编辑图片被静默发送给陌生服务。

### 中转站兼容检查

复用当前 CC Switch/Codex Provider：

```bash
python scripts/efg.py provider-check
```

手动测试另一个 Relay：

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
$env:OPENAI_IMAGE_HIGHRES_MODEL = "<你的 Provider 实际提供的最终质量图片模型>"
```

调用：

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template graphical-abstract \
  --final
```

如果用户要求 `--final` / `--highres`，但没有配置最终质量模型，也没有显式传图片 `--model`，CLI 会直接停止，**不会偷偷降级模型、画质、尺寸或 Provider**。

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

Wizard 支持：

- 查看全部工程/数学建模模板；
- 一步完成 Prompt → Image；
- 复用 Codex / CC Switch 当前 Provider；
- 手动官方 OpenAI / 自定义可信中转站；
- Provider compatibility probe；
- `--final` 高质量路由；
- 一步完成 Plot Request → Spec → Figure。

## Unified CLI

```bash
# 仅生成 Prompt
python scripts/efg.py prompt --figure-template problem-analysis --lang zh "建模背景"

# Prompt + 生图一步完成；默认优先复用 Codex/CC Switch Provider
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run

# 检查当前 Codex/CC Switch Provider 的图片兼容性，不生成图片
python scripts/efg.py provider-check

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
- Codex / CC Switch provider 解析与 secret-redaction
- 官方地址和手动第三方中转站信任规则
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
6. 当前 Codex/CC Switch Provider 可以直接复用；手动覆盖其他中转站仍需显式信任。
7. 最终质量请求不得静默降级。
8. Runtime 必须精简、可检查。
9. 最终输出尽量保留可复现证据链和可编辑 handoff。

## License

见 [LICENSE](LICENSE)。
