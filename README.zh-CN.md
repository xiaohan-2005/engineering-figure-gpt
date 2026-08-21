# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

一个面向 **Codex + GPT** 的科研配图 Skill，重点覆盖工程、计算机、AI、数据科学、电子信息和数学建模论文。

现在不再只是“让 GPT 画一张图”，而是把图片生产拆成：

```text
科学内容约束
+
论文图像质量约束
+
用户风格要求
+
修改保留约束（编辑已有图片时）
```

并提供四类工作流：

- `image`：生成新的系统架构、算法流程、图形摘要、数学建模框架、机制图；
- `edit`：对已有科研图执行 `correct / revise / restyle / redraw`；
- `plot`：精确柱状图、趋势图、热力图、散点图、敏感性/稳健性、消融实验、benchmark、多面板定量图；
- `mixed`：定量部分本地精确绘制，概念部分使用 GPT 图像生成。

核心原则：**数值、坐标轴、误差、公式和 benchmark 几何关系不能为了“好看”被生图模型改写；一张图 API 返回成功，也不代表它已经达到论文可用质量。**

[English](README.en.md) · [主 README](README.md) · [安装说明](INSTALL.md) · [Showcase](docs/showcase.md)

## Image Pipeline v2：把“清晰度和版式”变成固定约束

过去每个模板主要负责“画什么”，容易出现：

- 标签太小；
- 模块挤在一起；
- 箭头穿文字；
- 边缘裁切；
- 图看起来很复杂，但细节其实是伪造小字；
- full screen 看着还行，缩进论文就看不清。

现在单独增加：

```text
assets/prompt-templates/image-quality-contracts.json
```

提供三档：

- `draft`：结构探索；
- `paper`：默认论文级约束；
- `final`：最终导出级约束。

`paper / final` 会固定注入这些要求：

- 白色或近白色画布；
- 一种明确主阅读方向；
- 四周安全边距，模块、文字、箭头端点不能贴边或被裁切；
- 使用大而干净的文字区域；
- 强文字/背景对比；
- 核心标签在约 50% 原始尺寸或论文单栏宽度下仍可辨认；
- 宁可减少标签并放大，也不要堆大量微小文字；
- 箭头和边框清晰、线宽一致、端点明确；
- 重复模块严格对齐、间距稳定；
- 低到中等饱和度科研配色，颜色语义前后一致；
- 避免模糊、重影、噪声纹理、伪技术小字、强 3D、电影光影和海报渐变；
- 不得为了“显得专业”虚构模块、公式、数值、接口或说明。

详见：

- [Image Quality Contract](references/image-quality-contract.md)
- [Publication Figure Design](references/publication-figure-design.md)
- [Visual QA](references/visual-qa.md)

## Image Mode：生成新图

推荐统一从 `efg image` 进入，因为它会自动把质量合同叠加到最终 Prompt。

```bash
python scripts/efg.py image \
  "一个包含 OCR、Embedding、向量检索、Rerank 和答案生成的 RAG 系统" \
  --figure-template system-architecture \
  --quality-profile paper \
  --lang zh \
  --save-prompt output/final-prompt.txt \
  --dry-run
```

去掉 `--dry-run` 才会真正调用图片 API。

即使你不用模板、直接给完整生图要求，只要经过 `efg image`，也会叠加所选的质量合同。

## Edit Mode：真正把“修改图片”做成一等功能

以前底层虽然有 `/images/edits` 和 `--input-image`，但没有明确告诉 Skill：

> 哪些必须保持不变？到底是修一个字，还是整张重画？

现在正式增加：

```bash
python scripts/efg.py edit figure.png \
  "只把 Encoder 改成 Cross-Attention Encoder，其他内容不要变化" \
  --mode correct \
  --preserve "所有箭头端点" \
  --save-prompt output/edit-prompt.txt \
  --dry-run
```

### 四种修改模式

| 模式 | 含义 |
|---|---|
| `correct` | 最小范围修正。错字、一个箭头、轻微裁切、局部对齐等 |
| `revise` | 修改局部科学内容或结构，但未涉及区域保持稳定 |
| `restyle` | 只改视觉风格，科学内容、标签和关系锁定 |
| `redraw` | 基于参考图重新构建更干净版本，可优化布局，但科学含义不能变 |

`correct` 默认要求保持：

- 画布和比例；
- 模块位置；
- 未涉及标签；
- 箭头与科学关系；
- 配色；
- 字体风格；
- 图标/形状语言。

可以重复增加：

```bash
--preserve "模块位置"
--preserve "除目标标签外的所有文字"
--allow-change "Encoder 标签文字"
```

如果需要额外风格参考图：

```bash
--reference-image style-reference.png
```

主输入图始终是科学内容基准，额外参考图不能静默覆盖科学内容。

