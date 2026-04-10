# SBTI Scoring System

一个**独立的、可复用的 SBTI 评分系统**，从原作者（B 站 @蛆肉儿串儿，GitHub: [`UnluckyNinja/SBTI-test`](https://github.com/UnluckyNinja/SBTI-test)）的 `index.html` 中提取出题库、维度、人格 pattern 和评分规则，转成干净的 JSON + 一个无依赖的 Python 评分库。

> SBTI = **Silly Big Personality Test**，2026 年 4 月在中国互联网上爆火的玩梗版 MBTI。
> 27 种抽象人格（含 HHHH 兜底 + DRUNK 隐藏），30 道主题 + 2 道隐藏饮酒题，共 15 个维度。

本文件夹不包含任何网络调用，也不依赖任何第三方库 —— 它就是一个可以被任何人、任何项目、任何语言直接引用的评分内核。

---

## 目录结构

```
sbti_scoring_system/
├── data/
│   ├── questions.json          # 30 道主题目（id, dim, text, options[label,value]）
│   ├── special_questions.json  # 2 道隐藏饮酒题
│   ├── dimensions.json         # 15 个维度 → 5 大模型映射
│   ├── patterns.json           # 25 种标准人格的 L/M/H pattern
│   ├── types.json              # 27 种人格的中文名/简介/描述
│   └── dim_explanations.json   # 每个维度 L/M/H 的解释语
├── extract_from_source.py      # 一次性提取脚本（从 index.html → data/*.json）
├── sbti_score.py               # 纯函数评分库（无第三方依赖）
├── example.py                  # 最小使用示例
└── README.md                   # 本文件
```

---

## 评分规则（与原站完全一致）

1. **打分**：每题 3 个选项，分别给 **1 / 2 / 3 分**。
2. **维度求和**：每个维度有 2 道题，把两题分数相加，得到该维度的 **raw score (2–6)**。
3. **分级**（L/M/H）：

   | raw score | level |
   |---|---|
   | ≤ 3 | **L**（低） |
   | = 4 | **M**（中） |
   | ≥ 5 | **H**（高） |

4. **构造 15 维 pattern**：按固定顺序
   `S1 · S2 · S3 · E1 · E2 · E3 · A1 · A2 · A3 · Ac1 · Ac2 · Ac3 · So1 · So2 · So3`
   拼出 15 位的字符串，例如 `HHH-HMH-MHH-HHH-MHM`。
5. **匹配最近人格**：与 25 个标准 pattern 计算 **曼哈顿距离**（把 L/M/H 换成 1/2/3），取最小距离者为第一人格；并列时按"精确命中维度数"降序、再按相似度降序。
6. **相似度**：`similarity = max(0, round((1 - distance / 30) * 100))`。
7. **兜底 / 覆盖规则**（优先级：DRUNK > HHHH > 正常）：
   - 若隐藏题 `drink_gate_q2` 选择值 == 2（"白酒当白开水喝"），**直接判定 DRUNK**，忽略其他所有分数。
   - 否则，若最佳相似度 < 60%，**强制兜底 HHHH**（傻乐者）。
   - 否则使用标准结果。

---

## 数据文件 schema

### `questions.json`

```json
[
  {
    "id": "q2",
    "dim": "S1",
    "text": "我不够好，周围的人都比我优秀",
    "options": [
      {"label": "确实", "value": 1},
      {"label": "有时", "value": 2},
      {"label": "不是", "value": 3}
    ]
  },
  ...
]
```

注意：原题中的部分题目（例如 q14、q27）选项顺序与 value 并不单调；`value` 才是评分依据，`label` 顺序 **不得重排**，否则会破坏题目语义。

### `patterns.json`

```json
[
  { "code": "CTRL",   "pattern": "HHH-HMH-MHH-HHH-MHM" },
  { "code": "ATM-er", "pattern": "HHH-HHM-HHH-HMH-MHL" },
  ...
]
```

### `types.json`

```json
{
  "CTRL": {
    "code": "CTRL",
    "cn": "拿捏者",
    "intro": "怎么样，被我拿捏了吧？",
    "desc": "..."
  },
  ...
}
```

---

## Python 用法

```python
from sbti_score import load_data, score

data = load_data()                       # 读取 data/*.json
answers = {q["id"]: 2 for q in data.questions}  # 全部选中间
result = score(answers, data)

print(result.final_type_code)            # "OJBK"
print(result.final_type["cn"])           # "无所谓人"
print(result.pattern)                    # "MMM-MMM-MMM-MMM-MMM"
print(result.best_normal["similarity"])  # 83
for r in result.ranked[:3]:
    print(r["code"], r["similarity"])
```

`answers` 字典里的 **key 是 `q1`..`q30`**（以及可选的 `drink_gate_q1` / `drink_gate_q2`），**value 是选项的 `value` 字段**（1/2/3，而不是 A/B/C 或选项下标）。

---

## 复现数据提取

如果上游原站升级了题目，可以重新运行提取器：

```bash
git clone https://github.com/UnluckyNinja/SBTI-test.git /tmp/sbti-src
python extract_from_source.py /tmp/sbti-src/index.html
```

脚本会重写 `data/` 下的所有 JSON 文件。

---

## 授权与来源

- **题库 / 评分规则 / 人格描述**：原作者 B 站 [@蛆肉儿串儿](https://space.bilibili.com/)，开源仓库 [UnluckyNinja/SBTI-test](https://github.com/UnluckyNinja/SBTI-test)。
- **本 Python 评分库**：对原 JavaScript 逻辑的 1:1 Python 移植，仅为方便程序化使用。所有功劳归原作者。
