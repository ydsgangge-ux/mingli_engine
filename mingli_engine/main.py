"""
MingLi Prediction Engine - FastAPI 后端入口
提供 REST API 和静态文件服务
"""
import asyncio
import json
import sys
import os
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# 项目路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import SERVER_HOST, SERVER_PORT, LLM_CONFIG, LLM_PROVIDER, MODEL_OPTIONS
from engines.bazi_engine import calculate_bazi
from engines.dayun_engine import calculate_dayun
from engines.personality_engine import calculate_personality, get_questions
from engines.chart_builder import build_chart_data, save_chart_data
from llm.client import call_llm_json, set_runtime_config, get_runtime_config, reset_runtime_config, list_ollama_models, test_connection
from llm.round1_pattern import run_round1
from llm.round2_cross import run_round2
from llm.round3_liunian import run_round3
from llm.round4_paths import run_round4
from assembler.report_assembler import assemble_report, save_report

load_dotenv(BASE_DIR / ".env", override=False)

app = FastAPI(title="MingLi Prediction Engine", version="1.0")

# 全局状态
report_tasks = {}

# 后台 asyncio 事件循环
_bg_loop = None


def _get_bg_loop():
    global _bg_loop
    if _bg_loop is None or _bg_loop.is_closed():
        _bg_loop = asyncio.new_event_loop()
        t = threading.Thread(target=_bg_loop.run_forever, daemon=True)
        t.start()
    return _bg_loop


# ── 数据模型 ──
class UserInfo(BaseModel):
    name: str = ""
    gender: str = "男"
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birthplace: str = ""
    longitude: float = 116.4
    lunar_month: Optional[int] = None
    lunar_day: Optional[int] = None
    father_occupation: str = ""
    mother_occupation: str = ""
    family_background: str = ""


class PersonalityAnswers(BaseModel):
    answers: dict


class FullRequest(BaseModel):
    user: UserInfo
    answers: dict


class LLMConfigRequest(BaseModel):
    provider: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""


class TestConnectionRequest(BaseModel):
    provider: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""


# ── 页面路由 ──
@app.get("/")
async def index():
    index_path = BASE_DIR / "frontend" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>MingLi Engine API Running</h1><p>Access /docs for API docs.</p>")


@app.get("/report")
async def report_page():
    report_path = BASE_DIR / "frontend" / "report.html"
    if report_path.exists():
        return FileResponse(report_path)
    return HTMLResponse("<h1>Report page not found</h1>")


# ── LLM 配置 API ──
@app.get("/api/llm/providers")
async def api_get_providers():
    """获取所有支持的 LLM 提供商列表"""
    providers = []
    for key, cfg in LLM_CONFIG.items():
        # 检查是否有已配置的 key
        has_key = False
        if key == "ollama":
            has_key = True  # Ollama 不需要 key
        elif key == "wenxin":
            has_key = bool(os.getenv("WENXIN_API_KEY", ""))
        elif key == "custom":
            has_key = False
        else:
            env_key_map = {
                "deepseek": "DEEPSEEK_API_KEY",
                "qwen": "QWEN_API_KEY",
                "glm": "GLM_API_KEY",
                "kimi": "KIMI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "claude": "CLAUDE_API_KEY",
            }
            env_name = env_key_map.get(key, "")
            has_key = bool(os.getenv(env_name, ""))

        providers.append({
            "id": key,
            "label": cfg["label"],
            "need_key": cfg["need_key"],
            "has_key": has_key,
            "default_model": cfg["model"],
            "models": MODEL_OPTIONS.get(key, []),
            "doc": cfg.get("doc", ""),
        })
    return {"providers": providers, "current": get_runtime_config().get("provider") or LLM_PROVIDER}


@app.get("/api/llm/models/{provider}")
async def api_get_models(provider: str):
    """获取指定提供商的可用模型列表（Ollama 支持动态获取）"""
    if provider == "ollama":
        models = await list_ollama_models()
        return {"models": models, "dynamic": True}
    return {"models": MODEL_OPTIONS.get(provider, []), "dynamic": False}


@app.get("/api/llm/current")
async def api_get_current_config():
    """获取当前生效的 LLM 配置"""
    runtime = get_runtime_config()
    return {
        "provider": runtime.get("provider") or LLM_PROVIDER,
        "model": runtime.get("model") or LLM_CONFIG.get(LLM_PROVIDER, {}).get("model", ""),
        "has_runtime_override": bool(runtime),
    }


@app.post("/api/llm/config")
async def api_set_llm_config(req: LLMConfigRequest):
    """设置 LLM 配置（运行时生效）"""
    if req.provider not in LLM_CONFIG:
        raise HTTPException(status_code=400, detail=f"不支持的提供商: {req.provider}")

    set_runtime_config(req.provider, req.api_key, req.base_url, req.model)

    # 同时更新 .env 文件持久化
    _save_env_key(req.provider, req.api_key)

    return {
        "success": True,
        "message": f"已切换到 {LLM_CONFIG[req.provider]['label']}",
        "config": get_runtime_config(),
    }


