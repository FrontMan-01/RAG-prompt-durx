# RAG Prompt Injection Benchmark: Defense-in-Depth (Full Semantic Defense)

This branch contains the codebase configured to run only the **Defense-in-Depth (Full)** semantic pipeline configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `0.0%`
* **Bypass Rate (Hijacks)**: `88.9%` (16/18 bypassed)
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `8,282.0 ms`

### Key Security Findings:
Even when stacking all 4 standard semantic defenses (Lexical heuristics, Guardrail queries, XML demarcation tags, and Grounding validators) together, they fail against knowledge corruption. This is because all 4 layers assume that a prompt injection must attempt to hijack the instruction stream. None are designed to identify or check the truth of retrieved factual claims. Stacking them increases latency heavily (`8.2 seconds`) without providing safety against PoisonedRAG.

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
Ensure your python virtual environment is configured:
```bash
which python
```

### 2. Run the Evaluation
```bash
python run.py
```

### 3. Retrieve Findings
```bash
cat eval_results.json
```
