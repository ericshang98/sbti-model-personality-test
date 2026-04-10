"""Re-run only the models that failed in the previous run."""
import asyncio
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "sbti_scoring_system"))
from sbti_score import load_data, score  # noqa: E402

import config  # noqa: E402
from run_test import run_for_model  # noqa: E402

FAILED = [
    "openai/gpt-4.1",
    "qwen/qwen3-max",
    "z-ai/glm-5",
    "z-ai/glm-4.6",
    "moonshotai/kimi-k2.5",
]


async def main() -> None:
    data = load_data(config.SCORING_DIR / "data")
    async with httpx.AsyncClient() as client:
        for model in FAILED:
            print(f"\n=== RERUN {model} ===")
            raw, answers = await run_for_model(
                client, model, data.questions, data.special_questions
            )
            raw_path = config.RAW_DIR / f"{model.replace('/', '_')}.jsonl"
            with raw_path.open("w", encoding="utf-8") as f:
                for r in raw:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            ok = sum(1 for q in data.questions if q["id"] in answers)
            print(f"  answered: {ok}/30")
            if ok < len(data.questions):
                # try to fill missing by picking any available letter
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
