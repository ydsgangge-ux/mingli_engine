# LLM Provider Configuration
LLM_PROVIDER = "deepseek"  # 默认 provider

LLM_CONFIG = {
    # ── 国产大模型（优先推荐）──
    "deepseek": {
        "api_url": "https://api.deepseek.com",
        "model": "deepseek-v4-flash",
        "max_tokens": 4000,
        "label": "DeepSeek",
        "need_key": True,
        "doc": "https://platform.deepseek.com/api_keys",
    },
    "qwen": {
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode",
        "model": "qwen3.7-max",
        "max_tokens": 4000,
        "label": "通义千问 (阿里云)",
        "need_key": True,
        "doc": "https://dashscope.console.aliyun.com/apiKey",
    },
    "glm": {
        "api_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-5.1",
        "max_tokens": 4000,
        "label": "智谱 GLM",
        "need_key": True,
        "doc": "https://open.bigmodel.cn/usercenter/apikeys",
    },
    "kimi": {
        "api_url": "https://api.moonshot.cn",
        "model": "kimi-k2.6",
        "max_tokens": 4000,
        "label": "Kimi (月之暗面)",
        "need_key": True,
        "doc": "https://platform.moonshot.cn/console/api-keys",
    },
    "wenxin": {
        "api_url": "",
        "model": "ernie-4.5-8k",
        "max_tokens": 4000,
        "label": "文心一言 (百度)",
        "need_key": True,
        "doc": "https://cloud.baidu.com/product/wenxinworkshop",
    },
    # ── 国际模型 ──
    "openai": {
        "api_url": "https://api.openai.com",
        "model": "gpt-5.3-instant",
        "max_tokens": 4000,
        "label": "OpenAI GPT",
        "need_key": True,
        "doc": "https://platform.openai.com/api-keys",
    },
    "claude": {
        "api_url": "https://api.anthropic.com",
        "model": "claude-opus-4-8",
        "max_tokens": 4000,
        "label": "Claude (Anthropic)",
        "need_key": True,
        "doc": "https://console.anthropic.com/settings/keys",
    },
    # ── 本地部署 ──
    "ollama": {
        "api_url": "http://localhost:11434",
        "model": "qwen2.5:14b",
        "max_tokens": 4000,
        "label": "Ollama (本地)",
        "need_key": False,
        "doc": "https://ollama.ai",
    },
    # ── 自定义 OpenAI 兼容 ──
    "custom": {
        "api_url": "",
        "model": "",
        "max_tokens": 4000,
        "label": "自定义 (OpenAI兼容)",
        "need_key": True,
        "doc": "",
    },
}

# 可选模型列表（用于前端下拉）
MODEL_OPTIONS = {
    "deepseek": ["deepseek-v4-pro", "deepseek-v4-flash", "deepseek-chat", "deepseek-reasoner"],
    "qwen": ["qwen3.7-max", "qwen3.6-max-preview", "qwen3.6-plus", "qwen3.6-flash", "qwen3-max", "qwen-max", "qwen-plus", "qwen-turbo"],
    "glm": ["glm-5.1", "glm-5", "glm-4.5", "glm-4.5-air", "glm-4.5-flash", "glm-4.5-x", "glm-4.5-airx"],
    "kimi": ["kimi-k2.6", "kimi-k2.6-thinking", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    "wenxin": ["ernie-4.5-8k", "ernie-4.0-8k", "ernie-3.5-8k", "completions_pro"],
    "openai": ["gpt-5.5", "gpt-5.4", "gpt-5.3", "gpt-5.3-instant", "gpt-5", "gpt-4.1", "gpt-4.1-mini"],
    "claude": ["claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-haiku-4-20250414"],
    "ollama": [],
    "custom": [],
}

# API keys loaded from .env
# DEEPSEEK_API_KEY=xxx
# QWEN_API_KEY=xxx
# GLM_API_KEY=xxx
# KIMI_API_KEY=xxx
# WENXIN_API_KEY=xxx (格式: API_KEY:SECRET_KEY)
# OPENAI_API_KEY=xxx
# CLAUDE_API_KEY=xxx

# Retry settings
LLM_TIMEOUT = 120  # seconds (Ollama 本地推理较慢)
LLM_MAX_RETRIES = 3
LLM_RETRY_BACKOFF = 2

# Server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 18766

# Engine version
ENGINE_VERSION = "1.0"
