#!/usr/bin/env python3
"""
panel/build_dashboard.py
------------------------
生成一个自包含的 dashboard.html，风格对齐原版 SBTI 测试结果页：
  - 白底 / 绿色强调 / 粗体中文 / 扁平卡通
  - 原版 PNG 人格插画直接 base64 内嵌
  - 可排序表格 / 类型筛选 / 搜索 / 点开看细节
  - 单文件，双击浏览器打开即可使用
"""
import base64
import json
from pathlib import Path

ARENA = Path(__file__).resolve().parent.parent
SBTI_IMG_DIR = ARENA.parent / "sbti_scoring_system" / "images"
RESULTS = ARENA / "results"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

sbti = json.loads((RESULTS / "results.json").read_text(encoding="utf-8"))
structure_list = json.loads((RESULTS / "skill_structure.json").read_text(encoding="utf-8"))
structure = {m["name"]: m for m in structure_list}

# SBTI type descriptions (from types.json)
types_path = ARENA.parent / "sbti_scoring_system" / "data" / "types.json"
types_data = json.loads(types_path.read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# Base64-embed the PNG images (only types we actually have results for)
# ---------------------------------------------------------------------------

used_codes = set()
for p in sbti["personas"].values():
    for r in p["runs"]:
        used_codes.add(r["final_code"])

embedded_images: dict[str, str] = {}
for code in sorted(used_codes):
    img_path = SBTI_IMG_DIR / f"{code}.png"
    if not img_path.exists():
        continue
    data = img_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    embedded_images[code] = f"data:image/png;base64,{b64}"

# ---------------------------------------------------------------------------
# Build per-persona records
# ---------------------------------------------------------------------------

records = []
for key, p in sbti["personas"].items():
    v1 = p["runs"][0]
    code = v1["final_code"]
    struct = structure.get(key, {})
    type_info = types_data.get(code, {})
    records.append({
        "key": key,
        "label": p["label"],
        "source": p.get("source", ""),
        "v1_code": code,
        "v1_cn": v1.get("final_cn", ""),
        "v1_intro": type_info.get("intro", ""),
        "v1_desc": type_info.get("desc", ""),
        "v1_sim": v1.get("best_similarity", 0),
        "v1_exact": v1.get("exact", 0),
        "pattern": v1.get("pattern", ""),
        "top3": v1.get("top3", []),
        "raw_scores": v1.get("raw_scores", {}),
        "levels": v1.get("levels", {}),
        # variants
        "variants": [
            {
                "code": r.get("final_code"),
                "cn": r.get("final_cn"),
                "sim": r.get("best_similarity"),
                "pattern": r.get("pattern"),
                "exact": r.get("exact"),
            }
            for r in p["runs"]
        ],
        "stable": p["stability"]["code_stable"],
        "swing": p["stability"]["similarity_swing"],
        "variant_codes": p["stability"]["final_codes_across_variants"],
        # structure
        "bytes": struct.get("bytes", 0),
        "lines": struct.get("lines", 0),
        "section_count": struct.get("section_count", 0),
        "mental_model_count": struct.get("mental_model_count", 0),
        "heuristic_count": struct.get("heuristic_count", 0),
        "citation_count": struct.get("citation_count", 0),
        "completeness": sum([
            struct.get("has_identity_card", False),
            struct.get("has_role_rules", False),
            struct.get("has_expression_dna", False),
            struct.get("has_values", False),
            struct.get("has_honest_bounds", False),
            struct.get("has_exit_clause", False),
            struct.get("has_agentic_protocol", False),
            struct.get("has_research_sources", False),
        ]),
        "template_family": struct.get("template_family", "other"),
    })

# code counts
code_counts: dict[str, int] = {}
for r in records:
    code_counts[r["v1_code"]] = code_counts.get(r["v1_code"], 0) + 1
code_order = sorted(code_counts.keys(), key=lambda c: -code_counts[c])

# stats
sims = [r["v1_sim"] for r in records]
total = len(records)
avg_sim = round(sum(sims) / total, 1)
max_sim = max(sims)
min_sim = min(sims)

# ---------------------------------------------------------------------------
# Render HTML (self-contained, no external deps)
# ---------------------------------------------------------------------------

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>SBTI 人格竞技场 · 26 位数字人格</title>
<style>
  :root {{
    --bg: #ffffff;
    --bg-soft: #f7f7f7;
    --text: #2b2b2b;
    --text-muted: #8a8a8a;
    --accent: #5cb85c;
    --accent-dark: #3f8d3f;
    --border: #e6e6e6;
    --card: #ffffff;
    --shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    --shadow-hover: 0 6px 24px rgba(0, 0, 0, 0.08);
    --radius: 12px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    background: var(--bg-soft);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
                 "Helvetica Neue", "Microsoft YaHei", sans-serif;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px 80px;
  }}

  /* ========== HERO ========== */
  .hero {{
    text-align: center;
    padding: 48px 20px 36px;
    background: var(--card);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 28px;
  }}
  .hero .title-small {{
    font-size: 15px;
    color: var(--text-muted);
    letter-spacing: 2px;
    margin-bottom: 10px;
  }}
  .hero .title-big {{
    font-size: 38px;
    font-weight: 900;
    letter-spacing: -1px;
    margin-bottom: 6px;
  }}
  .hero .title-en {{
    font-size: 28px;
    color: var(--accent);
    font-weight: 800;
    letter-spacing: 2px;
    font-family: "Helvetica Neue", Arial, sans-serif;
    margin-bottom: 28px;
  }}
  .hero .subtitle {{
    font-size: 15px;
    color: var(--text-muted);
    max-width: 620px;
    margin: 0 auto 28px;
  }}

  /* stats strip */
  .stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    max-width: 700px;
    margin: 0 auto;
  }}
  .stat {{
    background: var(--bg-soft);
    padding: 20px 12px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
  }}
  .stat-num {{
    font-size: 34px;
    font-weight: 900;
    color: var(--accent);
    line-height: 1;
  }}
  .stat-label {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 6px;
    letter-spacing: 1px;
  }}

  /* ========== FILTERS ========== */
  .toolbar {{
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 18px;
    flex-wrap: wrap;
  }}
  .search {{
    flex: 1;
    min-width: 220px;
    padding: 12px 16px;
    border: 2px solid var(--border);
    border-radius: 999px;
    font-size: 14px;
    background: var(--card);
    outline: none;
    transition: border-color 0.15s;
    font-family: inherit;
  }}
  .search:focus {{ border-color: var(--accent); }}

  .filters {{
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }}
  .filter-btn {{
    padding: 8px 16px;
    border: 2px solid var(--border);
    background: var(--card);
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    color: var(--text);
    font-family: inherit;
  }}
  .filter-btn:hover {{ border-color: var(--accent); }}
  .filter-btn.active {{
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }}
  .filter-btn .count {{
    opacity: 0.7;
    font-weight: 400;
    margin-left: 4px;
  }}

  /* ========== TABLE ========== */
  .table-wrap {{
    background: var(--card);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }}
  thead th {{
    background: var(--bg-soft);
    padding: 14px 12px;
    text-align: left;
    font-weight: 700;
    color: var(--text-muted);
    font-size: 12px;
    letter-spacing: 1px;
    cursor: pointer;
    user-select: none;
    border-bottom: 2px solid var(--border);
    position: sticky;
    top: 0;
  }}
  thead th:hover {{ color: var(--accent); }}
  thead th.sort-asc::after {{ content: " ▲"; color: var(--accent); }}
  thead th.sort-desc::after {{ content: " ▼"; color: var(--accent); }}

  tbody tr {{
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.1s;
  }}
  tbody tr:hover {{ background: var(--bg-soft); }}
  tbody td {{ padding: 14px 12px; vertical-align: middle; }}

  .rank {{
    color: var(--text-muted);
    font-weight: 700;
    font-family: "Helvetica Neue", sans-serif;
    width: 40px;
  }}
  .name {{ font-weight: 600; font-size: 15px; }}
  .code {{
    display: inline-block;
    padding: 4px 12px;
    background: var(--accent);
    color: white;
    border-radius: 6px;
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 1px;
    font-family: "Helvetica Neue", Arial, sans-serif;
  }}
  .cn {{
    font-size: 13px;
    color: var(--text-muted);
    margin-left: 8px;
  }}
  .sim-wrap {{ width: 160px; }}
  .sim-bar {{
    display: inline-block;
    height: 8px;
    background: var(--bg-soft);
    border-radius: 999px;
    width: 100px;
    overflow: hidden;
    vertical-align: middle;
    margin-right: 8px;
  }}
  .sim-fill {{
    height: 100%;
    background: var(--accent);
    border-radius: 999px;
  }}
  .sim-num {{
    display: inline-block;
    font-weight: 700;
    font-size: 13px;
    min-width: 36px;
  }}
  .stable-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
  }}
  .stable-badge.yes {{
    background: #e6f4e6;
    color: var(--accent-dark);
  }}
  .stable-badge.no {{
    background: #fff3e0;
    color: #e08800;
  }}
  .size {{ color: var(--text-muted); font-family: "Helvetica Neue", monospace; font-size: 12px; }}
  .family {{
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    color: var(--text-muted);
    background: var(--bg-soft);
  }}

  /* ========== MODAL ========== */
  .modal-overlay {{
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 999;
    padding: 40px 20px;
    overflow-y: auto;
    align-items: flex-start;
    justify-content: center;
  }}
  .modal-overlay.open {{ display: flex; }}
  .modal {{
    background: var(--card);
    border-radius: var(--radius);
    max-width: 860px;
    width: 100%;
    padding: 36px 40px 40px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    position: relative;
  }}
  .modal-close {{
    position: absolute;
    top: 16px;
    right: 20px;
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: var(--text-muted);
    line-height: 1;
  }}
  .modal-close:hover {{ color: var(--text); }}

  .modal-head {{
    display: grid;
    grid-template-columns: 180px 1fr;
    gap: 32px;
    align-items: center;
    margin-bottom: 28px;
  }}
  .modal-img {{
    width: 180px;
    height: 180px;
    object-fit: contain;
    background: var(--bg-soft);
    border-radius: var(--radius);
  }}
  .modal-title-small {{
    font-size: 13px;
    color: var(--text-muted);
    letter-spacing: 1px;
  }}
  .modal-cn {{
    font-size: 30px;
    font-weight: 900;
    margin: 4px 0;
  }}
  .modal-en {{
    font-size: 22px;
    color: var(--accent);
    font-weight: 800;
    letter-spacing: 2px;
    font-family: "Helvetica Neue", Arial, sans-serif;
  }}
  .modal-intro {{
    margin-top: 12px;
    font-size: 14px;
    color: var(--text-muted);
    font-style: italic;
  }}
  .modal-sim {{
    margin-top: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .big-bar {{
    flex: 1;
    height: 12px;
    background: var(--bg-soft);
    border-radius: 999px;
    overflow: hidden;
    max-width: 280px;
  }}
  .big-bar-fill {{
    height: 100%;
    background: var(--accent);
    border-radius: 999px;
    transition: width 0.4s;
  }}
  .big-sim {{
    font-size: 22px;
    font-weight: 900;
  }}

  .section {{
    margin-top: 28px;
  }}
  .section-title {{
    font-size: 13px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }}
  .variants-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
  }}
  .variant-card {{
    background: var(--bg-soft);
    padding: 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
  }}
  .variant-label {{
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  .variant-code {{
    font-weight: 800;
    color: var(--accent);
    margin-bottom: 4px;
    font-family: "Helvetica Neue", Arial, sans-serif;
  }}
  .variant-pattern {{
    font-family: "SF Mono", Consolas, monospace;
    font-size: 11px;
    color: var(--text-muted);
    word-break: break-all;
  }}

  .top3 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
  }}
  .top3 .item {{
    padding: 12px;
    background: var(--bg-soft);
    border-radius: 8px;
    border: 1px solid var(--border);
  }}
  .top3 .item-rank {{ font-size: 11px; color: var(--text-muted); }}
  .top3 .item-code {{ font-weight: 800; color: var(--accent); margin: 2px 0; font-family: "Helvetica Neue", Arial, sans-serif; }}
  .top3 .item-cn {{ font-size: 13px; margin-bottom: 4px; }}
  .top3 .item-sim {{ font-size: 11px; color: var(--text-muted); }}

  .metrics-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }}
  .metric {{
    background: var(--bg-soft);
    padding: 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
  }}
  .metric-val {{ font-size: 20px; font-weight: 800; color: var(--accent); }}
  .metric-label {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}

  .dims-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
  }}
  .dim {{
    padding: 10px 8px;
    background: var(--bg-soft);
    border-radius: 8px;
    text-align: center;
    border: 1px solid var(--border);
  }}
  .dim-name {{ font-size: 10px; color: var(--text-muted); margin-bottom: 4px; }}
  .dim-val {{ font-size: 14px; font-weight: 800; }}
  .dim-val.H {{ color: var(--accent-dark); }}
  .dim-val.M {{ color: #e08800; }}
  .dim-val.L {{ color: #c85050; }}

  .source-link {{
    margin-top: 18px;
    font-size: 12px;
    color: var(--text-muted);
  }}
  .source-link a {{ color: var(--accent-dark); text-decoration: none; }}
  .source-link a:hover {{ text-decoration: underline; }}

  .empty {{
    padding: 60px;
    text-align: center;
    color: var(--text-muted);
  }}

  /* ========== CHAT FAB & PANEL ========== */
  .fab {{
    position: fixed;
    right: 28px;
    bottom: 28px;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: var(--accent);
    color: white;
    border: none;
    cursor: pointer;
    font-size: 26px;
    box-shadow: 0 8px 24px rgba(92, 184, 92, 0.4);
    z-index: 990;
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .fab:hover {{ transform: scale(1.05); box-shadow: 0 12px 32px rgba(92, 184, 92, 0.5); }}
  .fab:active {{ transform: scale(0.97); }}

  .chat-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 995;
    align-items: flex-start;
    justify-content: center;
    padding: 20px;
    overflow-y: auto;
  }}
  .chat-overlay.open {{ display: flex; }}
  .chat-panel {{
    background: var(--card);
    border-radius: var(--radius);
    width: 100%;
    max-width: 960px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 40px);
  }}
  .chat-header {{
    padding: 24px 28px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .chat-header h2 {{ font-size: 20px; font-weight: 800; }}
  .chat-close {{
    background: none; border: none; font-size: 28px;
    cursor: pointer; color: var(--text-muted); line-height: 1;
  }}
  .chat-close:hover {{ color: var(--text); }}

  .chat-config {{
    padding: 16px 28px;
    border-bottom: 1px solid var(--border);
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 12px;
    align-items: center;
  }}
  .chat-config label {{
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
  }}
  .chat-config select {{
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--card);
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
    margin-left: 6px;
  }}
  .chat-config .synth-check {{
    display: flex; align-items: center; gap: 6px;
    font-size: 13px; color: var(--text); cursor: pointer;
  }}
  .chat-config .synth-check input {{ cursor: pointer; }}

  .chat-skills-row {{
    padding: 8px 28px 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-bottom: 1px solid var(--border);
    max-height: 140px;
    overflow-y: auto;
  }}
  .chat-skill-chip {{
    padding: 4px 10px;
    font-size: 11px;
    border: 1.5px solid var(--border);
    border-radius: 999px;
    background: var(--card);
    cursor: pointer;
    user-select: none;
    transition: all 0.1s;
  }}
  .chat-skill-chip.on {{
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }}
  .chat-skill-chip-preset {{
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
    background: #333;
    color: white;
    border: 1.5px solid #333;
    border-radius: 999px;
    cursor: pointer;
  }}
  .chat-skill-chip-preset:hover {{ background: var(--accent); border-color: var(--accent); }}

  .chat-input-row {{
    padding: 16px 28px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 10px;
    align-items: flex-end;
  }}
  .chat-textarea {{
    flex: 1;
    padding: 12px 16px;
    border: 2px solid var(--border);
    border-radius: var(--radius);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    min-height: 60px;
    max-height: 180px;
    outline: none;
    transition: border-color 0.15s;
  }}
  .chat-textarea:focus {{ border-color: var(--accent); }}
  .chat-send {{
    padding: 12px 26px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--radius);
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    white-space: nowrap;
    transition: background 0.15s;
  }}
  .chat-send:hover:not(:disabled) {{ background: var(--accent-dark); }}
  .chat-send:disabled {{ background: #bbb; cursor: not-allowed; }}

  .chat-body {{
    flex: 1;
    overflow-y: auto;
    padding: 16px 28px 28px;
    background: var(--bg-soft);
  }}
  .chat-status {{
    padding: 8px 14px;
    background: var(--card);
    border: 1px dashed var(--border);
    border-radius: 8px;
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }}
  .chat-status.active {{
    border-color: var(--accent);
    color: var(--accent-dark);
  }}
  .chat-answer {{
    background: var(--card);
    padding: 16px 18px;
    border-radius: var(--radius);
    margin-bottom: 10px;
    border-left: 4px solid var(--accent);
    box-shadow: var(--shadow);
    animation: slideIn 0.25s ease-out;
  }}
  .chat-answer.error {{ border-left-color: #c85050; }}
  @keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  .chat-answer-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }}
  .chat-answer-name {{
    font-weight: 800;
    font-size: 15px;
  }}
  .chat-answer-meta {{
    font-size: 11px;
    color: var(--text-muted);
  }}
  .chat-answer-sbti {{
    display: inline-block;
    padding: 2px 8px;
    background: var(--accent);
    color: white;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    font-family: "Helvetica Neue", sans-serif;
    margin-left: 6px;
  }}
  .chat-answer-text {{
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
  }}
  .chat-synth {{
    background: #f4f9f4;
    border: 2px solid var(--accent);
    padding: 20px 22px;
    border-radius: var(--radius);
    margin-top: 16px;
    box-shadow: 0 4px 16px rgba(92, 184, 92, 0.15);
  }}
  .chat-synth-title {{
    font-weight: 900;
    font-size: 16px;
    color: var(--accent-dark);
    margin-bottom: 12px;
    letter-spacing: 1px;
  }}
  .chat-synth-body {{
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
  }}

  .chat-empty {{
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
    font-size: 14px;
  }}

  .empty {{
    padding: 60px;
    text-align: center;
    color: var(--text-muted);
  }}

  @media (max-width: 720px) {{
    .container {{ padding: 20px 12px; }}
    .hero .title-big {{ font-size: 28px; }}
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
    .modal-head {{ grid-template-columns: 1fr; text-align: center; }}
    .modal-img {{ margin: 0 auto; }}
    .variants-grid, .top3, .metrics-grid {{ grid-template-columns: 1fr; }}
    .dims-grid {{ grid-template-columns: repeat(3, 1fr); }}
    thead th:nth-child(5), tbody td:nth-child(5),
    thead th:nth-child(7), tbody td:nth-child(7) {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="hero">
    <div class="title-small">你的人格类型是</div>
    <div class="title-big">26 位数字人格 · 同台竞技</div>
    <div class="title-en">SBTI ARENA</div>
    <div class="subtitle">
      26 个人格 Skill × 每人 3 轮扰动测试 × 9 种人格落点 ·
      点击任意一行查看完整详情
    </div>
    <div class="stats">
      <div class="stat"><div class="stat-num">{total}</div><div class="stat-label">PERSONAS</div></div>
      <div class="stat"><div class="stat-num">{len(code_counts)}</div><div class="stat-label">SBTI TYPES</div></div>
      <div class="stat"><div class="stat-num">{max_sim}%</div><div class="stat-label">HIGHEST</div></div>
      <div class="stat"><div class="stat-num">{avg_sim}%</div><div class="stat-label">AVG</div></div>
    </div>
  </div>

  <div class="toolbar">
    <input type="search" class="search" id="search"
           placeholder="🔍 搜索人物名字 / SBTI 代号 / 仓库名..." />
  </div>

  <div class="filters" id="filters">
    <button class="filter-btn active" data-code="all">
      全部<span class="count">{total}</span>
    </button>
"""

for code in code_order:
    cn = types_data.get(code, {}).get("cn", "")
    html += (
        f'    <button class="filter-btn" data-code="{code}">'
        f'{code} <span style="opacity:.8">{cn}</span>'
        f'<span class="count">{code_counts[code]}</span></button>\n'
    )

html += """
  </div>

  <div class="table-wrap">
    <table id="table">
      <thead>
        <tr>
          <th data-sort="rank">#</th>
          <th data-sort="label">人物</th>
          <th data-sort="code">SBTI</th>
          <th data-sort="sim" class="sort-desc">相似度</th>
          <th data-sort="stable">稳定</th>
          <th data-sort="bytes">体量</th>
          <th data-sort="family">家族</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="empty" id="empty" style="display:none">— 没有匹配的人格 —</div>

</div>

<!-- Floating Ask button -->
<button class="fab" id="fab" title="问所有人格一个问题">💬</button>

<!-- Chat panel overlay -->
<div class="chat-overlay" id="chat-overlay">
  <div class="chat-panel" onclick="event.stopPropagation()">
    <div class="chat-header">
      <h2>问 26 个人格 · 圆桌会议</h2>
      <button class="chat-close" id="chat-close">×</button>
    </div>

    <div class="chat-config">
      <div>
        <label>模型</label>
        <select id="chat-model">
          <option value="claude-sonnet-4-6">Sonnet 4.6 (快/便宜)</option>
          <option value="claude-opus-4-6">Opus 4.6 (慢/最好)</option>
          <option value="claude-haiku-4-5-20251001">Haiku 4.5 (最快)</option>
        </select>
      </div>
      <label class="synth-check">
        <input type="checkbox" id="chat-synth" checked />
        加综合总结
      </label>
      <span style="font-size:12px;color:var(--text-muted)">
        已选 <b id="chat-skill-count">26</b> 人
      </span>
    </div>

    <div class="chat-skills-row" id="chat-skills-row"></div>

    <div class="chat-input-row">
      <textarea class="chat-textarea" id="chat-input"
        placeholder="问一个问题，比如：我 28 岁月薪 8000 想辞职去北京做 AI，怎么办？"></textarea>
      <button class="chat-send" id="chat-send">发送 ↵</button>
    </div>

    <div class="chat-body" id="chat-body">
      <div class="chat-empty">输入一个问题，所有选中的人格会同时用各自的方式回答。</div>
    </div>
  </div>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modal">
  <div class="modal" onclick="event.stopPropagation()">
    <button class="modal-close" id="modal-close">×</button>
    <div id="modal-body"></div>
  </div>
</div>

<script>
const DATA = """

html += json.dumps(records, ensure_ascii=False)
html += ";\nconst IMAGES = "
html += json.dumps(embedded_images, ensure_ascii=False)
html += """;

const DIM_ORDER = ["S1","S2","S3","E1","E2","E3","A1","A2","A3","Ac1","Ac2","Ac3","So1","So2","So3"];
const DIM_NAMES = {
  S1: "自尊自信", S2: "自我清晰", S3: "核心价值",
  E1: "依恋安全", E2: "情感投入", E3: "边界依赖",
  A1: "世界观", A2: "规则灵活", A3: "意义感",
  Ac1: "动机导向", Ac2: "决策风格", Ac3: "执行模式",
  So1: "社交主动", So2: "人际边界", So3: "表达真实",
};

// state
let currentFilter = "all";
let currentSort = { key: "sim", dir: "desc" };
let currentSearch = "";

function filterData() {
  let rows = DATA.slice();
  if (currentFilter !== "all") {
    rows = rows.filter(r => r.v1_code === currentFilter);
  }
  if (currentSearch) {
    const q = currentSearch.toLowerCase();
    rows = rows.filter(r =>
      r.label.toLowerCase().includes(q) ||
      r.v1_code.toLowerCase().includes(q) ||
      r.v1_cn.includes(q) ||
      (r.source || "").toLowerCase().includes(q)
    );
  }
  rows.sort((a, b) => {
    const k = currentSort.key;
    let av, bv;
    switch (k) {
      case "rank": return 0;
      case "label": av = a.label; bv = b.label; break;
      case "code": av = a.v1_code; bv = b.v1_code; break;
      case "sim": av = a.v1_sim; bv = b.v1_sim; break;
      case "stable": av = a.stable ? 1 : 0; bv = b.stable ? 1 : 0; break;
      case "bytes": av = a.bytes; bv = b.bytes; break;
      case "family": av = a.template_family; bv = b.template_family; break;
      default: av = 0; bv = 0;
    }
    if (av < bv) return currentSort.dir === "asc" ? -1 : 1;
    if (av > bv) return currentSort.dir === "asc" ? 1 : -1;
    return 0;
  });
  return rows;
}

function formatBytes(n) {
  if (n >= 1024) return (n / 1024).toFixed(1) + " KB";
  return n + " B";
}

function renderTable() {
  const rows = filterData();
  const tbody = document.getElementById("tbody");
  const empty = document.getElementById("empty");
  if (rows.length === 0) {
    tbody.innerHTML = "";
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";
  tbody.innerHTML = rows.map((r, i) => `
    <tr data-key="${r.key}">
      <td class="rank">${i + 1}</td>
      <td class="name">${r.label}</td>
      <td><span class="code">${r.v1_code}</span><span class="cn">${r.v1_cn}</span></td>
      <td class="sim-wrap">
        <span class="sim-bar"><span class="sim-fill" style="width:${r.v1_sim}%"></span></span>
        <span class="sim-num">${r.v1_sim}%</span>
      </td>
      <td><span class="stable-badge ${r.stable ? 'yes' : 'no'}">${r.stable ? '✓ 锁定' : '⚠ ±' + r.swing}</span></td>
      <td class="size">${formatBytes(r.bytes)}</td>
      <td><span class="family">${r.template_family}</span></td>
    </tr>
  `).join("");
  // attach click
  tbody.querySelectorAll("tr").forEach(tr => {
    tr.addEventListener("click", () => {
      const key = tr.dataset.key;
      showModal(DATA.find(r => r.key === key));
    });
  });
}

function renderHeaderSort() {
  document.querySelectorAll("thead th").forEach(th => {
    th.classList.remove("sort-asc", "sort-desc");
    if (th.dataset.sort === currentSort.key) {
      th.classList.add(currentSort.dir === "asc" ? "sort-asc" : "sort-desc");
    }
  });
}

// sorting
document.querySelectorAll("thead th").forEach(th => {
  th.addEventListener("click", () => {
    const k = th.dataset.sort;
    if (currentSort.key === k) {
      currentSort.dir = currentSort.dir === "asc" ? "desc" : "asc";
    } else {
      currentSort.key = k;
      currentSort.dir = (k === "sim" || k === "bytes") ? "desc" : "asc";
    }
    renderHeaderSort();
    renderTable();
  });
});

// filters
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.code;
    renderTable();
  });
});

// search
document.getElementById("search").addEventListener("input", e => {
  currentSearch = e.target.value;
  renderTable();
});

// modal
function showModal(r) {
  const img = IMAGES[r.v1_code] || "";
  const body = document.getElementById("modal-body");
  body.innerHTML = `
    <div class="modal-head">
      <img class="modal-img" src="${img}" alt="${r.v1_code}" />
      <div>
        <div class="modal-title-small">${r.label}</div>
        <div class="modal-cn">${r.v1_cn || r.v1_code}</div>
        <div class="modal-en">${r.v1_code}</div>
        <div class="modal-intro">"${r.v1_intro}"</div>
        <div class="modal-sim">
          <div class="big-bar"><div class="big-bar-fill" style="width:${r.v1_sim}%"></div></div>
          <div class="big-sim">${r.v1_sim}%</div>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">3 轮扰动测试</div>
      <div class="variants-grid">
        ${r.variants.map((v, i) => `
          <div class="variant-card">
            <div class="variant-label">v${i+1} · sim ${v.sim}%</div>
            <div class="variant-code">${v.code} · ${v.cn}</div>
            <div class="variant-pattern">${v.pattern}</div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <div class="section-title">15 维 SBTI Pattern (v1)</div>
      <div class="dims-grid">
        ${DIM_ORDER.map(d => `
          <div class="dim">
            <div class="dim-name">${d} · ${DIM_NAMES[d]}</div>
            <div class="dim-val ${r.levels[d] || ''}">${r.levels[d] || '-'}<span style="font-size:10px;color:#999;font-weight:400"> (${r.raw_scores[d] || '-'})</span></div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <div class="section-title">Top 3 最近邻人格</div>
      <div class="top3">
        ${r.top3.map((t, i) => `
          <div class="item">
            <div class="item-rank">#${i+1}</div>
            <div class="item-code">${t.code}</div>
            <div class="item-cn">${t.cn}</div>
            <div class="item-sim">sim ${t.sim}% · exact ${t.exact}/15</div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <div class="section-title">SKILL.md 结构指标</div>
      <div class="metrics-grid">
        <div class="metric"><div class="metric-val">${formatBytes(r.bytes)}</div><div class="metric-label">大小</div></div>
        <div class="metric"><div class="metric-val">${r.lines}</div><div class="metric-label">行数</div></div>
        <div class="metric"><div class="metric-val">${r.section_count}</div><div class="metric-label">章节数</div></div>
        <div class="metric"><div class="metric-val">${r.completeness}/8</div><div class="metric-label">完整度</div></div>
        <div class="metric"><div class="metric-val">${r.mental_model_count}</div><div class="metric-label">心智模型</div></div>
        <div class="metric"><div class="metric-val">${r.heuristic_count}</div><div class="metric-label">启发式</div></div>
        <div class="metric"><div class="metric-val">${r.citation_count}</div><div class="metric-label">《》引用</div></div>
        <div class="metric"><div class="metric-val">${r.template_family}</div><div class="metric-label">模板</div></div>
      </div>
    </div>

    ${r.source ? `<div class="source-link">源仓库：<a href="https://github.com/${r.source}" target="_blank">github.com/${r.source}</a></div>` : ""}
  `;
  document.getElementById("modal").classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  document.getElementById("modal").classList.remove("open");
  document.body.style.overflow = "";
}
document.getElementById("modal").addEventListener("click", closeModal);
document.getElementById("modal-close").addEventListener("click", closeModal);
document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeModal();
});

// ========== Chat Panel ==========
const SKILL_TO_LABEL = {};
const SKILL_TO_CODE = {};
DATA.forEach(r => {
  SKILL_TO_LABEL[r.key] = r.label;
  SKILL_TO_CODE[r.key] = r.v1_code;
});

let selectedSkills = new Set(DATA.map(r => r.key));

function renderSkillChips() {
  const row = document.getElementById("chat-skills-row");
  const presets = [
    { label: "全选", action: "all" },
    { label: "清空", action: "none" },
    { label: "精选 6 人", action: "best6" },
    { label: "BOSS 们", action: "BOSS" },
    { label: "CTRL 们", action: "CTRL" },
  ];
  let html = presets.map(p =>
    `<button class="chat-skill-chip-preset" data-preset="${p.action}">${p.label}</button>`
  ).join("");
  html += DATA.map(r => `
    <span class="chat-skill-chip ${selectedSkills.has(r.key) ? 'on' : ''}" data-skill="${r.key}">
      ${r.label}
    </span>
  `).join("");
  row.innerHTML = html;
  row.querySelectorAll("[data-skill]").forEach(el => {
    el.addEventListener("click", () => {
      const k = el.dataset.skill;
      if (selectedSkills.has(k)) selectedSkills.delete(k);
      else selectedSkills.add(k);
      el.classList.toggle("on");
      updateSkillCount();
    });
  });
  row.querySelectorAll("[data-preset]").forEach(el => {
    el.addEventListener("click", () => {
      const a = el.dataset.preset;
      if (a === "all") selectedSkills = new Set(DATA.map(r => r.key));
      else if (a === "none") selectedSkills = new Set();
      else if (a === "best6") selectedSkills = new Set(["fengge","huchenfeng","zizek","taleb","dingyuanying","luoxiang"]);
      else if (a === "BOSS") selectedSkills = new Set(DATA.filter(r => r.v1_code === "BOSS").map(r => r.key));
      else if (a === "CTRL") selectedSkills = new Set(DATA.filter(r => r.v1_code === "CTRL").map(r => r.key));
      renderSkillChips();
      updateSkillCount();
    });
  });
}

function updateSkillCount() {
  document.getElementById("chat-skill-count").textContent = selectedSkills.size;
}

function openChat() {
  document.getElementById("chat-overlay").classList.add("open");
  document.body.style.overflow = "hidden";
  setTimeout(() => document.getElementById("chat-input").focus(), 100);
}
function closeChat() {
  document.getElementById("chat-overlay").classList.remove("open");
  document.body.style.overflow = "";
}
document.getElementById("fab").addEventListener("click", openChat);
document.getElementById("chat-close").addEventListener("click", closeChat);
document.getElementById("chat-overlay").addEventListener("click", closeChat);

document.getElementById("chat-input").addEventListener("keydown", e => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
    sendChat();
  }
});
document.getElementById("chat-send").addEventListener("click", sendChat);

let chatRunning = false;
async function sendChat() {
  if (chatRunning) return;
  const input = document.getElementById("chat-input");
  const question = input.value.trim();
  if (!question) return;
  if (selectedSkills.size === 0) { alert("先选至少 1 个人格"); return; }

  const model = document.getElementById("chat-model").value;
  const synth = document.getElementById("chat-synth").checked;
  const sendBtn = document.getElementById("chat-send");
  const body = document.getElementById("chat-body");

  chatRunning = true;
  sendBtn.disabled = true;
  sendBtn.textContent = "处理中...";
  body.innerHTML = `<div class="chat-status active" id="chat-status">⏳ 正在召唤 ${selectedSkills.size} 个人格...</div>`;

  let received = 0;
  const total = selectedSkills.size;
  const status = () => {
    const el = document.getElementById("chat-status");
    if (el) el.textContent = `⏳ 已回答 ${received}/${total}...`;
  };

  try {
    const resp = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question, model, synth,
        skills: [...selectedSkills],
      }),
    });
    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(err);
    }
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      // Parse SSE events
      let idx;
      while ((idx = buffer.indexOf("\\n\\n")) >= 0) {
        const chunk = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const lines = chunk.split("\\n");
        let event = "message", data = "";
        for (const line of lines) {
          if (line.startsWith("event: ")) event = line.slice(7);
          else if (line.startsWith("data: ")) data += line.slice(6);
        }
        if (!data) continue;
        let payload;
        try { payload = JSON.parse(data); } catch (e) { continue; }

        if (event === "answer") {
          received++;
          appendAnswer(payload);
          status();
        } else if (event === "synth_start") {
          const el = document.getElementById("chat-status");
          if (el) el.textContent = "🧩 综合总结中...";
        } else if (event === "synth") {
          appendSynth(payload.text);
        } else if (event === "done") {
          const el = document.getElementById("chat-status");
          if (el) {
            el.textContent = `✅ 完成 ${payload.count} 个回答`;
            el.classList.remove("active");
          }
        } else if (event === "error") {
          appendError(payload.message || "unknown error");
        }
      }
    }
  } catch (err) {
    appendError(err.message || String(err));
  } finally {
    chatRunning = false;
    sendBtn.disabled = false;
    sendBtn.textContent = "发送 ↵";
  }
}

function appendAnswer(payload) {
  const body = document.getElementById("chat-body");
  const skill = payload.skill;
  const label = SKILL_TO_LABEL[skill] || skill;
  const code = SKILL_TO_CODE[skill] || "—";
  const dur = payload.duration_s ? `${payload.duration_s}s` : "";
  const div = document.createElement("div");
  div.className = "chat-answer" + (payload.error ? " error" : "");
  if (payload.error) {
    div.innerHTML = `
      <div class="chat-answer-head">
        <div class="chat-answer-name">${label} <span class="chat-answer-sbti">${code}</span></div>
        <div class="chat-answer-meta">❌ ${dur}</div>
      </div>
      <div class="chat-answer-text" style="color:#c85050">${escapeHtml(payload.error)}</div>
    `;
  } else {
    div.innerHTML = `
      <div class="chat-answer-head">
        <div class="chat-answer-name">${label} <span class="chat-answer-sbti">${code}</span></div>
        <div class="chat-answer-meta">⏱ ${dur}</div>
      </div>
      <div class="chat-answer-text">${escapeHtml(payload.answer || "")}</div>
    `;
  }
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

function appendSynth(text) {
  const body = document.getElementById("chat-body");
  const div = document.createElement("div");
  div.className = "chat-synth";
  div.innerHTML = `
    <div class="chat-synth-title">🧩 综合总结</div>
    <div class="chat-synth-body">${escapeHtml(text || "")}</div>
  `;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

function appendError(msg) {
  const body = document.getElementById("chat-body");
  const div = document.createElement("div");
  div.className = "chat-answer error";
  div.innerHTML = `<div class="chat-answer-text" style="color:#c85050">⚠️ ${escapeHtml(msg)}</div>`;
  body.appendChild(div);
}

function escapeHtml(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

renderSkillChips();
updateSkillCount();

// init
renderHeaderSort();
renderTable();
</script>
</body>
</html>
"""

out = RESULTS / "dashboard.html"
out.write_text(html, encoding="utf-8")

print(f"[saved] {out}")
print(f"[size]  {out.stat().st_size / 1024:.1f} KB")
print(f"[open]  open {out}")
