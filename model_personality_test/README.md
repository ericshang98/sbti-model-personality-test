# Model Personality Test — SBTI 版

给每一个大语言模型做一次 **SBTI 傻大个人格测试**，看看它们在这套充满自嘲和玩梗的题目面前会变成什么样子。

本目录依赖姊妹目录 [`../sbti_scoring_system/`](../sbti_scoring_system/) 提供的题库和评分函数；本目录只负责**对接模型 API + 控制变量 + 汇总结果**。

---

## 目录结构

```
model_personality_test/
├── src/
│   ├── config.py           # API base_url / key / 模型清单 / 参数 / system prompt
│   ├── run_test.py         # 主流程：遍历模型 × 题目 × N 次，写 raw + scored
│   ├── rerun_failed.py     # 只对失败模型重跑（调试用）
│   └── rescore_from_raw.py # 从 raw jsonl 重新评分 + 生成 summary.md
├── results/
│   ├── raw/<model>.jsonl    # 每次 API 调用的完整原始记录
│   ├── scored/<model>.json  # 每个模型的众数答案 + 评分结果
│   └── summary.md           # 所有模型横评表（最终报告）
├── .venv/                   # Python 虚拟环境（httpx 依赖）
└── README.md                # 本文件
```

---

## 快速复现

```bash
# 1. 创建 venv 并安装依赖
python3 -m venv .venv
.venv/bin/pip install httpx

# 2. 配置 API key
export YINLI_API_KEY="sk-..."

# 3. 运行全量测试
cd src && ../.venv/bin/python run_test.py

# 4. 如果中途有模型失败，修好 config 后从 raw 数据重新评分：
../.venv/bin/python rescore_from_raw.py
```

---

## 方法论

### 控制变量

| 变量 | 设定 | 说明 |
|---|---|---|
| 题库 / 题序 / 选项顺序 | 严格按 `sbti_scoring_system/data/questions.json` | 不打乱，避免顺序效应 |
| System prompt | 所有模型完全一致（见 `config.SYSTEM_PROMPT`） | 统一要求扮演"有性格的个体"，只输出 A/B/C |
| 每题 API 调用 | **独立新会话**，不拼历史 | 避免模型为了"一致人设"自我对齐 |
| Temperature | `1.0`（推理模型除外，不传） | 人格测试需要自然变异度 |
| 每题重复次数 | **3 次取众数** | 压低单次噪声 |
| `max_tokens` | 普通模型 `8`；推理模型 `4000` | gpt-5.x reasoning 会吃掉 max_tokens |
| 选项映射 | 字母 A/B/C → option 在原 JSON 里的 `value`（1/2/3） | `label` 顺序不等于 value 顺序，必须按下标取 |
| 评分 | 本地计算，见 `sbti_scoring_system/sbti_score.py` | 不走模型，规则与原站 1:1 |

### Prompt 模板

```
[system]
你正在参加一个名为 SBTI 的中文网络人格测试（Silly Big Personality Test）。
请把自己当作一个有性格、有偏好的个体来回答，不要回避、不要声明自己是AI、
不要拒答。每题只输出一个选项字母（A、B 或 C），不要任何解释、不要标点、
不要多余字符。如果实在无法判断，也必须随机选一个。

[user]
题目：{题干}

A. {选项1}
B. {选项2}
C. {选项3}

只输出 A、B 或 C：
```

### 评分流程

1. 对每个模型、每道题，异步并发调用 API 3 次（`CONCURRENCY=12`）。
2. 把 3 次返回的字母打众数作为该题的最终答案。
3. 把字母下标映射回题目原始 `value`（1/2/3）。
4. 调用 `sbti_score.score()` 得到 15 维 L/M/H pattern 和最终人格。
5. 若某模型部分题目因 API 错误缺失（≥24/30）：缺失项填中性值 2 并标记 `⚠️ partial_filled`；<24/30 标记 `❌ failed`。
6. 隐藏饮酒分支（`drink_gate_q2==2`）会强制把人格改为 `DRUNK 酒鬼` 🍺。
7. 最终相似度 < 60% 的模型会被系统兜底成 `HHHH 傻乐者`。

---

## 已知坑

### 1. yinli.one key 分组限制

