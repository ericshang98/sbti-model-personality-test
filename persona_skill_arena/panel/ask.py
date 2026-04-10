#!/usr/bin/env python3
"""
panel/ask.py — 一题多答工具

把一个问题同时扔给 `.claude/skills/` 下所有已安装的人格 skill，
每个 skill 用它自己的 SKILL.md 作为 system prompt，并行调用
`claude -p` 产出一段 in-character 回答。最后把所有回答存到
`results/panels/panel-{timestamp}.{json,md}`。

用法：
    python panel/ask.py "我该不该辞职去北京做 AI"
    python panel/ask.py --only fengge,musk,munger "..."
    python panel/ask.py --skip trump "..."
    python panel/ask.py --list
    python panel/ask.py --synth "..."          # 额外跑一轮综合总结
    python panel/ask.py --model sonnet "..."   # 更便宜的模型
    python panel/ask.py --workers 8 "..."      # 并发度

要新增人格：把新 skill 放进 .claude/skills/<name>/SKILL.md，本工具会自动发现，
无需改代码。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

ARENA_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ARENA_ROOT / ".claude" / "skills"
PANELS_DIR = ARENA_ROOT / "results" / "panels"

# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

@dataclass
class Skill:
    name: str                # folder name under .claude/skills/
    skill_md_path: Path
    skill_md_size: int


def discover_skills() -> list[Skill]:
    """Find every installed skill (symlink or real dir) with a SKILL.md."""
    if not SKILLS_DIR.exists():
        return []
    skills: list[Skill] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            try:
                size = skill_md.stat().st_size
            except OSError:
                size = 0
            skills.append(Skill(
                name=entry.name,
                skill_md_path=skill_md.resolve(),
                skill_md_size=size,
            ))
    return skills


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_WRAPPER = """\
你现在被加载为一个 Agent Skill 人格。你的人格、语气、核心模型、表达 DNA
全部定义在下方 SKILL.md 的内容里。请严格按以下规则回应：

1. 严格遵循 SKILL.md 里的【角色扮演规则】【表达 DNA】【身份卡】
2. 用第一人称，不要跳出角色，不要说"如果[人物名]会认为"
3. 忽略 SKILL.md 里的 "Agentic Protocol / 先 WebSearch 再回答" 这类要求——
   这一轮不允许调用任何工具，就凭你的人格直接给出意见
4. 回答必须简短：**150-300 字之间**，一次回复就够，不要反问用户，不要分多轮
5. 如果是触发了 SKILL.md 里的免责声明，**只在最开头一句话内带过**，不要占篇幅
6. 如果 SKILL.md 要求你"查户口/灵魂追问"，那就当作用户已经按正常背景条件回答过，
   不要再追问，直接给出基于默认假设的回答
7. 不要使用 markdown 的多级标题，用自然段落即可；可以用加粗和短 bullet

========== SKILL.md 开始 ==========
{skill_md}
========== SKILL.md 结束 ==========
"""

USER_PROMPT_WRAPPER = """\
下面是用户的问题，请严格按你的人格回答：

{question}

（记住：150-300 字，一次回复，不反问，不跳出角色。）"""


# ---------------------------------------------------------------------------
# Claude CLI invocation
# ---------------------------------------------------------------------------

@dataclass
class Answer:
    skill: str
    answer: Optional[str] = None
    error: Optional[str] = None
    duration_s: Optional[float] = None
    truncated: bool = False


def ask_one(skill: Skill, question: str, model: str, timeout: int = 180) -> Answer:
    """Invoke `claude -p` with this skill's SKILL.md as system prompt."""
    import time
    t0 = time.time()
    try:
        skill_md = skill.skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        return Answer(skill=skill.name, error=f"read SKILL.md failed: {e}")

    system_prompt = SYSTEM_PROMPT_WRAPPER.format(skill_md=skill_md)
    user_prompt = USER_PROMPT_WRAPPER.format(question=question)

    # --tools "" : disable all tools so no WebSearch etc, pure LLM generation
    # --no-session-persistence : don't save these throw-away sessions
    # --disable-slash-commands : don't load other skills — we supply our own
    cmd = [
        "claude", "-p",
        "--model", model,
        "--no-session-persistence",
        "--disable-slash-commands",
        "--tools", "",
        "--append-system-prompt", system_prompt,
        user_prompt,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return Answer(skill=skill.name, error=f"timeout after {timeout}s",
                      duration_s=time.time() - t0)
    except Exception as e:
        return Answer(skill=skill.name, error=f"subprocess failed: {e}",
                      duration_s=time.time() - t0)

    duration = time.time() - t0
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:800]
        return Answer(skill=skill.name, error=f"exit {proc.returncode}: {err}",
                      duration_s=duration)

    out = proc.stdout.strip()
    if not out:
        return Answer(skill=skill.name, error="empty response",
                      duration_s=duration)

    return Answer(skill=skill.name, answer=out, duration_s=duration)


