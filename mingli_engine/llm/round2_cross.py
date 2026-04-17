"""
R2 - 交叉验证
引入紫微+奇门，验证R1结论，识别矛盾点
"""
import json
from .client import call_llm_json


SYSTEM_PROMPT = """你是一位三系术数（八字、紫微斗数、奇门遁甲）交叉验证专家。上一轮已完成八字格局定性。

你的任务是：
1. 用紫微斗数命宫、官禄宫、财帛宫的星曜配置验证R1结论
2. 用奇门遁甲终身局的宫位能量做第三维度印证
3. 明确标注三系一致项（增强置信度）和矛盾项（降低置信度，提示解读限制）
4. 矛盾不可强行调和——如实列出，说明各系统的解释框架差异"""

USER_PROMPT_TEMPLATE = """以下是完整的命理数据：

## 八字排盘
{bazi_json}

## R1格局定性结论
{round1_json}

## 紫微斗数
{ziwei_json}

## 奇门遁甲
{qimen_json}

请进行交叉验证，输出严格符合以下JSON结构：
{{
  "consensus": [
    {{
      "point": "一致的观点描述",
      "bazi": "八字依据",
      "ziwei": "紫微依据（如无紫微数据则填'无数据'）",
      "confidence": 0.85
    }}
  ],
  "contradictions": [
    {{
      "point": "矛盾的观点描述",
      "bazi": "八字说法",
      "ziwei": "紫微说法",
      "note": "框架差异说明"
    }}
  ],
  "marriage_portrait": "婚姻感情画像（200-300字，综合三系分析）",
  "career_sectors": ["适合行业1", "适合行业2", "适合行业3"],
  "ziwei_special_patterns": ["紫微特殊格局1"]
}}

consensus 至少3项，contradictions 0-3项。"""


async def run_round2(chart_data: dict, round1_result: dict, provider: str = None) -> dict:
    """执行R2交叉验证"""
    bazi = chart_data.get("bazi", {})
    ziwei = chart_data.get("ziwei", {})
    qimen = chart_data.get("qimen", {})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
            bazi_json=json.dumps(bazi, ensure_ascii=False, indent=2),
            round1_json=json.dumps(round1_result, ensure_ascii=False, indent=2),
            ziwei_json=json.dumps(ziwei, ensure_ascii=False, indent=2) if ziwei else "{}（无紫微数据）",
            qimen_json=json.dumps(qimen, ensure_ascii=False, indent=2) if qimen else "{}（无奇门数据）",
        )},
    ]

    result = await call_llm_json(messages, provider)
    print("[R2] 交叉验证完成")
    return result
