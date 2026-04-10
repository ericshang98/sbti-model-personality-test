"""Qwen is rate-limited to 20 RPM on OpenRouter. Rerun it sequentially."""
import asyncio
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "sbti_scoring_system"))
from sbti_score import load_data, score  # noqa: E402

import config  # noqa: E402
from run_test import ask_with_retry  # noqa: E402


MODEL = "qwen/qwen3-max"


async def main() -> None:
    data = load_data(config.SCORING_DIR / "data")
    all_qs = data.questions + data.special_questions
    # Very tight concurrency + a floor delay — stay well under 20 RPM.
    sem = asyncio.Semaphore(1)
    raw = []
    async with httpx.AsyncClient() as client:
        for i, q in enumerate(all_qs):
            for run_idx in range(config.RUNS_PER_QUESTION):
                rec = await ask_with_retry(client, sem, MODEL, q, run_idx)
                raw.append(rec)
                if rec["letter"]:
                    print(f"  [{i + 1:2d}/{len(all_qs)}] {q['id']:15s} run{run_idx} -> {rec['letter']}")
                else:
                    print(f"  [{i + 1:2d}/{len(all_qs)}] {q['id']:15s} run{run_idx} -> ERR {str(rec.get('error'))[:80]}")
                await asyncio.sleep(3.2)  # ~18 RPM

    raw_path = config.RAW_DIR / "qwen_qwen3-max.jsonl"
    with raw_path.open("w", encoding="utf-8") as f:
        for r in raw:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # aggregate
    from collections import Counter
    from run_test import LETTERS

    by_qid: dict[str, list[str]] = {}
    for r in raw:
        if r["letter"]:
            by_qid.setdefault(r["qid"], []).append(r["letter"])
    answers: dict[str, int] = {}
    for q in all_qs:
        letters = by_qid.get(q["id"], [])
        if letters:
            mode = Counter(letters).most_common(1)[0][0]
            idx = LETTERS.index(mode)
            if idx < len(q["options"]):
                answers[q["id"]] = q["options"][idx]["value"]

    main_ok = sum(1 for q in data.questions if q["id"] in answers)
    print(f"\nanswered: {main_ok}/30")
    if main_ok < len(data.questions):
        return
    result = score(answers, data)
    (config.SCORED_DIR / "qwen_qwen3-max.json").write_text(
        json.dumps(
            {
                "model": MODEL,
                "answers": answers,
                "raw_scores": result.raw_scores,
                "levels": result.levels,
                "pattern": result.pattern,
                "final": result.final_type_code,
                "final_cn": result.final_type.get("cn", ""),
                "special": result.special,
                "drunk_triggered": result.drunk_triggered,
                "top3": [
                    {"code": r["code"], "cn": r.get("cn", ""),
                     "similarity": r["similarity"], "exact": r["exact"]}
                    for r in result.ranked[:3]
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"  -> {result.final_type_code} ({result.final_type.get('cn','')})"
        f"  pattern={result.pattern}  sim={result.best_normal['similarity']}%"
    )


if __name__ == "__main__":
    asyncio.run(main())
