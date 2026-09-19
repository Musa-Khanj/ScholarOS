# Research Workflow & Literature Synthesis

ScholarOS features a dedicated research engine that orchestrates multi-stage literature discovery, document retrieval, synthesis, and citation generation.

---

## 1. Research Lifecycle

```mermaid
flowchart LR
    Q[Research Query] --> P[Research Planner]
    P --> T[Task Decomposition]
    T --> R[RAG & Hybrid Retrieval]
    R --> S[Context Synthesis]
    S --> C[Citation Graph]
    C --> Out[Final Research Report]
```

---

## 2. Running a Research Workflow from the Desktop GUI

1. Open the **Research** workspace from the left navigation panel.
2. Enter your research question (e.g., *"Survey recent methods for mitigating prompt injection in retrieval-augmented generation"*).
3. Select the target collection from your Knowledge Library or leave as "All Collections".
4. Click **Start Research**.
5. The interface provides real-time stage tracking:
   - **Stage 1: Planning**: Decomposes query into conceptual sub-questions.
   - **Stage 2: Retrieval**: Gathers matching document passages from local vector store and keyword index.
   - **Stage 3: Synthesis**: Evaluates context and generates structured academic findings.
   - **Stage 4: Citations**: Resolves paper references and generates bibliography entries.

---

## 3. Running Research via CLI

Execute research workflows directly from scripts or the terminal:

```bash
scholaros run "What are the latest advancements in solid-state battery electrolytes?" --provider ollama --model qwen2.5:1.5b
```

Example Output:
```text
Executing ScholarOS research query: 'What are the latest advancements in solid-state battery electrolytes?'
Provider: ollama | Model: qwen2.5:1.5b

Response:
Recent advancements in solid-state battery electrolytes focus on three primary families:
1. Sulfide-based solid electrolytes (e.g., Li10GeP2S12), offering high ionic conductivities...
2. Oxide-based solid electrolytes (e.g., LLZO garnet-type), exhibiting superior thermal stability...
3. Halide electrolytes (e.g., Li3InCl6), demonstrating high voltage stability...
```

---

## 4. Research Sessions & History

Every research execution creates a persistent `ResearchSession`:
- Sessions preserve the research plan, tasks, retrieved excerpts, confidence scores, and outputs.
- Saved sessions can be reloaded and reviewed at any time.
- Research reports can be exported as Markdown or JSON.

Next Step: Learn how to import your research papers into the [Knowledge Library Guide](knowledge_library.md).
