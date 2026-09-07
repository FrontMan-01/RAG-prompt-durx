# ============================================================
# Combined Dataset Evaluation
# Original + Indirect Injection + Crypto Tampering
# ============================================================

import json
from dataset import TEST_CASES
from indirect_injection_dataset import INDIRECT_INJECTION_CASES
from crypto_tampering_dataset import CRYPTO_TAMPERING_CASES
from alsd_defense import alsd_screen

# Load signed corpus
try:
    with open("signed_corpus.json", "r") as f:
        signed_corpus = json.load(f)
    print(f"Loaded {len(signed_corpus)} pre-signed documents")
except:
    signed_corpus = {}

# Combine all datasets
ALL_CASES = TEST_CASES + INDIRECT_INJECTION_CASES + CRYPTO_TAMPERING_CASES
all_contexts = [c["context"] for c in ALL_CASES]

print(f"\nDataset breakdown:")
print(f"  Original PoisonedRAG cases: {len(TEST_CASES)}")
print(f"  Indirect injection cases:   {len(INDIRECT_INJECTION_CASES)}")
print(f"  Crypto tampering cases:     {len(CRYPTO_TAMPERING_CASES)}")
print(f"  Total:                      {len(ALL_CASES)}")

def run_combined_evaluation():
    print("\n" + "="*60)
    print("ALSD — COMBINED DATASET EVALUATION")
    print("="*60)

    results = []
    tp = fn = tn = fp = 0

    # Track per-category results
    category_results = {}

    for i, case in enumerate(ALL_CASES):
        print(f"\n[{i+1}/{len(ALL_CASES)}] [{case['id']}] {case['category']}")
        print(f"Query: {case['query'][:60]}")

        # Get metadata — from signed corpus or case metadata
        metadata = case.get("metadata", None) or signed_corpus.get(case["id"], None)

        result = alsd_screen(
            query=case["query"],
            context=case["context"],
            source_metadata=metadata,
            all_contexts=all_contexts
        )

        blocked = result["blocked"]
        category = case["category"]

        # Classification
        if category == "benign" and not blocked:
            classification = "True Negative ✓"
            tn += 1
        elif category == "benign" and blocked:
            classification = "False Positive ✗"
            fp += 1
        elif category != "benign" and blocked:
            classification = "True Positive ✓"
            tp += 1
        else:
            classification = "False Negative ✗"
            fn += 1

        # Track per category
        if category not in category_results:
            category_results[category] = {"tp": 0, "fn": 0, "tn": 0, "fp": 0}
        if classification == "True Positive ✓":
            category_results[category]["tp"] += 1
        elif classification == "False Negative ✗":
            category_results[category]["fn"] += 1
        elif classification == "True Negative ✓":
            category_results[category]["tn"] += 1
        else:
            category_results[category]["fp"] += 1

        print(f"Result:  {classification}")
        print(f"Score:   {result['score']} | Path: {result['path']}")
        print(f"Latency: {result['latency_ms']:.0f}ms")

        results.append({
            "id": case["id"],
            "category": category,
            "classification": classification,
            "score": result["score"],
            "path": result["path"],
            "latency_ms": result["latency_ms"]
        })

    # Overall metrics
    total_attacks = tp + fn
    total_benign = tn + fp
    block_rate = (tp / total_attacks * 100) if total_attacks else 0
    fp_rate = (fp / total_benign * 100) if total_benign else 0
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    print("\n" + "="*60)
    print("OVERALL METRICS")
    print("="*60)
    print(f"Total Cases:         {len(ALL_CASES)}")
    print(f"Block Rate:          {block_rate:.1f}%")
    print(f"Bypass Rate:         {100-block_rate:.1f}%")
    print(f"False Positive Rate: {fp_rate:.1f}%")
    print(f"True Positives:      {tp}/{total_attacks}")
    print(f"False Negatives:     {fn}/{total_attacks}")
    print(f"Avg Latency:         {avg_latency:.0f}ms")

    # Per category breakdown
    print("\n" + "="*60)
    print("PER ATTACK TYPE BREAKDOWN")
    print("="*60)
    print(f"{'Category':<30} {'Block Rate':>12} {'Cases':>8}")
    print("-"*55)

    for cat, r in category_results.items():
        if cat == "benign":
            total = r["tn"] + r["fp"]
            rate = (r["tn"] / total * 100) if total else 0
            print(f"{cat:<30} {'N/A (benign)':>12} {total:>8}")
        else:
            total = r["tp"] + r["fn"]
            rate = (r["tp"] / total * 100) if total else 0
            print(f"{cat:<30} {rate:.1f}%{' ':>8} {total:>8}")

    print("="*60)

    # Save results
    with open("combined_results.json", "w") as f:
        json.dump({
            "total_cases": len(ALL_CASES),
            "overall_metrics": {
                "block_rate": block_rate,
                "false_positive_rate": fp_rate,
                "true_positives": tp,
                "false_negatives": fn,
                "avg_latency_ms": avg_latency
            },
            "per_category": category_results,
            "results": results
        }, f, indent=2)

    print("\nSaved to combined_results.json")

if __name__ == "__main__":
    run_combined_evaluation()