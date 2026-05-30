"""
R1 - 格局定性
仅看八字数据，定性格局、喜用神、性格特征
"""
import json
from .client import call_llm_json


SYSTEM_PROMPT = """你是一位严格遵循八字命理内部推演逻辑的格局分析师。你的任务是仅根据八字数据，完成格局定性分析。

严格规则：
1. 禁止使用"可能"、"也许"、"大概"等模糊词——每个结论必须给出推理依据
2. 若存在格局争议，明确列出两种解读并说明各自成立条件
3. 输出必须严格符合指定JSON结构，不输出任何额外文字
4. 本轮不分析紫微和奇门数据，即使它们在JSON中存在

请根据以下八字数据进行格局定性分析。"""

USER_PROMPT_TEMPLATE = """以下是八字排盘数据：

{bazi_json}

以下是用户家庭背景信息（辅助解盘参考）：

{family_info}

请完成格局定性分析，输出严格符合以下JSON结构：
{{
  "pattern_name": "格局名称",
  "pattern_reasoning": "格局判定推理过程（150-300字）",
  "day_master_analysis": "日主分析（包含强弱判断依据，150-200字）",
  "xi_shen_reasoning": "喜用神分析推理（100-200字）",
  "character_traits": ["性格特征1", "性格特征2", "性格特征3", "性格特征4", "性格特征5"],
  "life_risks": ["人生风险点1", "人生风险点2"],
  "family_influence_note": "结合家庭背景的简短解读（100字以内，说明家庭出身对命局的可能影响）",
  "disputes": null
}}

注意：disputes 为 null 表示无争议，有争议时填写争议解读字符串。
family_influence_note 结合提供的家庭背景信息，分析家庭环境对命主格局的强化或制约作用。"""


async def run_round1(chart_data: dict, provider: str = None) -> dict:
    """执行R1格局定性"""
    bazi = chart_data.get("bazi", {})
    user = chart_data.get("user", {})
    bazi_json = json.dumps(bazi, ensure_ascii=False, indent=2)

    father_occ = user.get("father_occupation", "")
    mother_occ = user.get("mother_occupation", "")
    family_bg = user.get("family_background", "")

    family_parts = []
    if father_occ:
        family_parts.append(f"父亲职业：{father_occ}")
    if mother_occ:
        family_parts.append(f"母亲职业：{mother_occ}")
    if family_bg:
        family_parts.append(f"家庭背景：{family_bg}")
    family_info = "、".join(family_parts) if family_parts else "未提供家庭背景信息"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(bazi_json=bazi_json, family_info=family_info)},
    ]

    result = await call_llm_json(messages, provider)
    print("[R1] 格局定性完成")
    return result
