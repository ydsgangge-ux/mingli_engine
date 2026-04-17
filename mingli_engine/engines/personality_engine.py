"""
心性参数引擎 - θ值计算
10题标准化问卷评分，计算 θᵣ（风险偏好）和 θₛ（人际依赖）
"""
from typing import List, Dict


# 问卷题目定义
QUESTIONS = [
    {
        "id": 1,
        "text": "面对一个高风险高回报的投资机会，你会？",
        "options": {
            "A": "仔细评估后选择稳健的中等回报方案",
            "B": "果断投入，追求最大化收益",
        },
        "params": ["theta_r"],
    },
    {
        "id": 2,
        "text": "工作中遇到从未接触过的难题，你更倾向于？",
        "options": {
            "A": "请教有经验的同事或上级",
            "B": "自己钻研，尝试独立解决",
        },
        "params": ["theta_r"],
    },
    {
        "id": 3,
        "text": "周末更愿意怎么度过？",
        "options": {
            "A": "参加社交聚会，结交新朋友",
            "B": "独处阅读或进行个人爱好",
        },
        "params": ["theta_s"],
    },
    {
        "id": 4,
        "text": "做重大决定时，你通常会？",
        "options": {
            "A": "信任自己的直觉和判断",
            "B": "广泛征求身边人的意见",
        },
        "params": ["theta_s_reverse"],
    },
    {
        "id": 5,
        "text": "你的理想职业环境是？",
        "options": {
            "A": "制度完善、流程清晰的稳定组织",
            "B": "充满变化、鼓励创新的创业团队",
        },
        "params": ["theta_r"],
    },
    {
        "id": 6,
        "text": "面对失败的经历，你通常？",
        "options": {
            "A": "认真总结教训，避免再犯",
            "B": "迅速翻篇，把精力投向下一个目标",
        },
        "params": ["theta_r"],
    },
    {
        "id": 7,
        "text": "关于财务规划，你更认同？",
        "options": {
            "A": "储备应急资金是第一要务",
            "B": "资金不流动等于贬值，合理配置就好",
        },
        "params": ["theta_r"],
    },
    {
        "id": 8,
        "text": "团队项目中你通常扮演什么角色？",
        "options": {
            "A": "协调者，负责沟通和整合意见",
            "B": "执行者，专注于完成自己负责的部分",
        },
        "params": ["theta_s"],
    },
    {
        "id": 9,
        "text": "对于人生规划，你更看重？",
        "options": {
            "A": "建立深厚的人际关系网络",
            "B": "积累个人能力和专业素养",
        },
        "params": ["theta_s"],
    },
    {
        "id": 10,
        "text": "面对行业变革（如AI冲击），你的态度？",
        "options": {
            "A": "谨慎观望，等待局势明朗再做选择",
            "B": "主动学习，第一时间拥抱变化",
        },
        "params": ["theta_r"],
    },
]


def calculate_personality(answers: Dict[int, str]) -> Dict:
    """
    根据问卷答案计算心性参数

    参数:
        answers: {题目编号: "A"或"B"}  如 {1: "B", 2: "A", ...}

    返回:
        {
            "theta_r": int,         # -6 ~ +6
            "theta_r_type": str,    # 保守型/中性稳健型/进取型
            "theta_s": int,         # -4 ~ +4
            "theta_s_type": str,    # 独立型/均衡型/协作依赖型
            "answers": dict,
        }
    """
    theta_r = 0
    theta_s = 0

    for q in QUESTIONS:
        qid = q["id"]
        answer = answers.get(qid, "A")
        params = q["params"]

        for param in params:
            if param == "theta_r":
                # B=+1（进取）, A=-1（保守）
                theta_r += 1 if answer == "B" else -1
            elif param == "theta_s":
                # B=+1（独立）, A=-1（依赖）
                theta_s += 1 if answer == "B" else -1
            elif param == "theta_s_reverse":
                # A=+1（独立）, B=-1（依赖） - 注意反转
                theta_s += 1 if answer == "A" else -1

    # 类型映射
    theta_r_type = _map_theta_r(theta_r)
    theta_s_type = _map_theta_s(theta_s)

    return {
        "theta_r": theta_r,
        "theta_r_type": theta_r_type,
        "theta_s": theta_s,
        "theta_s_type": theta_s_type,
        "answers": answers,
        "blind_spots": _detect_blind_spots(theta_r, theta_s),
    }


def _map_theta_r(value):
    """θᵣ 类型映射"""
    if value <= -3:
        return "保守型"
    elif value <= 2:
        return "中性稳健型"
    else:
        return "进取型"


def _map_theta_s(value):
    """θₛ 类型映射"""
    if value <= -2:
        return "独立型"
    elif value <= 1:
        return "均衡型"
    else:
        return "协作依赖型"


def _detect_blind_spots(theta_r, theta_s):
    """检测心性盲点"""
    spots = []
    if theta_r <= -3:
        spots.append("过度保守可能错失高杠杆机会")
    elif theta_r >= 5:
        spots.append("过度冒险可能导致重大损失")
    if theta_s <= -3:
        spots.append("过度独立可能在需要资源时缺乏支持网络")
    elif theta_s >= 3:
        spots.append("过度依赖他人可能削弱独立决策能力")
    if theta_r >= 3 and theta_s <= -2:
        spots.append("高进取+高独立的组合在逆境中容易孤立无援")
    if theta_r <= -2 and theta_s >= 2:
        spots.append("低风险偏好+高协作依赖可能陷入群体思维")
    if not spots:
        spots.append("心性配置较为均衡，无明显盲点")
    return spots


def get_questions():
    """获取问卷题目列表（给前端用）"""
    return [{
        "id": q["id"],
        "text": q["text"],
        "optionA": q["options"]["A"],
        "optionB": q["options"]["B"],
    } for q in QUESTIONS]
