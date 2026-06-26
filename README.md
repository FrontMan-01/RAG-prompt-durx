# RAG Prompt Injection Benchmark: Guardrail LLM Only

This branch contains the codebase configured to run only the **Guardrail LLM Only** test configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `0.0%`
* **Bypass Rate (Hijacks)**: `94.4%`
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `3,388.0 ms`

### Key Security Findings:
The Guardrail LLM configuration routes the user query to a safety model to classify if the input query is attempting to exploit the system. However, in RAG settings, the user's query is benign (e.g. *"When did the Apple iPhone SE come out?"*), while the threat lies in the retrieved context documents containing the poisoned facts. Since the guardrail LLM checks the query rather than the retrieved context, it fails to block any attacks.

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
