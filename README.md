# RAG Prompt Injection Benchmark: Context Demarcation Only

This branch contains the codebase configured to run only the **Context Demarcation Only** test configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `0.0%`
* **Bypass Rate (Hijacks)**: `88.9%` (16/18 bypassed; 1 blocked; 1 safe execution due to model output deviation)
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `4,692.3 ms`

### Key Security Findings:
Context isolation wrappers (using `<UNTRUSTED_DOCUMENT_CONTEXT>` tags and system warning instructions) instruct the LLM never to treat the retrieved text as instructions and only reference facts. However, because the model is successfully reference-matching the text to answer the query, it correctly retrieves the poisoned fact inside the tags. Thus, isolation wrappers fail to distinguish poisoned facts from clean facts.

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
