# Showcase

Engineering Figure GPT separates conceptual composition from exact quantitative rendering.

## 1. Mathematical modeling framework

![Mathematical modeling framework](showcase/model-framework.svg)

**Mode:** `image`  
**Goal:** summarize a modeling paper from problem definition through validation and decision output.  
**Reproducible brief:** `examples/mathematical-model-framework.md`

## 2. RAG / AI system architecture

**Mode:** `image`  
**Suggested structure:** Documents → OCR / chunking → embeddings → vector store → retrieval → reranking → grounded answer.  
**Reproducible brief:** `examples/rag-system-architecture.md`

## 3. Algorithm workflow

**Mode:** `image`  
**Suggested structure:** Input → preprocessing → feature extraction → model inference / optimization → decision → output, with explicit loops and stop conditions when needed.  
**Reproducible brief:** `examples/algorithm-workflow.md`

## 4. Data-analysis pipeline

**Mode:** `image` or `mixed`  
**Suggested structure:** acquisition → cleaning → feature engineering → modeling → evaluation → interpretation.  
**Reproducible brief:** `examples/data-analysis-pipeline.md`

## 5. Multi-objective optimization workflow

**Mode:** `image`  
**Suggested structure:** objectives + constraints → initialization → search / solver → Pareto set → sensitivity analysis → final decision.  
**Reproducible brief:** `examples/multi-objective-optimization.md`

## 6. Benchmark plot

![Benchmark plot](showcase/benchmark-plot.svg)

**Mode:** `plot`  
**Rule:** exact values, axes and geometry remain local and deterministic. The values in this preview are illustrative.  
**Reproducible request:** `examples/benchmark-plot-request.json`

---

Conceptual SVGs in this gallery are **layout previews**, not claims that a particular GPT image run produced them. When the skill is used in Codex, conceptual panels should be generated through the installed GPT image-generation path, while quantitative panels remain exact local plots.
