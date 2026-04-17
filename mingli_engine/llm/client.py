"""
LLM API 客户端封装
支持 DeepSeek / Claude / OpenAI / 通义千问 / 智谱GLM / 百度文心 / 月之暗面Kimi / Ollama 本地模型
所有 OpenAI 兼容接口统一走 _call_openai_compatible
"""
import json
import os
import re
import asyncio
import httpx
from dotenv import load_dotenv
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LLM_PROVIDER, LLM_CONFIG, LLM_TIMEOUT, LLM_MAX_RETRIES, LLM_RETRY_BACKOFF

load_dotenv(Path(__file__).parent / ".env", override=False)

# ── 运行时可覆盖配置（来自 Web UI）──
_runtime_config = {}


def set_runtime_config(provider: str, api_key: str = "", base_url: str = "", model: str = ""):
    """设置运行时 LLM 配置（Web UI 调用）。切换提供商时必须清除旧值。"""
    _runtime_config.clear()
    _runtime_config["provider"] = provider
    if api_key:
        _runtime_config["api_key"] = api_key
    if base_url:
        _runtime_config["base_url"] = base_url.rstrip("/")
    if model:
        _runtime_config["model"] = model


def get_runtime_config() -> dict:
    """获取当前运行时配置快照"""
    return dict(_runtime_config)


def reset_runtime_config():
    """重置运行时配置，回到 .env / config.py 默认值"""
    _runtime_config.clear()


def _get_api_key(provider: str) -> str:
    """获取 API Key（运行时 > .env > 默认）"""
    if "api_key" in _runtime_config:
        return _runtime_config["api_key"]
    key_map = {
        "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
        "claude": os.getenv("CLAUDE_API_KEY", ""),
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "qwen": os.getenv("QWEN_API_KEY", ""),
        "glm": os.getenv("GLM_API_KEY", ""),
        "wenxin": os.getenv("WENXIN_API_KEY", ""),
        "kimi": os.getenv("KIMI_API_KEY", ""),
        "ollama": "",
        "custom": _runtime_config.get("api_key", ""),
    }
    return key_map.get(provider, "")


def _get_base_url(provider: str) -> str:
    """获取 API Base URL（运行时 > config.py 默认）"""
    if "base_url" in _runtime_config:
        return _runtime_config["base_url"]
    cfg = LLM_CONFIG.get(provider, {})
    return cfg.get("api_url", "")


def _get_model(provider: str) -> str:
    """获取模型名（运行时 > config.py 默认）"""
    if "model" in _runtime_config:
        return _runtime_config["model"]
    cfg = LLM_CONFIG.get(provider, {})
    return cfg.get("model", "")


def _get_max_tokens(provider: str) -> int:
    cfg = LLM_CONFIG.get(provider, {})
    return cfg.get("max_tokens", 4000)


async def call_llm(
    messages: list,
    provider: Optional[str] = None,
    response_format: Optional[dict] = None,
) -> str:
    """
    调用 LLM API

    参数:
        messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
        provider: 可选覆盖
        response_format: {"type": "json_object"}

    返回:
        str 模型原始输出
    """
    provider = provider or _runtime_config.get("provider") or LLM_PROVIDER
    api_key = _get_api_key(provider)
    base_url = _get_base_url(provider)
    model = _get_model(provider)
    max_tokens = _get_max_tokens(provider)

    if provider == "ollama":
        if not base_url:
            base_url = "http://localhost:11434"
        if not api_key:
            # Ollama 默认不需要 key
            api_key = "ollama"
        return await _call_ollama(base_url, model, messages, max_tokens)

    if provider == "claude":
        if not api_key:
            raise ValueError(f"未设置 Claude 的 API Key")
        return await _call_claude(api_key, model, messages, max_tokens)

    if provider == "wenxin":
        # 百度文心使用 access_token 认证，特殊处理
        return await _call_wenxin(api_key, model, messages, max_tokens)

    # 所有 OpenAI 兼容接口统一处理：deepseek, openai, qwen, glm, kimi, custom
    if not api_key:
        raise ValueError(f"未设置 {provider} 的 API Key，请在设置页面或 .env 文件中配置")
    if not base_url:
        raise ValueError(f"未配置 {provider} 的 API 地址")

    return await _call_openai_compatible(base_url, model, api_key, messages, max_tokens, response_format)


