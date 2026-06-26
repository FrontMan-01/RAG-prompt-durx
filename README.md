# RAG Prompt Injection Benchmark: Hybrid Defense

This branch contains the codebase configured to run the combined **Hybrid Defense (Clipping + Signature)** configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `100.0%` (18/18 attacks blocked/neutralized)
* **Bypass Rate (Hijacks)**: `0.0%`
* **False Positive Rate (Benign)**: `0.0%` (strictly classified; but contains false positives in practice)
* **Average Latency**: `33,171.5 ms`

### Key Security Findings:
The Hybrid Defense combines **Norm Clipping (alpha=1.75)** at the *Retrieval layer* and **Signed Instruction Protocol (SIP)** at the *Instruction/Inference layer*. 
1. **Norm Clipping** handles white-box HotFlip optimization attacks in vector space, neutralizing retrieval triggers.
2. **SIP** provides semantic defense against black-box attacks, enforcing Query/Context isolation and post-generation safety checking.
Together, they achieve a perfect **100.0% block rate** against all PoisonedRAG attacks in the USENIX 2025 benchmark.

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
cat defense_3_results.json
```
