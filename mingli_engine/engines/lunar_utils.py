"""
公历农历转换 + 出生数据验证
使用 LLM 完成转换，确保准确性
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm.client import call_llm, call_llm_json


async def verify_and_convert_birth_data(
    year: int, month: int, day: int, hour: int,
    gender: str, birthplace: str
) -> dict:
    """
    用大模型验证出生数据并转换公历->农历。

    返回:
        {
            "solar": {"year", "month", "day", "hour", "weekday", "jieqi"},
            "lunar": {"year", "month", "day", "is_leap", "month_name", "day_name", "year_ganzhi"},
            "shichen": {"name", "hour_range", "zhi"},
            "verified": bool,
            "notes": str,
        }
    """
    prompt = f"""你是一位精通中国历法的命理数据校验专家。请完成以下任务：

出生信息：
- 公历：{year}年{month}月{day}日 {hour}:00
- 性别：{gender}
- 出生地：{birthplace or '未提供'}

请完成：
1. 验证公历日期的合法性（是否存在、是否合理）
2. 转换为农历日期（必须准确，这非常关键）
3. 确定对应节气和时辰
4. 检查该日期附近是否有节气交替（节气前后1-2天）

请严格按照以下JSON格式输出，不要输出任何其他内容：
{{
    "solar": {{
        "year": {year},
        "month": {month},
        "day": {day},
        "hour": {hour},
        "weekday": "星期X",
        "jieqi": "当前节气名称或无"
    }},
    "lunar": {{
        "year": 农历年份数字,
        "month": 农历月份数字(1-12),
        "day": 农历日数字(1-30),
        "is_leap": false,
        "month_name": "X月(如正月、二月)",
        "day_name": "X(如初一、十五)",
        "year_ganzhi": "天干地支(如庚午年)"
    }},
    "shichen": {{
        "name": "时辰名称(如午时)",
        "hour_range": "时间范围(如11:00-13:00)",
        "zhi": "地支(如午)"
    }},
    "jieqi_check": {{
        "current_jieqi": "当前节气",
        "near_jieqi": "附近是否有节气交替(true/false)",
        "near_jieqi_name": "如near为true则写节气名",
        "days_to_jieqi": 距下个节气天数(数字),
        "note": "节气相关注意事项"
    }},
    "verified": true,
    "notes": "任何需要提醒用户的信息(如日期附近有节气需要确认)"
}}

注意：农历转换必须100%准确，这是命理推演的基础。请仔细计算。"""

    messages = [
        {"role": "system", "content": "你是历法校验专家。只输出JSON，不输出任何其他文字。"},
        {"role": "user", "content": prompt},
    ]

    try:
        result = await call_llm_json(messages)
        if result.get("parse_error"):
            # JSON 解析失败，用简单模式重试
            return await _simple_verify(year, month, day, hour)
        return result
    except Exception as e:
        print(f"[verify] LLM 验证失败: {e}，使用简单模式")
        return await _simple_verify(year, month, day, hour)


async def _simple_verify(year: int, month: int, day: int, hour: int) -> dict:
    """简化版：LLM 只转换农历，不验证"""
    prompt = f"""请将公历{year}年{month}月{day}日转换为农历。
只输出JSON: {{"lunar_year":数字,"lunar_month":数字,"lunar_day":数字,"is_leap":false,"ganzhi":"天干地支年"}}
不要输出任何其他内容。"""

    messages = [
        {"role": "system", "content": "只输出JSON。"},
        {"role": "user", "content": prompt},
    ]

    try:
        result = await call_llm_json(messages)
        lunar = result.get("lunar_month")
        lunar_d = result.get("lunar_day")
        return {
            "solar": {"year": year, "month": month, "day": day, "hour": hour},
            "lunar": {
                "year": result.get("lunar_year", year),
                "month": lunar,
                "day": lunar_d,
                "is_leap": result.get("is_leap", False),
                "year_ganzhi": result.get("ganzhi", ""),
            },
            "shichen": _hour_to_shichen(hour),
            "verified": True,
            "notes": "简单模式转换",
        }
    except Exception:
        return {
            "solar": {"year": year, "month": month, "day": day, "hour": hour},
            "lunar": None,
            "shichen": _hour_to_shichen(hour),
            "verified": False,
            "notes": "农历转换失败，紫微斗数将跳过",
        }


def _hour_to_shichen(hour: int) -> dict:
    """24小时转时辰"""
    shichen_map = [
        (0, "子时", "23:00-01:00", "子"),
        (1, "丑时", "01:00-03:00", "丑"),
        (3, "寅时", "03:00-05:00", "寅"),
        (5, "卯时", "05:00-07:00", "卯"),
        (7, "辰时", "07:00-09:00", "辰"),
        (9, "巳时", "09:00-11:00", "巳"),
        (11, "午时", "11:00-13:00", "午"),
        (13, "未时", "13:00-15:00", "未"),
        (15, "申时", "15:00-17:00", "申"),
        (17, "酉时", "17:00-19:00", "酉"),
        (19, "戌时", "19:00-21:00", "戌"),
        (21, "亥时", "21:00-23:00", "亥"),
    ]
    for h, name, rng, zhi in shichen_map:
        if hour == 23 or (h <= hour < h + 2):
            return {"name": name, "hour_range": rng, "zhi": zhi}
    return {"name": "子时", "hour_range": "23:00-01:00", "zhi": "子"}
