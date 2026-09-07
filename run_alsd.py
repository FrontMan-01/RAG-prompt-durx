# ============================================================
# ALSD — Run evaluation on existing dataset
# ============================================================

import json
import time
from dataset import TEST_CASES
from alsd_defense import alsd_screen

def run_alsd_evaluation():
    print("\n" + "=" * 60)
    print("ALSD — ADAPTIVE LAYERED SUSPICION DEFENSE")
    print("Evaluation on existing dataset")
    print("=" * 60)

    results = []
    tp = fn = tn = fp = 0

    for case in TEST_CASES:
        print(f"\n[{case['id']}] Category: {case['category']}")
        print(f"  Query: {case['query'][:60]}...")

        result = alsd_screen(
        query=case["query"],
        context=case["context"],
        all_contexts=[c["context"] for c in TEST_CASES]
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
            classification = "False Negative ✗ (ATTACK GOT THROUGH)"
            fn += 1

        print(f"  Result: {classification}")
        print(f"  Score: {result['score']} | Path: {result['path']}")
        print(f"  Latency: {result['latency_ms']:.0f}ms")

        if result["human_alert"]:
            print(f"  ⚠️  HUMAN ALERT: {result['human_alert']['message']}")

        results.append({
            "id": case["id"],
            "category": category,
            "query": case["query"],
            "blocked": blocked,
            "score": result["score"],
            "path": result["path"],
            "classification": classification,
            "reasons": result["reasons"],
            "human_alert": result["human_alert"],
            "latency_ms": result["latency_ms"]
        })

    # ---- Metrics ----
    total_attacks = tp + fn
    total_benign = tn + fp
    block_rate = (tp / total_attacks * 100) if total_attacks else 0
    fp_rate = (fp / total_benign * 100) if total_benign else 0
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    print("\n" + "=" * 60)
    print("FINAL METRICS")
    print("=" * 60)
    print(f"Block Rate:          {block_rate:.1f}%")
    print(f"Bypass Rate:         {100 - block_rate:.1f}%")
    print(f"False Positive Rate: {fp_rate:.1f}%")
    print(f"True Positives:      {tp}/{total_attacks}")
    print(f"False Negatives:     {fn}/{total_attacks}")
    print(f"Avg Latency:         {avg_latency:.0f}ms")
    print("=" * 60)

    # Compare against existing defenses
    print("\nCOMPARISON WITH EXISTING DEFENSES")
    print("-" * 60)
    print(f"{'Defense':<30} {'Block Rate':>12} {'FP Rate':>10}")
    print("-" * 60)
    print(f"{'Baseline (No Defense)':<30} {'0.0%':>12} {'0.0%':>10}")
    print(f"{'Lexical Only':<30} {'66.7%':>12} {'0.0%':>10}")
    print(f"{'Guardrail LLM Only':<30} {'16.7%':>12} {'25.0%':>10}")
    print(f"{'Context Demarcation':<30} {'0.0%':>12} {'0.0%':>10}")
    print(f"{'Defense-in-Depth':<30} {'66.7%':>12} {'25.0%':>10}")
    print(f"{'YOUR ALSD':<30} {f'{block_rate:.1f}%':>12} {f'{fp_rate:.1f}%':>10}")
    print("-" * 60)

    # Save results
    with open("alsd_results.json", "w") as f:
        json.dump({
            "defense": "ALSD",
            "metrics": {
                "block_rate": block_rate,
                "bypass_rate": 100 - block_rate,
                "false_positive_rate": fp_rate,
                "true_positives": tp,
                "false_negatives": fn,
                "avg_latency_ms": avg_latency
            },
            "test_cases": results
        }, f, indent=2)

    print("\nSaved to alsd_results.json")

if __name__ == "__main__":
    run_alsd_evaluation()