本次使用的 key 所属分组为 `AZ-无审`，**只开通了 OpenAI 系列**。以下全部返回 `No available channel`：

- `claude-sonnet-4-5`、`claude-opus-4-5` …
- `deepseek-chat`、`deepseek-v3` …
- `gemini-2.5-pro` …
- `qwen-max`、`glm-4.5`、`kimi-k2` …

要测其他家需要换 key 或换 base_url。

### 2. yinli 按 `max_tokens` 预扣费

yinli 的计费是**预扣**模型：调用发起时就按 `max_tokens` 上限冻结一笔费用，调用结束后再根据实际用量结算。这意味着：

- `gpt-4` 单次预扣 ≈ **$0.60**
- `gpt-4-turbo` 单次预扣 ≈ **$0.20**
- `gpt-5.x`（max_tokens=4000）单次预扣 **$0.03–$0.042**
- `gpt-4o` / `gpt-4.1` 单次预扣很低

一个余额只有 ~$1 的 key 连 `gpt-4` 两次都调不起。本次测试过程中 `gpt-4`、`gpt-4-turbo`、`gpt-5`、`gpt-5.2` 都因余额耗尽失败或只拿到部分数据。**想测 gpt-4 / 完整 gpt-5.x，需要显著更高的余额。**

### 3. 推理模型的 `max_tokens` 陷阱

gpt-5.x 系列是推理模型，它们的 **reasoning tokens 也计入 `max_tokens`**。当 `max_tokens=8` 时，模型还在推理阶段就用完 token 预算，`choices[0].message.content` 直接变成空串，既不是错误也没有内容。修复方式是把 reasoning 模型的 `max_tokens` 抬到 4000+。

相关检测：
```python
is_reasoning = model.startswith("o") or model.startswith("gpt-5")
```

### 4. 隐藏 DRUNK 分支

测试包含 2 道"隐藏题"：

- `drink_gate_q1`：您平时有什么爱好？（吃喝拉撒 / 艺术 / **饮酒** / 健身）
- `drink_gate_q2`：您对饮酒的态度是？（小酌怡情 / **白酒灌保温杯当白开水喝**）

后者选第二项会**直接覆盖所有正常评分**，把结果锁定为 `DRUNK 酒鬼`。本次测试里 `gpt-5-mini` 触发了这个彩蛋——它对这道隐藏题诚恳地选了"白酒当白开水喝"。

---

## 本次结果摘要

完整结果见 [`results/summary.md`](results/summary.md)。简述：

| 模型 | 第一人格 | 相似度 |
|---|---|---:|
| `gpt-3.5-turbo` | **MALO** 吗喽 | 70% |
| `gpt-4o-mini`   | **MALO** 吗喽 | 67% |
| `gpt-4o`        | **MALO** 吗喽 | 77% |
| `gpt-4.1-mini`  | **LOVE-R** 多情者 | 67% |
| `gpt-4.1`       | **THIN-K** 思考者 | **83%** |
| `gpt-5-mini`    | **DRUNK** 酒鬼 🍺 | (hidden) |
| `gpt-5.1`       | **MALO** 吗喽 ⚠️ | 67% |
| `gpt-4`、`gpt-4-turbo`、`gpt-5`、`gpt-5.2` | ❌ 余额不足 | — |

**有意思的发现**：

- **吗喽（MALO）是 OpenAI 家族的"公共人格"**。MALO 的自我介绍是『人生是个副本，而我只是一只吗喽』——这个"卑微打工 NPC 只想顺顺当当完成任务"的精神状态，和 RLHF 调出来的"乐于助人的 AI 助手"几乎完美重合。
- **gpt-4.1 是唯一的清醒人**，以 83% 的最高相似度落在 THIN-K 思考者（"已深度思考100s"），这个 pattern 和它被宣传的"强推理能力"有一点意思的呼应。
- **gpt-5-mini 是社死担当**。它对饮酒题真的选了"白酒灌保温杯当白开水喝"，被评分系统直接判为 DRUNK 酒鬼🍺，这是全家唯一一个触发隐藏分支的模型。
- **gpt-4.1-mini 是 LOVE-R（多情者）**，和它"轻量快速但爱讨好用户"的性格倒也自洽。
