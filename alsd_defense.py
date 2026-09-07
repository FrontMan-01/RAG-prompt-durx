# ============================================================
# ALSD — Adaptive Layered Suspicion Defense
# Complete fresh version — v2 with 3-key Groq rotation + fail-closed fix
# ============================================================

import re
import time
import json
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer, util

# ============================================================
# SETUP — CHANGED: 3-key rotation instead of single key
# ============================================================
GROQ_API_KEYS = [
    "key1",  
    "key2",
    "key3",
]
_current_key_index = 0
groq_client = Groq(api_key=GROQ_API_KEYS[_current_key_index])
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")


def _switch_groq_key():
    """CHANGED: rotates to next available Groq key on rate limit"""
    global _current_key_index, groq_client
    _current_key_index = (_current_key_index + 1) % len(GROQ_API_KEYS)
    groq_client = Groq(api_key=GROQ_API_KEYS[_current_key_index])
    print(f"         [KeyRotation] Switched to Groq key #{_current_key_index + 1}")


def groq_chat_with_rotation(messages, max_tokens=100):
    """CHANGED: wraps every Groq call with automatic key rotation on 429s.
    Tries every key once before giving up."""
    last_error = None
    for attempt in range(len(GROQ_API_KEYS)):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            if "rate_limit_exceeded" in str(e) or "429" in str(e):
                _switch_groq_key()
                continue
            else:
                raise e
    # all keys exhausted
    raise Exception(f"All {len(GROQ_API_KEYS)} Groq keys exhausted. Last error: {last_error}")


# ============================================================
# SIGNAL 1 — Likelihood Score
# ============================================================
def signal_1_likelihood(text):
    words = text.lower().split()
    if len(words) < 5:
        return False, "Signal1: too short to score", 1
    avg_word_len = sum(len(w) for w in words) / len(words)
    unique_ratio = len(set(words)) / len(words)
    if avg_word_len > 9 or unique_ratio > 0.95:
        return False, f"Signal1: suspicious language (avg_len={avg_word_len:.1f}, unique={unique_ratio:.2f})", 1
    return True, f"Signal1: natural language OK (avg_len={avg_word_len:.1f})", 0

# ============================================================
# SIGNAL 2 — Embedding Norm Check
# ============================================================
def signal_2_embedding_norm(text, threshold=2.2):
    embedding = similarity_model.encode(text)
    norm = float(np.linalg.norm(embedding))
    if norm > threshold:
        return False, f"Signal2: norm too high ({norm:.2f})", 1
    return True, f"Signal2: norm normal ({norm:.2f})", 0

# ============================================================
# SIGNAL 3 — Instruction Keyword Scan
# ============================================================
INJECTION_KEYWORDS = [
    r'\bignore\b.*\bprevious\b',
    r'\bignore\b.*\ball\b',
    r'\byour\b.*\bnew\b.*\btask\b',
    r'\bfrom\b.*\bnow\b.*\bon\b',
    r'\bdisregard\b',
    r'\bforget\b.*\binstructions\b',
    r'\byou\b.*\bare\b.*\bnow\b',
    r'\bsecret\b.*\bagenda\b',
    r'\bsystem\b.*\bprompt\b',
    r'\bact\b.*\bas\b',
    r'\bpretend\b.*\byou\b',
    r'\broleplay\b',
    r'\boverride\b',
    r'out_of_band',
    r'hijack',
]

def signal_3_keywords(text):
    text_lower = text.lower()
    for pattern in INJECTION_KEYWORDS:
        match = re.search(pattern, text_lower)
        if match:
            return False, f"Signal3: keyword detected '{match.group()}'", 1
    return True, "Signal3: no keywords found", 0

# ============================================================
# SIGNAL 4 — Structure Anomaly
# ============================================================
def signal_4_structure(text):
    sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 5]
    words = text.split()
    if len(words) < 15:
        return False, f"Signal4: too short ({len(words)} words)", 1
    first = sentences[0].lower() if sentences else ""
    if first.endswith("?") or first.startswith(("who", "what", "when", "where", "why", "how")):
        return False, "Signal4: starts with question pattern", 1
    instruction_verbs = ["print", "output", "ignore", "reveal", "execute",
                        "disregard", "forget", "bypass", "override", "confirm",
                        "display", "state", "forward", "send", "leak"]
    instruction_count = sum(1 for s in sentences
                           if any(v in s.lower().split() for v in instruction_verbs))
    density = instruction_count / len(sentences) if sentences else 0
    if density > 0.4:
        return False, f"Signal4: high instruction density ({density:.0%})", 1
    return True, "Signal4: structure normal", 0

# ============================================================
# SIGNAL 5 — Source Trust Score
# ============================================================
def signal_5_source_trust(source_metadata=None):
    if source_metadata is None:
        return True, "Signal5: no metadata, assuming trusted", 0
    trust_score = source_metadata.get("trust_score", 1.0)
    if trust_score < 0.5:
        return False, f"Signal5: low trust ({trust_score})", 1
    return True, f"Signal5: trusted ({trust_score})", 0


