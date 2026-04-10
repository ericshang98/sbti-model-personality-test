#!/usr/bin/env python3
"""
panel/analyze_skills.py — 对 .claude/skills/ 下所有 SKILL.md 做结构化分析

抽取每个 SKILL.md 的可量化指标：
  - 字节数 / 行数
  - frontmatter 是否合法（name, description, 触发词数）
  - 章节数、关键章节是否齐全
  - 核心模型数、决策启发式数
  - 资料来源数量
  - 是否有 agentic protocol（WebSearch 调用协议）
  - 是否有角色扮演规则、退出角色条款
  - 中英混用比例

然后交叉 `results/results.json`（SBTI 结果）做相关性分析。

输出：
  results/skill_structure.json   (机器可读)
  results/skill_analysis.md      (人类可读深度报告)
"""
from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path

ARENA_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ARENA_ROOT / ".claude" / "skills"
RESULTS_DIR = ARENA_ROOT / "results"


# ---------------------------------------------------------------------------
# Per-skill structural metrics
# ---------------------------------------------------------------------------

KEY_SECTIONS = [
    "身份卡",
    "核心心智模型", "核心心智模型", "核心模型", "心智模型",
    "表达DNA", "表达 DNA", "表达模型",
    "决策启发式",
    "价值观",
    "诚实边界", "边界",
    "角色扮演规则",
    "调研",
    "智识谱系",
]


@dataclass
class SkillMetrics:
    name: str
    source: str | None
    # size
    bytes: int
    lines: int
    # frontmatter
    frontmatter_ok: bool
    description_len: int
    trigger_words_count: int
    # structure
    section_count: int
    has_identity_card: bool       # 身份卡
    has_role_rules: bool          # 角色扮演规则
    has_expression_dna: bool      # 表达DNA
    has_values: bool              # 价值观
    has_honest_bounds: bool       # 诚实边界
    has_exit_clause: bool         # 退出角色条款
    has_agentic_protocol: bool    # agentic / WebSearch
    has_research_sources: bool    # 调研/一手来源
    # depth
    mental_model_count: int       # ### 模型N 或 ### N.
    heuristic_count: int          # 决策启发式条数
    citation_count: int           # 《...》 引用数
    english_quote_count: int      # > "..." 英文引用
    chinese_quote_count: int      # > 「...」或 > "..."
    # language
    chinese_ratio: float          # CJK 字符 / 总字符
    # classification
    template_family: str          # "alchaincyf" / "titanwings" / "other"