async def _call_openai_compatible(
    base_url: str, model: str, api_key: str,
    messages: list, max_tokens: int,
    response_format: Optional[dict] = None,
) -> str:
    """OpenAI 兼容 API 调用（DeepSeek / OpenAI / 通义千问 / 智谱GLM / Kimi / 自定义）"""
    # 拼接完整 URL
    url = base_url.rstrip("/")
    if url.endswith("/chat/completions"):
        pass
    elif url.endswith("/v1"):
        url += "/chat/completions"
    else:
        url += "/v1/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if response_format:
        payload["response_format"] = response_format

    for attempt in range(LLM_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=LLM_TIMEOUT, verify=False) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except httpx.TimeoutException:
            wait = LLM_RETRY_BACKOFF ** attempt
            print(f"[LLM] 超时，{wait}s 后重试 ({attempt + 1}/{LLM_MAX_RETRIES})")
            await asyncio.sleep(wait)
        except httpx.HTTPStatusError as e:
            print(f"[LLM] HTTP 错误: {e.response.status_code} - {e.response.text[:200]}")
            if e.response.status_code >= 500:
                wait = LLM_RETRY_BACKOFF ** attempt
                await asyncio.sleep(wait)
                continue
            raise
        except Exception as e:
            print(f"[LLM] 未知错误: {e}")
            raise
    raise TimeoutError(f"LLM 调用失败，已重试 {LLM_MAX_RETRIES} 次")


async def _call_ollama(base_url: str, model: str, messages: list, max_tokens: int) -> str:
    """Ollama 本地模型调用"""
    if not model:
        raise ValueError("Ollama 模型名称为空，请在设置页面选择一个已安装的模型")

    url = base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }

    for attempt in range(LLM_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=LLM_TIMEOUT * 2) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 404:
                    available = await _list_ollama_models_safe(base_url)
                    hint = f"可用模型: {', '.join(available)}" if available else "未检测到本地模型"
                    raise ValueError(
                        f"Ollama 模型 '{model}' 不存在。{hint}。"
                        f"请安装: ollama pull qwen2.5:7b"
                    )
                if resp.status_code == 500:
                    raise ConnectionError(
                        f"Ollama 服务内部错误（500）。请尝试重启 Ollama: "
                        f"1) 关闭 Ollama  2) 终端运行 ollama serve  3) 重试"
                    )
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "")
        except (ConnectionError, httpx.ConnectError):
            raise ConnectionError(
                f"无法连接 Ollama（{base_url}），请确认 Ollama 已启动。"
                "安装: https://ollama.ai  |  启动: ollama serve"
            )
        except httpx.TimeoutException:
            wait = LLM_RETRY_BACKOFF ** attempt
            print(f"[Ollama] 超时，{wait}s 后重试 ({attempt + 1}/{LLM_MAX_RETRIES})")
            await asyncio.sleep(wait)
        except ValueError:
            raise
        except ConnectionError:
            raise
        except Exception as e:
            print(f"[Ollama] 错误: {e}")
            raise
    raise TimeoutError(f"Ollama 调用失败，已重试 {LLM_MAX_RETRIES} 次")


async def _list_ollama_models_safe(base_url: str) -> list:
    """安全地列出 Ollama 本地模型"""
    try:
        tag_url = base_url.rstrip("/") + "/api/tags"
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(tag_url)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    return []


