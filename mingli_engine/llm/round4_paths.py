"""
R4 - 路径生成
结合θ参数，为每个流年生成2~3条分叉路径
"""
import json
from .client import call_llm_json


SYSTEM_PROMPT = """你是一位整合命理趋势与心理决策模型的路径规划师。

核心原则：
- 路径不是"预测"，而是"情景规划"
- 每条路径必须说明触发条件（什么样的人倾向选择这条路）
- 每条路径包含可能结果、与命局喜用神的匹配度
- θ参数仅用于过滤和排序路径，不决定路径内容
- 对当前用户要有明确的推荐建议"""

USER_PROMPT_TEMPLATE = """以下是完整数据：

## 用户心性参数
θᵣ（风险偏好）= {theta_r}（{theta_r_type}）
θₛ（人际依赖）= {theta_s}（{theta_s_type}）

## 八字 + 喜用神
{bazi_json}

## 大运流年
{dayun_json}

## R1格局定性
{round1_json}

## R2交叉验证
{round2_json}

## R3流年推演
{round3_json}

请基于以上数据为每个关键流年生成个性化路径，输出严格符合以下JSON结构：
{{
  "paths_by_year": {{
    "流年干支": [
      {{
        "path_name": "路径名称（如：进取独立型）",
        "trigger_profile": "θᵣ/θₛ条件描述（什么样的人会走这条路）",
        "trajectory": "可能的发展轨迹描述（3-5句话）",
        "fate_alignment": "高/中/低",
        "optimization": "如何在此路径上引入命局喜用（2-3句话）",
        "recommended_for_user": true
      }},
      {{
        "path_name": "稳健合作型",
        "trigger_profile": "...",
        "trajectory": "...",
        "fate_alignment": "中",
        "optimization": "...",
        "recommended_for_user": false
      }}
    ]
  }},
  "major_decisions": {{
    "marriage": "婚姻方面的重大决策建议（200字）",
    "career_change": "职业转换的决策建议（200字）",
    "investment": "投资理财的决策建议（200字）"
  }},
  "fate_score": {{
    "base": 72,
    "k_env": 0.8,
    "k_era": 1.1,
    "final_F": 81.2
  }}
}}

每个流年至少2条路径。fate_score 的 base 参考 R3 能量曲线平均值。"""

THETA_TYPE_MAP = {
    "保守型": "倾向于规避风险、稳健行事",
    "中性稳健型": "风险承受力适中、理性决策",
    "进取型": "偏好主动出击、接受高风险高回报",
    "独立型": "倾向独立决策、不依赖他人意见",
    "均衡型": "人际关系和独立决策较为平衡",
    "协作依赖型": "倾向团队协作、重视人际关系",
}


async def run_round4(chart_data: dict, round1_result: dict, round2_result: dict,
                    round3_result: dict, provider: str = None) -> dict:
    """执行R4路径生成"""
    personality = chart_data.get("personality", {})
    bazi = chart_data.get("bazi", {})
    dayun = chart_data.get("dayun", {})

    theta_r = personality.get("theta_r", 0)
    theta_r_type = personality.get("theta_r_type", "中性稳健型")
    theta_s = personality.get("theta_s", 0)
    theta_s_type = personality.get("theta_s_type", "均衡型")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
            theta_r=theta_r,
            theta_r_type=f"{theta_r_type}（{THETA_TYPE_MAP.get(theta_r_type, '')}）",
            theta_s=theta_s,
            theta_s_type=f"{theta_s_type}（{THETA_TYPE_MAP.get(theta_s_type, '')}）",
            bazi_json=json.dumps(bazi, ensure_ascii=False, indent=2),
            dayun_json=json.dumps(dayun, ensure_ascii=False, indent=2),
            round1_json=json.dumps(round1_result, ensure_ascii=False, indent=2),
            round2_json=json.dumps(round2_result, ensure_ascii=False, indent=2),
            round3_json=json.dumps(round3_result, ensure_ascii=False, indent=2),
        )},
    ]

    result = await call_llm_json(messages, provider)
    print("[R4] 路径生成完成")
    return result
