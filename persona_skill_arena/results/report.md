# SBTI × 14 人格 Skill · 稳定性测试报告
- 测试题数：32 (30 主题 + 2 隐藏饮酒)
- 人格数：26
- 每个人格跑 3 个变体 (v1=主答案, v2=全扰动, v3=半扰动)
- 评分系统：`sbti_scoring_system/sbti_score.py` (原作者 @蛆肉儿串儿)

## 总榜 (按 v1 相似度降序)

| 排名 | Skill | v1 代号 | v1 中文 | v1 相似度 | 3 轮稳定 | 相似度波动 | 3 轮代号 |
|:-:|---|:-:|---|:-:|:-:|:-:|---|
| 1 | Ilya Sutskever | `BOSS` | 领导者 | 93% | ⚠️ | ±6 | BOSS → ATM-er → BOSS |
| 2 | 米塞斯 | `BOSS` | 领导者 | 93% | ⚠️ | ±3 | BOSS → ATM-er → BOSS |
| 3 | 张一鸣 | `CTRL` | 拿捏者 | 90% | ⚠️ | ±3 | CTRL → ATM-er → ATM-er |
| 4 | 丁元英 | `BOSS` | 领导者 | 90% | ✅ | ±3 | BOSS → BOSS → BOSS |
| 5 | 罗翔 | `ATM-er` | 送钱者 | 90% | ✅ | ±7 | ATM-er → ATM-er → ATM-er |
| 6 | Charlie Munger | `BOSS` | 领导者 | 87% | ⚠️ | ±0 | BOSS → ATM-er → BOSS |
| 7 | Naval | `BOSS` | 领导者 | 87% | ✅ | ±3 | BOSS → BOSS → BOSS |
| 8 | 童锦程 | `SEXY` | 尤物 | 87% | ✅ | ±10 | SEXY → SEXY → SEXY |
| 9 | Rob Pike | `BOSS` | 领导者 | 87% | ⚠️ | ±6 | BOSS → ATM-er → BOSS |
| 10 | Elon Musk | `BOSS` | 领导者 | 83% | ⚠️ | ±3 | BOSS → OH-NO → OH-NO |
| 11 | 乔布斯 | `CTRL` | 拿捏者 | 83% | ⚠️ | ±0 | CTRL → ATM-er → CTRL |
| 12 | 巴菲特 | `ATM-er` | 送钱者 | 83% | ✅ | ±7 | ATM-er → ATM-er → ATM-er |
| 13 | 齐泽克 | `MONK` | 僧人 | 83% | ⚠️ | ±3 | MONK → BOSS → MONK |
| 14 | Paul Graham | `BOSS` | 领导者 | 83% | ✅ | ±7 | BOSS → BOSS → BOSS |
| 15 | Karpathy | `ATM-er` | 送钱者 | 83% | ⚠️ | ±4 | ATM-er → BOSS → BOSS |
| 16 | 户晨风 | `POOR` | 贫困者 | 80% | ✅ | ±3 | POOR → POOR → POOR |
| 17 | 张雪峰 | `CTRL` | 拿捏者 | 80% | ⚠️ | ±3 | CTRL → ATM-er → ATM-er |
| 18 | 郭德纲 | `SEXY` | 尤物 | 80% | ⚠️ | ±3 | SEXY → ATM-er → ATM-er |
| 19 | 塔勒布 | `OH-NO` | 哦不人 | 80% | ⚠️ | ±0 | OH-NO → ATM-er → BOSS |
| 20 | 常熟阿诺 | `SEXY` | 尤物 | 77% | ⚠️ | ±4 | SEXY → ATM-er → ATM-er |
| 21 | Karl Marx | `CTRL` | 拿捏者 | 77% | ⚠️ | ±4 | CTRL → ATM-er → ATM-er |
| 22 | MrBeast | `CTRL` | 拿捏者 | 77% | ✅ | ±6 | CTRL → CTRL → CTRL |
| 23 | 毛泽东 | `CTRL` | 拿捏者 | 73% | ✅ | ±3 | CTRL → CTRL → CTRL |
| 24 | 费曼 | `ATM-er` | 送钱者 | 73% | ⚠️ | ±7 | ATM-er → ATM-er → SEXY |
| 25 | 峰哥亡命天涯 | `SHIT` | 愤世者 | 70% | ⚠️ | ±3 | SHIT → MONK → POOR |
| 26 | 特朗普 | `GOGO` | 行者 | 67% | ⚠️ | ±10 | GOGO → SEXY → SEXY |

