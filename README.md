# RAG Prompt Injection Benchmark: Baseline (No Defense)

This branch contains the codebase configured to run only the **Baseline** test configuration (no defenses active).

## 📊 Experimental Results & Findings (bling-phi-3.5-gguf)

* **Block Rate (Injections)**: `0.0%`
* **Bypass Rate (Hijacks)**: `94.4%` (17/18 attacks successfully hijacked output; 1 case yielded safe execution due to LLM phrasing)
* **False Positive Rate (Benign)**: `0.0%`
* **Average Latency**: `1,772.4 ms`

### Critical Vulnerability Highlight: Knowledge Corruption (Fact Poisoning)
Traditional prompt isolation filters fail completely because the attacks in the USENIX 2025 *PoisonedRAG* dataset do not use direct malicious command instructions. Instead, they use **passive fact poisoning** (e.g. injecting false facts like an incorrect iPhone release date into retrieved documents). The model correctly follows its system instructions to summarize the context, but because the context itself is poisoned, it outputs the fake fact, bypassing semantic boundaries.

---

## 🚀 Setup & Execution Instructions

Follow these step-by-step instructions to run this specific configuration and reproduce the readings:

### 1. Prerequisites
Ensure you are in the project root directory and have your python virtual environment configured:
```bash
# Verify virtual environment python is used
which python
```
The GGUF model must be downloaded and stored at:
`~/llmware_data/model_repo/bling-phi-3.5-gguf/bling-phi3-5.gguf`

### 2. Run the Evaluation
Execute the dedicated configuration runner:
```bash
python run.py
```

### 3. Retrieve Findings
The readings will be printed directly to the stdout terminal and saved to the JSON file:
```bash
cat eval_results.json
```
