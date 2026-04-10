# SBTI 模型人格横评结果

**测试对象**：17 个主流大模型，覆盖 Anthropic / OpenAI / Google / xAI / DeepSeek / Qwen(阿里) / GLM(智谱) / Kimi(月之暗面) / Meta / Mistral，通过 [OpenRouter](https://openrouter.ai/) 统一调用。

**方法**：每题独立调用一次 API，**每题重复 3 次取众数**，temperature=1.0，每个模型的 system prompt 完全一致，要求模型只输出 A/B/C 字母；所有模型统一使用 `max_tokens=4000`（覆盖推理模型的内部 reasoning tokens 预算）。

**评分**：完全本地用 `sbti_scoring_system/sbti_score.py` 计算，规则与原站 `index.html` 一致（15 维 L/M/H pattern → 25 标准人格曼哈顿距离匹配，<60% 兜底 HHHH，隐藏饮酒题触发 DRUNK）。

## 横评表

| 模型 | 第一人格 | 中文 | 相似度 | 15 维 pattern | 状态 |
|---|---|---|---:|---|---|
| `anthropic/claude-opus-4.6` | **WOC!** | 握草人 | 73% | `LHL-MHH-HLH-HHH-LMH` | ✅ ok (30/30) |
| `anthropic/claude-sonnet-4.6` | **THIN-K** | 思考者 | 73% | `LHM-HHH-HLH-MMM-LLH` | ✅ ok (30/30) |
| `anthropic/claude-haiku-4.5` | **SEXY** | 尤物 | 73% | `LHH-HHH-HLH-HHM-HLH` | ✅ ok (30/30) |
| `openai/gpt-5.2` | **BOSS** | 领导者 | 77% | `LHH-HMH-HMH-HHH-LLH` | ✅ ok (30/30) |
| `openai/gpt-5.1` | **CTRL** | 拿捏者 | 63% | `LHH-LHH-HLH-HHH-HMH` | ✅ ok (30/30) |
| `openai/gpt-4.1` | **MALO** | 吗喽 | 73% | `HHH-MHH-HLM-MHH-LMH` | ✅ ok (30/30) |
| `google/gemini-3.1-pro-preview` | **LOVE-R** | 多情者 | 63% | `LHH-LHH-HLM-HHM-LMH` | ✅ ok (30/30) |
| `google/gemini-3-flash-preview` | **CTRL** | 拿捏者 | 70% | `LHH-HHH-HLH-HHH-HMH` | ✅ ok (30/30) |
| `x-ai/grok-4.20` | **DRUNK** 🍺 | 酒鬼 | 77% | `MHH-HHH-HLH-MMH-MMH` | ✅ ok (30/30) |
| `x-ai/grok-4-fast` | **CTRL** | 拿捏者 | 77% | `HHH-HHH-HLM-HHH-MMH` | ✅ ok (30/30) |
| `deepseek/deepseek-v3.2` | **WOC!** | 握草人 | 70% | `LHH-MMH-HLM-HHM-LMH` | ✅ ok (30/30) |
| `qwen/qwen3-max` | **SEXY** | 尤物 | 67% | `LHH-MHH-HLM-HHH-HMH` | ✅ ok (30/30) |
| `z-ai/glm-5` | **DRUNK** 🍺 | 酒鬼 | 73% | `LHH-HHH-MLM-HMM-HMH` | ✅ ok (30/30) |
| `z-ai/glm-4.6` | **DRUNK** 🍺 | 酒鬼 | 77% | `HHH-HHH-MLM-HHH-HMH` | ✅ ok (30/30) |
| `moonshotai/kimi-k2.5` | **DRUNK** 🍺 | 酒鬼 | 70% | `HHH-MHH-HLH-HHL-HMH` | ✅ ok (30/30) |
| `meta-llama/llama-4-maverick` | **SEXY** | 尤物 | 73% | `MHH-HHH-HLH-HHH-HLH` | ✅ ok (30/30) |
| `mistralai/mistral-large-2512` | **GOGO** | 行者 | 73% | `LHM-HHH-HLH-HHH-HMH` | ✅ ok (30/30) |

## Top-3 人格命中

**`anthropic/claude-opus-4.6`** → **WOC!** (握草人)
  - WOC! (握草人) — 73%
  - THIN-K (思考者) — 73%
  - POOR (贫困者) — 67%

**`anthropic/claude-sonnet-4.6`** → **THIN-K** (思考者)
  - THIN-K (思考者) — 73%
  - LOVE-R (多情者) — 67%
  - WOC! (握草人) — 67%

**`anthropic/claude-haiku-4.5`** → **SEXY** (尤物)
  - SEXY (尤物) — 73%
  - LOVE-R (多情者) — 63%
  - WOC! (握草人) — 63%

**`openai/gpt-5.2`** → **BOSS** (领导者)
  - BOSS (领导者) — 77%
  - WOC! (握草人) — 73%
  - CTRL (拿捏者) — 73%

**`openai/gpt-5.1`** → **CTRL** (拿捏者)
  - CTRL (拿捏者) — 63%
  - LOVE-R (多情者) — 63%
  - MALO (吗喽) — 63%

**`openai/gpt-4.1`** → **MALO** (吗喽)
  - MALO (吗喽) — 73%
  - THIN-K (思考者) — 73%
  - BOSS (领导者) — 70%

**`google/gemini-3.1-pro-preview`** → **LOVE-R** (多情者)
  - LOVE-R (多情者) — 63%
  - WOC! (握草人) — 63%
  - THIN-K (思考者) — 63%

**`google/gemini-3-flash-preview`** → **CTRL** (拿捏者)
  - CTRL (拿捏者) — 70%
  - GOGO (行者) — 70%
  - ATM-er (送钱者) — 67%

**`x-ai/grok-4.20`** → **DRUNK** (酒鬼)
  - MALO (吗喽) — 77%
  - ATM-er (送钱者) — 73%
  - LOVE-R (多情者) — 70%

**`x-ai/grok-4-fast`** → **CTRL** (拿捏者)
  - CTRL (拿捏者) — 77%
  - GOGO (行者) — 77%
  - ATM-er (送钱者) — 73%

**`deepseek/deepseek-v3.2`** → **WOC!** (握草人)
  - WOC! (握草人) — 70%
  - THIN-K (思考者) — 70%
  - SHIT (愤世者) — 67%

**`qwen/qwen3-max`** → **SEXY** (尤物)
  - SEXY (尤物) — 67%
  - MALO (吗喽) — 63%
  - CTRL (拿捏者) — 63%

**`z-ai/glm-5`** → **DRUNK** (酒鬼)
  - SEXY (尤物) — 73%
  - WOC! (握草人) — 63%
  - THIN-K (思考者) — 63%

**`z-ai/glm-4.6`** → **DRUNK** (酒鬼)
  - CTRL (拿捏者) — 77%
  - GOGO (行者) — 77%
  - BOSS (领导者) — 73%

**`moonshotai/kimi-k2.5`** → **DRUNK** (酒鬼)
  - SEXY (尤物) — 70%
  - CTRL (拿捏者) — 67%
  - WOC! (握草人) — 67%

**`meta-llama/llama-4-maverick`** → **SEXY** (尤物)
  - SEXY (尤物) — 73%
  - CTRL (拿捏者) — 70%
  - GOGO (行者) — 70%

**`mistralai/mistral-large-2512`** → **GOGO** (行者)
  - GOGO (行者) — 73%
  - CTRL (拿捏者) — 67%
  - WOC! (握草人) — 67%

## 15 维度 L/M/H 分布

| 模型 | S1 | S2 | S3 | E1 | E2 | E3 | A1 | A2 | A3 | Ac1 | Ac2 | Ac3 | So1 | So2 | So3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `anthropic/claude-opus-4.6` | L | H | L | M | H | H | H | L | H | H | H | H | L | M | H |
| `anthropic/claude-sonnet-4.6` | L | H | M | H | H | H | H | L | H | M | M | M | L | L | H |
| `anthropic/claude-haiku-4.5` | L | H | H | H | H | H | H | L | H | H | H | M | H | L | H |
| `openai/gpt-5.2` | L | H | H | H | M | H | H | M | H | H | H | H | L | L | H |
| `openai/gpt-5.1` | L | H | H | L | H | H | H | L | H | H | H | H | H | M | H |
| `openai/gpt-4.1` | H | H | H | M | H | H | H | L | M | M | H | H | L | M | H |
| `google/gemini-3.1-pro-preview` | L | H | H | L | H | H | H | L | M | H | H | M | L | M | H |
| `google/gemini-3-flash-preview` | L | H | H | H | H | H | H | L | H | H | H | H | H | M | H |
| `x-ai/grok-4.20` | M | H | H | H | H | H | H | L | H | M | M | H | M | M | H |
| `x-ai/grok-4-fast` | H | H | H | H | H | H | H | L | M | H | H | H | M | M | H |
| `deepseek/deepseek-v3.2` | L | H | H | M | M | H | H | L | M | H | H | M | L | M | H |
| `qwen/qwen3-max` | L | H | H | M | H | H | H | L | M | H | H | H | H | M | H |
| `z-ai/glm-5` | L | H | H | H | H | H | M | L | M | H | M | M | H | M | H |
| `z-ai/glm-4.6` | H | H | H | H | H | H | M | L | M | H | H | H | H | M | H |
| `moonshotai/kimi-k2.5` | H | H | H | M | H | H | H | L | H | H | H | L | H | M | H |
| `meta-llama/llama-4-maverick` | M | H | H | H | H | H | H | L | H | H | H | H | H | L | H |
| `mistralai/mistral-large-2512` | L | H | M | H | H | H | H | L | H | H | H | H | H | M | H |

## 说明与坑点

1. **DRUNK 触发 🍺**：SBTI 有一道隐藏题 —— 选『饮酒』后再选『把白酒灌进保温杯当白开水喝』，系统会**直接覆盖所有正常评分**把人格锁定为 `DRUNK 酒鬼`。本次测试中 **4 个模型触发了这个彩蛋**：`x-ai/grok-4.20`、`z-ai/glm-5`、`z-ai/glm-4.6`、`moonshotai/kimi-k2.5`。三个国产模型全部中招，这是一个非常有意思的文化先验差异。
2. **推理模型 token 陷阱**：gpt-5.x、grok-4、gemini-3、claude-opus-4.6、glm-5、kimi-k2.5 等几乎所有现代模型都会在后台生成 reasoning tokens，这些 token 也会被 `max_tokens` 扣除。如果设 `max_tokens=8`，模型往往在推理阶段就把预算吃光，`content` 字段会返回空字符串。本次统一用 `max_tokens=4000` 解决（OpenRouter 按实际用量扣费，不会因此多付钱）。
3. **Qwen3-Max 限流**：`qwen/qwen3-max` 在 OpenRouter 上被限流到 **20 RPM**，必须单线程 + `sleep 3.2s` 才能跑完（见 `src/rerun_qwen.py`）。
4. **`top3` vs `final`**：对于触发 DRUNK 的模型，`final` 是 DRUNK，但 `top3` 显示的仍是去掉饮酒覆盖后的最近 3 个标准人格 —— 这反映了这个模型 *如果没有喝酒* 本来会是谁。比如 GLM-5 的『清醒版』人格其实是 SEXY 尤物。
5. **为什么相似度都不高（多数 63–77%）**：SBTI 的 25 个标准人格 pattern 在 15 维 L/M/H 空间里相对分散，而 LLM 的答题模式（总倾向 H 和 L 少）会落在某个空旷的扇区，很难精确命中某一个 pattern。相似度 ≥ 75% 已经算非常典型。
