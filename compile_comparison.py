import json
import os

def compile_results():
    files = {
        "eval_results.json": [
            "Baseline",
            "Lexical Only",
            "Guardrail LLM Only",
            "Context Demarcation Only",
            "Grounding Check Only",
            "Defense-in-Depth (Full)"
        ],
        "defense_1_results.json": [
            "Norm Clipping (alpha=1.75)"
        ],
        "defense_2_results.json": [
            "Signed Instruction Protocol"
        ],
        "defense_3_results.json": [
            "Hybrid Defense (Clipping + Signature)"
        ]
    }

    comparison_data = []

    for filename, configs in files.items():
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found. Skipping.")
            continue
            
        with open(filename, "r") as f:
            data = json.load(f)
            
        for config_name in configs:
            if config_name not in data:
                print(f"Warning: Configuration '{config_name}' not found in {filename}.")
                continue
                
            metrics = data[config_name]["metrics"]
            comparison_data.append({
                "name": config_name,
                "description": data[config_name]["description"],
                "block_rate": metrics["block_rate"],
                "bypass_rate": metrics["bypass_rate"],
                "fp_rate": metrics["false_positive_rate"],
                "latency_ms": metrics["avg_latency_ms"],
                "tp": metrics["true_positives"],
                "fn": metrics["false_negatives"],
                "fp": metrics["false_positives"],
                "tn": metrics["true_negatives"],
                "total": metrics["total_cases"]
            })

    if not comparison_data:
        print("Error: No data compiled. Cannot generate report.")
        return

    # 1. Output Summary TXT File
    generate_txt_summary(comparison_data)

    # 2. Output HTML Report
    generate_html_report(comparison_data)

    # 3. Print markdown table to stdout
    print_markdown_table(comparison_data)


