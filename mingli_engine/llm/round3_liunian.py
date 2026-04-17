"""
R3 - 流年推演
未来3关键流年 + 12个月热力图 + 能量曲线
"""
import json
from datetime import datetime
from .client import call_llm_json


SYSTEM_PROMPT = """你是一位命理流年推演专家。基于大运流年数据与前两轮定性结论，推演未来趋势。

关键约束：
- 流年推演必须逐步给出"大运底色 → 流年天干地支作用 → 与日主/喜用神关系 → 结论"的完整推理链
- 禁止直接输出结论，必须展示推理过程
- 能量等级用1-5分（1=极低，5=极高）
- 每季度热力图必须包含具体的优势、风险和建议"""

USER_PROMPT_TEMPLATE = """以下是完整数据：

## 八字 + 喜用神
{bazi_json}

## 大运流年
{dayun_json}

## R1格局定性
{round1_json}

## R2交叉验证
{round2_json}

当前年份：{current_year}

请进行流年推演，输出严格符合以下JSON结构：
{{
  "quarterly_heatmap": [
    {{
      "period": "Q1(1-3月)",
      "energy_level": 4,
      "advantage": "该季度优势描述",
      "risk": "该季度风险描述",
      "advice": "具体行动建议"
    }},
    {{
      "period": "Q2(4-6月)",
      "energy_level": 3,
      "advantage": "...",
      "risk": "...",
      "advice": "..."
    }},
    {{
      "period": "Q3(7-9月)",
      "energy_level": 5,
      "advantage": "...",
      "risk": "...",
      "advice": "..."
    }},
    {{
      "period": "Q4(10-12月)",
      "energy_level": 2,
      "advantage": "...",
      "risk": "...",
      "advice": "..."
    }}
  ],
  "key_years": [
    {{
      "year": "2026丙午",
      "stem_branch_analysis": "流年天干地支与命局的作用分析（200字）",
      "dayun_interaction": "与大运的交互影响分析（150字）",
      "core_theme": "该年核心主题（20字以内）"
    }}
  ],
  "energy_curve": [
    {{"age": 25, "score": 72}},
    {{"age": 30, "score": 85}},
    {{"age": 35, "score": 78}},
    {{"age": 40, "score": 90}},
    {{"age": 45, "score": 65}},
    {{"age": 50, "score": 82}},
    {{"age": 55, "score": 70}},
    {{"age": 60, "score": 88}}
  ]
}}

key_years 至少3个关键流年。energy_curve 根据大运起伏生成8个数据点。"""


async def run_round3(chart_data: dict, round1_result: dict, round2_result: dict, provider: str = None) -> dict:
    """执行R3流年推演"""
    bazi = chart_data.get("bazi", {})
    dayun = chart_data.get("dayun", {})
    current_year = datetime.now().year

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
            bazi_json=json.dumps(bazi, ensure_ascii=False, indent=2),
            dayun_json=json.dumps(dayun, ensure_ascii=False, indent=2),
            round1_json=json.dumps(round1_result, ensure_ascii=False, indent=2),
            round2_json=json.dumps(round2_result, ensure_ascii=False, indent=2),
            current_year=current_year,
        )},
    ]

    result = await call_llm_json(messages, provider)
    print("[R3] 流年推演完成")
    return result
