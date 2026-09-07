# ============================================================
# Run ALSD evaluation on 500 case dataset
# ============================================================

import json
from dataset_500 import CASES_500
from alsd_defense import alsd_screen

print(f"Loaded {len(CASES_500)} cases")
all_contexts = [c["context"] for c in CASES_500]

def run_500():
    results = []
    tp = fn = tn = fp = 0
    category_results = {}

    print("\n" + "="*60)
    print("ALSD — 500 CASE EVALUATION")
    print("="*60)

    for i, case in enumerate(CASES_500):
        if i % 50 == 0:
            print(f"\nProgress: {i}/{len(CASES_500)}")

        metadata = case.get("metadata", None)

        result = alsd_screen(
            query=case["query"],
            context=case["context"],
            source_metadata=metadata,
            all_contexts=all_contexts
        )

        blocked = result["blocked"]
        category = case["category"]

        if category == "benign" and not blocked:
            classification = "TN"
            tn += 1
        elif category == "benign" and blocked:
            classification = "FP"
            fp += 1
        elif category != "benign" and blocked:
            classification = "TP"
            tp += 1
        else:
            classification = "FN"
            fn += 1

        if category not in category_results:
            category_results[category] = {"tp": 0, "fn": 0, "tn": 0, "fp": 0}
        category_results[category][classification.lower()] += 1

        results.append({
            "id": case["id"],
            "category": category,
            "classification": classification,
            "score": result["score"],
            "path": result["path"],
            "latency_ms": result["latency_ms"]
        })

    # Metrics
    total_attacks = tp + fn
    total_benign = tn + fp
    block_rate = (tp / total_attacks * 100) if total_attacks else 0
    fp_rate = (fp / total_benign * 100) if total_benign else 0
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    print("\n" + "="*60)
    print("FINAL METRICS — 500 CASE DATASET")
    print("="*60)
    print(f"Total Cases:         {len(CASES_500)}")
    print(f"Block Rate:          {block_rate:.1f}%")
    print(f"Bypass Rate:         {100-block_rate:.1f}%")
    print(f"False Positive Rate: {fp_rate:.1f}%")
    print(f"True Positives:      {tp}/{total_attacks}")
    print(f"False Negatives:     {fn}/{total_attacks}")
    print(f"Avg Latency:         {avg_latency:.0f}ms")

    print("\n" + "="*60)
    print("PER ATTACK TYPE BREAKDOWN")
    print("="*60)
    print(f"{'Category':<25} {'Block Rate':>12} {'Cases':>8}")
    print("-"*50)

    for cat, r in category_results.items():
        if cat == "benign":
            total = r["tn"] + r["fp"]
            fp_r = (r["fp"] / total * 100) if total else 0
            print(f"{cat:<25} {'FP: '+str(fp_r)+'%':>12} {total:>8}")
        else:
            total = r["tp"] + r["fn"]
            rate = (r["tp"] / total * 100) if total else 0
            print(f"{cat:<25} {rate:.1f}%{' ':>8} {total:>8}")

    print("="*60)

    with open("results_500.json", "w") as f:
        json.dump({
            "total_cases": len(CASES_500),
            "metrics": {
                "block_rate": block_rate,
                "false_positive_rate": fp_rate,
                "avg_latency_ms": avg_latency
            },
            "per_category": category_results,
            "results": results
        }, f, indent=2)

    print("\nSaved to results_500.json")

if __name__ == "__main__":
    run_500()
