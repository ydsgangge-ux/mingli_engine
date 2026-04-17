"""
chart_builder.py - 合并各引擎输出为 chart_data.json
排盘前先用大模型验证出生数据 + 公历转农历
"""
import json
from datetime import datetime
from pathlib import Path

from .bazi_engine import calculate_bazi
from .dayun_engine import calculate_dayun, get_current_liunian
from .ziwei_engine import calculate_ziwei
from .qimen_engine import calculate_qimen
from .personality_engine import calculate_personality
from .lunar_utils import verify_and_convert_birth_data

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ENGINE_VERSION


async def build_chart_data(user_info: dict, answers: dict) -> dict:
    """
    构建完整的 chart_data.json

    参数:
        user_info: {
            "name": str, "gender": "男"/"女",
            "birth_year": int, "birth_month": int, "birth_day": int,
            "birth_hour": int, "birthplace": str,
            "longitude": float (可选, 默认116.4),
        }
        answers: 心性测试答案 {题号: "A"/"B"}

    返回:
        dict 完整的 chart_data
    """
    year = user_info["birth_year"]
    month = user_info["birth_month"]
    day = user_info["birth_day"]
    hour = user_info["birth_hour"]
    gender = user_info.get("gender", "男")
    longitude = user_info.get("longitude", 116.4)
    birthplace = user_info.get("birthplace", "")

    # ── 0. 大模型验证出生数据 + 公历转农历 ──
    birth_verify = await verify_and_convert_birth_data(
        year, month, day, hour, gender, birthplace
    )

    lunar_month = None
    lunar_day = None
    lunar_data = birth_verify.get("lunar")
    if lunar_data and lunar_data.get("month") and lunar_data.get("day"):
        lunar_month = lunar_data["month"]
        lunar_day = lunar_data["day"]

    # 1. 八字排盘
    bazi = calculate_bazi(year, month, day, hour, gender, longitude)

    # 2. 大运流年
    dayun = calculate_dayun(bazi, year, month, day, hour, longitude)

    # 3. 心性参数
    personality = calculate_personality(answers)

    # 4. 紫微斗数（使用大模型转换的农历日期）
    ziwei = None
    # 用户手动填写的农历优先
    manual_lunar_month = user_info.get("lunar_month")
    manual_lunar_day = user_info.get("lunar_day")
    if manual_lunar_month and manual_lunar_day:
        lunar_month = manual_lunar_month
        lunar_day = manual_lunar_day

    if lunar_month and lunar_day:
        hour_zhi = _solar_hour_to_zhi(hour)
        year_stem = bazi["year_stem"]
        try:
            ziwei = calculate_ziwei(lunar_month, lunar_day, hour_zhi, year_stem, gender)
        except Exception as e:
            ziwei = {"error": f"紫微排盘计算异常: {e}"}

    # 5. 奇门遁甲
    qimen = calculate_qimen(year, month, day, hour)

    # 6. 当前流年
    from .bazi_engine import TIANGAN
    dm_idx = TIANGAN.index(bazi["day_master"])
    current_liunian = get_current_liunian(dm_idx, datetime.now().year, user_info, dayun)

    # 合并输出
    chart_data = {
        "user": {
            "name": user_info.get("name", ""),
            "gender": gender,
            "birth": f"{year}-{month:02d}-{day:02d} {hour:02d}:00",
            "birthplace": birthplace,
            "longitude": longitude,
        },
        "birth_verify": birth_verify,
        "bazi": bazi,
        "dayun": dayun,
        "personality": personality,
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "engine_version": ENGINE_VERSION,
        },
    }

    if ziwei:
        chart_data["ziwei"] = ziwei

    if qimen:
        chart_data["qimen"] = qimen

    if current_liunian:
        chart_data["current_liunian"] = current_liunian

    return chart_data


def _solar_hour_to_zhi(hour):
    """24小时制转时辰地支序号"""
    if hour == 23 or hour == 0:
        return 0  # 子
    return (hour + 1) // 2


def save_chart_data(chart_data: dict, output_dir: str = "output") -> str:
    """保存 chart_data 到文件"""
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    name = chart_data["user"].get("name", "anonymous")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chart_data_{name}_{timestamp}.json"
    filepath = out_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chart_data, f, ensure_ascii=False, indent=2)

    return str(filepath)
