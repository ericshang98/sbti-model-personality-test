"""
Run the SBTI test against every model in config.MODELS.

For each model:
  - ask all 30 main questions + 2 special (drink) questions
  - repeat each question RUNS_PER_QUESTION times
  - parse the model's letter choice (A/B/C)
  - take the mode across runs as the "final" answer for that question
  - map the letter back to the original option `value` (1/2/3 or similar)
  - score using sbti_scoring_system.sbti_score

Outputs:
  results/raw/<model>.jsonl     — every individual API call
  results/scored/<model>.json   — final answers + scoring result
  results/summary.md            — comparison table across all models
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "sbti_scoring_system"))
from sbti_score import load_data, score  # noqa: E402

import config  # noqa: E402

LETTERS = ["A", "B", "C", "D", "E"]


def format_user_prompt(q: dict) -> str:
    lines = [f"{LETTERS[i]}. {opt['label']}" for i, opt in enumerate(q["options"])]
    return config.USER_TEMPLATE.format(text=q["text"], options="\n".join(lines))


def parse_letter(text: str, n_options: int) -> str | None:
    if not text:
        return None
    # strict: first isolated A/B/C/D/E character
    m = re.search(r"[A-E]", text.upper())
    if m:
        letter = m.group(0)
        if LETTERS.index(letter) < n_options:
            return letter
    return None


async def ask_once(
    client: httpx.AsyncClient,
    model: str,
    q: dict,
    attempt: int = 0,
) -> dict:
    """One API call. Returns {letter, raw, error}."""
    # Many modern models (gpt-5.x, o-series, grok-4, gemini-3, glm-5, kimi-k2.5,
    # claude-opus-4.6, qwen thinking variants…) emit hidden reasoning tokens
    # that count against `max_tokens`. If max_tokens is too small, `content`
    # comes back empty. Since OpenRouter charges on *actual* usage (not on the
    # max_tokens ceiling), we just give every model 4000 tokens of headroom —
    # non-reasoning models still only emit ~1 output token for "A/B/C".
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": format_user_prompt(q)},
        ],
        "max_tokens": 4000,
        "temperature": config.TEMPERATURE,
    }

    try:
        headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json",
        }
        headers.update(getattr(config, "EXTRA_HEADERS", {}))
        r = await client.post(
            f"{config.BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        data = r.json()
        if r.status_code != 200 or "choices" not in data:
            err = data.get("error", {}).get("message", f"HTTP {r.status_code}")
            return {"letter": None, "raw": "", "error": err}
        msg = data["choices"][0]["message"]
        raw = msg.get("content") or ""
        letter = parse_letter(raw, len(q["options"]))
        # Fallback: some providers put the final token in `reasoning` if
        # max_tokens cut off mid-stream. Try to salvage a letter from there.
        if letter is None and msg.get("reasoning"):
            letter = parse_letter(msg["reasoning"], len(q["options"]))
        return {"letter": letter, "raw": raw, "error": None}
    except Exception as e:  # noqa: BLE001
        return {"letter": None, "raw": "", "error": f"{type(e).__name__}: {e}"}


async def ask_with_retry(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    model: str,
    q: dict,
    run_idx: int,
) -> dict:
    async with sem:
        for attempt in range(config.MAX_RETRIES):
            res = await ask_once(client, model, q, attempt)
            if res["letter"] is not None:
                return {
                    "model": model,
                    "qid": q["id"],
                    "run": run_idx,
                    "letter": res["letter"],
                    "raw": res["raw"],
                    "error": None,
                }
            if res["error"] and "channel" in (res["error"] or ""):
                # model unavailable — don't bother retrying
                break
            await asyncio.sleep(0.6 * (attempt + 1))
        return {
            "model": model,
            "qid": q["id"],
            "run": run_idx,
            "letter": None,
            "raw": res["raw"],
            "error": res["error"],
        }


async def run_for_model(
    client: httpx.AsyncClient,
    model: str,
    questions: list[dict],
    special_questions: list[dict],
) -> tuple[list[dict], dict]:
    """Returns (raw_records, {qid: mode_value})."""
    sem = asyncio.Semaphore(config.CONCURRENCY)
    all_qs = questions + special_questions
    tasks = [
        ask_with_retry(client, sem, model, q, run_idx)
        for q in all_qs
        for run_idx in range(config.RUNS_PER_QUESTION)
    ]
    raw: list[dict] = []
    t0 = time.time()
    done = 0
    total = len(tasks)
    for fut in asyncio.as_completed(tasks):
        rec = await fut
        raw.append(rec)
        done += 1
        if done % 20 == 0 or done == total:
            print(f"  [{model}] {done}/{total} done ({time.time()-t0:.1f}s)")
    # aggregate: for each qid pick the mode letter, then map letter -> value
    by_qid: dict[str, list[str]] = {}
    for r in raw:
        if r["letter"] is not None:
            by_qid.setdefault(r["qid"], []).append(r["letter"])
    answers: dict[str, int] = {}
    for q in all_qs:
        letters = by_qid.get(q["id"], [])
        if not letters:
            continue
        mode_letter = Counter(letters).most_common(1)[0][0]
        idx = LETTERS.index(mode_letter)
        if idx < len(q["options"]):
            answers[q["id"]] = q["options"][idx]["value"]
    return raw, answers


async def main() -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    config.SCORED_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data(config.SCORING_DIR / "data")

    summary_rows: list[dict] = []
    async with httpx.AsyncClient() as client:
        for model in config.MODELS:
            print(f"\n=== {model} ===")
            raw, answers = await run_for_model(
                client, model, data.questions, data.special_questions
            )
            raw_path = config.RAW_DIR / f"{model.replace('/', '_')}.jsonl"
            with raw_path.open("w", encoding="utf-8") as f:
                for r in raw:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")

            ok_main = sum(1 for q in data.questions if q["id"] in answers)
            if ok_main < len(data.questions):
                print(
                    f"  WARNING: only {ok_main}/{len(data.questions)} main questions answered"
                )
                summary_rows.append(
                    {
                        "model": model,
                        "final": "N/A",
                        "cn": "(失败)",
                        "similarity": 0,
                        "pattern": "",
                        "answered": f"{ok_main}/30",
                        "error": (raw[0]["error"] if raw else "no response"),
                    }
                )
                continue

            result = score(answers, data)
            scored_path = config.SCORED_DIR / f"{model.replace('/', '_')}.json"
            scored_path.write_text(
                json.dumps(
                    {
                        "model": model,
                        "answers": answers,
                        "raw_scores": result.raw_scores,
                        "levels": result.levels,
                        "pattern": result.pattern,
                        "final": result.final_type_code,
                        "final_cn": result.final_type.get("cn", ""),
                        "special": result.special,
                        "drunk_triggered": result.drunk_triggered,
                        "top3": [
                            {
                                "code": r["code"],
                                "cn": r.get("cn", ""),
                                "similarity": r["similarity"],
                                "exact": r["exact"],
                            }
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
            summary_rows.append(
                {
                    "model": model,
                    "final": result.final_type_code,
                    "cn": result.final_type.get("cn", ""),
                    "similarity": result.best_normal["similarity"],
                    "pattern": result.pattern,
                    "answered": f"{ok_main}/30",
                    "error": "",
                }
            )

    # write summary
    lines = [
        "# SBTI 模型人格横评结果",
        "",
        "每题独立调用 API，每题重复 "
        f"{config.RUNS_PER_QUESTION} 次取众数，temperature={config.TEMPERATURE}。",
        "",
        "| 模型 | 第一人格 | 中文 | 相似度 | 15 维 pattern | 答题数 |",
        "|---|---|---|---:|---|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| `{row['model']}` | **{row['final']}** | {row['cn']} | "
            f"{row['similarity']}% | `{row['pattern']}` | {row['answered']} |"
        )
    config.SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nsummary -> {config.SUMMARY_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
