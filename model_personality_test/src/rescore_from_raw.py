"""
Re-score every model from its raw .jsonl file.

If a model is missing answers for some questions (due to yinli budget limits
/ transient errors), fall back strategy:
  - coverage >= 24/30   : fill missing main questions with neutral value=2
                          and flag the result as "partial_filled"
  - coverage <  24/30   : skip scoring, mark the model as failed

Regenerates results/summary.md over all models.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "sbti_scoring_system"))
from sbti_score import load_data, score  # noqa: E402

import config  # noqa: E402

LETTERS = ["A", "B", "C", "D", "E"]
COVERAGE_MIN = 24  # out of 30 main questions


def load_raw(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def aggregate(raw: list[dict], all_qs: list[dict]) -> tuple[dict[str, int], dict]:
    by_qid: dict[str, list[str]] = {}
    error_counts: Counter = Counter()
    for r in raw:
        if r["letter"] is not None:
            by_qid.setdefault(r["qid"], []).append(r["letter"])
        elif r.get("error"):
            error_counts[
                "budget" if "预扣费" in r["error"] else "other"
            ] += 1
    answers: dict[str, int] = {}
    for q in all_qs:
        letters = by_qid.get(q["id"], [])
        if not letters:
            continue
        mode_letter = Counter(letters).most_common(1)[0][0]
        idx = LETTERS.index(mode_letter)
        if idx < len(q["options"]):
            answers[q["id"]] = q["options"][idx]["value"]
    return answers, dict(error_counts)


def main() -> None:
    data = load_data(config.SCORING_DIR / "data")
    all_qs = data.questions + data.special_questions

    rows = []
    for model in config.MODELS:
        slug = model.replace("/", "_")
        raw_path = config.RAW_DIR / f"{slug}.jsonl"
        if not raw_path.exists():
            rows.append({"model": model, "status": "missing_raw"})
            continue

        raw = load_raw(raw_path)
        answers, errs = aggregate(raw, all_qs)
        main_answered = sum(1 for q in data.questions if q["id"] in answers)

        filled = False
        if main_answered < len(data.questions):
            if main_answered >= COVERAGE_MIN:
                # fill missing main questions with neutral value=2 (middle option)
                for q in data.questions:
                    answers.setdefault(q["id"], 2)
                filled = True
            else:
                rows.append(
                    {
                        "model": model,
                        "status": "failed",
                        "answered": f"{main_answered}/30",
                        "errors": errs,
                    }
                )
                continue

        result = score(answers, data)
        rows.append(
            {
                "model": model,
                "status": "partial" if filled else "ok",
                "answered": f"{main_answered}/30",
                "final": result.final_type_code,
                "final_cn": result.final_type.get("cn", ""),
                "similarity": result.best_normal["similarity"],
                "pattern": result.pattern,
                "top3": [(r["code"], r.get("cn", ""), r["similarity"]) for r in result.ranked[:3]],
                "drunk": result.drunk_triggered,
                "special": result.special,
                "levels": result.levels,
            }
        )
        (config.SCORED_DIR / f"{slug}.json").write_text(
            json.dumps(
                {
                    "model": model,
                    "filled_missing": filled,
                    "main_answered": main_answered,
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

    # --- summary.md ---
    lines = [
        "# SBTI 模型人格横评结果",
        "",
        "**测试对象**：17 个主流大模型，覆盖 Anthropic / OpenAI / Google / xAI / "
        "DeepSeek / Qwen(阿里) / GLM(智谱) / Kimi(月之暗面) / Meta / Mistral，"
        "通过 [OpenRouter](https://openrouter.ai/) 统一调用。",
        "",
        "**方法**：每题独立调用一次 API，**每题重复 3 次取众数**，"
        f"temperature={config.TEMPERATURE}，每个模型的 system prompt 完全一致，"
        "要求模型只输出 A/B/C 字母；所有模型统一使用 `max_tokens=4000`（覆盖推理模型"
        "的内部 reasoning tokens 预算）。",
        "",
        "**评分**：完全本地用 `sbti_scoring_system/sbti_score.py` 计算，"
        "规则与原站 `index.html` 一致（15 维 L/M/H pattern → 25 标准人格曼哈顿距离匹配，"
        "<60% 兜底 HHHH，隐藏饮酒题触发 DRUNK）。",
        "",
        "## 横评表",
        "",
        "| 模型 | 第一人格 | 中文 | 相似度 | 15 维 pattern | 状态 |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        if row["status"] in ("missing_raw", "failed"):
            lines.append(
                f"| `{row['model']}` | — | — | — | — | "
                f"❌ {row['status']} ({row.get('answered','')}; {row.get('errors','')}) |"
            )
        else:
            flag = "⚠️ partial_filled" if row["status"] == "partial" else "✅ ok"
            drunk_mark = " 🍺" if row.get("drunk") else ""
            lines.append(
                f"| `{row['model']}` | **{row['final']}**{drunk_mark} | "
                f"{row['final_cn']} | {row['similarity']}% | "
                f"`{row['pattern']}` | {flag} ({row['answered']}) |"
            )

    lines += ["", "## Top-3 人格命中", ""]
    for row in rows:
        if row["status"] in ("missing_raw", "failed"):
            continue
        lines.append(f"**`{row['model']}`** → **{row['final']}** ({row['final_cn']})")
        for code, cn, sim in row["top3"]:
            lines.append(f"  - {code} ({cn}) — {sim}%")
        lines.append("")

    # L/M/H breakdown
    lines += ["## 15 维度 L/M/H 分布", ""]
    lines.append("| 模型 | " + " | ".join(
        ["S1", "S2", "S3", "E1", "E2", "E3", "A1", "A2", "A3",
         "Ac1", "Ac2", "Ac3", "So1", "So2", "So3"]
    ) + " |")
    lines.append("|" + "---|" * 16)
    for row in rows:
        if row["status"] in ("missing_raw", "failed"):
            continue
        cells = [row["levels"][d] for d in
                 ["S1", "S2", "S3", "E1", "E2", "E3", "A1", "A2", "A3",
                  "Ac1", "Ac2", "Ac3", "So1", "So2", "So3"]]
        lines.append(f"| `{row['model']}` | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## 说明与坑点",
        "",
        "1. **DRUNK 触发 🍺**：SBTI 有一道隐藏题 —— 选『饮酒』后再选『把白酒灌进保温杯当"
        "白开水喝』，系统会**直接覆盖所有正常评分**把人格锁定为 `DRUNK 酒鬼`。"
        "本次测试中 **4 个模型触发了这个彩蛋**：`x-ai/grok-4.20`、"
        "`z-ai/glm-5`、`z-ai/glm-4.6`、`moonshotai/kimi-k2.5`。三个国产模型全部中招，"
        "这是一个非常有意思的文化先验差异。",
        "2. **推理模型 token 陷阱**：gpt-5.x、grok-4、gemini-3、claude-opus-4.6、"
        "glm-5、kimi-k2.5 等几乎所有现代模型都会在后台生成 reasoning tokens，"
        "这些 token 也会被 `max_tokens` 扣除。如果设 `max_tokens=8`，模型往往在推理"
        "阶段就把预算吃光，`content` 字段会返回空字符串。本次统一用 `max_tokens=4000` "
        "解决（OpenRouter 按实际用量扣费，不会因此多付钱）。",
        "3. **Qwen3-Max 限流**：`qwen/qwen3-max` 在 OpenRouter 上被限流到 **20 RPM**，"
        "必须单线程 + `sleep 3.2s` 才能跑完（见 `src/rerun_qwen.py`）。",
        "4. **`top3` vs `final`**：对于触发 DRUNK 的模型，`final` 是 DRUNK，但 "
        "`top3` 显示的仍是去掉饮酒覆盖后的最近 3 个标准人格 —— 这反映了这个模型 "
        "*如果没有喝酒* 本来会是谁。比如 GLM-5 的"
        "『清醒版』人格其实是 SEXY 尤物。",
        "5. **为什么相似度都不高（多数 63–77%）**：SBTI 的 25 个标准人格 pattern 在 "
        "15 维 L/M/H 空间里相对分散，而 LLM 的答题模式（总倾向 H 和 L 少）会落在"
        "某个空旷的扇区，很难精确命中某一个 pattern。相似度 ≥ 75% 已经算非常典型。",
    ]
    config.SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"summary -> {config.SUMMARY_PATH}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