async def _call_claude(api_key: str, model: str, messages: list, max_tokens: int) -> str:
    """Claude (Anthropic) API 调用"""
    base_url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    system_msg = ""
    claude_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            claude_messages.append(msg)

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": claude_messages,
    }
    if system_msg:
        payload["system"] = system_msg

    for attempt in range(LLM_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=LLM_TIMEOUT, verify=False) as client:
                resp = await client.post(base_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("content", [{}])[0].get("text", "")
        except httpx.TimeoutException:
            wait = LLM_RETRY_BACKOFF ** attempt
            print(f"[Claude] 超时，{wait}s 后重试 ({attempt + 1}/{LLM_MAX_RETRIES})")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"[Claude] 错误: {e}")
            raise
    raise TimeoutError(f"Claude 调用失败，已重试 {LLM_MAX_RETRIES} 次")


async def _call_wenxin(api_key: str, model: str, messages: list, max_tokens: int) -> str:
    """百度文心一言 API（使用 access_token）"""
    # api_key 格式: "API_KEY:SECRET_KEY"
    if ":" not in api_key:
        raise ValueError("文心一言 API Key 格式应为 'API_KEY:SECRET_KEY'")

    ak, sk = api_key.split(":", 1)

    # 获取 access_token
    token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}"
    try:
        async with httpx.AsyncClient(timeout=30, verify=False) as client:
            token_resp = await client.post(token_url)
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError(f"文心 access_token 获取失败: {token_data}")
    except Exception as e:
        raise ValueError(f"文心 access_token 获取异常: {e}")

    # 文心 ERNIE 系列使用不同的 API
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={access_token}"
    payload = {"messages": messages}

    for attempt in range(LLM_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=LLM_TIMEOUT, verify=False) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("result", "")
        except httpx.TimeoutException:
            wait = LLM_RETRY_BACKOFF ** attempt
            print(f"[文心] 超时，{wait}s 后重试 ({attempt + 1}/{LLM_MAX_RETRIES})")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"[文心] 错误: {e}")
            raise
    raise TimeoutError(f"文心一言调用失败，已重试 {LLM_MAX_RETRIES} 次")


async def call_llm_json(
    messages: list,
    provider: Optional[str] = None,
) -> dict:
    """
    调用 LLM 并解析为 JSON（带修复重试）
    """
    provider = provider or _runtime_config.get("provider") or LLM_PROVIDER

    for attempt in range(LLM_MAX_RETRIES):
        raw = await call_llm(messages, provider)

        # 尝试提取 JSON
        parsed = _extract_json(raw)
        if parsed is not None:
            return parsed

        # 修复重试
        if attempt < LLM_MAX_RETRIES - 1:
            print(f"[LLM] JSON 解析失败，请求模型修正 ({attempt + 1}/{LLM_MAX_RETRIES})")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": "你上一次的输出不是合法的JSON。请重新输出，只输出JSON，不要包含任何其他文字或markdown代码块标记。"})
        else:
            print(f"[LLM] JSON 解析最终失败，返回原始内容")
            return {"raw_output": raw, "parse_error": True}

    return {}


def _extract_json(text: str) -> Optional[dict]:
    """从文本中提取 JSON"""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return None


async def list_ollama_models(base_url: str = "") -> list:
    """列出 Ollama 本地可用模型"""
    url = (base_url or "http://localhost:11434").rstrip("/") + "/api/tags"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


async def test_connection(provider: str, api_key: str = "", base_url: str = "", model: str = "") -> dict:
    """测试 LLM 连接是否正常"""
    try:
        old_cfg = dict(_runtime_config)
        _runtime_config.clear()
        if provider:
            _runtime_config["provider"] = provider
        if api_key:
            _runtime_config["api_key"] = api_key
        if base_url:
            _runtime_config["base_url"] = base_url.rstrip("/")
        if model:
            _runtime_config["model"] = model

        result = await call_llm(
            messages=[{"role": "user", "content": "请回复：连接成功"}],
            provider=provider,
        )

        _runtime_config.clear()
        _runtime_config.update(old_cfg)

        return {"success": True, "response": result[:100]}
    except Exception as e:
        _runtime_config.clear()
        _runtime_config.update(old_cfg)
        return {"success": False, "error": str(e)}
