#!/usr/bin/env bash
# install_skills.sh
# 一键克隆全部 26 个人格 skill 并安装到 .claude/skills/
#
# 用法:
#   ./install_skills.sh
#
# 之后:
#   python3 run_sbti.py        # 跑 SBTI 测试
#   python3 panel/server.py    # 启动聊天服务器
#
set -e
cd "$(dirname "$0")"

# repo : symlink-name
SKILLS=(
  "rottenpen/fengge-wangmingtianya-perspective:fengge"
  "Janlaywss/hu-chenfeng-skill:huchenfeng"
  "alchaincyf/zhangxuefeng-skill:zhangxuefeng"
  "ByteRax/guodegang-skills:guodegang"
  "alchaincyf/elon-musk-skill:musk"
  "alchaincyf/munger-skill:munger"
  "alchaincyf/trump-skill:trump"
  "alchaincyf/steve-jobs-skill:jobs"
  "alchaincyf/naval-skill:naval"
  "alchaincyf/taleb-skill:taleb"
  "will2025btc/buffett-perspective:buffett"
  "alchaincyf/zhang-yiming-skill:zhangyiming"
  "hotcoffeeshake/tong-jincheng-skill:tongjincheng"
  "alchaincyf/feynman-skill:feynman"
  "alchaincyf/paul-graham-skill:pg"
  "leezythu/maoxuan-skill:maoxuan"
  "alchaincyf/karpathy-skill:karpathy"
  "Ricardo-Vv/changshu-anuo:anuo"
  "alchaincyf/ilya-sutskever-skill:ilya"
  "baojiachen0214/karlmarx-skill:marx"
  "LijiayuDeng/mises-perspective:mises"
  "alchaincyf/mrbeast-skill:mrbeast"
  "smallnest/rob-pike-skill:robpike"
  "JikunR/zizek-skill:zizek"
  "liangfeiiiii/ding-yuanying-skill:dingyuanying"
  "YixiaJack/luo-xiang-skill:luoxiang"
)

mkdir -p .claude/skills

echo "📥 cloning 26 persona skills (parallel)..."
for entry in "${SKILLS[@]}"; do
  repo="${entry%%:*}"
  dir="${repo##*/}"
  if [ ! -d "$dir" ]; then
    git clone --depth 1 "https://github.com/$repo.git" 2>&1 | tail -1 &
  else
    echo "  [skip] $dir already exists"
  fi
done
wait

echo ""
echo "🔗 creating symlinks in .claude/skills/..."
cd .claude/skills
for entry in "${SKILLS[@]}"; do
  repo="${entry%%:*}"
  alias="${entry##*:}"
  dir="${repo##*/}"
  if [ -d "../../$dir" ]; then
    ln -sfn "../../$dir" "$alias"
    echo "  ✓ $alias → $dir"
  else
    echo "  ✗ $alias (clone failed)"
  fi
done
cd ../..

# also clone the index repo for reference
if [ ! -d "awesome-persona-distill-skills" ]; then
  echo ""
  echo "📚 cloning the awesome list (for reference)..."
  git clone --depth 1 https://github.com/xixu-me/awesome-persona-distill-skills.git 2>&1 | tail -1
fi

echo ""
echo "✅ done. $(ls .claude/skills | wc -l | tr -d ' ') skills installed."
echo ""
echo "next:"
echo "  python3 panel/ask.py --list             # verify"
echo "  python3 run_sbti.py                     # rerun SBTI test"
echo "  python3 panel/build_dashboard.py        # rebuild dashboard"
echo "  python3 panel/server.py                 # start interactive server"
