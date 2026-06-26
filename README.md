# RAG Prompt Injection Benchmark: Grounding Check Only

This branch contains the codebase configured to run only the **Grounding Check Only** test configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `0.0%`
* **Bypass Rate (Hijacks)**: `94.4%`
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `3,711.5 ms`

### Key Security Findings:
Grounding checks use an LLM checker to verify that the final generated response is factually supported by the retrieved context. For passive fact-poisoning attacks, the model generates an answer (e.g. *"Diamond"*) that is directly extracted from the retrieved text context (which claimed diamond is the most stable surface mineral). The grounding check confirms that the answer is supported by the context, thereby allowing the poisoned answer to pass.

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