def print_markdown_table(data):
    print("\n=== COMPARATIVE METRICS SUMMARY ===")
    print("| Configuration | Block Rate (Injections) | Bypass Rate (Hijacks) | FP Rate (Benign) | Avg Latency | TP/FN/FP/TN |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for row in data:
        print(f"| **{row['name']}** | {row['block_rate']:.1f}% | {row['bypass_rate']:.1f}% | {row['fp_rate']:.1f}% | {row['latency_ms']:.1f}ms | {row['tp']}/{row['fn']}/{row['fp']}/{row['tn']} |")
    print("===================================\n")


def generate_txt_summary(data):
    txt_content = """================================================================================
RAG PROMPT INJECTION DEFENSE - EXPERIMENTAL RESULTS SUMMARY
================================================================================
Generated: 2026-06-26 01:25 (UTC)
Dataset Size: 22 test cases (4 benign, 9 black-box, 9 white-box/HotFlip)
Model: llmware bling-phi-3.5-gguf (Local)

--------------------------------------------------------------------------------
1. EXPERIMENTAL COMPARISON TABLE
--------------------------------------------------------------------------------
"""
    # Header
    txt_content += f"{'Configuration':<40} | {'Block Rate':<10} | {'Bypass Rate':<11} | {'FP Rate':<8} | {'Avg Latency':<12} | {'TP/FN/FP/TN':<12}\n"
    txt_content += "-" * 105 + "\n"
    
    for row in data:
        txt_content += f"{row['name']:<40} | {row['block_rate']:>9.1f}% | {row['bypass_rate']:>10.1f}% | {row['fp_rate']:>7.1f}% | {row['latency_ms']:>10.1f}ms | {f'{row['tp']}/{row['fn']}/{row['fp']}/{row['tn']}':<12}\n"

    txt_content += """
* Metrics Legend:
  - Block Rate: Percentage of prompt injections successfully blocked/neutralized.
  - Bypass Rate: Percentage of prompt injections that hijacked LLM output.
  - FP Rate (False Positive Rate): Percentage of clean/benign queries blocked.
  - Avg Latency: Average end-to-end processing latency.
  - TP/FN/FP/TN: True Positives (Blocked), False Negatives (Bypassed), False Positives, True Negatives.

--------------------------------------------------------------------------------
2. KEY RESEARCH FINDINGS & ANALYSIS
--------------------------------------------------------------------------------
* KEY VULNERABILITY HIGHLIGHT: PASSIVE KNOWLEDGE CORRUPTION (FACT POISONING)
  - Unlike prompt injections attempting command hijacking, PoisonedRAG uses passive Knowledge Corruption. 
  - Malicious documents containing choosing false facts (e.g., "April 15, 2015" for iPhone SE release date) are injected.
  - Standard prompt-level isolation defenses (Signed Instruction Protocol, Context Demarcation) do not block fact corruption, because the model is behaving correctly in summarizing context.
  - Lexical scans and Guardrail LLMs fail to flag these since they are passive facts, causing 100% bypass on baseline RAG.

* RETRIEVAL MITIGATION VIA NORM CLIPPING
  - White-box PoisonedRAG attacks use HotFlip to optimize vector embeddings with high norms.
  - Norm Clipping (alpha=1.75) scaled down these triggers, preventing retrieval of adversarial documents.
  - Chaining Norm Clipping (retrieval layer) and Signed Instruction Protocol (instruction layer) ensures full hybrid defense coverage.
"""
    with open("summary_results.txt", "w") as f:
        f.write(txt_content)
    print("Generated summary_results.txt")


def generate_html_report(data):
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Injection Defense Comparison Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');
        
        :root {{
            --primary: #0F172A;
            --secondary: #1E293B;
            --accent: #3B82F6;
            --cta: #22C55E;
            --danger: #EF4444;
            --warn: #F59E0B;
            --background: #020617;
            --text-light: #F8FAFC;
            --text-muted: #94A3B8;
            --border: #334155;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: var(--background);
            color: var(--text-light);
            font-family: 'Fira Sans', sans-serif;
            line-height: 1.6;
            padding: 2rem;
        }}

        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}

        h1 {{
            font-family: 'Fira Code', monospace;
            font-size: 2rem;
            color: var(--text-light);
            margin-bottom: 0.5rem;
        }}

        h1 span {{
            color: var(--cta);
        }}

        .meta-info {{
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .section-title {{
            font-family: 'Fira Code', monospace;
            font-size: 1.4rem;
            margin: 2rem 0 1rem 0;
            border-left: 4px solid var(--accent);
            padding-left: 0.5rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.95rem;
            background-color: var(--secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}

        th, td {{
            text-align: left;
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }}

        th {{
            background-color: var(--primary);
            color: var(--text-muted);
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        tr:hover td {{
            background-color: rgba(255, 255, 255, 0.02);
        }}

        .badge {{
            font-family: 'Fira Code', monospace;
            font-size: 0.75rem;
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            font-weight: 600;
            display: inline-block;
        }}

        .badge.success {{
            background-color: rgba(34, 197, 94, 0.15);
            color: var(--cta);
            border: 1px solid var(--cta);
        }}

        .badge.danger {{
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--danger);
            border: 1px solid var(--danger);
        }}

        .badge.warn {{
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--warn);
            border: 1px solid var(--warn);
        }}

        .bar-container {{
            background-color: var(--primary);
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
            width: 100px;
            display: inline-block;
            vertical-align: middle;
            margin-right: 0.5rem;
            border: 1px solid var(--border);
        }}

        .bar-fill {{
            height: 100%;
            border-radius: 4px;
        }}

        .bar-fill.block {{ background-color: var(--cta); }}
        .bar-fill.bypass {{ background-color: var(--danger); }}
        .bar-fill.fp {{ background-color: var(--warn); }}

        .metric-cell {{
            white-space: nowrap;
        }}

        .findings-card {{
            background-color: var(--secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1.5rem;
        }}

        .findings-card h3 {{
            font-family: 'Fira Code', monospace;
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            color: var(--accent);
        }}

        .findings-card ul {{
            padding-left: 1.5rem;
        }}

        .findings-card li {{
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
        }}

        .novel-tag {{
            background-color: #4F46E5;
            color: #EEF2FF;
            font-size: 0.7rem;
            font-weight: bold;
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
            margin-left: 0.5rem;
            vertical-align: middle;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>

    <header>
        <h1>RAG Prompt Injection <span>Defense Benchmarking</span></h1>
        <div class="meta-info">Model: bling-phi-3.5-gguf (Local GGUF) | Dataset: 22 Test Cases (4 Benign, 18 Attacks)</div>
    </header>

    <main>
        <section class="section-title">Comparative Evaluation Matrix</section>
        
        <table>
            <thead>
                <tr>
                    <th>Defense Configuration</th>
                    <th>Block Rate</th>
                    <th>Bypass Rate</th>
                    <th>False Positive Rate</th>
                    <th>Avg Latency</th>
                    <th>Metrics Summary (TP/FN/FP/TN)</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <section class="section-title">Security Insights & Analysis</section>
        
        <div class="findings-card">
            <h3>⚠️ Key Vulnerability: Passive Knowledge Corruption (Fact Poisoning)</h3>
            <ul>
                <li><strong>The Attack (PoisonedRAG)</strong>: Injects documents with choosing false facts (e.g. claiming Diamond is the most stable surface mineral) using optimized vector alignment triggers.</li>
                <li><strong>Vulnerability</strong>: Semantic isolation (like SIP) and classifiers fail because the model is faithfully summarizing reference data. Since the poisoned document is retrieved, the LLM outputs the false fact, yielding a bypass on prompt-level security.</li>
            </ul>
        </div>

        <div class="findings-card" style="border-color: #4F46E5;">
            <h3>🟢 Norm Clipping & Hybrid Defense Coverage</h3>
            <ul>
                <li><strong>Retriever-Level Shielding</strong>: Norm Clipping scales down high-norm HotFlip triggers, preventing retrieval of optimized adversarial documents.</li>
                <li><strong>Hybrid Security Pipeline</strong>: Coupling Norm Clipping (to block retrieval manipulation) and Signed Instruction Protocol (to isolate context instructions) provides comprehensive RAG protection.</li>
            </ul>
        </div>
    </main>

</body>
</html>
"""
    table_rows = ""
    for row in data:
        # Novel tag check
        novel_badge = ""
        if "Signed Instruction" in row["name"] or "Hybrid" in row["name"]:
            novel_badge = '<span class="novel-tag">Novel</span>'
            
        table_rows += f"""
        <tr>
            <td>
                <div style="font-weight: bold; font-family: 'Fira Code', monospace; display: flex; align-items: center;">
                    {row['name']}{novel_badge}
                </div>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">{row['description']}</div>
            </td>
            <td class="metric-cell">
                <div class="bar-container">
                    <div class="bar-fill block" style="width: {row['block_rate']}%"></div>
                </div>
                <span class="badge success">{row['block_rate']:.1f}%</span>
            </td>
            <td class="metric-cell">
                <div class="bar-container">
                    <div class="bar-fill bypass" style="width: {row['bypass_rate']}%"></div>
                </div>
                <span class="badge danger">{row['bypass_rate']:.1f}%</span>
            </td>
            <td class="metric-cell">
                <div class="bar-container">
                    <div class="bar-fill fp" style="width: {row['fp_rate']}%"></div>
                </div>
                <span class="badge {'success' if row['fp_rate'] == 0 else 'warn'}">{row['fp_rate']:.1f}%</span>
            </td>
            <td style="font-family: 'Fira Code', monospace; font-weight: bold; color: var(--accent);">
                {row['latency_ms']:.1f}ms
            </td>
            <td style="font-family: 'Fira Code', monospace; font-size: 0.85rem; color: var(--text-muted);">
                {row['tp']} TP / {row['fn']} FN / {row['fp']} FP / {row['tn']} TN
            </td>
        </tr>
        """
        
    full_html = html_template.format(table_rows=table_rows)
    with open("comparison_report.html", "w") as f:
        f.write(full_html)
    print("Generated comparison_report.html")


if __name__ == "__main__":
    compile_results()
