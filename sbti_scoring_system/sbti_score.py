"""
SBTI scoring library — a clean Python port of the original JavaScript scoring
logic found in UnluckyNinja/SBTI-test/index.html (SBTI 人格测试, by B站
@蛆肉儿串儿).

Public API:
    load_data(data_dir)                  -> SBTIData
    score(answers, data)                 -> SBTIResult

Where `answers` is a dict {question_id: chosen_value} mapping each main
question id (q1..q30) to its chosen option *value* (1, 2, or 3). Optional
keys `drink_gate_q1` and `drink_gate_q2` control the hidden DRUNK branch:
if `drink_gate_q2` == 2, DRUNK is forced regardless of everything else.

The scoring rule, verbatim from the original:
  * each of 15 dimensions has 2 questions, each contributing 1/2/3 points
  * dimension sum s:  s <= 3 -> "L" ; s == 4 -> "M" ; s >= 5 -> "H"
  * build a 15-element level vector in fixed dimensionOrder
  * Manhattan distance to each of 25 NORMAL_TYPES patterns
  * similarity = max(0, round((1 - distance/30) * 100))
  * if similarity < 60       -> fallback HHHH ("傻乐者")
  * if drink_gate_q2 == 2    -> override DRUNK ("酒鬼")
  * else                     -> best normal match
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DIMENSION_ORDER: list[str] = [
    "S1", "S2", "S3",
    "E1", "E2", "E3",
    "A1", "A2", "A3",
    "Ac1", "Ac2", "Ac3",
    "So1", "So2", "So3",
]
DRUNK_TRIGGER_QID = "drink_gate_q2"
DRUNK_TRIGGER_VALUE = 2  # chosen value that forces DRUNK
HHHH_SIMILARITY_THRESHOLD = 60


@dataclass
class SBTIData:
    questions: list[dict[str, Any]]
    special_questions: list[dict[str, Any]]
    dimensions: dict[str, dict[str, str]]
    patterns: list[dict[str, str]]
    types: dict[str, dict[str, str]]
    dim_explanations: dict[str, dict[str, str]]


@dataclass
class SBTIResult:
    raw_scores: dict[str, int]
    levels: dict[str, str]           # dim -> "L"/"M"/"H"
    pattern: str                      # e.g. "HHH-HMH-MHH-HHH-MHM"
    ranked: list[dict[str, Any]]      # 25 normal types, best-first
    best_normal: dict[str, Any]
    final_type_code: str              # including possible DRUNK/HHHH override
    final_type: dict[str, Any]
    special: bool                     # True if override (DRUNK or HHHH)
    drunk_triggered: bool


def load_data(data_dir: str | Path | None = None) -> SBTIData:
    base = Path(data_dir) if data_dir else Path(__file__).parent / "data"

    def _load(name: str) -> Any:
        return json.loads((base / name).read_text(encoding="utf-8"))

    return SBTIData(
        questions=_load("questions.json"),
        special_questions=_load("special_questions.json"),
        dimensions=_load("dimensions.json"),
        patterns=_load("patterns.json"),
        types=_load("types.json"),
        dim_explanations=_load("dim_explanations.json"),
    )


def _sum_to_level(score: int) -> str:
    if score <= 3:
        return "L"
    if score == 4:
        return "M"
    return "H"


def _level_num(level: str) -> int:
    return {"L": 1, "M": 2, "H": 3}[level]


def _parse_pattern(pattern: str) -> list[str]:
    return list(pattern.replace("-", ""))


def score(answers: dict[str, int], data: SBTIData) -> SBTIResult:
    # 1. sum dimension scores
    raw_scores: dict[str, int] = {d: 0 for d in data.dimensions}
    for q in data.questions:
        val = answers.get(q["id"])
        if val is None:
            raise ValueError(f"missing answer for {q['id']}")
        raw_scores[q["dim"]] += int(val)

    # 2. bucket to L/M/H
    levels = {d: _sum_to_level(s) for d, s in raw_scores.items()}

    # 3. build user vector & rank
    user_vec = [_level_num(levels[d]) for d in DIMENSION_ORDER]
    ranked: list[dict[str, Any]] = []
    for entry in data.patterns:
        vec = [_level_num(l) for l in _parse_pattern(entry["pattern"])]
        distance = sum(abs(a - b) for a, b in zip(user_vec, vec))
        exact = sum(1 for a, b in zip(user_vec, vec) if a == b)
        similarity = max(0, round((1 - distance / 30) * 100))
        ranked.append(
            {
                "code": entry["code"],
                "pattern": entry["pattern"],
                "distance": distance,
                "exact": exact,
                "similarity": similarity,
                **data.types.get(entry["code"], {}),
            }
        )
    ranked.sort(
        key=lambda r: (r["distance"], -r["exact"], -r["similarity"])
    )
    best = ranked[0]

    # 4. overrides: DRUNK (highest priority) > HHHH fallback
    drunk_triggered = answers.get(DRUNK_TRIGGER_QID) == DRUNK_TRIGGER_VALUE
    if drunk_triggered:
        final_code = "DRUNK"
        special = True
    elif best["similarity"] < HHHH_SIMILARITY_THRESHOLD:
        final_code = "HHHH"
        special = True
    else:
        final_code = best["code"]
        special = False
    final_type = {"code": final_code, **data.types.get(final_code, {})}

    # 5. assemble pattern string for display
    groups = ["".join(_parse_pattern("".join(levels[d] for d in DIMENSION_ORDER))[i:i + 3])
              for i in range(0, 15, 3)]
    pattern_str = "-".join(groups)

    return SBTIResult(
        raw_scores=raw_scores,
        levels=levels,
        pattern=pattern_str,
        ranked=ranked,
        best_normal=best,
        final_type_code=final_code,
        final_type=final_type,
        special=special,
        drunk_triggered=drunk_triggered,
    )


__all__ = [
    "DIMENSION_ORDER",
    "SBTIData",
    "SBTIResult",
    "load_data",
    "score",
]
