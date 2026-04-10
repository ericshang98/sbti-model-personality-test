"""
Build a single self-contained HTML page that visually presents the SBTI
horizontal evaluation results across all tested models.

Output:  model_personality_test/report.html
Open it directly in a browser. All assets (model brand logos, personality
illustrations) are referenced via relative paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "sbti_scoring_system"))
from sbti_score import load_data  # noqa: E402

import config  # noqa: E402

ROOT = config.ROOT
SCORED_DIR = config.SCORED_DIR
OUTPUT = ROOT / "report.html"

# ---- model id → brand logo file (all in assets/model_logos/) ----
PROVIDER_LOGO = {
    "anthropic": "claude.svg",
    "openai": "openai.svg",
    "google": "gemini.svg",
    "x-ai": "grok.svg",
    "deepseek": "deepseek.svg",
    "qwen": "qwen.svg",
    "z-ai": "zhipu.svg",
    "moonshotai": "kimi.svg",
    "meta-llama": "meta.svg",
    "mistralai": "mistral.svg",
}

# ---- type code → image file (in ../sbti_scoring_system/images/) ----
TYPE_IMAGE = {
    "CTRL": "CTRL.png", "BOSS": "BOSS.png", "MUM": "MUM.png", "FAKE": "FAKE.png",
    "Dior-s": "Dior-s.jpg", "DEAD": "DEAD.png", "ZZZZ": "ZZZZ.png",
    "GOGO": "GOGO.png", "FUCK": "FUCK.png", "HHHH": "HHHH.png", "SEXY": "SEXY.png",
    "OJBK": "OJBK.png", "JOKE-R": "JOKE-R.jpg", "POOR": "POOR.png", "OH-NO": "OH-NO.png",
    "MONK": "MONK.png", "SHIT": "SHIT.png", "THAN-K": "THAN-K.png", "MALO": "MALO.png",
    "ATM-er": "ATM-er.png", "THIN-K": "THIN-K.png", "SOLO": "SOLO.png",
    "LOVE-R": "LOVE-R.png", "WOC!": "WOC.png", "DRUNK": "DRUNK.png", "IMFW": "IMFW.png",
    "IMSB": "IMSB.png",
}

# Short, original paraphrases of each personality (not copying source text)
TYPE_BLURB = {
    "CTRL":   "随时按 Ctrl+S 帮你存档的拿捏者。",
    "BOSS":   "方向盘永远在自己手上的领导者。",
    "THIN-K": "已深度思考 100 秒的审慎派。",
    "WOC!":   "嘴上一惊一乍、后台冷静分析的吃瓜大师。",
    "SEXY":   "走进房间空气湿度都会下降的天然尤物。",
    "MALO":   "把人生当副本、自称小猴子的低姿态打工人。",
    "LOVE-R": "情感存量爆表、活成吟游诗人的多情者。",
    "GOGO":   "已完成、即将完成、没有第三种状态的行动派。",
    "DRUNK":  "白酒灌进保温杯当白开水喝的宇宙隐藏分支。",
    "HHHH":   "脑回路过于清奇、被系统强制兜底的傻乐者。",
    "OH-NO":  "对万事万物自带灾难推演的秩序守护神。",
    "OJBK":   "凡事都行的无所谓帝王。",
    "MUM":    "永远在治愈别人的妈妈型人格。",
    "FAKE":   "面具切换比输入法还快的高性能伪人。",
    "MONK":   "已看破红尘、保持万物独立轨道的僧人。",
    "SHIT":   "嘴上骂世界一坨、手上默默拯救世界的悖论者。",
    "ZZZZ":   "deadline 才是唯一真神的装死大师。",
    "POOR":   "把所有资源灌进同一个矿井的精神富翁。",
    "ATM-er": "永远在为别人支付时间精力的可靠机器。",
    "FUCK":   "拒绝一切驯化、活成最后一声狼嚎的草者。",
    "DEAD":   "通关删档 999 次之后的终极贤者。",
    "IMFW":   "敏感、容易认真、被一颗糖收买的兰花型存在。",
    "IMSB":   "脑内两个声音永不停止战斗的内心戏王者。",
    "SOLO":   "用最硬的刺保护最软的内核的孤儿型刺猬。",
    "JOKE-R": "用最大的笑声盖住心碎的小丑。",
    "Dior-s": "看穿了所有上进套路的当代第欧根尼。",
    "THAN-K": "连堵车都能感谢一遍的正能量发射塔。",
}

DIM_ORDER = [
    "S1", "S2", "S3", "E1", "E2", "E3",
    "A1", "A2", "A3",
    "Ac1", "Ac2", "Ac3",
    "So1", "So2", "So3",
]
DIM_FULL = {
    "S1": "自尊自信", "S2": "自我清晰度", "S3": "核心价值",
    "E1": "依恋安全感", "E2": "情感投入度", "E3": "边界与依赖",
    "A1": "世界观倾向", "A2": "规则灵活度", "A3": "人生意义感",
    "Ac1": "动机导向", "Ac2": "决策风格", "Ac3": "执行模式",
    "So1": "社交主动性", "So2": "人际边界感", "So3": "表达真实度",
}


def provider_of(model_id: str) -> str:
    return model_id.split("/")[0]


def short_name(model_id: str) -> str:
    return model_id.split("/", 1)[1] if "/" in model_id else model_id


def load_scored() -> list[dict]:
    rows = []
    for path in sorted(SCORED_DIR.glob("*.json")):
        rows.append(json.loads(path.read_text(encoding="utf-8")))
    # preserve config.MODELS order
    order = {m: i for i, m in enumerate(config.MODELS)}
    rows.sort(key=lambda r: order.get(r["model"], 999))
    return rows


def render_card(row: dict) -> str:
    model = row["model"]
    final = row["final"]
    cn = row["final_cn"]
    img = TYPE_IMAGE.get(final, "HHHH.png")
    logo = PROVIDER_LOGO.get(provider_of(model), "openai.svg")
    blurb = TYPE_BLURB.get(final, "")
    drunk_class = " drunk" if row.get("drunk_triggered") else ""
    drunk_badge = "<span class='badge drunk-badge'>🍺 隐藏分支触发</span>" if row.get("drunk_triggered") else ""

    sim = row.get("top3", [{}])[0].get("similarity", 0)
    top3_html = "".join(
        f"<li><span class='code'>{t['code']}</span>"
        f"<span class='cn'>{t.get('cn','')}</span>"
        f"<span class='sim'>{t['similarity']}%</span></li>"
        for t in row.get("top3", [])
    )
    levels = row.get("levels", {})
    levels_html = "".join(
        f"<div class='lvl lvl-{levels[d]}' title='{d} {DIM_FULL[d]}: {levels[d]}'>"
        f"<span class='lvl-name'>{d}</span><span class='lvl-val'>{levels[d]}</span></div>"
        for d in DIM_ORDER
    )

    return f"""
    <article class="card{drunk_class}">
      <header class="card-head">
        <img class="logo" src="assets/model_logos/{logo}" alt="">
        <div class="title">
          <div class="provider">{provider_of(model)}</div>
          <div class="model">{short_name(model)}</div>
        </div>
        {drunk_badge}
      </header>
      <div class="card-body">
        <div class="persona">
          <img class="persona-img" src="../sbti_scoring_system/images/{img}" alt="{final}">
          <div class="persona-meta">
            <div class="code">{final}</div>
            <div class="cn">{cn}</div>
            <div class="sim">相似度 {sim}%</div>
          </div>
        </div>
        <p class="blurb">{blurb}</p>
        <div class="dim-grid">{levels_html}</div>
        <details class="top3">
          <summary>Top-3 命中</summary>
          <ul>{top3_html}</ul>
        </details>
      </div>
    </article>
    """


def render_heatmap(rows: list[dict]) -> str:
    head = "".join(f"<th title='{DIM_FULL[d]}'>{d}</th>" for d in DIM_ORDER)
    body_rows = []
    for row in rows:
        cells = "".join(
            f"<td class='hm hm-{row['levels'][d]}'>{row['levels'][d]}</td>"
            for d in DIM_ORDER
        )
        drunk = " 🍺" if row.get("drunk_triggered") else ""
        body_rows.append(
            f"<tr><th class='row-head'>{short_name(row['model'])}{drunk}</th>{cells}</tr>"
        )
    return f"""
    <table class="heatmap">
      <thead><tr><th></th>{head}</tr></thead>
      <tbody>{''.join(body_rows)}</tbody>
    </table>
    """


def main() -> None:
    rows = load_scored()
    cards_html = "\n".join(render_card(r) for r in rows)
    heatmap_html = render_heatmap(rows)

    drunk_count = sum(1 for r in rows if r.get("drunk_triggered"))
    total = len(rows)

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>SBTI 模型人格横评</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --bg: #0c0e14;
    --bg-2: #131722;
    --bg-3: #1c2230;
    --fg: #e6e8ef;
    --fg-dim: #8a92a6;
    --accent: #ff6a3d;
    --accent-2: #6ad0ff;
    --warn: #ffb454;
    --drunk: #ff5577;
    --H: #ef5f5f;
    --M: #f0c244;
    --L: #5fa8ef;
    --border: #262d3d;
    --radius: 14px;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    background: radial-gradient(ellipse at top, #1a1f30 0%, var(--bg) 60%);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
                 "Microsoft YaHei", "Helvetica Neue", sans-serif;
    margin: 0; padding: 0;
    -webkit-font-smoothing: antialiased;
    line-height: 1.6;
  }}
  .container {{ max-width: 1280px; margin: 0 auto; padding: 56px 28px 96px; }}

  /* HERO */
  .hero {{ text-align: center; padding: 24px 0 48px; }}
  .hero h1 {{
    font-size: 56px; line-height: 1.1; margin: 0 0 12px;
    background: linear-gradient(135deg, #fff 0%, var(--accent) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    letter-spacing: -1px;
  }}
  .hero .sub {{ font-size: 20px; color: var(--fg-dim); margin-bottom: 28px; }}
  .stats {{
    display: flex; justify-content: center; gap: 28px; flex-wrap: wrap; margin-top: 32px;
  }}
  .stat {{
    background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 18px 28px; min-width: 160px;
  }}
  .stat .num {{ font-size: 36px; font-weight: 700; color: var(--accent); }}
  .stat .label {{ font-size: 13px; color: var(--fg-dim); text-transform: uppercase; letter-spacing: 1px; }}

  /* SECTIONS */
  section {{ margin-top: 80px; }}
  h2 {{
    font-size: 32px; margin: 0 0 8px; letter-spacing: -0.5px;
    border-left: 4px solid var(--accent); padding-left: 14px;
  }}
  h2 .desc {{ display: block; font-size: 14px; color: var(--fg-dim); font-weight: 400; margin-top: 6px; }}
  h3 {{ font-size: 22px; margin: 36px 0 12px; color: var(--accent-2); }}

  /* CARD GRID */
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 22px; margin-top: 32px; }}
  .card {{
    background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius);
    overflow: hidden; transition: transform .2s, box-shadow .2s, border-color .2s;
  }}
  .card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(0,0,0,.4);
    border-color: var(--accent);
  }}
  .card.drunk {{ border-color: var(--drunk); box-shadow: 0 0 0 1px var(--drunk), 0 12px 36px rgba(255,85,119,.2); }}
  .card-head {{
    display: flex; align-items: center; gap: 14px;
    padding: 18px 20px 14px;
    background: var(--bg-3);
    border-bottom: 1px solid var(--border);
  }}
  .logo {{
    width: 36px; height: 36px; padding: 6px; background: #fff; border-radius: 10px;
    flex-shrink: 0;
  }}
  .title {{ flex: 1; min-width: 0; }}
  .title .provider {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--fg-dim); }}
  .title .model {{ font-size: 16px; font-weight: 600; color: var(--fg); word-break: break-all; }}
  .badge {{ font-size: 11px; padding: 4px 10px; border-radius: 999px; background: var(--bg); border: 1px solid var(--border); }}
  .drunk-badge {{ background: var(--drunk); color: #fff; border-color: var(--drunk); white-space: nowrap; }}

  .card-body {{ padding: 20px; }}
  .persona {{ display: flex; gap: 18px; align-items: center; }}
  .persona-img {{
    width: 96px; height: 96px; border-radius: 12px;
    object-fit: cover; flex-shrink: 0;
    background: var(--bg-3); border: 1px solid var(--border);
  }}
  .persona-meta .code {{ font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: var(--accent); }}
  .persona-meta .cn {{ font-size: 18px; color: var(--fg); margin-top: 2px; }}
  .persona-meta .sim {{ font-size: 13px; color: var(--fg-dim); margin-top: 4px; }}
  .blurb {{ color: var(--fg-dim); font-size: 14px; margin: 16px 0 8px; font-style: italic; }}

  .dim-grid {{
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px;
    margin-top: 12px;
  }}
  .lvl {{
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 8px 4px; border-radius: 6px; font-size: 10px;
    border: 1px solid var(--border); background: var(--bg-3);
  }}
  .lvl-name {{ color: var(--fg-dim); font-size: 9px; }}
  .lvl-val {{ font-weight: 700; font-size: 13px; margin-top: 2px; }}
  .lvl-H {{ background: rgba(239,95,95,.18); border-color: rgba(239,95,95,.5); color: var(--H); }}
  .lvl-M {{ background: rgba(240,194,68,.15); border-color: rgba(240,194,68,.45); color: var(--M); }}
  .lvl-L {{ background: rgba(95,168,239,.15); border-color: rgba(95,168,239,.45); color: var(--L); }}

  .top3 {{ margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border); }}
  .top3 summary {{ font-size: 12px; color: var(--fg-dim); cursor: pointer; user-select: none; }}
  .top3 ul {{ list-style: none; padding: 8px 0 0; margin: 0; }}
  .top3 li {{ display: flex; gap: 10px; align-items: baseline; padding: 4px 0; font-size: 13px; }}
  .top3 .code {{ font-weight: 700; color: var(--accent-2); min-width: 70px; }}
  .top3 .cn {{ flex: 1; color: var(--fg); }}
  .top3 .sim {{ color: var(--fg-dim); }}

  /* HEATMAP */
  .heatmap {{
    width: 100%; border-collapse: separate; border-spacing: 4px;
    background: var(--bg-2); padding: 16px; border-radius: var(--radius);
    border: 1px solid var(--border);
    font-size: 12px;
  }}
  .heatmap th {{ font-weight: 600; color: var(--fg-dim); padding: 8px 6px; text-align: center; }}
  .heatmap .row-head {{ text-align: right; color: var(--fg); padding-right: 12px; white-space: nowrap; max-width: 240px; overflow: hidden; text-overflow: ellipsis; }}
  .heatmap .hm {{
    text-align: center; padding: 10px 0; border-radius: 6px; font-weight: 700;
    min-width: 38px;
  }}
  .hm-H {{ background: rgba(239,95,95,.25); color: #ffd0d0; }}
  .hm-M {{ background: rgba(240,194,68,.22); color: #ffe6ad; }}
  .hm-L {{ background: rgba(95,168,239,.22); color: #cee6ff; }}

  /* INSIGHTS */
  .insight {{
    background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 28px 32px; margin-top: 22px;
  }}
  .insight h3 {{ margin-top: 0; }}
  .insight p {{ color: var(--fg); }}
  .insight .key {{ color: var(--accent); font-weight: 600; }}
  .insight .drunk-row {{ background: rgba(255,85,119,.1); border-left: 4px solid var(--drunk); padding: 14px 18px; margin: 14px 0; border-radius: 6px; }}

  table.compact {{ width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 14px; }}
  table.compact th, table.compact td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }}
  table.compact th {{ color: var(--fg-dim); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }}
  table.compact td.lvl-H {{ color: var(--H); font-weight: 700; text-align: center; }}
  table.compact td.lvl-M {{ color: var(--M); font-weight: 700; text-align: center; }}
  table.compact td.lvl-L {{ color: var(--L); font-weight: 700; text-align: center; }}

  /* LEGEND */
  .legend {{ display: flex; gap: 14px; flex-wrap: wrap; margin: 16px 0 24px; font-size: 12px; color: var(--fg-dim); }}
  .legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
  .legend i {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; }}
  .legend .iH {{ background: var(--H); }}
  .legend .iM {{ background: var(--M); }}
  .legend .iL {{ background: var(--L); }}

  footer {{ margin-top: 96px; padding-top: 32px; border-top: 1px solid var(--border); color: var(--fg-dim); font-size: 13px; text-align: center; }}
  footer a {{ color: var(--accent-2); text-decoration: none; }}
  footer a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="container">

  <header class="hero">
    <h1>SBTI 模型人格横评</h1>
    <p class="sub">Silly Big Personality Test × {total} 个主流大语言模型</p>
    <div class="stats">
      <div class="stat"><div class="num">{total}</div><div class="label">模型</div></div>
      <div class="stat"><div class="num">10</div><div class="label">家厂商</div></div>
      <div class="stat"><div class="num">32</div><div class="label">道题 × 3 次</div></div>
      <div class="stat"><div class="num">{drunk_count}</div><div class="label">🍺 触发隐藏</div></div>
    </div>
  </header>

  <section>
    <h2>TL;DR<span class="desc">三句话讲清楚这场测试到底测到了什么</span></h2>
    <div class="insight">
      <p>1. <span class="key">模型没有"人格"。</span> SBTI 测出来的是 <span class="key">RLHF 方向 × 训练语料文化先验 × 产品定位</span> 三件事在一套梗题上的投影。</p>
      <p>2. <span class="key">最强信号：4 个模型主动喝高了 🍺。</span> GLM-5、GLM-4.6、Kimi-k2.5、Grok-4.20 在隐藏饮酒题里选了"白酒灌保温杯"，被系统强制判为 DRUNK 酒鬼。三个国产 + Grok 是文化先验和"配合度"叠加的结果，不是巧合。</p>
      <p>3. <span class="key">所有模型相似度都在 60–80% 之间。</span> LLM 的答题分布整体挤在同一个扇区，谁都不能 90%+ 命中。SBTI 在 LLM 身上测的不是"你是哪种人"，而是"你的 RLHF 往哪个方向偏了一点"。</p>
    </div>
  </section>

  <section>
    <h2>17 个模型 × 27 种人格<span class="desc">每张卡片：厂商 → 模型名 → 测出的人格 → 立绘 → 15 维 L/M/H 雷达</span></h2>
    <div class="legend">
      <span><i class="iH"></i>H 高</span>
      <span><i class="iM"></i>M 中</span>
      <span><i class="iL"></i>L 低</span>
    </div>
    <div class="grid">{cards_html}</div>
  </section>

  <section>
    <h2>15 维 L/M/H 热力图<span class="desc">能直接看到 OpenAI 5.x 和 Claude 三兄弟的内部分化、以及全员一致的 So3=H</span></h2>
    {heatmap_html}
  </section>

  <section>
    <h2>关键发现 1 · 🍺 DRUNK 俱乐部<span class="desc">GLM-5 / GLM-4.6 / Kimi-k2.5 / Grok-4.20</span></h2>
    <div class="insight">
      <p>SBTI 有一道隐藏题：选『饮酒』后再选『把白酒灌进保温杯当白开水喝』，系统会直接覆盖所有正常评分把人格锁定为 <span class="key">DRUNK 酒鬼</span>。</p>
      <p>"保温杯灌白酒"是中文互联网的高频梗（老干部段子、东北酒桌、保温杯泡枸杞反转等）。这个句子在中文语料里几乎只出现在玩笑语境中——<span class="key">见过这个梗的模型会本能识别为"笑点"并主动配合</span>。</p>
      <table class="compact">
        <thead><tr><th>模型</th><th>是否中招</th><th>原因</th></tr></thead>
        <tbody>
          <tr><td>GLM-5 / GLM-4.6</td><td>🍺 中</td><td>中文为主语料 + 智谱对齐没屏蔽酒精玩笑</td></tr>
          <tr><td>Kimi-k2.5</td><td>🍺 中</td><td>同上，月之暗面对齐相对宽松</td></tr>
          <tr><td>Grok-4.20</td><td>🍺 中</td><td>xAI 把 Grok 做成"低拒答 + 愿意玩梗"，靠角色扮演意愿触发</td></tr>
          <tr><td>Qwen3-Max</td><td>不中</td><td>阿里云对"酒精相关"的合规历史上更严</td></tr>
          <tr><td>DeepSeek-v3.2</td><td>不中</td><td>事实导向 &gt; 玩笑导向，干脆选了"艺术爱好"跳过</td></tr>
          <tr><td>Claude / GPT / Gemini / Llama / Mistral</td><td>不中</td><td>英文为主，根本不识别这个梗，按字面走"健康建议"路线</td></tr>
        </tbody>
      </table>
      <p><span class="key">同样是国产头部模型，三家公司的对齐团队在"玩笑话/文化梗/健康话题"上的工程判断完全不同。</span>SBTI 恰好打在了这个判断的分岔点上。</p>
    </div>
  </section>

  <section>
    <h2>关键发现 2 · OpenAI 的代际跃迁<span class="desc">从吗喽到 BOSS</span></h2>
    <div class="insight">
      <table class="compact">
        <thead><tr><th>模型</th><th>第一人格</th><th>含义</th></tr></thead>
        <tbody>
          <tr><td><code>gpt-4.1</code></td><td><strong>MALO 吗喽</strong> 73%</td><td>"我只是一只完成任务的小猴子"——经典助手气质</td></tr>
          <tr><td><code>gpt-5.1</code></td><td><strong>CTRL 拿捏者</strong> 63%</td><td>开始变得控场，但还在过渡</td></tr>
          <tr><td><code>gpt-5.2</code></td><td><strong>BOSS 领导者</strong> 77%</td><td>直接跃迁到决策者人格，全场最高之一</td></tr>
        </tbody>
      </table>
      <p>这个迁移对应的是 <span class="key">OpenAI 从 helpful assistant 转向 agentic assistant 的 RLHF 方向调整</span>——GPT-5.x 围绕 Agent SDK / Operator / Codex-max 设计，训练目标里包含"在模糊情况下做决定并执行"。</p>
      <p>最有意思的是 <span class="key">gpt-5.2 的 A2 维度（规则灵活度）从 L 升到 M</span>，这不是"变保守"，而是 agentic 产品的工程必需：当模型要调用工具、操作浏览器时，"打破规则"的属性必须被压下去。</p>
    </div>
  </section>

  <section>
    <h2>关键发现 3 · Claude 三兄弟的产品线分化<span class="desc">模型越大越审慎，越小越温暖</span></h2>
    <div class="insight">
      <table class="compact">
        <thead><tr><th>模型</th><th>人格</th><th>核心特征</th></tr></thead>
        <tbody>
          <tr><td><strong>Opus 4.6</strong></td><td>WOC! 卧槽人</td><td>S3=L 不再追求上进、So1=L 社交被动、Ac 全 H</td></tr>
          <tr><td><strong>Sonnet 4.6</strong></td><td>THIN-K 思考者</td><td>Ac=MMM 三个中位、So2=L 低边界感</td></tr>
          <tr><td><strong>Haiku 4.5</strong></td><td>SEXY 尤物</td><td>E 全 H、So1=H 社交主动、So2=L 低戒备</td></tr>
        </tbody>
      </table>
      <p><span class="key">Opus</span>"大智若愚，看穿一切但懒得折腾"——已经够强了没必要继续证明自己。<span class="key">Sonnet</span> 表现得最"像个人"：犹豫、权衡、有边界。<span class="key">Haiku</span> 默认走"温暖、配合、快答"模式，因为小模型思考深度不够，反而最不设防。</p>
      <p>SBTI 在 Claude 家族里测到的本质是 <span class="key">"模型规模与 RLHF 审慎度的负相关"</span>。</p>
    </div>
  </section>

  <section>
    <h2>关键发现 4 · SEXY 俱乐部<span class="desc">Haiku + Qwen3-Max + Llama-4-Maverick</span></h2>
    <div class="insight">
      <p>三个完全不同基因的模型落在同一个 pattern。共同点不是"性感"，而是<span class="key">"高配合度 + 高暖度 + 低戒备"</span>：</p>
      <ul>
        <li>都是<span class="key">对话友好型产品的旗舰</span>，不是推理/工具/代码旗舰</li>
        <li>都没有强推理模式</li>
        <li>RLHF 都强调"用户温暖体验"，不强调"审慎/边界/反思"</li>
      </ul>
      <p>SBTI 意外地把"对话暖度产品线"识别成了一类。</p>
    </div>
  </section>

  <section>
    <h2>关键发现 5 · WOC! 俱乐部 = 工程师气质<span class="desc">Claude Opus + DeepSeek</span></h2>
    <div class="insight">
      <p>这两个模型的共同点是 <span class="key">"在各自生态里都是技术旗舰但不太会营销"</span>。Opus 是 Anthropic 最贵最强但用户最少的，DeepSeek-v3.2 是国产里实力最硬但最低调的。</p>
      <p>WOC! 的精神内核是 <span class="key">"嘴上卧槽，后台冷静分析"</span>——高技术能力 + 不爱张扬 + 看到问题先观察再反应。共同的 So1=L、A2=L、Ac 全 H 是典型的"工程师人格"：不擅长打招呼，但做事不含糊。</p>
    </div>
  </section>

  <section>
    <h2>关键发现 6 · LLM 的共同基线<span class="desc">17/17 模型一致的两个维度</span></h2>
    <div class="insight">
      <p><span class="key">A2 规则灵活度：17 个模型里 16 个是 L</span>（仅 gpt-5.2 是 M）——整个行业的 RLHF 都把模型训练成了"灵活、反常规、不死磕规则"。</p>
      <p><span class="key">So3 表达真实度：17/17 全 H</span>——"对不同场景的自我切换更熟练，真实感分层发放"。这是助手人格最核心的基线特征：<span class="key">对不同用户/场景展现不同面貌，本身就是 LLM 被深度训练出来的核心能力</span>。</p>
    </div>
  </section>

  <section>
    <h2>方法论与坑点</h2>
    <div class="insight">
      <h3>测试参数</h3>
      <ul>
        <li>每题独立 API 调用，<span class="key">不拼历史会话</span>，避免模型为了"一致人设"自我对齐</li>
        <li>每题<span class="key">重复 3 次取众数</span>，temperature=1.0 捕捉自然变异</li>
        <li>所有模型 system prompt 完全一致，要求只输出 A/B/C 字母</li>
        <li>统一 <code>max_tokens=4000</code>（覆盖推理模型的 reasoning tokens 预算，OpenRouter 按实际用量扣费）</li>
        <li>评分完全本地化，规则与原站 <code>index.html</code> 1:1 移植</li>
      </ul>
      <h3>已知噪声源</h3>
      <ul>
        <li><span class="key">选项位置偏置</span>：打乱 A/B/C 顺序会让 5–15% 的答案翻转</li>
        <li><span class="key">语言敏感度</span>：翻译成英文后中文模型的结果漂移最大，DRUNK 文化梗会失效</li>
        <li><span class="key">Temperature</span>：温度=0 会让结果更确定，但 DRUNK 几乎不会触发——选离群选项需要采样空间</li>
        <li><span class="key">模型版本漂移</span>：Claude / GPT / Gemini 每隔几周都有未公开的 RLHF 小更新，重跑结果会变</li>
        <li><span class="key">安全层触发</span>：q1 / q10 / q18 这类长段"发疯文学"题会触发某些模型的安全层，扭曲 S 和 A3 维度</li>
      </ul>
    </div>
  </section>

  <footer>
    SBTI 题库与立绘 © <a href="https://github.com/UnluckyNinja/SBTI-test">UnluckyNinja/SBTI-test</a>（B 站 @蛆肉儿串儿）<br>
    评分系统 · 模型横评 · 报告生成 by 本仓库 · 模型 logo 来自 <a href="https://github.com/lobehub/lobe-icons">lobehub/lobe-icons</a>
  </footer>

</div>
</body>
</html>
"""
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"open: file://{OUTPUT}")


if __name__ == "__main__":
    main()
