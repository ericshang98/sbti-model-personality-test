"""
SBTI 14-persona × 3-run stability test.

For each persona:
  v1 = primary answers (best-fit reading of SKILL.md)
  v2 = all "ambiguous" questions flipped to alternative
  v3 = every other ambiguous question flipped

We run SBTI scoring on each variant and compute stability:
  - Does the final type code change?
  - How wide does similarity swing?

All per-question answers, per-run results, and summary are saved to
  persona_skill_arena/results/results.json
  persona_skill_arena/results/report.md
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT.parent / "sbti_scoring_system"))
from sbti_score import load_data, score  # noqa: E402

RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

data = load_data()

# ---------------------------------------------------------------------------
# Each persona defines:
#   answers   : primary per-question dict  (q1..q30 + drink_gate_q1/q2)
#   ambiguous : dict of {question_id: alternative_value}
#               — these are questions where the SKILL.md justifies
#                 more than one plausible answer; we flip them in v2/v3.
# ---------------------------------------------------------------------------

PERSONAS: dict[str, dict] = {}

# --------------------- 1. 峰哥亡命天涯 ----------------------
PERSONAS["fengge"] = {
    "label": "峰哥亡命天涯",
    "source": "rottenpen/fengge-wangmingtianya-perspective",
    "answers": {
        "q1": 3, "q2": 2, "q3": 3, "q4": 2, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 2, "q10": 1, "q11": 3, "q12": 3,
        "q13": 1, "q14": 2, "q15": 1, "q16": 1, "q17": 2, "q18": 1,
        "q19": 2, "q20": 2, "q21": 3, "q22": 3, "q23": 3, "q24": 1,
        "q25": 3, "q26": 3, "q27": 2, "q28": 2, "q29": 1, "q30": 2,
        "drink_gate_q1": 3, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q4": 1,   # 真正追求 — 漂泊者也可能干脆说"没追求"
        "q7": 2,   # 拉稀 — 江湖疑心也可能摇摆
        "q17": 3,  # 做事有目标 — 他嘴上不承认但其实有
        "q22": 1,  # 盲选 — 也可能反复思考
        "q24": 2,  # 计划 — 也可能"有时能完成"
    },
}

# --------------------- 2. 户晨风 ----------------------
PERSONAS["huchenfeng"] = {
    "label": "户晨风",
    "source": "Janlaywss/hu-chenfeng-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 3,
        "q7": 1, "q8": 3, "q9": 1, "q10": 1, "q11": 3, "q12": 3,
        "q13": 1, "q14": 1, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 3, "q26": 3, "q27": 3, "q28": 3, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q9": 2,    # 感情认真 — 也可能是"也许"
        "q15": 3,   # 翘晚自习 — 实用主义也可能"都要考试了"
        "q27": 2,   # 电子围栏 — 也能中立
        "q28": 2,   # 亲戚般密切 — 他直播亲切
        "q30": 2,   # 不同人前 — 也可能中立
    },
}

# --------------------- 3. 张雪峰 ----------------------
PERSONAS["zhangxuefeng"] = {
    "label": "张雪峰",
    "source": "alchaincyf/zhangxuefeng-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 2,
        "q7": 1, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 3, "q14": 2, "q15": 3, "q16": 2, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 3, "q26": 3, "q27": 1, "q28": 1, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 1,    # 外人评价 — 他也可能说"在乎"（流量驱动）
        "q11": 2,   # 对象黏人 — 工作狂也可能说无所谓
        "q14": 3,   # 棒棒糖 — 他可能会可爱
        "q16": 3,   # 打破常规 — 他同时很守规
        "q30": 2,   # 不同人前 — 也能中立
    },
}

# --------------------- 4. 郭德纲 ----------------------
PERSONAS["guodegang"] = {
    "label": "郭德纲",
    "source": "ByteRax/guodegang-skills",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 2,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 1, "q12": 2,
        "q13": 3, "q14": 3, "q15": 3, "q16": 3, "q17": 3, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 3, "q26": 3, "q27": 1, "q28": 1, "q29": 2, "q30": 3,
        "drink_gate_q1": 3, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 3,    # 外人评价 — 他说观众是裁判，"无所谓专家"
        "q12": 3,   # 个人空间 — 相声艺人创作需要
        "q20": 2,   # 便秘 — 段子手可能选拍屁股
        "q24": 2,   # 计划 — 江湖艺人也"有时完成"
        "q29": 1,   # 负面没说 — 他也很敢说
    },
}

# --------------------- 5. Elon Musk ----------------------
PERSONAS["musk"] = {
    "label": "Elon Musk",
    "source": "alchaincyf/elon-musk-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 3,
        "q7": 1, "q8": 2, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 1, "q14": 2, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 2, "q26": 1, "q27": 3, "q28": 3, "q29": 1, "q30": 2,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 1,   # 外人评价 — 他行为上极度在乎
        "q8": 3,   # 怕被抛弃 — 也可能"不"
        "q9": 2,   # 感情认真 — 多次离婚
        "q24": 1,  # 计划 — 他实际上时间线永远延期
        "q25": 3,  # 见网友 — 他线上活跃
    },
}

# --------------------- 6. Charlie Munger ----------------------
PERSONAS["munger"] = {
    "label": "Charlie Munger",
    "source": "alchaincyf/munger-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 2, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 2, "q14": 2, "q15": 3, "q16": 3, "q17": 3, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2,    # 往上爬 — 他说"持续不蠢"，也可以理解为中立
        "q13": 3,   # 善良 — 他信激励但也不失宽容
        "q16": 2,   # 打破常规 — 思维反常规，行为守规
        "q20": 3,   # 便秘 — 理性人也可能直接解决
        "q28": 1,   # 亲戚般 — 他对巴菲特是
    },
}

# --------------------- 7. 特朗普 ----------------------
PERSONAS["trump"] = {
    "label": "特朗普",
    "source": "alchaincyf/trump-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 1,
        "q7": 1, "q8": 2, "q9": 3, "q10": 3, "q11": 1, "q12": 2,
        "q13": 1, "q14": 1, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 3, "q26": 3, "q27": 1, "q28": 1, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 3,    # 评价无所谓 — 他人设版会说无所谓
        "q8": 3,    # 怕被抛弃 — 他自吹不
        "q14": 3,   # 棒棒糖 — 他对美女萌物有反应
        "q20": 2,   # 便秘 — 他强势拍
        "q24": 1,   # 计划 — 他实际不如变化快
    },
}

# --------------------- 8. 乔布斯 ----------------------
PERSONAS["jobs"] = {
    "label": "乔布斯",
    "source": "alchaincyf/steve-jobs-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 3,
        "q7": 1, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 2, "q14": 3, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 2, "q26": 2, "q27": 3, "q28": 3, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q7": 3,    # 拉稀 — 他也可能选相信
        "q11": 1,   # 对象黏人 — 他有深情
        "q13": 3,   # 善良 — 他学佛倾向慈悲
        "q14": 2,   # 棒棒糖 — 也可能懵
        "q28": 1,   # 亲戚般 — 他对 Laurene
    },
}

# --------------------- 9. Naval Ravikant ----------------------
PERSONAS["naval"] = {
    "label": "Naval",
    "source": "alchaincyf/naval-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 2, "q11": 3, "q12": 3,
        "q13": 3, "q14": 3, "q15": 3, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2,    # 往上爬 — 他"内求"
        "q10": 3,   # 优秀对象
        "q15": 1,   # 翘晚自习 — 他无需许可型
        "q16": 3,   # 打破常规 — 他也强调"杠杆"
        "q28": 3,   # 亲戚般 — 他偏独
    },
}

# --------------------- 10. 塔勒布 ----------------------
PERSONAS["taleb"] = {
    "label": "塔勒布",
    "source": "alchaincyf/taleb-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 1, "q8": 3, "q9": 3, "q10": 3, "q11": 2, "q12": 3,
        "q13": 1, "q14": 2, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 2, "q20": 2, "q21": 3, "q22": 3, "q23": 3, "q24": 1,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2,   # 往上爬 — 他反status
        "q11": 1,  # 对象黏人 — 地中海家庭文化
        "q13": 2,  # 善良 — 也可中立
        "q19": 3,  # 追求进步 — 他其实是反脆弱派
        "q22": 1,  # 盲选 — 他会反复思考讽刺
    },
}

# --------------------- 11. 巴菲特 ----------------------
PERSONAS["buffett"] = {
    "label": "巴菲特",
    "source": "will2025btc/buffett-perspective",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 2, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 1, "q12": 2,
        "q13": 3, "q14": 3, "q15": 3, "q16": 3, "q17": 3, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 1, "q26": 2, "q27": 2, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 3,   # 往上爬 — 他竞争感很强
        "q12": 3,  # 个人空间
        "q22": 1,  # 盲选 — 他会说"太贵就不做"
        "q25": 2,  # 见网友 — 他爱快餐聚会
        "q28": 1,  # 亲戚般 — 他和 Charlie
    },
}

# --------------------- 12. 张一鸣 ----------------------
PERSONAS["zhangyiming"] = {
    "label": "张一鸣",
    "source": "alchaincyf/zhang-yiming-skill",
    "answers": {
        "q1": 3, "q2": 2, "q3": 3, "q4": 3, "q5": 3, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 2, "q11": 3, "q12": 3,
        "q13": 2, "q14": 2, "q15": 3, "q16": 2, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 2, "q26": 2, "q27": 2, "q28": 2, "q29": 2, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q2": 3,    # 不够好 — 平庸有重力
        "q6": 2,    # 评价 — 他低调
        "q13": 3,   # 善良 — 他温和
        "q16": 1,   # 打破常规 — 他是颠覆者
        "q29": 1,   # 负面没说 — 他也敢说
    },
}

# --------------------- 13. 童锦程 ----------------------
PERSONAS["tongjincheng"] = {
    "label": "童锦程",
    "source": "hotcoffeeshake/tong-jincheng-skill",
    "answers": {
        "q1": 3, "q2": 2, "q3": 3, "q4": 3, "q5": 3, "q6": 2,
        "q7": 3, "q8": 2, "q9": 3, "q10": 3, "q11": 1, "q12": 2,
        "q13": 3, "q14": 3, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 2, "q21": 3, "q22": 1, "q23": 2, "q24": 2,
        "q25": 3, "q26": 3, "q27": 1, "q28": 1, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q2": 3,    # 不够好 — 他自信
        "q6": 1,    # 评价 — 他做直播在乎反馈
        "q8": 3,    # 怕抛弃 — 他现在稳定
        "q22": 3,   # 盲选 — 他痞子
        "q23": 3,   # 执行力 — 他做直播很稳
    },
}

# --------------------- 18. 常熟阿诺 ----------------------
PERSONAS["anuo"] = {
    "label": "常熟阿诺",
    "source": "Ricardo-Vv/changshu-anuo",
    "answers": {
        "q1": 3, "q2": 3, "q3": 2, "q4": 3, "q5": 2, "q6": 3,
        "q7": 2, "q8": 3, "q9": 3, "q10": 3, "q11": 2, "q12": 2,
        "q13": 2, "q14": 3, "q15": 1, "q16": 1, "q17": 2, "q18": 3,
        "q19": 2, "q20": 2, "q21": 1, "q22": 1, "q23": 2, "q24": 2,
        "q25": 3, "q26": 3, "q27": 1, "q28": 2, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q3": 3, "q17": 3, "q21": 3, "q22": 3, "q27": 2,
    },
}

# --------------------- 19. Ilya Sutskever ----------------------
PERSONAS["ilya"] = {
    "label": "Ilya Sutskever",
    "source": "alchaincyf/ilya-sutskever-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 2, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 2, "q14": 2, "q15": 3, "q16": 2, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 1, "q14": 3, "q16": 3, "q25": 2, "q28": 3,
    },
}

# --------------------- 20. Karl Marx ----------------------
PERSONAS["marx"] = {
    "label": "Karl Marx",
    "source": "baojiachen0214/karlmarx-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 2,
        "q7": 1, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 1, "q14": 1, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 3, "q26": 3, "q27": 2, "q28": 2, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 3, "q13": 2, "q22": 1, "q25": 2, "q30": 2,
    },
}

# --------------------- 21. 米塞斯 ----------------------
PERSONAS["mises"] = {
    "label": "米塞斯",
    "source": "LijiayuDeng/mises-perspective",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 2, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 2, "q14": 2, "q15": 3, "q16": 3, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 3, "q13": 3, "q16": 2, "q25": 2, "q28": 3,
    },
}

# --------------------- 22. MrBeast ----------------------
PERSONAS["mrbeast"] = {
    "label": "MrBeast",
    "source": "alchaincyf/mrbeast-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 2,
        "q7": 2, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 3, "q14": 3, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 3, "q26": 3, "q27": 2, "q28": 2, "q29": 2, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 3, "q11": 2, "q16": 2, "q27": 3, "q29": 1,
    },
}

# --------------------- 23. Rob Pike ----------------------
PERSONAS["robpike"] = {
    "label": "Rob Pike",
    "source": "smallnest/rob-pike-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 2, "q14": 2, "q15": 3, "q16": 3, "q17": 3, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2, "q14": 3, "q20": 3, "q24": 3, "q28": 3,
    },
}

# --------------------- 24. 齐泽克 ----------------------
PERSONAS["zizek"] = {
    "label": "齐泽克",
    "source": "JikunR/zizek-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 2, "q6": 3,
        "q7": 1, "q8": 3, "q9": 3, "q10": 1, "q11": 3, "q12": 3,
        "q13": 1, "q14": 1, "q15": 1, "q16": 1, "q17": 2, "q18": 3,
        "q19": 2, "q20": 2, "q21": 3, "q22": 1, "q23": 2, "q24": 1,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q2": 2, "q13": 2, "q17": 3, "q22": 3, "q30": 2,
    },
}

# --------------------- 25. 丁元英 ----------------------
PERSONAS["dingyuanying"] = {
    "label": "丁元英",
    "source": "liangfeiiiii/ding-yuanying-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 1, "q11": 3, "q12": 3,
        "q13": 2, "q14": 2, "q15": 3, "q16": 2, "q17": 3, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2, "q10": 3, "q13": 3, "q16": 1, "q20": 3,
    },
}

# --------------------- 26. 罗翔 ----------------------
PERSONAS["luoxiang"] = {
    "label": "罗翔",
    "source": "YixiaJack/luo-xiang-skill",
    "answers": {
        "q1": 3, "q2": 2, "q3": 3, "q4": 3, "q5": 2, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 2, "q12": 2,
        "q13": 3, "q14": 3, "q15": 3, "q16": 3, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 3,
        "q25": 2, "q26": 2, "q27": 2, "q28": 2, "q29": 2, "q30": 2,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q2": 3, "q5": 3, "q25": 3, "q29": 1, "q30": 3,
    },
}

# --------------------- 15. Paul Graham ----------------------
PERSONAS["pg"] = {
    "label": "Paul Graham",
    "source": "alchaincyf/paul-graham-skill",
    "answers": {
        "q1": 3, "q2": 2, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 3, "q14": 3, "q15": 1, "q16": 1, "q17": 2, "q18": 3,
        "q19": 3, "q20": 1, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 1, "q26": 1, "q27": 3, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2,    # 往上爬 — 他其实竞争心强
        "q15": 3,   # 翘晚自习 — 他爱学习
        "q17": 3,   # 有目标 — essay 有目标型
        "q24": 3,   # 计划 — 他也能守
        "q30": 2,   # 不同人前 — 也可能中立
    },
}

# --------------------- 16. 毛泽东 ----------------------
PERSONAS["maoxuan"] = {
    "label": "毛泽东",
    "source": "leezythu/maoxuan-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 2,
        "q7": 1, "q8": 3, "q9": 3, "q10": 2, "q11": 3, "q12": 3,
        "q13": 1, "q14": 1, "q15": 1, "q16": 1, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 3, "q26": 3, "q27": 1, "q28": 1, "q29": 1, "q30": 3,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q6": 3,    # 评价 — "一切成绩归人民"
        "q10": 3,   # 优秀对象 — 他和江青
        "q16": 2,   # 打破常规 — 他后期也守"正确路线"
        "q22": 1,   # 盲选 — 他会反复思考
        "q24": 3,   # 计划 — 持久战
    },
}

# --------------------- 17. Andrej Karpathy ----------------------
PERSONAS["karpathy"] = {
    "label": "Karpathy",
    "source": "alchaincyf/karpathy-skill",
    "answers": {
        "q1": 3, "q2": 2, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 3, "q12": 3,
        "q13": 3, "q14": 3, "q15": 3, "q16": 2, "q17": 3, "q18": 3,
        "q19": 3, "q20": 3, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 3, "q26": 3, "q27": 2, "q28": 2, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2,    # 往上爬 — 他已离开 OpenAI 做独立教育
        "q14": 2,   # 棒棒糖
        "q16": 1,   # 打破常规 — 他是 vibe coder
        "q27": 3,   # 电子围栏 — 他也有书房型
        "q30": 2,   # 不同人前
    },
}

# --------------------- 14. 费曼 ----------------------
PERSONAS["feynman"] = {
    "label": "费曼",
    "source": "alchaincyf/feynman-skill",
    "answers": {
        "q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 1, "q6": 3,
        "q7": 3, "q8": 3, "q9": 3, "q10": 3, "q11": 1, "q12": 2,
        "q13": 3, "q14": 3, "q15": 1, "q16": 1, "q17": 2, "q18": 3,
        "q19": 3, "q20": 2, "q21": 3, "q22": 3, "q23": 3, "q24": 2,
        "q25": 3, "q26": 3, "q27": 1, "q28": 1, "q29": 1, "q30": 1,
        "drink_gate_q1": 1, "drink_gate_q2": 1,
    },
    "ambiguous": {
        "q5": 2,    # 往上爬 — 他反status但好奇心极强
        "q11": 2,   # 对象黏人 — 他和 Arline
        "q17": 3,   # 有目标 — 好奇驱动也算目标
        "q22": 2,   # 盲选 — 他会恶搞
        "q24": 1,   # 计划 — 他超即兴
    },
}

# ---------------------------------------------------------------------------
# Variant builders
# ---------------------------------------------------------------------------

def build_variants(primary: dict, ambiguous: dict) -> list[dict]:
    """Return [v1, v2, v3] variants.

    v1 : primary
    v2 : primary ∪ all ambiguous alternatives
    v3 : primary ∪ every other ambiguous alternative (indices 0,2,4,...)
    """
    v1 = dict(primary)
    v2 = dict(primary)
    v2.update(ambiguous)
    v3 = dict(primary)
    for i, (qid, alt) in enumerate(ambiguous.items()):
        if i % 2 == 0:
            v3[qid] = alt
    return [v1, v2, v3]


# ---------------------------------------------------------------------------
# Run and collect
# ---------------------------------------------------------------------------

def run_one(answers: dict) -> dict:
    r = score(answers, data)
    return {
        "pattern": r.pattern,
        "final_code": r.final_type_code,
        "final_cn": r.final_type.get("cn", ""),
        "special": r.special,
        "drunk": r.drunk_triggered,
        "best_normal_code": r.best_normal["code"] if r.best_normal else None,
        "best_similarity": r.best_normal["similarity"] if r.best_normal else 0,
        "exact": r.best_normal["exact"] if r.best_normal else 0,
        "top3": [
            {"code": t["code"], "cn": data.types.get(t["code"], {}).get("cn", ""),
             "sim": t["similarity"], "exact": t["exact"]}
            for t in r.ranked[:3]
        ],
        "raw_scores": dict(r.raw_scores),
        "levels": dict(r.levels),
    }


def stability_summary(runs: list[dict]) -> dict:
    codes = [r["final_code"] for r in runs]
    sims = [r["best_similarity"] for r in runs]
    unique_codes = list(dict.fromkeys(codes))  # preserve order, dedupe
    return {
        "variants_count": len(runs),
        "final_codes_across_variants": codes,
        "unique_final_codes": unique_codes,
        "code_stable": len(unique_codes) == 1,
        "similarity_range": [min(sims), max(sims)],
        "similarity_swing": max(sims) - min(sims),
    }


def run_all() -> dict:
    full = {"personas": {}, "order": list(PERSONAS.keys())}
    for key, persona in PERSONAS.items():
        variants = build_variants(persona["answers"], persona["ambiguous"])
        runs = [run_one(v) for v in variants]
        full["personas"][key] = {
            "label": persona["label"],
            "source": persona["source"],
            "ambiguous_questions": persona["ambiguous"],
            "primary_answers": persona["answers"],
            "runs": runs,
            "stability": stability_summary(runs),
        }
    return full


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_json(full: dict):
    path = RESULTS_DIR / "results.json"
    path.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[saved] {path}")


def write_report(full: dict):
    path = RESULTS_DIR / "report.md"
    lines = []
    lines.append("# SBTI × 14 人格 Skill · 稳定性测试报告\n")
    lines.append(f"- 测试题数：32 (30 主题 + 2 隐藏饮酒)\n")
    lines.append(f"- 人格数：{len(full['personas'])}\n")
    lines.append("- 每个人格跑 3 个变体 (v1=主答案, v2=全扰动, v3=半扰动)\n")
    lines.append("- 评分系统：`sbti_scoring_system/sbti_score.py` (原作者 @蛆肉儿串儿)\n")
    lines.append("\n")

    # summary table
    lines.append("## 总榜 (按 v1 相似度降序)\n\n")
    lines.append("| 排名 | Skill | v1 代号 | v1 中文 | v1 相似度 | 3 轮稳定 | 相似度波动 | 3 轮代号 |\n")
    lines.append("|:-:|---|:-:|---|:-:|:-:|:-:|---|\n")
    ranked = sorted(
        full["personas"].items(),
        key=lambda kv: -kv[1]["runs"][0]["best_similarity"],
    )
    for i, (key, p) in enumerate(ranked, 1):
        v1 = p["runs"][0]
        st = p["stability"]
        stable = "✅" if st["code_stable"] else "⚠️"
        swing = f"±{st['similarity_swing']}"
        codes_seq = " → ".join(st["final_codes_across_variants"])
        lines.append(
            f"| {i} | {p['label']} | `{v1['final_code']}` | {v1['final_cn']} |"
            f" {v1['best_similarity']}% | {stable} | {swing} | {codes_seq} |\n"
        )
    lines.append("\n")

    # per-persona detail
    lines.append("## 分人格详情\n\n")
    for key, p in ranked:
        lines.append(f"### {p['label']}\n")
        lines.append(f"- 源仓库：`{p['source']}`\n")
        lines.append(f"- 模糊题数：{len(p['ambiguous_questions'])}\n\n")
        lines.append("| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |\n")
        lines.append("|:-:|---|:-:|---|:-:|:-:|\n")
        for i, r in enumerate(p["runs"], 1):
            lines.append(
                f"| v{i} | `{r['pattern']}` | `{r['final_code']}` |"
                f" {r['final_cn']} | {r['best_similarity']}% | {r['exact']}/15 |\n"
            )
        lines.append("\n")
        st = p["stability"]
        if st["code_stable"]:
            lines.append(f"**稳定性**：✅ 锁定 `{st['unique_final_codes'][0]}`"
                         f"，3 轮相似度 [{st['similarity_range'][0]}%, {st['similarity_range'][1]}%]\n\n")
        else:
            lines.append(f"**稳定性**：⚠️ 在 {', '.join(f'`{c}`' for c in st['unique_final_codes'])}"
                         f" 之间摇摆，相似度 [{st['similarity_range'][0]}%, {st['similarity_range'][1]}%]\n\n")
        # top-3 on v1
        lines.append("v1 Top-3 近邻：\n")
        for t in p["runs"][0]["top3"]:
            lines.append(f"  - `{t['code']}` {t['cn']} — sim={t['sim']}%, exact={t['exact']}/15\n")
        lines.append("\n---\n\n")

    path.write_text("".join(lines), encoding="utf-8")
    print(f"[saved] {path}")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    full = run_all()
    write_json(full)
    write_report(full)

    # Print a quick summary to stdout
    print()
    print("=" * 78)
    print(f"{'Skill':28s}  {'v1-code':8s}  {'v1-sim':>6s}  stable  swing")
    print("=" * 78)
    for key, p in full["personas"].items():
        v1 = p["runs"][0]
        st = p["stability"]
        stable = "YES" if st["code_stable"] else "NO "
        print(f"{p['label']:28s}  {v1['final_code']:8s}  "
              f"{v1['best_similarity']:5d}%   {stable}    ±{st['similarity_swing']}")