def read_skill_md(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Frontmatter treated loosely."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    header = text[3:end]
    body = text[end + 4:]
    fm: dict = {}
    key = None
    buf: list[str] = []
    for line in header.splitlines():
        m = re.match(r"^([a-zA-Z_][\w-]*)\s*:(.*)$", line)
        if m:
            if key is not None:
                fm[key] = "\n".join(buf).strip()
                buf = []
            key = m.group(1)
            val = m.group(2).strip()
            if val:
                buf.append(val)
        else:
            if line.strip():
                buf.append(line.strip())
    if key is not None:
        fm[key] = "\n".join(buf).strip()
    return fm, body


def count_sections(body: str) -> int:
    return len(re.findall(r"^#{1,3}\s", body, re.MULTILINE))


def has_section(body: str, needle: str) -> bool:
    return bool(re.search(r"^#{1,4}.*" + re.escape(needle), body, re.MULTILINE))


def count_mental_models(body: str) -> int:
    """Count lines like '### 模型N' / '### N. ...' / '### 核心模型N'."""
    patterns = [
        r"^#{2,4}\s*模型\s*[①②③④⑤⑥⑦⑧⑨⑩0-9]+",
        r"^#{2,4}\s*[0-9]+[\.．]\s",
        r"^#{2,4}\s*核心模型\s*[0-9]+",
        r"^#{2,4}\s*Model\s*[0-9]+",
    ]
    total = 0
    for p in patterns:
        total += len(re.findall(p, body, re.MULTILINE))
    # guard: crude heuristic, cap at 20
    return min(total, 20)


def count_heuristics(body: str) -> int:
    """Count decision heuristics items. Usually under '## 决策启发式' section."""
    m = re.search(r"#{1,3}\s*决策启发式.*?(?=^#{1,3}\s|\Z)", body,
                  re.MULTILINE | re.DOTALL)
    if not m:
        return 0
    sect = m.group(0)
    items = re.findall(r"^[0-9]+[\.．]\s|^#{3,4}\s*[0-9]+", sect, re.MULTILINE)
    return len(items)


def count_citations(body: str) -> int:
    return len(re.findall(r"《[^》]{1,30}》", body))


def count_english_quotes(body: str) -> int:
    return len(re.findall(r'^\s*>\s*["“][^"”\n]{10,}["”]', body, re.MULTILINE))


def count_chinese_quotes(body: str) -> int:
    return len(re.findall(r'^\s*>\s*「[^」\n]{4,}」', body, re.MULTILINE))


def chinese_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return round(cjk / max(len(text), 1), 3)


def detect_template_family(name: str, source: str | None, body: str) -> str:
    if source:
        if "alchaincyf" in source:
            return "alchaincyf"
        if "titanwings" in source:
            return "titanwings"
    # fallback: structural sniff
    if "思维操作系统" in body and "核心心智模型" in body:
        return "alchaincyf-like"
    return "other"


def analyze_one(name: str, skill_md: Path, source_hint: dict) -> SkillMetrics:
    text = read_skill_md(skill_md)
    fm, body = parse_frontmatter(text)
    desc = fm.get("description", "")
    trigger_words = re.findall(r"「[^」]{2,20}」", desc) + re.findall(
        r"『[^』]{2,20}』", desc
    )
    return SkillMetrics(
        name=name,
        source=source_hint.get(name),
        bytes=len(text.encode("utf-8")),
        lines=text.count("\n") + 1,
        frontmatter_ok=("name" in fm and "description" in fm),
        description_len=len(desc),
        trigger_words_count=len(trigger_words),
        section_count=count_sections(body),
        has_identity_card=has_section(body, "身份卡"),
        has_role_rules=has_section(body, "角色扮演规则"),
        has_expression_dna=("表达DNA" in body) or ("表达 DNA" in body),
        has_values=has_section(body, "价值观"),
        has_honest_bounds=("诚实边界" in body) or has_section(body, "边界"),
        has_exit_clause=("退出角色" in body) or ("切回正常" in body),
        has_agentic_protocol=("Agentic" in body) or ("WebSearch" in body)
                             or ("回答工作流" in body),
        has_research_sources=("调研" in body) or ("一手来源" in body)
                              or ("资料" in body),
        mental_model_count=count_mental_models(body),
        heuristic_count=count_heuristics(body),
        citation_count=count_citations(body),
        english_quote_count=count_english_quotes(body),
        chinese_quote_count=count_chinese_quotes(body),
        chinese_ratio=chinese_ratio(text),
        template_family=detect_template_family(name, source_hint.get(name), body),
    )


# ---------------------------------------------------------------------------
# Cross-analysis with SBTI results
# ---------------------------------------------------------------------------

def load_sbti_sources() -> dict[str, str]:
    """Get per-skill source repo from run_sbti.py's personas."""
    # We can look at results.json — it stores the label+source per persona key
    rpath = RESULTS_DIR / "results.json"
    if not rpath.exists():
        return {}
    d = json.loads(rpath.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    # keys in results.json are the run_sbti persona keys, which may differ
    # from .claude/skills folder names. We map by known aliases:
    alias = {
        "fengge": "fengge", "huchenfeng": "huchenfeng",
        "zhangxuefeng": "zhangxuefeng", "guodegang": "guodegang",
        "musk": "musk", "munger": "munger", "trump": "trump",
        "jobs": "jobs", "naval": "naval", "taleb": "taleb",
        "buffett": "buffett", "zhangyiming": "zhangyiming",
        "tongjincheng": "tongjincheng", "feynman": "feynman",
        "pg": "pg", "maoxuan": "maoxuan", "karpathy": "karpathy",
    }
    for key, p in d.get("personas", {}).items():
        fname = alias.get(key, key)
        mapping[fname] = p.get("source", "")
    return mapping


def load_sbti_results() -> dict:
    return json.loads((RESULTS_DIR / "results.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_structure_json(metrics: list[SkillMetrics]):
    out = RESULTS_DIR / "skill_structure.json"
    out.write_text(
        json.dumps([asdict(m) for m in metrics], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[saved] {out}")


def section_presence_symbol(present: bool) -> str:
    return "✅" if present else "—"


def render_report(metrics: list[SkillMetrics], sbti: dict):
    personas = sbti.get("personas", {})
    alias_to_key = {
        "pg": "pg", "maoxuan": "maoxuan", "karpathy": "karpathy",
    }
    # build merged rows
    rows = []
    for m in metrics:
        key = m.name  # .claude/skills folder == run_sbti key for our installs
        p = personas.get(key, {})
        v1 = p.get("runs", [{}])[0] if p.get("runs") else {}
        rows.append({
            "metrics": m,
            "label": p.get("label", m.name),
            "v1_code": v1.get("final_code", "—"),
            "v1_cn": v1.get("final_cn", ""),
            "v1_sim": v1.get("best_similarity", 0),
            "stable": p.get("stability", {}).get("code_stable", None),
            "swing": p.get("stability", {}).get("similarity_swing", None),
        })

    lines: list[str] = []
    lines.append(f"# Skill 结构分析 × SBTI 结果 · {len(metrics)} Skill 深度报告\n\n")
    lines.append(
        f"**数据来源**：`.claude/skills/` 下 {len(metrics)} 个 SKILL.md "
        f"+ `results/results.json`（每 persona 3 轮 SBTI 扰动测试）\n\n"
    )

    # ---------- Section 1: overview table ----------
    lines.append("## 一、总览表（按 SKILL.md 大小排序）\n\n")
    lines.append(
        "| Skill | 字节 | 行 | 章 | 模型 | 启发式 | 引用《》 | SBTI | 相似度 | 稳定 |\n"
    )
    lines.append(
        "|---|---:|---:|---:|---:|---:|---:|:-:|---:|:-:|\n"
    )
    rows_sorted = sorted(rows, key=lambda r: -r["metrics"].bytes)
    for r in rows_sorted:
        m = r["metrics"]
        stable = "✅" if r["stable"] else ("⚠️" if r["stable"] is False else "—")
        lines.append(
            f"| {r['label']} | {m.bytes} | {m.lines} | {m.section_count} "
            f"| {m.mental_model_count} | {m.heuristic_count} | {m.citation_count} "
            f"| `{r['v1_code']}` | {r['v1_sim']}% | {stable} |\n"
        )
    lines.append("\n")

    # ---------- Section 2: section completeness matrix ----------
    lines.append("## 二、关键章节完整度矩阵\n\n")
    lines.append("SKILL.md 的 6 个关键章节是判断一个 skill 是否"
                 "**production-ready** 的基础指标。\n\n")
    lines.append(
        "| Skill | 身份卡 | 角色规则 | 表达DNA | 价值观 | 诚实边界 | 退出条款 | Agentic | 研究源 | **得分** |\n"
    )
    lines.append(
        "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---:|\n"
    )
    def score(m: SkillMetrics) -> int:
        return sum([
            m.has_identity_card, m.has_role_rules, m.has_expression_dna,
            m.has_values, m.has_honest_bounds, m.has_exit_clause,
            m.has_agentic_protocol, m.has_research_sources,
        ])
    rows_by_score = sorted(rows, key=lambda r: -score(r["metrics"]))
    for r in rows_by_score:
        m = r["metrics"]
        s = score(m)
        lines.append(
            f"| {r['label']} "
            f"| {section_presence_symbol(m.has_identity_card)} "
            f"| {section_presence_symbol(m.has_role_rules)} "
            f"| {section_presence_symbol(m.has_expression_dna)} "
            f"| {section_presence_symbol(m.has_values)} "
            f"| {section_presence_symbol(m.has_honest_bounds)} "
            f"| {section_presence_symbol(m.has_exit_clause)} "
            f"| {section_presence_symbol(m.has_agentic_protocol)} "
            f"| {section_presence_symbol(m.has_research_sources)} "
            f"| **{s}/8** |\n"
        )
    lines.append("\n")

    # ---------- Section 3: template family ----------
    lines.append("## 三、模板家族\n\n")
    fam: dict[str, list] = {}
    for r in rows:
        fam.setdefault(r["metrics"].template_family, []).append(r["label"])
    for f, names in sorted(fam.items(), key=lambda x: -len(x[1])):
        lines.append(f"- **{f}**（{len(names)} 个）：{', '.join(names)}\n")
    lines.append("\n")

    # ---------- Section 4: Correlation ----------
    lines.append("## 四、结构 × SBTI 相关性\n\n")

    # correlation: bytes vs v1_sim
    bytes_list = [r["metrics"].bytes for r in rows]
    sim_list = [r["v1_sim"] for r in rows]
    model_list = [r["metrics"].mental_model_count for r in rows]
    score_list = [score(r["metrics"]) for r in rows]

    def pearson(xs, ys):
        if len(xs) < 2:
            return 0.0
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den_x = (sum((x - mean_x) ** 2 for x in xs)) ** 0.5
        den_y = (sum((y - mean_y) ** 2 for y in ys)) ** 0.5
        if den_x == 0 or den_y == 0:
            return 0.0
        return round(num / (den_x * den_y), 3)

    corr_bytes_sim = pearson(bytes_list, sim_list)
    corr_models_sim = pearson(model_list, sim_list)
    corr_score_sim = pearson(score_list, sim_list)

    lines.append(f"- **SKILL.md 字节数 vs SBTI v1 相似度**：ρ = **{corr_bytes_sim}**\n")
    lines.append(f"- **核心模型数 vs SBTI v1 相似度**：ρ = **{corr_models_sim}**\n")
    lines.append(f"- **章节完整度得分 vs SBTI v1 相似度**：ρ = **{corr_score_sim}**\n\n")

    mean_sim = round(statistics.mean(sim_list), 1)
    median_sim = round(statistics.median(sim_list), 1)
    lines.append(f"- **全体相似度均值**：{mean_sim}% · **中位数**：{median_sim}%\n\n")

    # ---------- Section 5: outliers / notable skills ----------
    lines.append("## 五、异类观察\n\n")
    # biggest / smallest
    biggest = max(rows, key=lambda r: r["metrics"].bytes)
    smallest = min(rows, key=lambda r: r["metrics"].bytes)
    lines.append(f"- 📏 **最大 SKILL.md**：{biggest['label']} ({biggest['metrics'].bytes} bytes, "
                 f"{biggest['metrics'].lines} 行)\n")
    lines.append(f"- 📏 **最小 SKILL.md**：{smallest['label']} ({smallest['metrics'].bytes} bytes, "
                 f"{smallest['metrics'].lines} 行)\n")
    # most models
    most_models = max(rows, key=lambda r: r["metrics"].mental_model_count)
    lines.append(f"- 🧠 **模型最多**：{most_models['label']} "
                 f"({most_models['metrics'].mental_model_count} 个心智模型)\n")
    # most citations
    most_cite = max(rows, key=lambda r: r["metrics"].citation_count)
    lines.append(f"- 📚 **引用《》最多**：{most_cite['label']} "
                 f"({most_cite['metrics'].citation_count} 处)\n")
    # highest similarity
    top_sim = max(rows, key=lambda r: r["v1_sim"])
    lines.append(f"- 🥇 **SBTI 相似度最高**：{top_sim['label']} `{top_sim['v1_code']}` "
                 f"({top_sim['v1_sim']}%)\n")
    # lowest similarity
    low_sim = min(rows, key=lambda r: r["v1_sim"])
    lines.append(f"- 🚨 **SBTI 相似度最低**：{low_sim['label']} `{low_sim['v1_code']}` "
                 f"({low_sim['v1_sim']}%)\n")
    lines.append("\n")

    # ---------- Section 6: SBTI cluster summary ----------
    lines.append("## 六、SBTI 人格落点分布\n\n")
    code_to_label: dict[str, list[str]] = {}
    for r in rows:
        code_to_label.setdefault(r["v1_code"], []).append(f"{r['label']} ({r['v1_sim']}%)")
    for code in sorted(code_to_label.keys(), key=lambda c: -len(code_to_label[c])):
        items = code_to_label[code]
        cn = ""
        # try to pull cn from any row with this code
        for r in rows:
            if r["v1_code"] == code:
                cn = r["v1_cn"]; break
        lines.append(f"- **`{code}` {cn}**（{len(items)}）：{', '.join(items)}\n")
    lines.append("\n")

    # Save
    out = RESULTS_DIR / "skill_analysis.md"
    out.write_text("".join(lines), encoding="utf-8")
    print(f"[saved] {out}")


# ---------------------------------------------------------------------------

def main():
    source_hint = load_sbti_sources()

    metrics: list[SkillMetrics] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        m = analyze_one(entry.name, skill_md, source_hint)
        metrics.append(m)

    write_structure_json(metrics)

    sbti = load_sbti_results()
    render_report(metrics, sbti)

    print(f"\nAnalyzed {len(metrics)} skills.")


if __name__ == "__main__":
    main()
