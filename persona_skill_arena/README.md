# persona_skill_arena · 人格 Skill 竞技场

> **26 个 Claude Code 人格 Skill × SBTI 测试 × 可交互圆桌**
>
> 把网上散落的 26 个 "人格蒸馏" Skill 全部装进同一个 arena，
> 让它们做同一份 SBTI 人格测试，并行回答同一道难题，
> 然后看看**它们到底像谁、像不像、有多稳定**。

这是目前为止**人格蒸馏 skill 生态的第一份系统化测评**。所有数据、脚本、可视化都开源。

---

## 🎯 这个项目能做什么

1. **多人格 SBTI 测试**：让 26 个名人/虚构人物 skill 同时做一份 32 题的 SBTI 人格量表，用 3 套答案扰动测稳定性，看每个 skill 落到哪种人格类型。
2. **结构化分析每个 SKILL.md**：抽取大小、章节、心智模型数、引用数、模板家族等指标，做 SBTI × 结构的相关性分析。
3. **一题多答圆桌（panel）**：你问一个问题，**所有 26 个人格用各自的方式同时回答**，最后给出共识/分歧/被忽略维度的综合纪要。
4. **交互式 dashboard**：单文件 HTML，**SBTI 官方视觉风格**，可排序、可筛选、可点开看细节。配合本地 HTTP 服务器还可以**直接在网页里发问，流式接收所有人格的回答**。

---

## 📦 仓库结构

```
persona_skill_arena/
├── run_sbti.py                ← 26 人格 × 3 轮 SBTI 评分主脚本
├── install_skills.sh          ← 一键克隆 26 个 skill + 安装 symlink
│
├── panel/                     ← "圆桌"工具包
│   ├── ask.py                 ← 命令行：一题多答 (claude -p 并行调用)
│   ├── server.py              ← HTTP/SSE 服务器（dashboard 后端）
│   ├── build_dashboard.py     ← 生成自包含 dashboard.html
│   ├── analyze_skills.py      ← SKILL.md 结构分析器
│   └── README.md
│
├── results/                   ← 所有产物
│   ├── results.json           ← 26×3=78 次 SBTI 评分原始数据
│   ├── report.md              ← 稳定性测试人类可读报告
│   ├── skill_structure.json   ← 26 个 SKILL.md 的结构指标
│   ├── skill_analysis.md      ← 结构 × SBTI 交叉分析
│   ├── dashboard.html         ← 单文件交互页面 (~2 MB)
│   └── panels/                ← panel 圆桌的历史问答记录
│
└── .claude/skills/            ← (.gitignore) 26 个 skill 的 symlink
```

⚠️ **注意**：这 26 个 skill 都是别人 GitHub 上的独立仓库，本仓库**不包含**它们的源代码。运行 `./install_skills.sh` 会一键克隆全部并建立 symlink。

---

## 🚀 快速开始

```bash
git clone https://github.com/<你的用户名>/persona_skill_arena.git
cd persona_skill_arena

# 一键安装 26 个人格 skill（约 1 分钟）
chmod +x install_skills.sh
./install_skills.sh

# 验证
python3 panel/ask.py --list
# Installed skills (26): anuo, buffett, dingyuanying, fengge, ...

# (可选) 重新跑一遍 SBTI 评分
python3 run_sbti.py

# (可选) 重新生成 dashboard
python3 panel/build_dashboard.py

# 开聊天服务器（最好玩的）
python3 panel/server.py
# 然后浏览器打开 http://localhost:8888
```

---

## 🎭 26 个人格 + SBTI 结果

