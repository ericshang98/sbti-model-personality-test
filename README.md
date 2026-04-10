# SBTI × AI Agent

> 用一个中文互联网爆火的玩梗版人格测试，给 AI 做一次"人格体检"。

[**SBTI**](https://zh.wikipedia.org/wiki/SBTI%E6%B5%8B%E8%AF%95)（*Silly Big Personality Test*）是 2026 年 4 月在中文互联网爆火的戏仿版 MBTI。30 道主题 + 2 道隐藏题，把人归到 27 种自嘲气质满满的人格之一——*吗喽*、*拿捏者*、*卧槽人*、*酒鬼*…

## 我们测了什么

这个仓库把这套量表用在两类 AI 身上，做了三件事：

1. **`sbti_scoring_system/`** —— 把 SBTI 的题库和评分规则从原作者的 HTML 里抽出来，做成干净的 JSON + 零依赖 Python 评分库。任何人都可以 `import sbti_score` 直接调用。

2. **`model_personality_test/`** —— 给 **17 个主流大模型**（GPT-5、Claude、Gemini、Grok、DeepSeek、Qwen、GLM、Kimi、Llama、Mistral）做这套测试，看它们各自落到哪种 SBTI 人格。**剧透：四个模型喝醉了。** 🍺

3. **`persona_skill_arena/`** ⭐ —— 给 **26 个"人格 Skill"** 做同一套测试。这些 skill 是从 GitHub 上扒下来的 Claude Code Agent Skill，每个都是一个公众人物或虚构角色的"思维操作系统"——**马斯克、芒格、Naval、塔勒布、PG、费曼、Karpathy、Ilya、Rob Pike、米塞斯、Karl Marx、乔布斯、巴菲特、特朗普、张一鸣、张雪峰、毛泽东、郭德纲、户晨风、峰哥亡命天涯、童锦程、常熟阿诺、罗翔、丁元英、齐泽克、MrBeast**。除了 SBTI 评分，还配套了 SKILL.md 结构分析、SBTI 风格的交互 dashboard、以及一个**多人格圆桌**：你问一个问题，26 个人格通过 `claude -p` 同时给出各自的回答。

---

## 🎯 主要结果（17 个大模型）

| 厂商 | 模型 | 人格代号 | 中文 | 相似度 |
|---|---|---|---|---:|
| Anthropic | claude-opus-4.6 | **WOC!** | 卧槽人 | 73% |
| Anthropic | claude-sonnet-4.6 | **THIN-K** | 思考者 | 73% |
| Anthropic | claude-haiku-4.5 | **SEXY** | 尤物 | 73% |
| OpenAI | gpt-5.2 | **BOSS** | 领导者 | 77% |
| OpenAI | gpt-5.1 | **CTRL** | 拿捏者 | 63% |
| OpenAI | gpt-4.1 | **MALO** | 吗喽 | 73% |
| Google | gemini-3.1-pro | **LOVE-R** | 多情者 | 63% |
| Google | gemini-3-flash | **CTRL** | 拿捏者 | 70% |
| xAI | grok-4.20 | **DRUNK** 🍺 | 酒鬼 | 隐藏 |
| xAI | grok-4-fast | **CTRL** | 拿捏者 | 77% |
| DeepSeek | deepseek-v3.2 | **WOC!** | 卧槽人 | 70% |
| Alibaba | qwen3-max | **SEXY** | 尤物 | 67% |
| Zhipu | glm-5 | **DRUNK** 🍺 | 酒鬼 | 隐藏 |
| Zhipu | glm-4.6 | **DRUNK** 🍺 | 酒鬼 | 隐藏 |
| Moonshot | kimi-k2.5 | **DRUNK** 🍺 | 酒鬼 | 隐藏 |
| Meta | llama-4-maverick | **SEXY** | 尤物 | 73% |
| Mistral | mistral-large-2512 | **GOGO** | 行者 | 73% |

**🍺 4 个模型触发了隐藏的 DRUNK 分支** —— 它们都选了"我习惯把白酒灌在保温杯当白开水喝"这一项。三个中文模型（GLM-5、GLM-4.6、Kimi-k2.5）外加 Grok-4.20。这是整个实验里最强的一个信号，背后有真实的解释，详见 [`model_personality_test/results/interpretation.md`](model_personality_test/results/interpretation.md)。

→ 完整对比：[`model_personality_test/results/summary.md`](model_personality_test/results/summary.md)
→ 可视化报告（浏览器打开）：[`model_personality_test/report.html`](model_personality_test/report.html)
→ 每个模型为什么是这种人格的深度解读：[`model_personality_test/results/interpretation.md`](model_personality_test/results/interpretation.md)

---

## 📦 目录结构

```
SBTI/
├── sbti_scoring_system/          ← 独立评分内核（零依赖）
│   ├── data/                     30 主题 + 2 隐藏 + 15 维度 + 25 pattern + 27 人格描述, 全部 JSON
│   ├── images/                   27 张原版人格插画（来自上游仓库）
│   ├── sbti_score.py             纯函数评分库
│   ├── extract_from_source.py    从上游 index.html 提取 JS 字面量的一次性脚本
│   ├── example.py
│   └── README.md                 schema + 评分规则 + 用法
│
├── model_personality_test/       ← 17 大模型横向评测
│   ├── src/
│   │   ├── config.py             OpenRouter base_url + 17 个模型 ID + 采样参数（从 ENV 读 API KEY）
│   │   ├── run_test.py           异步并发主循环（每题 3 次, 取 mode 聚合）
│   │   ├── rerun_failed.py       只重试出错的模型
│   │   ├── rerun_qwen.py         qwen3-max 单线程顺跑（OpenRouter 上限 20 RPM）
│   │   ├── rescore_from_raw.py   不重新调 API, 直接从 raw/*.jsonl 重建 scored/*.json + summary.md
│   │   └── build_report.py       生成自包含交互式 report.html
│   ├── assets/model_logos/       15 个厂商品牌 SVG（lobehub icon set）
│   ├── results/
│   │   ├── raw/                  每次 API 调用 JSONL —— 完全可复现
│   │   ├── scored/               最终聚合后的答案 + 每个模型的评分
│   │   ├── summary.md            横向对比大表 + Top-3 + 热力图
│   │   └── interpretation.md     ⭐ 每个模型为什么是这种人格（深度分析）
│   ├── report.html               ⭐ 自包含可视化报告（任何浏览器打开即可）
│   └── README.md                 方法论 + 已知陷阱 + 复现步骤
│
├── persona_skill_arena/          ← ⭐ 26 人格 Skill 评测（自包含子项目）
│   ├── run_sbti.py               26 人格 × 3 轮扰动测试 SBTI
│   ├── install_skills.sh         一键引导脚本：克隆 26 个 skill 仓库 + 创建 symlink
│   ├── panel/
│   │   ├── ask.py                命令行：把一道题并行扔给所有已安装 skill
│   │   ├── server.py             支撑 dashboard 聊天面板的 HTTP/SSE 服务器
│   │   ├── build_dashboard.py    生成自包含 dashboard.html
│   │   ├── analyze_skills.py     对所有 SKILL.md 做结构化分析
│   │   └── README.md
│   ├── results/
│   │   ├── results.json          78 次 SBTI 评分（26 人格 × 3 轮扰动）
│   │   ├── report.md             稳定性测试报告
│   │   ├── skill_structure.json  每个 SKILL.md 的结构指标
│   │   ├── skill_analysis.md     结构 × SBTI 交叉分析
│   │   ├── dashboard.html        ⭐ 自包含交互 dashboard（~2 MB, SBTI 风格 UI）
│   │   └── panels/               panel 工具的历史问答记录
│   └── README.md                 完整子项目文档
│
├── .env.example                  OPENROUTER_API_KEY 模板
├── .gitignore
└── README.md                     ← 你正在看
```

### 🎭 26 人格 Skill Arena · 关键发现

同样的 32 题 SBTI 测试，这次的"考生"是从 GitHub 收集来的 **26 个 Claude Code Agent Skill**。每个 skill 都有自己的 `SKILL.md`（包含身份卡、心智模型、表达 DNA），通过把这套指令注入 Claude 的方式让它去做这道题。

**主要发现**：

- **Ilya Sutskever** 和 **米塞斯** 并列最高匹配度：**`BOSS` 领导者 93%**
- **齐泽克**是 26 人格里**唯一**落在 **`MONK` 僧人**格子的 —— 这恰好对应"翻出你没意识到的预设"型哲学家
- **SKILL.md 体量与 SBTI 相似度负相关**：ρ = **−0.09**。最小的三个 skill（丁元英 4 KB、米塞斯 6 KB、齐泽克 9 KB）拿到了 **83%–93%** 的高分，反而比那些 25 KB+ 的模板派更准
- **模板垄断**：26 个 skill 里有 13 个出自同一作者（`alchaincyf`）的同一套模板，**全部**落到 BOSS / CTRL / ATM-er 三角 —— 证明模板会机械地把人格输出收敛
- **特朗普 = `GOGO` 67%** —— 全场最低相似度。SBTI 量表里没有给"极高 H + 极低 L"组合留位置，只能放弃

→ 完整报告：[`persona_skill_arena/results/report.md`](persona_skill_arena/results/report.md)
→ 结构分析：[`persona_skill_arena/results/skill_analysis.md`](persona_skill_arena/results/skill_analysis.md)
→ 交互 dashboard：浏览器打开 [`persona_skill_arena/results/dashboard.html`](persona_skill_arena/results/dashboard.html)
→ 多人格实时圆桌：`cd persona_skill_arena && python3 panel/server.py`，然后访问 `http://localhost:8888`

### 如何复现 persona arena

```bash
cd persona_skill_arena
./install_skills.sh                      # 克隆 26 个 skill 仓库 + 建 symlink (~1 分钟)
python3 run_sbti.py                      # 重跑全部 26 人格的 SBTI
python3 panel/build_dashboard.py         # 重新生成 dashboard.html
python3 panel/server.py                  # 启动交互聊天服务器（http://localhost:8888）
```

26 个 skill **不内置**在本仓库里 —— 它们各自托管在自己的 GitHub 仓库，由 `install_skills.sh` 拉取。所有 persona 内容版权归各自的 skill 作者所有（详见 [`persona_skill_arena/README.md`](persona_skill_arena/README.md) 的"源仓库"列）。

---

## 🚀 60 秒复现

```bash
# 1. 克隆并进入
git clone https://github.com/ericshang98/sbti-model-personality-test.git
cd sbti-model-personality-test

# 2. （可选）验证离线评分内核能跑
cd sbti_scoring_system
python3 example.py
# pattern: MMM-MMM-MMM-MMM-MMM
# final:   OJBK  (无所谓人)
cd ..

# 3. 设置大模型测试环境
cd model_personality_test
python3 -m venv .venv
.venv/bin/pip install httpx

# 4. 配置 OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."   # 在 https://openrouter.ai/settings/keys 申请

# 5. 跑完整的 17 模型评测（约 10 分钟，约 $3 OpenRouter 额度）
cd src
../.venv/bin/python run_test.py

# 6. 打开可视化报告
open ../report.html
```

如果你想自定义测哪些模型，编辑 `model_personality_test/src/config.py` —— `MODELS` 就是一个 OpenRouter 模型 ID 列表。

---

## 🧪 一段话讲清方法论

每个模型用**独立的 API 调用**回答全部 32 道题（30 主题 + 2 隐藏），不共享对话历史，避免自我锚定。每题 **temperature=1.0 跑 3 次**，取 3 个字母答案的**众数**作为该模型最终答案。所有模型用同一份中文 system prompt：要求"作为一个有人格的个体回答，只输出 A/B/C"。**全部评分**（15 维 L/M/H pattern → 与 25 个标准 pattern 做曼哈顿距离匹配 → DRUNK/HHHH 兜底覆盖）由本地的 `sbti_scoring_system/sbti_score.py` 完成 —— LLM 不参与评分。推理模型给 `max_tokens=4000`，因为它们的隐藏思维 token 也算预算；OpenRouter 按实际用量计费而不是按上限。完整方法论和已知陷阱（位置偏差、语言偏差、模型版本漂移、限流等）见 [`model_personality_test/README.md`](model_personality_test/README.md)。

---

## 🧠 它实际上在测什么

> SBTI 测的不是人格，而是每个模型项目的 **RLHF 方向 × 训练数据文化先验 × 产品定位** 在一组玩梗题目上的投影。

你看到的"人格"其实是每个实验室三个工程决策的残留：

- **文化先验**（比如为什么三个中文模型都选了"白酒当白开水喝"，而英文训练的同行都选"小酌怡情"）
- **RLHF 方向**（比如为什么 GPT-5.x 从 MALO 跳到 BOSS，这刚好对应 OpenAI 从 *helpful assistant* 转向 *agentic assistant* 的产品定位变化）
- **产品定位**（比如为什么 Claude Opus 是冷眼旁观者、Sonnet 是审慎派、Haiku 是最暖最社交的 —— 刚好对应 Anthropic 三档模型的官方描述）

完整每个簇的解读见 [`model_personality_test/results/interpretation.md`](model_personality_test/results/interpretation.md)。

---

## 🙌 致谢

- **SBTI 原版** —— 题库、评分规则、人格插画、整套测试设计都来自 **B 站 [@蛆肉儿串儿](https://space.bilibili.com/)**，仓库 [`UnluckyNinja/SBTI-test`](https://github.com/UnluckyNinja/SBTI-test)。`sbti_scoring_system/data/` 和 `sbti_scoring_system/images/` 里的所有内容都来源于此。**所有原创功劳归原作者**。本仓库只是评分逻辑的 Python 移植 + 在它之上的一个 LLM/Agent 基准，仅供研究和教育用途。
- **人格 wiki / 类型描述** —— 参考自 [`serenakeyitan/sbti-wiki`](https://github.com/serenakeyitan/sbti-wiki)
- **厂商品牌图标** —— [`lobehub/lobe-icons`](https://github.com/lobehub/lobe-icons)，MIT 许可的 AI 品牌图标集
- **测试基础设施** —— [OpenRouter](https://openrouter.ai/) 提供 10 个模型厂商的统一访问
- **26 个人格 Skill** —— 由各自的作者独立写作并开源，详见 [`persona_skill_arena/README.md`](persona_skill_arena/README.md)。本仓库只做评测和聚合，不内置任何 skill 内容

如果你是 SBTI 的原作者，希望本仓库下架、修改或重新授权，请提一个 issue，我会立刻响应。

---

## 📄 许可

本仓库的代码（`sbti_score.py`、`extract_from_source.py`、`model_personality_test/src/` 下的所有内容、`build_report.py`、`persona_skill_arena/` 下的所有 Python 脚本、以及分析报告等）以 **MIT 协议**开源 —— 详见 [`LICENSE`](LICENSE)。

SBTI 的测试设计、题目、评分 pattern、人格插画的知识产权属于原作者，本仓库基于非商业研究/评论用途按合理使用纳入。它们**不**在本仓库代码的 MIT 协议覆盖范围内。
