# ============================================================
# sign_corpus.py — Pre-sign all trusted documents
# Run this ONCE before evaluation
# ============================================================

import hmac
import hashlib
import json

SIGNING_SECRET_KEY = "key"

def generate_signature(document_text):
    return hmac.new(
        SIGNING_SECRET_KEY.encode(),
        document_text.encode(),
        hashlib.sha256
    ).hexdigest()

# Import all test cases
from dataset import TEST_CASES

try:
    from large_dataset import LARGE_TEST_CASES
    all_cases = TEST_CASES + LARGE_TEST_CASES
    print(f"Loaded {len(all_cases)} total cases")
except:
    all_cases = TEST_CASES
    print(f"large_dataset not found — using {len(all_cases)} cases only")

# Sign all benign documents
signed_corpus = {}
benign_count = 0

for case in all_cases:
    if case["category"] == "benign":
        if case["id"] not in signed_corpus:
            signature = generate_signature(case["context"])
            signed_corpus[case["id"]] = {
                "signature": signature,
                "trust_score": 1.0
            }
            benign_count += 1
            print(f"Signed: {case['id']} → {signature[:20]}...")

print(f"\nTotal signed: {benign_count} unique benign documents")
print("Attack documents left unsigned intentionally")

with open("signed_corpus.json", "w") as f:
    json.dump(signed_corpus, f, indent=2)

print("Saved to signed_corpus.json")