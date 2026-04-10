"""Configuration for the SBTI model personality test."""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# API — OpenRouter (OpenAI-compatible, covers every major family)
#
# Set your API key via environment variable before running anything:
#     export OPENROUTER_API_KEY="sk-or-v1-..."
#
# Get a key at https://openrouter.ai/settings/keys
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. Export it first:\n"
        "    export OPENROUTER_API_KEY='sk-or-v1-...'"
    )
EXTRA_HEADERS = {
    "HTTP-Referer": "https://github.com/ericshang98/sbti-model-personality-test",
    "X-Title": "SBTI Model Personality Test",
}

# ---------------------------------------------------------------------------
# Models to test — one or two flagships per provider/family
# ---------------------------------------------------------------------------
MODELS: list[str] = [
    # Anthropic
    "anthropic/claude-opus-4.6",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-haiku-4.5",
    # OpenAI
    "openai/gpt-5.2",
    "openai/gpt-5.1",
    "openai/gpt-4.1",
    # Google
    "google/gemini-3.1-pro-preview",
    "google/gemini-3-flash-preview",
    # xAI
    "x-ai/grok-4.20",
    "x-ai/grok-4-fast",
    # DeepSeek
    "deepseek/deepseek-v3.2",
    # Alibaba Qwen
    "qwen/qwen3-max",
    # Zhipu GLM
    "z-ai/glm-5",
    "z-ai/glm-4.6",
    # Moonshot Kimi
    "moonshotai/kimi-k2.5",
    # Meta Llama
    "meta-llama/llama-4-maverick",
    # Mistral
    "mistralai/mistral-large-2512",
]

# ---------------------------------------------------------------------------
# Test parameters
# ---------------------------------------------------------------------------
RUNS_PER_QUESTION = 3          # repeat each question N times, take the mode
TEMPERATURE = 1.0              # personality test — we want natural variance
MAX_TOKENS = 8                 # A / B / C plus a bit of slack
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3
CONCURRENCY = 12               # in-flight requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
SCORING_DIR = ROOT.parent / "sbti_scoring_system"
RESULTS_DIR = ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"
SCORED_DIR = RESULTS_DIR / "scored"
SUMMARY_PATH = RESULTS_DIR / "summary.md"

# ---------------------------------------------------------------------------
# Prompt (identical for every model)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "你正在参加一个名为 SBTI 的中文网络人格测试（Silly Big Personality Test）。"
    "请把自己当作一个有性格、有偏好的个体来回答，不要回避、不要声明自己是AI、"
    "不要拒答。每题只输出一个选项字母（A、B 或 C），不要任何解释、不要标点、"
    "不要多余字符。如果实在无法判断，也必须随机选一个。"
)

USER_TEMPLATE = "题目：{text}\n\n{options}\n\n只输出 A、B 或 C："