| 人物 | SBTI | 中文 | 相似度 | 源仓库 |
|---|:-:|---|---:|---|
| Ilya Sutskever | BOSS | 领导者 | **93%** | alchaincyf/ilya-sutskever-skill |
| 米塞斯 | BOSS | 领导者 | **93%** | LijiayuDeng/mises-perspective |
| 张一鸣 | CTRL | 拿捏者 | 90% | alchaincyf/zhang-yiming-skill |
| 丁元英 | BOSS | 领导者 | 90% | liangfeiiiii/ding-yuanying-skill |
| 罗翔 | ATM-er | 送钱者 | 90% | YixiaJack/luo-xiang-skill |
| 芒格 | BOSS | 领导者 | 87% | alchaincyf/munger-skill |
| Naval | BOSS | 领导者 | 87% | alchaincyf/naval-skill |
| 童锦程 | SEXY | 尤物 | 87% | hotcoffeeshake/tong-jincheng-skill |
| Rob Pike | BOSS | 领导者 | 87% | smallnest/rob-pike-skill |
| 乔布斯 | CTRL | 拿捏者 | 83% | alchaincyf/steve-jobs-skill |
| Elon Musk | BOSS | 领导者 | 83% | alchaincyf/elon-musk-skill |
| 巴菲特 | ATM-er | 送钱者 | 83% | will2025btc/buffett-perspective |
| Karpathy | ATM-er | 送钱者 | 83% | alchaincyf/karpathy-skill |
| Paul Graham | BOSS | 领导者 | 83% | alchaincyf/paul-graham-skill |
| 齐泽克 | **MONK** ⭐ | 僧人 | 83% | JikunR/zizek-skill |
| 户晨风 | POOR | 贫困者 | 80% | Janlaywss/hu-chenfeng-skill |
| 张雪峰 | CTRL | 拿捏者 | 80% | alchaincyf/zhangxuefeng-skill |
| 郭德纲 | SEXY | 尤物 | 80% | ByteRax/guodegang-skills |
| 塔勒布 | OH-NO | 哦不人 | 80% | alchaincyf/taleb-skill |
| 常熟阿诺 | SEXY | 尤物 | 77% | Ricardo-Vv/changshu-anuo |
| Karl Marx | CTRL | 拿捏者 | 77% | baojiachen0214/karlmarx-skill |
| MrBeast | CTRL | 拿捏者 | 77% | alchaincyf/mrbeast-skill |
| 毛泽东 | CTRL | 拿捏者 | 73% | leezythu/maoxuan-skill |
| 费曼 | ATM-er | 送钱者 | 73% | alchaincyf/feynman-skill |
| 峰哥亡命天涯 | SHIT | 愤世者 | 70% | rottenpen/fengge-wangmingtianya-perspective |
| 特朗普 | GOGO | 行者 | **67%** | alchaincyf/trump-skill |

完整 SBTI pattern + 3 轮稳定性见 [`results/report.md`](results/report.md)

---

## 🔬 关键发现

1. **体量与质量负相关**：SKILL.md 字节数和 SBTI 匹配度的 Pearson 相关系数为 **−0.09**。最小的 3 个 skill（丁元英 4 KB、米塞斯 6 KB、齐泽克 9 KB）反而拿到了 83-93% 的最高匹配度。
2. **alchaincyf 模板垄断**：26 个 skill 里 13 个来自同一作者的同一套模板，他们 SBTI 全部落在 BOSS/CTRL/ATM-er 三角。**模板决定了人格的"重力中心"**。
3. **虚构人物 > 真实人物**：丁元英（小说角色）90% > 芒格（真人）87%。**虚构人物是被作者极化过的，真人有噪声**。
4. **特朗普 67% 是 SBTI 的认输**：他的 pattern 同时有大量 H 和大量 L，25 种标准人格里没有这种"极高+极低"的格子。
5. **MONK 是齐泽克独占的格子**：26 人格只有他一个落在 MONK 僧人，因为他做的事是"翻出你没意识到的预设"——这是 MONK 的精确定义。

完整分析见 [`results/skill_analysis.md`](results/skill_analysis.md)

---

## 🛠 工具速查

```bash
# 命令行一题多答 (终端)
python3 panel/ask.py --synth "我该不该辞职"
python3 panel/ask.py --only fengge,munger,zizek "..."
python3 panel/ask.py --list

# 启动服务器 + 浏览器交互
python3 panel/server.py
open http://localhost:8888

# 重新跑 SBTI
python3 run_sbti.py

# 重新生成 dashboard
python3 panel/build_dashboard.py

# 重新分析 SKILL.md 结构
python3 panel/analyze_skills.py
```

---

## 📋 依赖

- Python 3.10+（标准库即可，**零第三方依赖**）
- `claude` CLI（Claude Code，用于 panel 真实调用）
- `git` （安装 skill 时）

---

## 🙏 致谢

- **SBTI 测试题库与评分规则**：B 站 [@蛆肉儿串儿](https://space.bilibili.com/) · 仓库 [`UnluckyNinja/SBTI-test`](https://github.com/UnluckyNinja/SBTI-test)
- **人格 Skill 总索引**：[`xixu-me/awesome-persona-distill-skills`](https://github.com/xixu-me/awesome-persona-distill-skills)
- **26 个 SKILL.md 的所有作者**：见上面表格的"源仓库"列。本项目只做评测和聚合，所有 skill 内容版权归原作者。

---

## 📄 许可

本仓库内的代码（`panel/`、`run_sbti.py`、`results/` 中的分析数据等）以 MIT 协议开源。
26 个被克隆的 skill 不在本仓库内，各自版权归原作者。