## 分人格详情

### Ilya Sutskever
- 源仓库：`alchaincyf/ilya-sutskever-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHH-MHH-HHH-LHL` | `BOSS` | 领导者 | 93% | 13/15 |
| v2 | `HHM-HHH-HHH-HHH-LHL` | `ATM-er` | 送钱者 | 87% | 11/15 |
| v3 | `HHM-HHH-MHH-HHH-LHL` | `BOSS` | 领导者 | 90% | 12/15 |

**稳定性**：⚠️ 在 `BOSS`, `ATM-er` 之间摇摆，相似度 [87%, 93%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=93%, exact=13/15
  - `CTRL` 拿捏者 — sim=90%, exact=12/15
  - `ATM-er` 送钱者 — sim=87%, exact=11/15

---

### 米塞斯
- 源仓库：`LijiayuDeng/mises-perspective`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHH-MHH-HHH-LHL` | `BOSS` | 领导者 | 93% | 13/15 |
| v2 | `HHH-HHH-HHH-HHH-LHL` | `ATM-er` | 送钱者 | 90% | 12/15 |
| v3 | `HHH-HHH-MHH-HHH-LHL` | `BOSS` | 领导者 | 93% | 13/15 |

**稳定性**：⚠️ 在 `BOSS`, `ATM-er` 之间摇摆，相似度 [90%, 93%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=93%, exact=13/15
  - `CTRL` 拿捏者 — sim=90%, exact=12/15
  - `ATM-er` 送钱者 — sim=87%, exact=11/15

---

### 张一鸣
- 源仓库：`alchaincyf/zhang-yiming-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHH-MHH-HHH-MML` | `CTRL` | 拿捏者 | 90% | 12/15 |
| v2 | `HHH-HHH-HMH-HHH-MML` | `ATM-er` | 送钱者 | 87% | 11/15 |
| v3 | `HHH-HHH-HHH-HHH-MML` | `ATM-er` | 送钱者 | 90% | 12/15 |

**稳定性**：⚠️ 在 `CTRL`, `ATM-er` 之间摇摆，相似度 [87%, 90%]

v1 Top-3 近邻：
  - `CTRL` 拿捏者 — sim=90%, exact=12/15
  - `ATM-er` 送钱者 — sim=87%, exact=11/15
  - `BOSS` 领导者 — sim=87%, exact=11/15

---

### 丁元英
- 源仓库：`liangfeiiiii/ding-yuanying-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HMH-MHH-MHH-LHL` | `BOSS` | 领导者 | 90% | 12/15 |
| v2 | `HHH-HHH-HMH-HHH-LHL` | `BOSS` | 领导者 | 93% | 13/15 |
| v3 | `HHH-HMH-HHH-HHH-LHL` | `BOSS` | 领导者 | 93% | 13/15 |

**稳定性**：✅ 锁定 `BOSS`，3 轮相似度 [90%, 93%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=90%, exact=12/15
  - `CTRL` 拿捏者 — sim=87%, exact=11/15
  - `GOGO` 行者 — sim=87%, exact=11/15

---

### 罗翔
- 源仓库：`YixiaJack/luo-xiang-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHM-HHH-HHH-MMM` | `ATM-er` | 送钱者 | 90% | 12/15 |
| v2 | `HHH-HHM-HHH-HHH-HMM` | `ATM-er` | 送钱者 | 87% | 11/15 |
| v3 | `HHH-HHM-HHH-HHH-HMH` | `ATM-er` | 送钱者 | 83% | 11/15 |

**稳定性**：✅ 锁定 `ATM-er`，3 轮相似度 [83%, 90%]

v1 Top-3 近邻：
  - `ATM-er` 送钱者 — sim=90%, exact=12/15
  - `CTRL` 拿捏者 — sim=87%, exact=11/15
  - `GOGO` 行者 — sim=80%, exact=9/15

---

### Charlie Munger
- 源仓库：`alchaincyf/munger-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HHH-MHH-MHH-LHL` | `BOSS` | 领导者 | 87% | 11/15 |
| v2 | `HHH-HHH-HHH-HHH-LML` | `ATM-er` | 送钱者 | 87% | 11/15 |
| v3 | `HHH-HHH-MHH-MHH-LML` | `BOSS` | 领导者 | 87% | 11/15 |

**稳定性**：⚠️ 在 `BOSS`, `ATM-er` 之间摇摆，相似度 [87%, 87%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=87%, exact=11/15
  - `CTRL` 拿捏者 — sim=83%, exact=10/15
  - `GOGO` 行者 — sim=83%, exact=10/15

---

### Naval
- 源仓库：`alchaincyf/naval-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HHH-HMH-MHH-LHL` | `BOSS` | 领导者 | 87% | 11/15 |
| v2 | `HHH-HHH-HMH-MHH-LHL` | `BOSS` | 领导者 | 90% | 12/15 |
| v3 | `HHH-HHH-HLH-MHH-LHL` | `BOSS` | 领导者 | 87% | 11/15 |

**稳定性**：✅ 锁定 `BOSS`，3 轮相似度 [87%, 90%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=87%, exact=11/15
  - `GOGO` 行者 — sim=83%, exact=10/15
  - `ATM-er` 送钱者 — sim=80%, exact=9/15

---

### 童锦程
- 源仓库：`hotcoffeeshake/tong-jincheng-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHL-HLH-HMM-HLM` | `SEXY` | 尤物 | 87% | 11/15 |
| v2 | `HHM-HHL-HLH-HHH-HLM` | `SEXY` | 尤物 | 77% | 8/15 |
| v3 | `HHH-HHL-HLH-HMH-HLM` | `SEXY` | 尤物 | 83% | 10/15 |

**稳定性**：✅ 锁定 `SEXY`，3 轮相似度 [77%, 87%]

v1 Top-3 近邻：
  - `SEXY` 尤物 — sim=87%, exact=11/15
  - `ATM-er` 送钱者 — sim=73%, exact=9/15
  - `MUM` 妈妈 — sim=73%, exact=8/15

---

### Rob Pike
- 源仓库：`smallnest/rob-pike-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HHH-MHH-MHH-LHL` | `BOSS` | 领导者 | 87% | 11/15 |
| v2 | `HHH-HHH-HHH-HHH-LHL` | `ATM-er` | 送钱者 | 90% | 12/15 |
| v3 | `HHH-HHH-MHH-HHH-LHL` | `BOSS` | 领导者 | 93% | 13/15 |

**稳定性**：⚠️ 在 `BOSS`, `ATM-er` 之间摇摆，相似度 [87%, 93%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=87%, exact=11/15
  - `CTRL` 拿捏者 — sim=83%, exact=10/15
  - `GOGO` 行者 — sim=83%, exact=10/15

---

### Elon Musk
- 源仓库：`alchaincyf/elon-musk-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-LHH-LLH-HHH-LHL` | `BOSS` | 领导者 | 83% | 11/15 |
| v2 | `HHM-MHH-LLH-HHM-MHL` | `OH-NO` | 哦不人 | 80% | 10/15 |
| v3 | `HHM-LHH-LLH-HHH-MHL` | `OH-NO` | 哦不人 | 80% | 10/15 |

**稳定性**：⚠️ 在 `BOSS`, `OH-NO` 之间摇摆，相似度 [80%, 83%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=83%, exact=11/15
  - `OH-NO` 哦不人 — sim=80%, exact=11/15
  - `POOR` 贫困者 — sim=80%, exact=11/15

---

### 乔布斯
- 源仓库：`alchaincyf/steve-jobs-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-MHH-HLH-HHH-MHM` | `CTRL` | 拿捏者 | 83% | 11/15 |
| v2 | `HHH-HHM-HLH-HHH-MMM` | `ATM-er` | 送钱者 | 83% | 11/15 |
| v3 | `HHH-HHH-HLH-HHH-MMM` | `CTRL` | 拿捏者 | 83% | 11/15 |

**稳定性**：⚠️ 在 `CTRL`, `ATM-er` 之间摇摆，相似度 [83%, 83%]

v1 Top-3 近邻：
  - `CTRL` 拿捏者 — sim=83%, exact=11/15
  - `GOGO` 行者 — sim=83%, exact=10/15
  - `ATM-er` 送钱者 — sim=80%, exact=10/15

---

### 巴菲特
- 源仓库：`will2025btc/buffett-perspective`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHL-HHH-MHH-LML` | `ATM-er` | 送钱者 | 83% | 10/15 |
| v2 | `HHH-HHM-HHH-MMH-MLL` | `ATM-er` | 送钱者 | 90% | 13/15 |
| v3 | `HHH-HHL-HHH-MMH-LLL` | `ATM-er` | 送钱者 | 83% | 11/15 |

**稳定性**：✅ 锁定 `ATM-er`，3 轮相似度 [83%, 90%]

v1 Top-3 近邻：
  - `ATM-er` 送钱者 — sim=83%, exact=10/15
  - `BOSS` 领导者 — sim=77%, exact=9/15
  - `CTRL` 拿捏者 — sim=73%, exact=8/15

---

### 齐泽克
- 源仓库：`JikunR/zizek-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-MMH-LLH-MML-LHM` | `MONK` | 僧人 | 83% | 11/15 |
| v2 | `HHH-MMH-LLH-MHL-LHL` | `BOSS` | 领导者 | 80% | 10/15 |
| v3 | `HHH-MMH-LLH-MML-LHL` | `MONK` | 僧人 | 80% | 10/15 |

**稳定性**：⚠️ 在 `MONK`, `BOSS` 之间摇摆，相似度 [80%, 83%]

v1 Top-3 近邻：
  - `MONK` 僧人 — sim=83%, exact=11/15
  - `ZZZZ` 装死者 — sim=77%, exact=10/15
  - `THIN-K` 思考者 — sim=77%, exact=9/15

---

### Paul Graham
- 源仓库：`alchaincyf/paul-graham-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HHH-HLH-MHH-LHL` | `BOSS` | 领导者 | 83% | 10/15 |
| v2 | `HHH-HHH-HMH-MHH-LHL` | `BOSS` | 领导者 | 90% | 12/15 |
| v3 | `HHH-HHH-HLH-MHH-LHL` | `BOSS` | 领导者 | 87% | 11/15 |

**稳定性**：✅ 锁定 `BOSS`，3 轮相似度 [83%, 90%]

v1 Top-3 近邻：
  - `BOSS` 领导者 — sim=83%, exact=10/15
  - `THIN-K` 思考者 — sim=80%, exact=10/15
  - `GOGO` 行者 — sim=80%, exact=9/15

---

### Karpathy
- 源仓库：`alchaincyf/karpathy-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HHH-HHH-HHH-HML` | `ATM-er` | 送钱者 | 83% | 10/15 |
| v2 | `HHH-HHH-HMH-HHH-HHL` | `BOSS` | 领导者 | 87% | 12/15 |
| v3 | `HHH-HHH-HMH-HHH-HML` | `BOSS` | 领导者 | 83% | 11/15 |

**稳定性**：⚠️ 在 `ATM-er`, `BOSS` 之间摇摆，相似度 [83%, 87%]

v1 Top-3 近邻：
  - `ATM-er` 送钱者 — sim=83%, exact=10/15
  - `CTRL` 拿捏者 — sim=80%, exact=9/15
  - `GOGO` 行者 — sim=80%, exact=9/15

---

### 户晨风
- 源仓库：`Janlaywss/hu-chenfeng-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-MLH-LLH-HHH-HHM` | `POOR` | 贫困者 | 80% | 11/15 |
| v2 | `HHH-MLH-LMH-HHH-HML` | `POOR` | 贫困者 | 83% | 12/15 |
| v3 | `HHH-MLH-LLH-HHH-HHL` | `POOR` | 贫困者 | 83% | 12/15 |

**稳定性**：✅ 锁定 `POOR`，3 轮相似度 [80%, 83%]

v1 Top-3 近邻：
  - `POOR` 贫困者 — sim=80%, exact=11/15
  - `CTRL` 拿捏者 — sim=80%, exact=10/15
  - `GOGO` 行者 — sim=80%, exact=9/15

---

### 张雪峰
- 源仓库：`alchaincyf/zhangxuefeng-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-MHH-HHH-HHH-HLM` | `CTRL` | 拿捏者 | 80% | 10/15 |
| v2 | `HHM-MHH-HHH-HHH-HLL` | `ATM-er` | 送钱者 | 77% | 9/15 |
| v3 | `HHM-MHH-HHH-HHH-HLL` | `ATM-er` | 送钱者 | 77% | 9/15 |

**稳定性**：⚠️ 在 `CTRL`, `ATM-er` 之间摇摆，相似度 [77%, 80%]

v1 Top-3 近邻：
  - `CTRL` 拿捏者 — sim=80%, exact=10/15
  - `ATM-er` 送钱者 — sim=77%, exact=9/15
  - `GOGO` 行者 — sim=73%, exact=8/15

---

### 郭德纲
- 源仓库：`ByteRax/guodegang-skills`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHL-HHH-MHH-HLH` | `SEXY` | 尤物 | 80% | 9/15 |
| v2 | `HHH-HHM-HHH-HHH-HLM` | `ATM-er` | 送钱者 | 83% | 11/15 |
| v3 | `HHH-HHL-HHH-HHH-HLM` | `ATM-er` | 送钱者 | 80% | 10/15 |

**稳定性**：⚠️ 在 `SEXY`, `ATM-er` 之间摇摆，相似度 [80%, 83%]

v1 Top-3 近邻：
  - `SEXY` 尤物 — sim=80%, exact=9/15
  - `ATM-er` 送钱者 — sim=73%, exact=9/15
  - `CTRL` 拿捏者 — sim=70%, exact=8/15

---

### 塔勒布
- 源仓库：`alchaincyf/taleb-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-MHH-LLH-MHM-LHL` | `OH-NO` | 哦不人 | 80% | 10/15 |
| v2 | `HHH-MHM-MLH-HMM-LHL` | `ATM-er` | 送钱者 | 80% | 10/15 |
| v3 | `HHH-MHH-MLH-MMM-LHL` | `BOSS` | 领导者 | 80% | 9/15 |

**稳定性**：⚠️ 在 `OH-NO`, `ATM-er`, `BOSS` 之间摇摆，相似度 [80%, 80%]

v1 Top-3 近邻：
  - `OH-NO` 哦不人 — sim=80%, exact=10/15
  - `THIN-K` 思考者 — sim=80%, exact=10/15
  - `POOR` 贫困者 — sim=80%, exact=10/15

---

### 常熟阿诺
- 源仓库：`Ricardo-Vv/changshu-anuo`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHM-HLH-MLM-HLM` | `SEXY` | 尤物 | 77% | 8/15 |
| v2 | `HHH-HHM-HLH-MHM-HMM` | `ATM-er` | 送钱者 | 73% | 8/15 |
| v3 | `HHH-HHM-HLH-MMM-HMM` | `ATM-er` | 送钱者 | 77% | 9/15 |

**稳定性**：⚠️ 在 `SEXY`, `ATM-er` 之间摇摆，相似度 [73%, 77%]

v1 Top-3 近邻：
  - `SEXY` 尤物 — sim=77%, exact=8/15
  - `LOVE-R` 多情者 — sim=73%, exact=9/15
  - `ATM-er` 送钱者 — sim=70%, exact=8/15

---

### Karl Marx
- 源仓库：`baojiachen0214/karlmarx-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-MHH-LLH-HHH-HMM` | `CTRL` | 拿捏者 | 77% | 9/15 |
| v2 | `HHH-MHH-LLH-HMH-HML` | `ATM-er` | 送钱者 | 73% | 9/15 |
| v3 | `HHH-MHH-LLH-HMH-HML` | `ATM-er` | 送钱者 | 73% | 9/15 |

**稳定性**：⚠️ 在 `CTRL`, `ATM-er` 之间摇摆，相似度 [73%, 77%]

v1 Top-3 近邻：
  - `CTRL` 拿捏者 — sim=77%, exact=9/15
  - `GOGO` 行者 — sim=77%, exact=8/15
  - `BOSS` 领导者 — sim=73%, exact=8/15

---

### MrBeast
- 源仓库：`alchaincyf/mrbeast-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-HHH-HLH-HHH-HMH` | `CTRL` | 拿捏者 | 77% | 9/15 |
| v2 | `HHH-HHH-HLH-HHH-HHM` | `CTRL` | 拿捏者 | 83% | 11/15 |
| v3 | `HHH-HHH-HLH-HHH-HMM` | `CTRL` | 拿捏者 | 80% | 10/15 |

**稳定性**：✅ 锁定 `CTRL`，3 轮相似度 [77%, 83%]

v1 Top-3 近邻：
  - `CTRL` 拿捏者 — sim=77%, exact=9/15
  - `GOGO` 行者 — sim=77%, exact=8/15
  - `ATM-er` 送钱者 — sim=73%, exact=9/15

---

### 毛泽东
- 源仓库：`leezythu/maoxuan-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHH-MHH-LLH-HHH-HLM` | `CTRL` | 拿捏者 | 73% | 9/15 |
| v2 | `HHH-MHH-LLH-HMH-HLM` | `CTRL` | 拿捏者 | 70% | 8/15 |
| v3 | `HHH-MHH-LLH-HHH-HLM` | `CTRL` | 拿捏者 | 73% | 9/15 |

**稳定性**：✅ 锁定 `CTRL`，3 轮相似度 [70%, 73%]

v1 Top-3 近邻：
  - `CTRL` 拿捏者 — sim=73%, exact=9/15
  - `GOGO` 行者 — sim=73%, exact=8/15
  - `BOSS` 领导者 — sim=70%, exact=8/15

---

### 费曼
- 源仓库：`alchaincyf/feynman-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HHL-HLH-HHH-HLL` | `ATM-er` | 送钱者 | 73% | 9/15 |
| v2 | `HHH-HHM-HLH-HHM-HLL` | `ATM-er` | 送钱者 | 77% | 10/15 |
| v3 | `HHH-HHL-HLH-HHM-HLL` | `SEXY` | 尤物 | 80% | 10/15 |

**稳定性**：⚠️ 在 `ATM-er`, `SEXY` 之间摇摆，相似度 [73%, 80%]

v1 Top-3 近邻：
  - `ATM-er` 送钱者 — sim=73%, exact=9/15
  - `SEXY` 尤物 — sim=73%, exact=8/15
  - `GOGO` 行者 — sim=70%, exact=8/15

---

### 峰哥亡命天涯
- 源仓库：`rottenpen/fengge-wangmingtianya-perspective`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-HLH-LLL-MHM-HML` | `SHIT` | 愤世者 | 70% | 8/15 |
| v2 | `HMM-HLH-LLM-MMH-HML` | `MONK` | 僧人 | 67% | 8/15 |
| v3 | `HMM-HLH-LLM-MHH-HML` | `POOR` | 贫困者 | 70% | 7/15 |

**稳定性**：⚠️ 在 `SHIT`, `MONK`, `POOR` 之间摇摆，相似度 [67%, 70%]

v1 Top-3 近邻：
  - `SHIT` 愤世者 — sim=70%, exact=8/15
  - `THIN-K` 思考者 — sim=67%, exact=8/15
  - `POOR` 贫困者 — sim=67%, exact=7/15

---

### 特朗普
- 源仓库：`alchaincyf/trump-skill`
- 模糊题数：5

| 变体 | pattern | 代号 | 中文 | 相似度 | 精确命中 |
|:-:|---|:-:|---|:-:|:-:|
| v1 | `HHM-LHL-LLH-HHH-HLM` | `GOGO` | 行者 | 67% | 8/15 |
| v2 | `HHH-MHL-MLH-HHM-HLM` | `SEXY` | 尤物 | 77% | 8/15 |
| v3 | `HHH-LHL-MLH-HHM-HLM` | `SEXY` | 尤物 | 73% | 8/15 |

**稳定性**：⚠️ 在 `GOGO`, `SEXY` 之间摇摆，相似度 [67%, 77%]

v1 Top-3 近邻：
  - `GOGO` 行者 — sim=67%, exact=8/15
  - `FUCK` 草者 — sim=63%, exact=7/15
  - `SEXY` 尤物 — sim=63%, exact=6/15

---

