"""
奇门遁甲起局引擎 - 纯算法实现
包含：阴阳遁判断、九宫置换、八门九星值符值使
"""
from datetime import datetime
from typing import Dict, List, Optional


# ── 常量 ──
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WUXING_GAN = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]

# 九宫（洛书排列）
# 4 9 2
# 3 5 7
# 8 1 6
GONG_NAMES = {
    1: "坎一宫（北方·水）", 2: "坤二宫（西南·土）",
    3: "震三宫（东方·木）", 4: "巽四宫（东南·木）",
    5: "中五宫（中央·土）", 6: "乾六宫（西北·金）",
    7: "兑七宫（西方·金）", 8: "艮八宫（东北·土）",
    9: "离九宫（南方·火）",
}

# 八门
BA_MEN = ["休门", "死门", "伤门", "杜门", "中门", "开门", "惊门", "生门"]

# 九星
JIU_XING = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]

# 八神
BA_SHEN = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

# 三奇六仪
SAN_QI_LIU_YI = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

# 节气对应遁局数
JIEQI_DUN = {
    # 阳遁（冬至到夏至）
    "冬至": 1, "小寒": 2, "大寒": 3, "立春": 8, "雨水": 9, "惊蛰": 1,
    "春分": 2, "清明": 3, "谷雨": 4, "立夏": 4, "小满": 5, "芒种": 6,
    "夏至": 9, "小暑": 8, "大暑": 7,
    # 阴遁（夏至到冬至）
    "立秋": 2, "处暑": 1, "白露": 9, "秋分": 8, "寒露": 7, "霜降": 6,
    "立冬": 6, "小雪": 5, "大雪": 4,
}

# 阳遁阴遁范围
YANG_DUN_JIEQI = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
                  "春分", "清明", "谷雨", "立夏", "小满", "芒种"]