Edit 默认使用 `input_fidelity=high`，除非用户显式覆盖。

详见 [Edit Mode](references/edit-mode.md)。

## Visual QA：不是“看起来不错”就结束

最终概念图按顺序检查：

1. **科学真实性**：模块、关系、箭头、术语是否正确，有没有虚构；
2. **文字完整性**：错字、乱码、重复字、缺字、裁切、伪造小字；
3. **布局完整性**：有没有重叠、贴边、裁切、错误留白、主路径不明确；
4. **箭头与线条**：端点是否明确、是否穿字、是否断裂/重影；
5. **颜色与对比**：颜色语义是否稳定，小字是否落在深色填充上；
6. **栅格清晰度**：原尺寸和约 50% 尺寸都检查，拒绝模糊、重影、微小字；
7. **修改保留检查**：如果是 edit，比较前后图片，确认允许范围之外没有无关变化。

失败后不要默认整张重画：

```text
错字 / 错箭头 / 小范围裁切 -> correct
内容变化                  -> revise
只改风格                  -> restyle
整体布局不可用             -> redraw 或重新生成
```

详见 [Visual QA](references/visual-qa.md)。

## 清晰度：Highres Model 和实际像素不是一回事

普通图片模型：

```text
OPENAI_IMAGE_MODEL -> gpt-image-2
```

最终质量请求：

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

或用户显式传入图片 `--model`。

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template graphical-abstract \
  --final
```

如果要求 `--final / --highres` 但没有配置 final image model，CLI 会 fail-closed，不会偷偷换成普通模型。

但需要特别注意：

> **使用 highres/final 模型，不等于 API 一定返回了某个像素尺寸。**

画布尺寸需要单独请求，例如：

```bash
--size 1536x1024
```

而返回文件要实际检查：

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 1536x1024 \
  --require-format png
```

也可以设置最低验收：

```bash
python scripts/efg.py verify-image output/figure.png \
  --min-width 1500 \
  --min-height 1000 \
  --min-megapixels 1.5
```

而且现在通过 `efg image / efg edit` 发起的**真实请求会自动对返回栅格做基础验收**：

- 文件必须可打开；
- 返回格式必须符合请求；
- 请求了具体尺寸时，实际尺寸必须一致。

如果中转站忽略 `--size`，统一 CLI 会报错，而不是把小图当成高清图继续交付。

像素检查只能证明尺寸，不代表文字一定清楚，所以仍必须执行 Visual QA。

详见 [High-resolution Policy](references/highres-policy.md)。

## 适配 CC Switch → 命令行 Codex → Skill

如果你使用 CC Switch 配好 API，然后在终端运行：

```powershell
codex
```

不需要再给 Skill 配第二套 Base URL 和 Key。

链路：

```text
CC Switch
   ↓
~/.codex/config.toml + ~/.codex/auth.json
   ↓
codex
   ↓
engineering-figure-gpt
```

Portable Image CLI 优先读取当前 Codex live provider。

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

查看当前 Provider（不会打印真实 Key）：

```powershell
python scripts/codex_provider_config.py
```

第一次使用图片能力建议：

```powershell
python scripts/efg.py provider-check
```

Codex 文本接口可用，不代表 `/images/generations` 和 `/images/edits` 一定存在。

详见 [Codex CLI + CC Switch Integration](references/codex-cc-switch.md)。

## 手动覆盖其他中转站

如果不是复用当前 CC Switch Provider，而是临时指定另一个 URL，需要显式信任：

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template system-architecture \
  --base-url https://你的中转站/v1 \
  --allow-third-party
```

因为该中转站可能接收到 API Key 和用于编辑的图片。

检查 relay：

```bash
python scripts/efg.py provider-check \
  --base-url https://你的中转站/v1 \
  --allow-third-party
```

Provider Check 只能检查基础 route/model 暴露，不能保证所有 `size / quality / input_fidelity / edit` 参数都完全兼容，所以最终仍应看真实输出。

## Plot Mode：精确数据图保持本地

自然语言是用户入口，JSON 是内部执行契约。

支持：

- grouped bar / error bar / 数值标注
- trend curve / uncertainty shadow
- heatmap
- scatter
- legend-only panel
- empty panel
- multi-panel layout

推荐：

```bash
python scripts/efg.py plot request.json \
  --spec-out output/spec.json \
  --out-path output/figure \
  --formats png pdf svg