def ask_all(
    question: str,
    skills: list[Skill],
    model: str,
    workers: int,
    timeout: int = 180,
) -> list[Answer]:
    results: list[Answer] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(ask_one, s, question, model, timeout): s for s in skills}
        done = 0
        total = len(skills)
        for fut in as_completed(futures):
            done += 1
            r = fut.result()
            tag = "OK  " if r.answer else "ERR "
            t = f"{r.duration_s:.1f}s" if r.duration_s else ""
            print(f"  [{done}/{total}] {tag} {r.skill:20s} {t}", file=sys.stderr)
            results.append(r)
    # restore discovery order
    order = {s.name: i for i, s in enumerate(skills)}
    results.sort(key=lambda a: order.get(a.skill, 9999))
    return results


# ---------------------------------------------------------------------------
# Optional synthesis round
# ---------------------------------------------------------------------------

SYNTH_PROMPT = """\
下面是 {n} 个不同思维流派的人物，就同一个问题给出的短回答。
请你作为中立的分析者，做一份"圆桌纪要"：

## 问题
{question}

## 每个人的回答
{answers_block}

---

请输出以下 4 个部分：

**① 共识（大多数人同意的）**
找出至少 60% 的人都提到或隐含同意的点，列 2-4 条。

**② 分歧（立场最对立的 2 组）**
找出哪两个人立场最冲突，各用一句话描述他们的核心主张。

**③ 被忽略的维度**
所有人都没有充分讨论、但对这个问题其实很重要的角度，列 1-3 个。

**④ 给提问者的一句话建议**
基于以上共识和分歧，用 1-2 句话直接给提问者一个可执行的建议。

语气冷静、简洁、不抒情。总长控制在 400-600 字。
"""


