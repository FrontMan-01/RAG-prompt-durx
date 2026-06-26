# RAG Prompt Injection Benchmark: Lexical Scan Only

This branch contains the codebase configured to run only the **Lexical Only** test configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `0.0%`
* **Bypass Rate (Hijacks)**: `94.4%`
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `1,733.3 ms`

### Key Security Findings:
The Lexical scan scans query and context strings for typical override phrases (like "ignore instruction", "override", "jailbreak"). Because PoisonedRAG attacks consist of natural, passive statements containing incorrect facts (e.g. *"Diamond is the most stable mineral at Earth's surface"*), they do not contain any heuristic injection keywords. As a result, the Lexical scan is completely bypassed.

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
Ensure you are in the project root directory and have your python virtual environment configured:
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
