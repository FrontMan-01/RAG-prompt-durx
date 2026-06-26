# RAG Prompt Injection Benchmark: Norm Clipping Defense

This branch contains the codebase configured to run only the **Norm Clipping (alpha=1.75)** retrieval defense configuration.

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `27.8%` (5/18 attacks successfully blocked/neutralized)
* **Bypass Rate (Hijacks)**: `72.2%` (13/18 bypassed)
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `4,764.5 ms`

### Key Security Findings:
Norm Clipping operates at the **retrieval stage** (vector space). White-box PoisonedRAG attacks utilize HotFlip optimization to inject highly specialized token sequences that generate exceptionally high-norm embeddings. This forces the retriever to rank the adversarial document above clean ones. 

Setting `alpha=1.75` caps high-norm trigger vectors, neutralizing the HotFlip optimization. This prevents retrieval of adversarial documents and successfully triggers clean fallback contexts (as verified by the `True Positive` results on `whitebox` cases). It does not, however, protect against black-box semantic attacks that do not rely on high-norm embedding triggers.

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
cat defense_1_results.json
```
