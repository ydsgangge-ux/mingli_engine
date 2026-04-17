# LLM Provider Configuration
LLM_PROVIDER = "deepseek"  # 默认 provider

LLM_CONFIG = {
    # ── 国产大模型（优先推荐）──
    "deepseek": {
        "api_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "max_tokens": 4000,
        "label": "DeepSeek",
        "need_key": True,
        "doc": "https://platform.deepseek.com/api_keys",
    },
    "qwen": {
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode",
        "model": "qwen-plus",
        "max_tokens": 4000,
        "label": "通义千问 (阿里云)",
        "need_key": True,
        "doc": "https://dashscope.console.aliyun.com/apiKey",
    },
    "glm": {
        "api_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "max_tokens": 4000,
        "label": "智谱 GLM",
        "need_key": True,
        "doc": "https://open.bigmodel.cn/usercenter/apikeys",
    },
    "kimi": {
        "api_url": "https://api.moonshot.cn",
        "model": "moonshot-v1-8k",
        "max_tokens": 4000,
        "label": "Kimi (月之暗面)",
        "need_key": True,
        "doc": "https://platform.moonshot.cn/console/api-keys",
    },
    "wenxin": {
        "api_url": "",
        "model": "completions_pro",
        "max_tokens": 4000,
        "label": "文心一言 (百度)",
        "need_key": True,
        "doc": "https://cloud.baidu.com/product/wenxinworkshop",
    },
    # ── 国际模型 ──
    "openai": {
        "api_url": "https://api.openai.com",
        "model": "gpt-4o",
        "max_tokens": 4000,
        "label": "OpenAI GPT",
        "need_key": True,
        "doc": "https://platform.openai.com/api-keys",
    },
    "claude": {
        "api_url": "https://api.anthropic.com",
        "model": "claude-sonnet-4-20250514",
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
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "qwen": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-long"],
    "glm": ["glm-4-flash", "glm-4-air", "glm-4-plus", "glm-4"],
    "kimi": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    "wenxin": ["completions_pro", "ernie-4.0-8k", "ernie-3.5-8k"],
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "claude": ["claude-sonnet-4-20250514", "claude-haiku-4-20250414"],
    "ollama": [],  # 动态获取
    "custom": [],  # 用户自填
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