YIN_DUN_JIEQI = ["夏至", "小暑", "大暑", "立秋", "处暑", "白露",
                 "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]

# 九宫八卦排列顺序
PALACE_ORDER_YANG = [1, 8, 3, 4, 9, 2, 7, 6]  # 阳遁顺布（不含中5宫）
PALACE_ORDER_YIN = [9, 2, 7, 6, 1, 8, 3, 4]    # 阴遁逆布

# 值符值使对应关系
ZHIFU_MEN_MAP = {
    1: ("天蓬", "休门"), 2: ("天芮", "死门"), 3: ("天冲", "伤门"),
    4: ("天辅", "杜门"), 5: ("天禽", "死门"), 6: ("天心", "开门"),
    7: ("天柱", "惊门"), 8: ("天任", "生门"), 9: ("天英", "景门"),
}


def calculate_qimen(year, month, day, hour):
    """
    奇门遁甲起局主入口

    参数:
        year, month, day, hour: 公历日期时间

    返回:
        dict 奇门遁甲完整局数据
    """
    # 1. 确定当前节气
    jieqi = _get_current_jieqi(month, day)
    is_yang = jieqi in YANG_DUN_JIEQI

    # 2. 确定遁局数
    ju_shu = _get_ju_shu(jieqi, year, month, day)

    # 3. 确定旬首和旬中
    xun_shou = _get_xun_shou(day)
    xun_kong = _get_xun_kong(xun_shou)

    # 4. 确定值符值使
    zhifu, zhishi = _get_zhifu_zhishi(ju_shu, is_yang, xun_shou)

    # 5. 起九宫局
    palace_data = _generate_palaces(ju_shu, is_yang, zhifu, zhishi, hour)

    return {
        "jieqi": jieqi,
        "is_yang_dun": is_yang,
        "dun_type": "阳遁" if is_yang else "阴遁",
        "ju_shu": ju_shu,
        "xun_shou": xun_shou,
        "xun_kong": xun_kong,
        "zhifu": zhifu,
        "zhishi": zhishi,
        "palaces": palace_data,
        "summary": _generate_summary(palace_data, is_yang, zhifu, zhishi),
    }


def _get_current_jieqi(month, day):
    """确定当前节气（简化版）"""
    jieqi_schedule = [
        (1, 6, "小寒"), (1, 20, "大寒"),
        (2, 4, "立春"), (2, 19, "雨水"), (3, 6, "惊蛰"), (3, 21, "春分"),
        (4, 5, "清明"), (4, 20, "谷雨"), (5, 6, "立夏"), (5, 21, "小满"),
        (6, 6, "芒种"), (6, 21, "夏至"), (7, 7, "小暑"), (7, 23, "大暑"),
        (8, 7, "立秋"), (8, 23, "处暑"), (9, 8, "白露"), (9, 23, "秋分"),
        (10, 8, "寒露"), (10, 23, "霜降"), (11, 7, "立冬"), (11, 22, "小雪"),
        (12, 7, "大雪"), (12, 22, "冬至"),
    ]

    current_jq = "冬至"
    for m, d, jq_name in jieqi_schedule:
        if (month, day) >= (m, d):
            current_jq = jq_name
    return current_jq


def _get_ju_shu(jieqi, year, month, day):
    """确定遁局数"""
    base_ju = JIEQI_DUN.get(jieqi, 1)
    # 上中下三元：每节气15天分三段
    day_of_period = _days_into_jieqi(month, day)
    if day_of_period <= 5:
        return base_ju  # 上元
    elif day_of_period <= 10:
        return base_ju + 1 if base_ju < 9 else 1  # 中元
    else:
        return base_ju + 2 if base_ju < 8 else (base_ju + 2) % 9 + 1  # 下元


def _days_into_jieqi(month, day):
    """计算距上一个节气的天数（简化）"""
    jieqi_schedule = [6, 20, 4, 19, 6, 21, 5, 20, 6, 21, 6, 21,
                      7, 23, 7, 23, 8, 23, 8, 23, 7, 22, 7, 22]
    idx = (month - 1) * 2
    prev_jie_day = jieqi_schedule[idx]
    if day >= prev_jie_day:
        return day - prev_jie_day
    return 10  # fallback


def _get_xun_shou(day):
    """计算旬首（甲子旬等）"""
    # 60甲子，每10个一旬
    # 甲子旬: 0-9, 甲戌旬: 10-19, 甲申旬: 20-29,
    # 甲午旬: 30-39, 甲辰旬: 40-49, 甲寅旬: 50-59
    xun_names = ["甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅"]
    xun_idx = (day - 1) % 60 // 10
    return xun_names[xun_idx]


def _get_xun_kong(xun_shou):
    """旬中空亡"""
    xun_kong_map = {
        "甲子": ["戌", "亥"], "甲戌": ["申", "酉"],
        "甲申": ["午", "未"], "甲午": ["辰", "巳"],
        "甲辰": ["寅", "卯"], "甲寅": ["子", "丑"],
    }
    return xun_kong_map.get(xun_shou, [])


def _get_zhifu_zhishi(ju_shu, is_yang, xun_shou):
    """
    确定值符（九星）和值使（八门）
    根据局数和旬首确定
    """
    # 值符值使：按旬首在局中的位置确定
    # 简化：根据局数直接对应
    star, men = ZHIFU_MEN_MAP.get(ju_shu, ("天禽", "死门"))
    return star, men


def _generate_palaces(ju_shu, is_yang, zhifu, zhishi, hour):
    """生成九宫局数据"""
    order = PALACE_ORDER_YANG if is_yang else PALACE_ORDER_YIN

    # 三奇六仪排布
    palaces = {}
    for i, gong in enumerate(order):
        qi_idx = (i + ju_shu - 1) % 9
        palaces[gong] = {
            "gong": gong,
            "name": GONG_NAMES[gong],
            "sanqi_liuyi": SAN_QI_LIU_YI[qi_idx] if qi_idx < len(SAN_QI_LIU_YI) else "",
            "star": _assign_star(gong, ju_shu, is_yang, i),
            "men": _assign_men(gong, ju_shu, is_yang, i),
            "shen": _assign_shen(gong, is_yang, i),
        }

    return palaces


def _assign_star(gong, ju_shu, is_yang, index):
    """分配九星"""
    star_order = JIU_XING[:8] if gong != 5 else ["天禽"]
    return star_order[index % len(star_order)]


def _assign_men(gong, ju_shu, is_yang, index):
    """分配八门"""
    men_order = BA_MEN[:8] if gong != 5 else ["中门"]
    return men_order[index % len(men_order)]


def _assign_shen(gong, is_yang, index):
    """分配八神"""
    shen_order = BA_SHEN if is_yang else list(reversed(BA_SHEN))
    return shen_order[index % len(shen_order)]


def _generate_summary(palaces, is_yang, zhifu, zhishi):
    """生成奇门局概要分析"""
    # 找吉门位置
    ji_men = ["开门", "休门", "生门"]
    ji_men_palaces = []
    for gong, data in palaces.items():
        if data["men"] in ji_men:
            ji_men_palaces.append(f"{data['name']}({data['men']})")

    # 找凶门
    xiong_men = ["死门", "惊门", "伤门"]
    xiong_men_palaces = []
    for gong, data in palaces.items():
        if data["men"] in xiong_men:
            xiong_men_palaces.append(f"{data['name']}({data['men']})")

    return {
        "dun_type": "阳遁" if is_yang else "阴遁",
        "zhifu": zhifu,
        "zhishi": zhishi,
        "ji_men_positions": ji_men_palaces,
        "xiong_men_positions": xiong_men_palaces,
        "brief": f"值符{zhifu}值使{zhishi}，吉门在{'、'.join(ji_men_palaces) if ji_men_palaces else '无明显吉门'}",
    }