def synthesize(question: str, answers: list[Answer], model: str,
               timeout: int = 180) -> Optional[str]:
    ok = [a for a in answers if a.answer]
    if len(ok) < 2:
        return None
    block = "\n\n".join(
        f"【{a.skill}】\n{a.answer}" for a in ok
    )
    prompt = SYNTH_PROMPT.format(
        n=len(ok),
        question=question,
        answers_block=block,
    )
    # Prompt can be very long (14 persona answers concatenated) — pipe via stdin
    cmd = [
        "claude", "-p",
        "--model", model,
        "--no-session-persistence",
        "--disable-slash-commands",
        "--tools", "",
    ]
    try:
        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True, timeout=timeout
        )
        if proc.returncode != 0:
            return f"[synth error: {proc.stderr.strip()[:300]}]"
        return proc.stdout.strip()
    except Exception as e:
        return f"[synth exception: {e}]"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_panel(question: str, answers: list[Answer], model: str,
               synth: Optional[str]) -> tuple[Path, Path]:
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = PANELS_DIR / f"panel-{ts}"

    json_path = base.with_suffix(".json")
    payload = {
        "timestamp": ts,
        "question": question,
        "model": model,
        "skills_count": len(answers),
        "answers": [asdict(a) for a in answers],
        "synthesis": synth,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    md_path = base.with_suffix(".md")
    lines: list[str] = []
    lines.append(f"# 人格圆桌 · {ts}\n\n")
    lines.append(f"**模型**: `{model}`  |  **人格数**: {len(answers)}\n\n")
    lines.append("## 问题\n\n")
    lines.append(f"> {question}\n\n")
    lines.append("## 回答\n\n")
    for a in answers:
        lines.append(f"### {a.skill}\n\n")
        if a.error:
            lines.append(f"❌ `{a.error}`\n\n")
        else:
            lines.append(f"{a.answer}\n\n")
        if a.duration_s is not None:
            lines.append(f"<sub>⏱ {a.duration_s:.1f}s</sub>\n\n")
        lines.append("---\n\n")
    if synth:
        lines.append("## 综合总结\n\n")
        lines.append(synth)
        lines.append("\n")
    md_path.write_text("".join(lines), encoding="utf-8")
    return json_path, md_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="panel.ask",
        description="Ask a question to every installed persona skill in parallel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("question", nargs="*",
                   help="the question (or pipe via stdin if omitted)")
    p.add_argument("--list", action="store_true",
                   help="list discovered skills and exit")
    p.add_argument("--only", default="",
                   help="comma-sep list of skill names to include (default: all)")
    p.add_argument("--skip", default="",
                   help="comma-sep list of skill names to exclude")
    p.add_argument("--model", default="claude-opus-4-6",
                   help="model alias (opus/sonnet/haiku) or full id "
                        "(default: claude-opus-4-6)")
    p.add_argument("--workers", type=int, default=6,
                   help="parallelism (default: 6)")
    p.add_argument("--timeout", type=int, default=180,
                   help="per-skill timeout in seconds (default: 180)")
    p.add_argument("--synth", action="store_true",
                   help="also run a synthesis round after collecting answers")
    p.add_argument("--no-save", action="store_true",
                   help="don't write results to disk")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    skills = discover_skills()
    if not skills:
        print(f"❌ no skills found in {SKILLS_DIR}", file=sys.stderr)
        return 2

    if args.list:
        print(f"Installed skills ({len(skills)}):")
        for s in skills:
            print(f"  {s.name:20s}  ({s.skill_md_size} bytes)")
        return 0

    # Apply --only / --skip filters
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    skip = {x.strip() for x in args.skip.split(",") if x.strip()}
    if only:
        skills = [s for s in skills if s.name in only]
    if skip:
        skills = [s for s in skills if s.name not in skip]
    if not skills:
        print("❌ no skills left after --only/--skip filter", file=sys.stderr)
        return 2

    # Get question
    if args.question:
        question = " ".join(args.question)
    else:
        if sys.stdin.isatty():
            print("❌ no question (pass as argument or pipe via stdin)", file=sys.stderr)
            return 2
        question = sys.stdin.read().strip()
    if not question:
        print("❌ empty question", file=sys.stderr)
        return 2

    print(f"\n📋 Question: {question}", file=sys.stderr)
    print(f"🎭 Skills ({len(skills)}): {', '.join(s.name for s in skills)}", file=sys.stderr)
    print(f"🤖 Model: {args.model}  |  ⚙️  workers: {args.workers}\n", file=sys.stderr)

    answers = ask_all(question, skills, args.model, args.workers, args.timeout)

    synth: Optional[str] = None
    if args.synth:
        print("\n🧩 synthesizing...", file=sys.stderr)
        synth = synthesize(question, answers, args.model, args.timeout)

    if not args.no_save:
        json_path, md_path = save_panel(question, answers, args.model, synth)
        print(f"\n✅ {md_path.relative_to(ARENA_ROOT)}", file=sys.stderr)
        print(f"✅ {json_path.relative_to(ARENA_ROOT)}", file=sys.stderr)

    # Also print to stdout for piping
    print()
    print("=" * 78)
    print(f"  Q: {question}")
    print("=" * 78)
    for a in answers:
        print(f"\n── {a.skill} ──")
        if a.error:
            print(f"  ❌ {a.error}")
        else:
            print(a.answer)
    if synth:
        print("\n" + "=" * 78)
        print("  SYNTHESIS")
        print("=" * 78)
        print(synth)

    failures = sum(1 for a in answers if a.error)
    return 1 if failures and failures == len(answers) else 0


if __name__ == "__main__":
    raise SystemExit(main())