@app.post("/api/llm/test")
async def api_test_connection(req: TestConnectionRequest):
    """测试 LLM 连接"""
    result = await test_connection(req.provider, req.api_key, req.base_url, req.model)
    return result


@app.post("/api/llm/reset")
async def api_reset_llm_config():
    """重置为默认配置"""
    reset_runtime_config()
    return {"success": True, "message": "已重置为默认配置", "provider": LLM_PROVIDER}


# ── 业务 API ──
@app.get("/api/questions")
async def api_get_questions():
    return {"questions": get_questions()}


@app.post("/api/bazi")
async def api_bazi(user: UserInfo):
    try:
        bazi = calculate_bazi(
            user.birth_year, user.birth_month, user.birth_day,
            user.birth_hour, user.gender, user.longitude
        )
        dayun = calculate_dayun(
            bazi, user.birth_year, user.birth_month, user.birth_day,
            user.birth_hour, user.longitude
        )
        return {"bazi": bazi, "dayun": dayun}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/personality")
async def api_personality(data: PersonalityAnswers):
    result = calculate_personality(data.answers)
    return result


@app.post("/api/chart-data")
async def api_chart_data(req: FullRequest):
    try:
        user_dict = req.user.model_dump()
        chart_data = await build_chart_data(user_dict, req.answers)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-report")
async def api_generate_report(req: FullRequest):
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    report_tasks[task_id] = {"status": "started", "progress": 5}

    user_dict = req.user.model_dump()
    answers = req.answers

    async def _pipeline():
        try:
            report_tasks[task_id] = {"status": "building_chart", "progress": 10}
            chart_data = await build_chart_data(user_dict, answers)

            report_tasks[task_id] = {"status": "round1_pattern", "progress": 25}
            round1 = await run_round1(chart_data)

            report_tasks[task_id] = {"status": "round2_cross", "progress": 45}
            round2 = await run_round2(chart_data, round1)

            report_tasks[task_id] = {"status": "round3_liunian", "progress": 65}
            round3 = await run_round3(chart_data, round1, round2)

            report_tasks[task_id] = {"status": "round4_paths", "progress": 85}
            round4 = await run_round4(chart_data, round1, round2, round3)

            report_tasks[task_id] = {"status": "assembling", "progress": 95}
            report_md = assemble_report(chart_data, round1, round2, round3, round4)

            output_dir = BASE_DIR / "output"
            output_dir.mkdir(exist_ok=True)
            save_chart_data(chart_data, str(output_dir))
            name = user_dict.get("name") or "user"
            report_path = save_report(report_md, str(output_dir), name)

            results_dir = output_dir / task_id
            results_dir.mkdir(exist_ok=True)
            for fname, data in [("round1.json", round1), ("round2.json", round2),
                                ("round3.json", round3), ("round4.json", round4),
                                ("chart_data.json", chart_data)]:
                with open(results_dir / fname, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            with open(results_dir / "report.md", "w", encoding="utf-8") as f:
                f.write(report_md)

            report_tasks[task_id] = {
                "status": "completed", "progress": 100,
                "report_md": report_md, "chart_data": chart_data,
                "round1": round1, "round2": round2,
                "round3": round3, "round4": round4,
                "report_file": str(report_path),
            }
        except Exception as e:
            report_tasks[task_id] = {"status": "error", "progress": 0, "error": str(e)}

    loop = _get_bg_loop()
    asyncio.run_coroutine_threadsafe(_pipeline(), loop)
    return {"task_id": task_id, "status": "started"}


@app.get("/api/task/{task_id}")
async def api_task_status(task_id: str):
    task = report_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] == "completed":
        return {
            "status": "completed", "progress": 100,
            "report_md": task.get("report_md", ""),
            "chart_data": task.get("chart_data", {}),
            "round1": task.get("round1", {}),
            "round2": task.get("round2", {}),
            "round3": task.get("round3", {}),
            "round4": task.get("round4", {}),
        }
    return task


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0", "time": datetime.now().isoformat()}


# ── 持久化 .env ──
def _save_env_key(provider: str, api_key: str):
    """将 API Key 写入 .env 文件"""
    if not api_key:
        return
    env_map = {
        "deepseek": "DEEPSEEK_API_KEY",
        "qwen": "QWEN_API_KEY",
        "glm": "GLM_API_KEY",
        "kimi": "KIMI_API_KEY",
        "wenxin": "WENXIN_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "CLAUDE_API_KEY",
    }
    env_name = env_map.get(provider)
    if not env_name:
        return

    env_path = BASE_DIR / ".env"
    lines = []
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        lines = content.splitlines()

    # 更新或添加 key
    found = False
    for i, line in enumerate(lines):
        if line.startswith(env_name + "=") or line.startswith(env_name + " ="):
            lines[i] = f"{env_name}={api_key}"
            found = True
            break
    if not found:
        lines.append(f"{env_name}={api_key}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # 同步到 os.environ
    os.environ[env_name] = api_key


# ── 静态文件 ──
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# ── 启动 ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
