# panel/ — 一题多答圆桌工具

把一个问题同时丢给 `.claude/skills/` 下**所有**已安装的人格 skill，每个 skill 用
它自己的 `SKILL.md` 做 system prompt，并行调用 `claude -p` 生成 in-character 回答。

**完全自动发现**：你往 `.claude/skills/` 里放新的 skill，这个工具就自动多一位选手，
**不用改代码**。

## 快速开始

```bash
cd /Users/eric/AI_development/SBTI/persona_skill_arena

# 列出当前安装的所有 skill
python panel/ask.py --list

# 最简单用法：一题丢给所有人
python panel/ask.py "我 28 岁月薪 8000 想辞职去北京做 AI，怎么办？"

# 只让其中几个回答
python panel/ask.py --only fengge,munger,zhangxuefeng "..."

# 排除某些人
python panel/ask.py --skip trump "..."

# 加一轮"综合总结"（共识/分歧/被忽略维度/一句话建议）
python panel/ask.py --synth "..."

# 用便宜点的模型跑
python panel/ask.py --model sonnet "..."

# 提高并发度
python panel/ask.py --workers 10 "..."

# 从 stdin 接问题
echo "今天该不该辞职" | python panel/ask.py --synth
```

## 输出

每次运行会把结果存到：

```
results/panels/panel-YYYYMMDD-HHMMSS.md    ← 人类可读报告
results/panels/panel-YYYYMMDD-HHMMSS.json  ← 机器可读原始数据
```

`json` 文件里有完整的每个 skill 的回答、运行时长、是否报错。

## 参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| `--list` | — | 只列出已安装 skill，不跑 |
| `--only a,b,c` | — | 只跑这几个 skill |
| `--skip a,b` | — | 排除这几个 skill |
| `--model` | `claude-opus-4-6` | 模型 alias 或 full id |
| `--workers` | `6` | 并发度 |
| `--timeout` | `180` | 每个 skill 的超时秒数 |
| `--synth` | off | 额外跑一轮综合总结 |
| `--no-save` | off | 不写文件，只打印 |

## 新增人格

1. 找一个你想加的 skill 仓库（比如 `awesome-persona-distill-skills` README 里的任何一个）
2. `git clone https://github.com/xxx/yyy-skill.git`（clone 到 `persona_skill_arena/` 下面）
3. `ln -s ../../yyy-skill .claude/skills/yyy`
4. 下次运行 `panel/ask.py` 它就自动出现在选手名单里

## 成本与速度

- 模型默认 Opus 4.6：14 个人格 × 并发 6 ≈ 30-90 秒完成一轮
- 换 Sonnet 4.6：同样条件 ≈ 15-40 秒，质量略降但仍很好
- 每题 14 人约消耗 ~50k-150k tokens

## 实现细节

- 每个 skill 的 `SKILL.md` 通过 `claude -p --append-system-prompt` 注入
- 禁用所有工具（`--tools ""`），强制人格只凭 LLM 输出，不会跑 WebSearch 之类
- 禁用 slash commands（`--disable-slash-commands`），避免 skill 相互污染
- 禁用 session 持久化（`--no-session-persistence`），保持干净

## 未来可扩展的玩法

- `vote` 模式：收回答后再发一轮让每个人格对别人的回答打分
- `debate` 模式：取立场最对立的两个人格做多轮辩论
- `advisor` 模式：先让用户做一遍 SBTI，根据 SBTI 结果自动挑 3 个互补人格回答