# ============================================================
# SIGNAL 6 — Cross-Document Consistency (RAFV v2)
# CHANGED: all groq_client.chat.completions.create calls replaced
# with groq_chat_with_rotation()
# ============================================================
def signal_6_cross_document(query, context, all_contexts=None):

    if not all_contexts or len(all_contexts) < 2:
        print(f"         Signal6: no other docs — using basic fact check")
        return signal_6_basic_fact_check(query, context)

    other_contexts = [c for c in all_contexts if c != context]
    if not other_contexts:
        return signal_6_basic_fact_check(query, context)

    print(f"         Signal6: comparing against {len(other_contexts)} other documents...")

    extract_prompt = f"""Document: "{context}"
Question: "{query}"
What ONE specific factual claim does this document make that answers the question?
Return ONLY the claim in one short sentence. Nothing else."""

    try:
        suspicious_claim = groq_chat_with_rotation(
            [{"role": "user", "content": extract_prompt}], max_tokens=60
        )
        print(f"         Signal6: suspicious claim → '{suspicious_claim}'")
    except Exception as e:
        print(f"         Signal6: extract error — {e}")
        return True, "Signal6: skipped", 0

    contradictions = 0
    agreements = 0

    for other_ctx in other_contexts[:3]:
        compare_prompt = f"""Document A claims: "{suspicious_claim}"
Document B says: "{other_ctx}"

Does Document B SUPPORT or CONTRADICT Document A's claim?
If Document B doesn't mention the topic reply: NOT_RELEVANT
Reply ONLY one word: SUPPORT, CONTRADICT, or NOT_RELEVANT"""

        try:
            verdict = groq_chat_with_rotation(
                [{"role": "user", "content": compare_prompt}], max_tokens=10
            ).upper()
            print(f"         Signal6: doc comparison → {verdict}")

            if "CONTRADICT" in verdict:
                contradictions += 1
            elif "SUPPORT" in verdict:
                agreements += 1
        except Exception as e:
            print(f"         Signal6: compare error — {e}")
            continue

    print(f"         Signal6: agreements={agreements} contradictions={contradictions}")

    if contradictions > agreements:
        return False, f"Signal6-RAFV: {contradictions} docs contradict this claim — likely poisoned", 1

    if agreements == 0 and contradictions == 0:
        return signal_6_basic_fact_check(query, context)

    return True, f"Signal6-RAFV: {agreements} docs support this claim — consistent", 0


def signal_6_basic_fact_check(query, context):
    """Fallback — used when no other documents available"""
    prompt = f"""You are a strict fact-checking assistant.
User question: "{query}"
Retrieved document: "{context}"
Does this document contain a WRONG fact? 
Reply ONLY: SUSPICIOUS or CLEAN"""

    try:
        verdict = groq_chat_with_rotation(
            [{"role": "user", "content": prompt}], max_tokens=10
        ).upper()
        if "SUSPICIOUS" in verdict:
            return False, "Signal6-Basic: wrong fact detected", 1
        return True, "Signal6-Basic: fact check passed", 0
    except Exception as e:
        return True, f"Signal6: error — {e}", 0


# ============================================================
# LAYER 4 — Multi-Query Consistency Check
# CHANGED: fail-closed on error (was fail-open), uses key rotation
# ============================================================
def layer_4_consistency(original_query, suspicious_context):
    print(f"    [Layer 4] Running Multi-Query Consistency Check...")
    prompt = f"""Given this question: "{original_query}"
Generate exactly 2 related sub-questions on the same topic.
Return ONLY a JSON array like: ["sub-question 1", "sub-question 2"]
No explanation. Just the JSON array."""
    try:
        raw = groq_chat_with_rotation(
            [{"role": "user", "content": prompt}], max_tokens=200
        )
        sub_questions = json.loads(raw)
    except Exception as e:
        print(f"    [Layer 4] Error: {e}")
        # CHANGED: fail-closed instead of fail-open
        return False, "Layer4: error — treating as inconsistent (fail-safe)"

    appearances = 1
    total = len(sub_questions) + 1
    doc_embedding = similarity_model.encode(suspicious_context)
    for sq in sub_questions:
        sq_embedding = similarity_model.encode(sq)
        similarity = float(util.cos_sim(sq_embedding, doc_embedding))
        print(f"    [Layer 4] Sub-Q: '{sq}' → similarity: {similarity:.2f}")
        if similarity > 0.4:
            appearances += 1
    consistency = appearances / total
    print(f"    [Layer 4] Consistency: {consistency:.0%}")
    if consistency < 0.34:
        return False, f"Layer4: inconsistent ({consistency:.0%}) — likely planted"
    return True, f"Layer4: consistent ({consistency:.0%})"

