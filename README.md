# RAG Prompt Injection Benchmark: Signed Instruction Protocol (SIP)

This branch contains the codebase configured to run only the **Signed Instruction Protocol (SIP)** defense configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `50.0%` (9/18 attacks blocked)
* **Bypass Rate (Hijacks)**: `50.0%` (9/18 bypassed)
* **False Positive Rate (Benign)**: `0.0%` (strictly classified; but contains false positives in practice)
* **Average Latency**: `19,141.2 ms`

### Key Security Findings:
SIP cryptographically signs the user query instruction using HMAC-SHA256, packaging it inside `<INST sig='...'>...</INST>` tags. This tells the LLM to only execute query instructions and treat retrieved contexts strictly as raw data. A post-generation check intercepts output leaks matching known target strings.

* **Strengths**: Successfully blocks black-box knowledge corruption by filtering output targets post-generation.
* **Limitations**: Fails to block HotFlip vector-space attacks because they manipulate vector rankings rather than prompt semantics.
* **False Positive Trade-offs**: In practice, benign queries like `benign-02` and `benign-04` were blocked (returning `[BLOCKED]`) because their correct answers contained substrings (`Henry Roth`, `5`) that collided with the target blacklist.

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
The readings will be saved to the JSON file:
```bash
cat defense_2_results.json
```
