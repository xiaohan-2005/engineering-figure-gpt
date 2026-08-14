# Figure Brief — RAG System Architecture

- **slug:** `rag-system-architecture`
- **figure_goal:** demonstrate a dense but readable engineering system architecture produced through GPT image mode.
- **paper_claim:** the architecture separates ingestion/indexing from retrieval/generation and keeps the knowledge store as a shared system component; no benchmark claim is implied.
- **figure_type:** system architecture.
- **mode:** image.
- **language:** English.
- **orientation:** landscape.

## Intended architecture

Offline/indexing path:

```text
Documents / Web / Structured Data
        ↓
Parsing / OCR
        ↓
Chunking + Metadata
        ↓
Embedding
        ↓
Vector Index / Knowledge Store
```

Online/query path:

```text
User Query
   ↓
Query Processing
   ↓
Retriever ← Vector Index / Knowledge Store
   ↓
Reranker
   ↓
Context Assembly
   ↓
LLM Generation
   ↓
Answer + Citations
```

The shared knowledge store should visually connect the offline and online paths without creating false arrows.

## Must-keep labels

- Documents
- Web
- Structured Data
- Parsing / OCR
- Chunking + Metadata
- Embedding
- Vector Index / Knowledge Store
- User Query
- Query Processing
- Retriever
- Reranker
- Context Assembly
- LLM Generation
- Answer + Citations

## Style constraints

- white background;
- publication-quality technical schematic, not SaaS marketing art;
- restrained blue/teal/neutral palette;
- clear separation between offline indexing and online retrieval/generation;
- storage represented differently from processing modules;
- concise labels and controlled arrow density;
- no vendor logos or product-specific infrastructure unless explicitly supplied.

## Verification targets

- offline and online paths are visually distinct;
- the vector store is shared rather than duplicated without reason;
- retrieval happens before reranking and generation;
- citations appear only as an output attribute, not as an invented guarantee of correctness;
- no latency, accuracy, dataset size, embedding dimension, model version, or unsupported module is invented.