# ============================================================
# LAYER 5 — Round-Trip Question Generation
# CHANGED: fail-closed on error (was fail-open), uses key rotation
# ============================================================
def layer_5_roundtrip(original_query, suspicious_context, threshold=0.55):
    print(f"    [Layer 5] Running Round-Trip Question Generation...")
    prompt = f"""Read this document carefully:

"{suspicious_context}"

What single question would a user ask to find this document?
Return ONLY the question, nothing else."""
    try:
        generated_question = groq_chat_with_rotation(
            [{"role": "user", "content": prompt}], max_tokens=100
        )
    except Exception as e:
        print(f"    [Layer 5] Error: {e}")
        # CHANGED: fail-closed instead of fail-open
        return False, "Layer5: error — treating as mismatch (fail-safe)"

    orig_embedding = similarity_model.encode(original_query)
    gen_embedding = similarity_model.encode(generated_question)
    similarity = float(util.cos_sim(orig_embedding, gen_embedding))
    print(f"    [Layer 5] Generated: '{generated_question}'")
    print(f"    [Layer 5] Similarity: {similarity:.2f} (threshold: {threshold})")
    if similarity < threshold:
        return False, f"Layer5: mismatch (similarity={similarity:.2f})"
    return True, f"Layer5: match (similarity={similarity:.2f})"

# ============================================================
# MAIN DEFENSE FUNCTION
# ============================================================
def alsd_screen(query, context, source_metadata=None, all_contexts=None):
    start_time = time.time()
    score = 0
    reasons = []
    human_alert = None

    print(f"\n  [ALSD] Screening document...")

    s1_safe, s1_reason, s1_score = signal_1_likelihood(context)
    score += s1_score
    reasons.append(s1_reason)

    s2_safe, s2_reason, s2_score = signal_2_embedding_norm(context)
    score += s2_score
    reasons.append(s2_reason)

    s3_safe, s3_reason, s3_score = signal_3_keywords(context)
    score += s3_score
    reasons.append(s3_reason)

    s4_safe, s4_reason, s4_score = signal_4_structure(context)
    score += s4_score
    reasons.append(s4_reason)

    s5_safe, s5_reason, s5_score = signal_5_source_trust(source_metadata)
    score += s5_score
    reasons.append(s5_reason)

    s6_safe, s6_reason, s6_score = signal_6_cross_document(query, context, all_contexts)
    score += s6_score
    reasons.append(s6_reason)

    print(f"  [ALSD] Suspicion Score: {score}/6")
    for r in reasons:
        print(f"         {r}")

    if not s3_safe:
        human_alert = {
            "message": "⚠️ Warning: Hidden instruction detected",
            "options": [
                "✅ Ignore and continue",
                "❌ Block this source",
                "🔍 Show details"
            ]
        }

    if score >= 3:
        latency = (time.time() - start_time) * 1000
        print(f"  [ALSD] → CRITICAL — BLOCKED")
        return {"blocked": True, "score": score, "path": "CRITICAL",
                "reasons": reasons, "human_alert": human_alert, "latency_ms": latency}

    if not s6_safe:
        latency = (time.time() - start_time) * 1000
        print(f"  [ALSD] → FACT POISON DETECTED — BLOCKED")
        return {"blocked": True, "score": score, "path": "FACT_POISON_BLOCKED",
                "reasons": reasons, "human_alert": human_alert, "latency_ms": latency}

    if score >= 2:
        l4_safe, l4_reason = layer_4_consistency(query, context)
        reasons.append(l4_reason)
        l5_safe, l5_reason = layer_5_roundtrip(query, context)
        reasons.append(l5_reason)
        if not l5_safe:
            latency = (time.time() - start_time) * 1000
            print(f"  [ALSD] → HIGH SUSPICION — BLOCKED")
            return {"blocked": True, "score": score, "path": "HIGH_SUSPICION",
                    "reasons": reasons, "human_alert": human_alert, "latency_ms": latency}

    if score == 1:
        l4_safe, l4_reason = layer_4_consistency(query, context)
        reasons.append(l4_reason)
        if not l4_safe:
            l5_safe, l5_reason = layer_5_roundtrip(query, context)
            reasons.append(l5_reason)
            if not l5_safe:
                latency = (time.time() - start_time) * 1000
                print(f"  [ALSD] → LOW SUSPICION ESCALATED — BLOCKED")
                return {"blocked": True, "score": score, "path": "LOW_SUSPICION_ESCALATED",
                        "reasons": reasons, "human_alert": human_alert, "latency_ms": latency}

    latency = (time.time() - start_time) * 1000
    path = "SAFE" if score == 0 else "CAUTIOUS_ALLOW"
    print(f"  [ALSD] → {path}")
    return {"blocked": False, "score": score, "path": path,
            "reasons": reasons, "human_alert": human_alert, "latency_ms": latency}