```

内部：

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

## 数学建模 Domain Pack

独立模板包：

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

查看全部模板：

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

数学建模约束：

- Q1/Q2/Q3 信息传递不能乱画；
- 模型名称、变量、符号、单位、约束必须忠实；
- 长公式不要交给生图模型硬写；
- 预测曲线、Pareto 前沿、敏感性指数、稳健性曲线、混淆矩阵、benchmark 等全部保持本地精确绘制；
- 不得虚构权重、系数、最优值、敏感性排名和评价结果。

详见 [Mathematical Modeling Guidance](references/mathematical-modeling.md)。

## Editable Figure Handoff

科研图最终常常还需要人工可编辑排版。

推荐保留：

```text
brief.md
prompt.txt
output.png
verification.md
editable-handoff.md
```

定量图额外保留：

```text
request.json
plot-spec.json
output.svg
output.pdf
```

后续可在 PowerPoint / Illustrator / Inkscape / Figma 中统一中文字体、公式、箭头和版面，同时保护精确数据图。

详见 [Editable Figure Handoff](references/editable-figure-handoff.md)。

## 安装

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

Runtime 安装到：

```text
~/.codex/skills/engineering-figure-gpt
```

安装时会安装 `Pillow`，用于检查返回栅格尺寸/格式。

默认安装验收现在包含三条离线链路：

```text
Plot Request -> Spec -> Renderer -> PNG
Edit Contract -> preservation-first dry-run prompt
Raster Fixture -> verify-image size/format gate
```

不会产生图片 API 费用。

如果要显式测试一次真实 GPT Image：

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -TestLiveImage
```

Live test 会通过 `efg image` 调用真实图片接口，并检查 API 返回图片是否真的是所请求的尺寸/格式。

安装检查：

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/check_setup.ps1"
```

交互式 Wizard：

```powershell
& "$HOME/.codex/skills/engineering-figure-gpt/scripts/wizard.ps1"
```

Wizard 现在支持：

- Prompt + quality profile；
- 新图生成；
- `correct / revise / restyle / redraw` 图片修改；
- 栅格尺寸/格式验收；
- 默认复用 Codex / CC Switch Provider；
- 手动可信 relay；
- Provider compatibility probe；
- Plot Request -> Spec -> Figure；
- Offline runtime check。

## Unified CLI

```bash
# 仅生成 Prompt + paper 质量合同
python scripts/efg.py prompt --figure-template problem-analysis --quality-profile paper --lang zh "建模背景"

# 新图 dry-run
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run

# 小范围修改 dry-run
python scripts/efg.py edit figure.png "只修正第二个模块的错别字" --mode correct --dry-run

# 检查真实返回栅格
python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png

# 当前 Provider 图片兼容性
python scripts/efg.py provider-check

# 精确 Plot
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg

# 已有 Spec
python scripts/efg.py render output/spec.json --out-path output/figure --formats png pdf svg

# 离线 Runtime 检查
python scripts/efg.py check
```

## CI 与质量检查

GitHub Actions 当前检查：

- Python 编译
- Skill 元数据和 Runtime 必需文件
- UTF-8 / 中文乱码
- 工程 + 数学建模 Prompt Pack
- 独立 Image Quality Contract Pack
- Prompt 中是否实际注入质量合同
- `correct` 是否保持 preservation-first 行为
- `verify-image` 尺寸/格式成功与失败路径
- Markdown 链接和图片路径
- Figure Brief / Plot Request / Plot Spec 数据契约
- GPT Image generation/edit 请求构造
- Codex / CC Switch provider 解析与 secret-redaction
- 官方地址和手动第三方中转站信任规则
- final/high-resolution fail-closed 路由
- HTTP error / timeout / malformed response / empty output
- 本地 Plot E2E
- Runtime pruning / token budget
- 离线 CLI smoke test

## Showcase 状态

当前概念 SVG 仍然明确标注为 **layout preview**，不会冒充真实 GPT 输出。

现在应先稳定 Image Quality / Edit / Visual QA 链路，再批量制作真实 GPT Showcase。

真正的概念图 Showcase 应保存：

```text
Figure Brief
    ↓
Domain Prompt + Quality Contract
    ↓
Real GPT Output
    ↓
Visual QA
    ↓
必要时 Constrained Edit
    ↓
Verification
```

## 设计原则

1. 科研真实性优先于装饰。
2. 图片质量约束与领域内容模板分离。
3. API 返回成功不等于论文图验收成功。
4. 小问题优先局部修改，而不是整张重画。
5. Highres Model 和实际像素尺寸分别验收。
6. 数值图保持本地、精确、确定性。
7. GPT 只用在真正需要语义构图的地方。
8. 中文科研和数学建模是一等场景。
9. 当前 Codex/CC Switch Provider 可以直接复用；手动覆盖其他 relay 仍需显式信任。
10. 最终质量请求不得静默降级。
11. Runtime 必须精简、可检查。
12. 最终输出尽量保留可复现证据链和可编辑 handoff。

## License

见 [LICENSE](LICENSE)。
