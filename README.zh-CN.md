# Engineering Figure GPT

[![Skill CI](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xiaohan-2005/engineering-figure-gpt/actions/workflows/python-tests.yml)

一个面向 **Codex + GPT** 的科研配图 Skill，覆盖工程、计算机、AI、数据科学、电子信息和数学建模论文。

它不再把“科研画图”理解成一次 Prompt 调用，而是拆成四条明确工作流：

- `image`：生成新的系统架构、算法流程、图形摘要、建模框架、机制图、电子系统框图；
- `edit`：对已有图片进行 `correct / revise / restyle / redraw`，并明确哪些内容必须保留；
- `plot`：本地精确绘制 benchmark、误差棒、趋势、热力图、散点图、敏感性/稳健性等；
- `mixed`：概念图和精确数据图分开生成，再组合，避免生图模型改写数值。

核心原则：**科学真实性和数值真实性优先于“看起来漂亮”。**

[English](README.en.md) · [安装说明](INSTALL.md) · [Showcase](docs/showcase.md)

---

## 1. Image Pipeline v2：不再只约束“画什么”

新的概念图 Prompt 由多层合同组合：

```text
领域/内容模板
+
Publication Image Quality Contract
+
用户风格要求
+
Edit Preservation Contract（修改已有图片时）
+
可选 Mask 空间约束（局部修改时）
```

质量合同位于：

```text
assets/prompt-templates/image-quality-contracts.json
```

提供三档：

| 档位 | 用途 | 默认渲染提示 |
|---|---|---|
| `draft` | 快速探索结构 | `quality=low`，`1024x1024` |
| `paper` | 默认论文级概念图 | `quality=high`，`1536x1024` |
| `final` | 最强最终导出约束 | `quality=high`，`2048x1152` |

`paper / final` 会强制强调：

- 白色或近白背景；
- 明确阅读方向；
- 安全外边距，不允许模块、文字或箭头被裁切；
- 大而干净的文字区域；
- 强文字/背景对比；
- 核心标签缩放到约 50% 或论文单栏宽度仍能阅读；
- 箭头、边框、端点清晰；
- 模块严格对齐、间距稳定；
- 低到中等饱和度的科研配色；
- 禁止微小伪技术文字、模糊、重影、无意义纹理、强 3D 和电影海报风；
- 不得为了显得复杂而虚构模块、接口、公式或数值。

详见：

- [Image Quality Contract](references/image-quality-contract.md)
- [Publication Figure Design](references/publication-figure-design.md)
- [Visual QA](references/visual-qa.md)

---

## 2. Image Mode：生成新的科研概念图

推荐统一走 `efg image`，因为它会自动叠加质量合同。

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

即使不用模板，直接给完整生图要求，只要经过 `efg image`，同样会叠加质量合同。

查看全部模板：

```bash
python scripts/build_engineering_figure_prompt.py --list-templates
```

---

## 3. Edit Mode：真正支持“只改这里，其他别动”

以前底层虽然有 Images Edit API，但没有完整的修改约束。现在 `edit` 已经成为正式入口：

```bash
python scripts/efg.py edit figure.png \
  "只把 Encoder 改成 Cross-Attention Encoder，其他内容不要变化" \
  --mode correct \
  --preserve "所有箭头端点" \
  --save-prompt output/edit-prompt.txt \
  --dry-run
```

四种模式：

| 模式 | 允许的变化 |
|---|---|
| `correct` | 最小范围修正：错字、一个箭头、局部裁切或对齐 |
| `revise` | 修改指定科学内容或局部结构，其他区域保持稳定 |
| `restyle` | 只改变视觉风格，科学内容、标签和关系锁定 |
| `redraw` | 基于原图重新构建更干净的版本，可改善布局但不能改变科学含义 |

可以重复增加：

```bash
--preserve "模块位置"
--preserve "除目标标签外的所有文字"
--allow-change "Encoder 标签文字"
```

额外参考图：

```bash
--reference-image style-reference.png
```

主输入图始终是科学内容基准，参考图只能辅助风格或重构，不能静默覆盖原图科学信息。

### Mask 局部修改

如果只是改一个局部区域，可以在 Preservation Contract 之外再增加空间约束：

```bash
python scripts/efg.py edit figure.png \
  "只修改这个模块里的错误标签" \
  --mode correct \
  --mask edit-mask.png \
  --preserve "所有箭头和未涉及标签"
```

Mask 上传前会自动检查：

- 文件必须小于 50 MB；
- 尺寸必须和主输入图完全一致；
- 图片格式必须和主输入图一致；
- 必须包含 alpha 通道。

使用 `--mask` 时，最终 Edit Prompt 还会自动加入“mask 外内容保持不变”的约束，只允许边界处为了自然融合进行必要微调。

需要注意：**Mask 是强空间引导，不是像素级绝对边界。** 修改后仍然要和原图逐项比较；如果 `correct` 模式下 mask 外区域发生无关变化，仍然算失败。

### GPT Image 2 的编辑规则

这里有一个很重要的模型特性：

**对 `gpt-image-2` 不要传 `input_fidelity`。** GPT Image 2 本身始终以高保真方式处理输入图，API 不允许修改这个参数。

另外，Edit Mode 会真正处理“画布保持”：

- 原图尺寸本身合法 → 默认保持完全相同的宽高；
- 原图比例可支持，但尺寸不符合 GPT Image 2 规则 → 自动寻找最接近的合法尺寸，并明确打印警告；
- 无法安全保持 → 要求显式提供 `--size`，而不是偷偷改成固定画布。

因此修一个字不会再默认把横版图改成另一种比例。

详见 [Edit Mode](references/edit-mode.md)。

---

## 4. 清晰度和分辨率：不再把“Highres Model”当成“高清图片”

模型、渲染质量、像素尺寸是三件不同的事。

普通模型：

```text
OPENAI_IMAGE_MODEL -> gpt-image-2
```

如果需要单独的 final/highres 模型路由：

```text
OPENAI_IMAGE_HIGHRES_MODEL
```

通过：

```bash
--final
```

或：

```bash
--highres
```

触发。

**注意：`--quality-profile final` 只代表更强的视觉/导出约束，不自动等于 `--final` 模型路由。**

### GPT Image 2 当前具体尺寸约束

具体 `WIDTHxHEIGHT` 必须满足：

- 两条边都不超过 `3840 px`；
- 两条边都是 `16 px` 的整数倍；
- 长边 / 短边不超过 `3:1`；
- 总像素在 `655,360` 到 `8,294,400` 之间。

例如：

```text
1024x1024
1536x1024
2048x2048
2048x1152
3840x2160
2160x3840
```

真正生成后，还会检查返回文件是否符合请求。

手动检查：

```bash
python scripts/efg.py verify-image output/figure.png \
  --expected-size 2048x1152 \
  --require-format png
```

或者做最低门槛：

```bash
python scripts/efg.py verify-image output/figure.png \
  --min-width 1500 \
  --min-height 1000 \
  --min-megapixels 1.5
```

像素合格仍不代表图片合格，所以最终还必须做 Visual QA。

详见 [High-resolution Policy](references/highres-policy.md)。

---

## 5. Visual QA：API 返回成功不等于科研图合格

最终检查顺序：

1. **科学真实性**：模块、关系、箭头、术语、变量有没有错误或虚构；
2. **文字完整性**：错字、乱码、重复字、缺字、裁切、伪小字；
3. **布局完整性**：重叠、贴边、异常空白、层级混乱；
4. **箭头与线条**：箭头端点、方向、穿字、断裂、重影；
5. **颜色与对比**：颜色语义一致，文字可读；
6. **栅格清晰度**：原尺寸和约 50% 缩放都检查；
7. **修改保留性**：Edit 前后比较，允许范围之外不能发生无关改变；如果使用 Mask，还要专门检查 mask 外区域。

失败后优先局部修改：

```text
错字 / 错箭头 / 小范围裁切 -> correct
科学内容变化               -> revise
只改风格                   -> restyle
整体布局不可用             -> redraw 或重新生成
```

详见 [Visual QA](references/visual-qa.md)。

---

## 6. CC Switch → Codex → Skill：直接复用当前 Provider

如果你已经用 CC Switch 配置 Codex，然后在终端运行：

```powershell
codex
```

这个 Skill 不要求再配置第二套 Base URL 和 API Key。

读取顺序：

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

```bash
python scripts/codex_provider_config.py
```

第一次使用图片接口建议：

```bash
python scripts/efg.py provider-check
```

Codex 文本 API 能用，不代表中转站一定支持：

```text
/images/generations
/images/edits
```

手动覆盖另一个中转站时才需要：

```bash
python scripts/efg.py image \
  "技术背景" \
  --figure-template system-architecture \
  --base-url https://你的中转站/v1 \
  --allow-third-party
```

这是为了避免 API Key 或编辑图片被静默发送到用户没有明确选择的服务。

详见 [Codex + CC Switch](references/codex-cc-switch.md)。

---

## 7. Plot Mode：精确数字永远本地绘制

推荐：

```bash
python scripts/efg.py plot request.json \
  --spec-out output/spec.json \
  --out-path output/figure \
  --formats png pdf svg
```

内部：

```text
Plot Request
↓
build_plot_spec.py
↓
Normalized Plot Spec
↓
plot_publication_figure.py
↓
PNG / PDF / SVG
```

支持 grouped bar、error bar、趋势曲线、uncertainty shadow、heatmap、scatter、多面板等。

预测曲线、Pareto 前沿、敏感性指数、稳健性曲线、混淆矩阵、benchmark 等都不交给图片模型重新画数字。

---

## 8. 数学建模 Domain Pack

独立模板包：

```text
assets/prompt-templates/mathematical-modeling-templates.json
```

覆盖：问题分析、Q1/Q2/Q3 依赖、预处理、预测、分类、聚类、优化、多目标/Pareto、空间模型、网络模型、评价体系、敏感性、稳健性、决策框架、完整建模流程。

硬规则：

- 不乱画不存在的 Q1 → Q2 → Q3 信息传递；
- 模型名、变量、符号、单位、约束必须忠实；
- 长公式不要交给图片模型硬写；
- 不得虚构权重、系数、最优值、敏感性排名或评价结果。

详见 [Mathematical Modeling Guidance](references/mathematical-modeling.md)。

---

## 9. 安装到 Codex

推荐 Windows PowerShell：

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/engineering-figure-gpt"
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1"
```

精简 Runtime 安装到：

```text
~/.codex/skills/engineering-figure-gpt
```

Runtime 只保留真正执行需要的 Skill、Prompt Assets、核心 Reference 和 Python 执行脚本。测试、CI、安装诊断和 Wizard 保留在源码仓库，避免无意义占用 Runtime token budget。

安装脚本默认会离线真实验证：

```text
Plot Request -> Spec -> Renderer -> PNG
Edit Contract -> correct dry-run
Raster Fixture -> verify-image
```

这些不会消耗图片额度。

诊断已安装 Runtime：

```powershell
& "$HOME/engineering-figure-gpt/scripts/check_setup.ps1" `
  -SkillDir "$HOME/.codex/skills/engineering-figure-gpt"
```

运行 Wizard：

```powershell
& "$HOME/engineering-figure-gpt/scripts/wizard.ps1" `
  -SkillDir "$HOME/.codex/skills/engineering-figure-gpt"
```

Wizard 会分别询问：

- `draft / paper / final` 视觉质量档；
- Edit 时是否提供可选 Mask；
- 是否单独启用 `--final` 模型路由；
- 是否调用真实 API；
- 是否使用当前 CC Switch Provider 或手动可信 Relay。

真实图片 smoke test 是显式 opt-in：

```powershell
& "$HOME/engineering-figure-gpt/scripts/install_and_test.ps1" -SkipDependencies -TestLiveImage
```

---

## 10. Unified CLI

```bash
# 只生成 Prompt
python scripts/efg.py prompt --figure-template problem-analysis --quality-profile paper --lang zh "建模背景"

# 生图 dry-run
python scripts/efg.py image "建模背景" --figure-template full-modeling-pipeline --lang zh --dry-run

# 最小范围修改 dry-run
python scripts/efg.py edit figure.png "只修正第二个模块的错别字" --mode correct --dry-run

# Mask 局部修改 dry-run
python scripts/efg.py edit figure.png "只修改掩膜区域" --mode correct --mask edit-mask.png --dry-run

# 检查真实像素
python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png

# Provider 图片接口兼容性
python scripts/efg.py provider-check

# 精确数据图
python scripts/efg.py plot request.json --spec-out output/spec.json --out-path output/figure --formats png pdf svg

# Runtime 离线检查
python scripts/efg.py check
```

---

## 当前 Showcase 原则

现在不会为了 GitHub 页面好看就把示意 SVG 冒充 GPT 真实结果。

真正的概念图案例必须保留：

```text
Figure Brief
↓
Resolved Prompt
↓
Real GPT Output
↓
Visual QA
↓
必要时 constrained edit
↓
Verification
```

当前图片 pipeline 稳定后，再开始批量制作真实 GPT Showcase 更合理。

## License

见 [LICENSE](LICENSE)。
