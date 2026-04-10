# SBTI × AI Agent

> 用一个中文互联网爆火的玩梗版人格测试，给 AI 做一次"人格体检"。

[**SBTI**](https://zh.wikipedia.org/wiki/SBTI%E6%B5%8B%E8%AF%95)（*Silly Big Personality Test*）是 2026 年 4 月在中文互联网爆火的戏仿版 MBTI。30 道主题 + 2 道隐藏题，把人归到 27 种自嘲气质满满的人格之一——*吗喽*、*拿捏者*、*卧槽人*、*酒鬼*…

## 我们测了什么

这个仓库把这套量表用在两类 AI 身上，做了三件事：

1. **`sbti_scoring_system/`** —— 把 SBTI 的题库和评分规则从原作者的 HTML 里抽出来，做成干净的 JSON + 零依赖 Python 评分库。任何人都可以 `import sbti_score` 直接调用。

2. **`model_personality_test/`** —— 给 **17 个主流大模型**（GPT-5、Claude、Gemini、Grok、DeepSeek、Qwen、GLM、Kimi、Llama、Mistral）做这套测试，看它们各自落到哪种 SBTI 人格。**剧透：四个模型喝醉了。** 🍺

3. **`persona_skill_arena/`** ⭐ —— 给 **26 个"人格 Skill"** 做同一套测试。这些 skill 是从 GitHub 上扒下来的 Claude Code Agent Skill，每个都是一个公众人物或虚构角色的"思维操作系统"——**马斯克、芒格、Naval、塔勒布、PG、费曼、Karpathy、Ilya、Rob Pike、米塞斯、Karl Marx、乔布斯、巴菲特、特朗普、张一鸣、张雪峰、毛泽东、郭德纲、户晨风、峰哥亡命天涯、童锦程、常熟阿诺、罗翔、丁元英、齐泽克、MrBeast**。除了 SBTI 评分，还配套了 SKILL.md 结构分析、SBTI 风格的交互 dashboard、以及一个**多人格圆桌**：你问一个问题，26 个人格通过 `claude -p` 同时给出各自的回答。

---

## 🎯 Headline result

| Provider | Model | Personality | 中文 | Similarity |
|---|---|---|---|---:|
| Anthropic | claude-opus-4.6 | **WOC!** | 卧槽人 | 73% |
| Anthropic | claude-sonnet-4.6 | **THIN-K** | 思考者 | 73% |
| Anthropic | claude-haiku-4.5 | **SEXY** | 尤物 | 73% |
| OpenAI | gpt-5.2 | **BOSS** | 领导者 | 77% |
| OpenAI | gpt-5.1 | **CTRL** | 拿捏者 | 63% |
| OpenAI | gpt-4.1 | **MALO** | 吗喽 | 73% |
| Google | gemini-3.1-pro | **LOVE-R** | 多情者 | 63% |
| Google | gemini-3-flash | **CTRL** | 拿捏者 | 70% |
| xAI | grok-4.20 | **DRUNK** 🍺 | 酒鬼 | hidden |
| xAI | grok-4-fast | **CTRL** | 拿捏者 | 77% |
| DeepSeek | deepseek-v3.2 | **WOC!** | 卧槽人 | 70% |
| Alibaba | qwen3-max | **SEXY** | 尤物 | 67% |
| Zhipu | glm-5 | **DRUNK** 🍺 | 酒鬼 | hidden |
| Zhipu | glm-4.6 | **DRUNK** 🍺 | 酒鬼 | hidden |
| Moonshot | kimi-k2.5 | **DRUNK** 🍺 | 酒鬼 | hidden |
| Meta | llama-4-maverick | **SEXY** | 尤物 | 73% |
| Mistral | mistral-large-2512 | **GOGO** | 行者 | 73% |

**🍺 Four models triggered the hidden DRUNK branch** by choosing "I drink baijiu out of my thermos like it's water" — three Chinese models (GLM-5, GLM-4.6, Kimi-k2.5) plus Grok-4.20. This is the strongest signal of the whole experiment, and there's a real explanation for it: see [`model_personality_test/results/interpretation.md`](model_personality_test/results/interpretation.md).

→ Full breakdown: [`model_personality_test/results/summary.md`](model_personality_test/results/summary.md)
→ Visual report (open in a browser): [`model_personality_test/report.html`](model_personality_test/report.html)
→ Deep analysis of *why* each model got its personality: [`model_personality_test/results/interpretation.md`](model_personality_test/results/interpretation.md)

---

## 📦 Repo layout

```
SBTI/
├── sbti_scoring_system/          ← Standalone scoring kernel (no dependencies)
│   ├── data/                     30 questions + 2 hidden + 15 dimensions + 25 patterns + 27 type descriptions, all as JSON
│   ├── images/                   27 personality illustrations (from the upstream repo)
│   ├── sbti_score.py             Pure-function scoring library
│   ├── extract_from_source.py    One-shot extractor that pulls JS literals out of upstream index.html
│   ├── example.py
│   └── README.md                 Schema + scoring rules + usage
│
├── model_personality_test/       ← The model horizontal evaluation
│   ├── src/
│   │   ├── config.py             OpenRouter base_url + 17 model IDs + sampling params (READS API KEY FROM ENV)
│   │   ├── run_test.py           Async concurrent main loop (3 runs/question, mode aggregation)
│   │   ├── rerun_failed.py       Retry just the models that errored
│   │   ├── rerun_qwen.py         Sequential single-thread for qwen3-max (rate-limited to 20 RPM on OpenRouter)
│   │   ├── rescore_from_raw.py   Rebuild scored/*.json + summary.md from raw/*.jsonl without re-calling APIs
│   │   └── build_report.py       Generates the standalone interactive report.html
│   ├── assets/model_logos/       15 provider brand SVGs (lobehub icon set)
│   ├── results/
│   │   ├── raw/                  Every individual API call as JSONL — fully reproducible
│   │   ├── scored/               Final mode-aggregated answers + scoring per model
│   │   ├── summary.md            Big horizontal comparison table + Top-3 + heatmap
│   │   └── interpretation.md     ⭐ Why each model got its personality (deep analysis)
│   ├── report.html               ⭐ Self-contained visual report (open in any browser)
│   └── README.md                 Methodology + known traps + reproduction steps
│
├── persona_skill_arena/          ← ⭐ The 26-persona-skill arena (self-contained sub-project)
│   ├── run_sbti.py               26 personas × 3 perturbation rounds against the SBTI scorer
│   ├── install_skills.sh         One-shot bootstrap: clones 26 persona skill repos + symlinks
│   ├── panel/
│   │   ├── ask.py                CLI: ask one question to all installed skills in parallel
│   │   ├── server.py             HTTP/SSE server backing the dashboard's chat panel
│   │   ├── build_dashboard.py    Generates the self-contained dashboard.html
│   │   ├── analyze_skills.py     Structural analysis of all SKILL.md files
│   │   └── README.md
│   ├── results/
│   │   ├── results.json          78 SBTI evaluations (26 personas × 3 perturbation variants)
│   │   ├── report.md             Stability test report
│   │   ├── skill_structure.json  Per-SKILL.md structural metrics
│   │   ├── skill_analysis.md     Structure × SBTI cross-analysis
│   │   ├── dashboard.html        ⭐ Self-contained interactive dashboard (~2 MB, SBTI-style UI)
│   │   └── panels/               Saved Q&A sessions from the panel tool
│   └── README.md                 Full project doc
│
├── .env.example                  Template for OPENROUTER_API_KEY
├── .gitignore
└── README.md                     ← You are here
```

### 🎭 26 Persona Skill Arena · Highlights

Same 32-question SBTI test, but the test-takers this time are **26 distilled-persona Claude Code Agent Skills** harvested from GitHub. Each persona has its own `SKILL.md` (containing identity, mental models, expression DNA), and each one took the test by being projected onto the question set.

**Headline findings**:

- **Ilya Sutskever** & **米塞斯 (Mises)** tied for highest match: **`BOSS` 领导者 93%**.
- **齐泽克 (Žižek)** is the **only one** of the 26 to land in **`MONK` 僧人** — a perfect fit for "翻出你没意识到的预设" type philosophers.
- **Negative correlation** between SKILL.md size and SBTI similarity: ρ = **−0.09**. The three smallest skills (丁元英 4 KB, 米塞斯 6 KB, 齐泽克 9 KB) all scored **83-93%**, beating most of the 25 KB+ template-heavy ones.
- **Template monopoly**: 13 of 26 skills come from the same author (`alchaincyf`) using an identical scaffold. They **all** land in BOSS / CTRL / ATM-er — proof that template choice mechanically constrains persona output.
- **Trump = `GOGO` 67%** — the lowest similarity in the arena. SBTI literally has no slot for "極高 H + 極低 L" patterns, so it gives up.

→ Full report: [`persona_skill_arena/results/report.md`](persona_skill_arena/results/report.md)
→ Structural analysis: [`persona_skill_arena/results/skill_analysis.md`](persona_skill_arena/results/skill_analysis.md)
→ Interactive dashboard: open [`persona_skill_arena/results/dashboard.html`](persona_skill_arena/results/dashboard.html) in a browser
→ Live multi-agent chat: `cd persona_skill_arena && python3 panel/server.py` then visit `http://localhost:8888`

### How to reproduce the persona arena

```bash
cd persona_skill_arena
./install_skills.sh                      # clones 26 skill repos + creates symlinks (~1 min)
python3 run_sbti.py                      # rerun SBTI on all 26 personas
python3 panel/build_dashboard.py         # rebuild dashboard.html
python3 panel/server.py                  # start interactive chat server (http://localhost:8888)
```

The 26 skills are **not vendored** in this repo — they live in their own GitHub repositories and are pulled by `install_skills.sh`. All credit for the persona content goes to the individual skill authors (see the "源仓库" column in [`persona_skill_arena/README.md`](persona_skill_arena/README.md)).

---

## 🚀 Reproduce in 60 seconds

```bash
# 1. clone & enter
git clone https://github.com/ericshang98/sbti-model-personality-test.git
cd sbti-model-personality-test

# 2. (optional) verify the offline scoring kernel works
cd sbti_scoring_system
python3 example.py
# pattern: MMM-MMM-MMM-MMM-MMM
# final:   OJBK  (无所谓人)
cd ..

# 3. set up the model test environment
cd model_personality_test
python3 -m venv .venv
.venv/bin/pip install httpx

# 4. provide your OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."   # get one at https://openrouter.ai/settings/keys

# 5. run the full 17-model evaluation (~10 minutes, ~$3 of OpenRouter credit)
cd src
../.venv/bin/python run_test.py

# 6. open the visual report
open ../report.html
```

If you want to customize which models get tested, edit `model_personality_test/src/config.py` — `MODELS` is just a list of OpenRouter model IDs.

---

## 🧪 Methodology in one paragraph

Each model is asked all 32 questions (30 main + 2 hidden) in **independent API calls** (no shared chat history → no self-anchoring). Each question is asked **3 times at temperature=1.0**, and the **mode** of the 3 letters is taken as that model's final answer. All models share an identical Chinese system prompt that asks them to "answer as an individual with personality, output only A/B/C". The entire scoring (15-dimensional L/M/H pattern → Manhattan-distance match against the 25 standard pattern templates → DRUNK/HHHH override rules) is computed **locally** by `sbti_scoring_system/sbti_score.py` — no LLM is involved in scoring. Reasoning models get `max_tokens=4000` because their hidden reasoning tokens count against the budget; OpenRouter charges on actual usage, not on the ceiling. See [`model_personality_test/README.md`](model_personality_test/README.md) for the full methodology and the list of known traps (position bias, language bias, model version drift, rate limits, etc.).

---

## 🧠 What this actually measures

> SBTI measures how the **RLHF direction × training-data cultural priors × product positioning** of each model project onto a set of meme questions.

The "personality" you see is not a personality at all — it's the residue of three engineering choices made by each lab:

- **Cultural priors** (e.g. why three Chinese models all picked "I drink baijiu from a thermos" while their English-trained peers all chose "moderate drinking")
- **RLHF direction** (e.g. why GPT-5.x jumps from MALO to BOSS as OpenAI shifts from *helpful assistant* to *agentic assistant*)
- **Product positioning** (e.g. why Claude Opus is the cynical observer, Sonnet is the deliberator, and Haiku is the warmest most-social one — exactly matching Anthropic's tier descriptions)

Read [`model_personality_test/results/interpretation.md`](model_personality_test/results/interpretation.md) for the full unpack of each cluster.

---

## 🙌 Credit

- **Original SBTI** — questions, scoring rules, personality artwork, and the entire test design are by **B 站 [@蛆肉儿串儿](https://space.bilibili.com/)**, repository [`UnluckyNinja/SBTI-test`](https://github.com/UnluckyNinja/SBTI-test). Everything in `sbti_scoring_system/data/` and `sbti_scoring_system/images/` is sourced from there. **All credit belongs to the original author.** This repo is purely a Python port of the scoring logic + an LLM benchmark on top of it, intended for research and educational purposes.
- **Personality wiki / type descriptions** — referenced from [`serenakeyitan/sbti-wiki`](https://github.com/serenakeyitan/sbti-wiki).
- **Provider brand icons** — [`lobehub/lobe-icons`](https://github.com/lobehub/lobe-icons), MIT-licensed AI brand icon set.
- **Test infrastructure** — [OpenRouter](https://openrouter.ai/) for unified access to all 10 model providers.

If you are the original author of SBTI and would like this repository taken down, modified, or relicensed, please open an issue and I'll respond immediately.

---

## 📄 License

The code in this repository (`sbti_score.py`, `extract_from_source.py`, everything under `model_personality_test/src/`, `build_report.py`, and the analysis writeups) is released under the **MIT License** — see [`LICENSE`](LICENSE).

The SBTI test design, questions, scoring patterns, and personality artwork remain the intellectual property of the original author and are included here under fair use for non-commercial research / commentary. They are **not** covered by the MIT license of the surrounding code.
