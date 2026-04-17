"""
紫微斗数安星引擎 - 纯算法实现
包含：命宫起例、十四主星安星、四化飞星、辅星
"""
from typing import Dict, List, Optional


# ── 常量 ──
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十四主星
MAIN_STARS = [
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁",
    "七杀", "破军",
]

# 辅星
SUB_STARS = ["文昌", "文曲", "左辅", "右弼", "天魁", "天钺",
             "禄存", "天马", "擎羊", "陀罗", "火星", "铃星",
             "地空", "地劫"]

# 十二宫位名称
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
    "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫",
]

# 命宫起例表：由出生月份和时辰查命宫位置
# 行=时辰地支序号(0=子), 列=农历月份(1-12), 值=命宫地支序号
MINGGONG_TABLE = [
    # 月份:  1   2   3   4   5   6   7   8   9  10  11  12
    [2,  1,  0, 11, 10,  9,  8,  7,  6,  5,  4,  3],  # 子时
    [3,  2,  1,  0, 11, 10,  9,  8,  7,  6,  5,  4],  # 丑时
    [4,  3,  2,  1,  0, 11, 10,  9,  8,  7,  6,  5],  # 寅时
    [5,  4,  3,  2,  1,  0, 11, 10,  9,  8,  7,  6],  # 卯时
    [6,  5,  4,  3,  2,  1,  0, 11, 10,  9,  8,  7],  # 辰时
    [7,  6,  5,  4,  3,  2,  1,  0, 11, 10,  9,  8],  # 巳时
    [8,  7,  6,  5,  4,  3,  2,  1,  0, 11, 10,  9],  # 午时
    [9,  8,  7,  6,  5,  4,  3,  2,  1,  0, 11, 10],  # 未时
    [10, 9,  8,  7,  6,  5,  4,  3,  2,  1,  0, 11],  # 申时
    [11, 10, 9,  8,  7,  6,  5,  4,  3,  2,  1,  0],  # 酉时
    [0,  11, 10, 9,  8,  7,  6,  5,  4,  3,  2,  1],  # 戌时
    [1,  0,  11, 10, 9,  8,  7,  6,  5,  4,  3,  2],  # 亥时
]

# 身宫位置表：由出生月份和时辰
SHENGONG_OFFSETS = [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9]

# 紫微星起例：由五行局和出生日查紫微星所在宫位
# 五行局：水二局、木三局、金四局、土五局、火六局
ZIWEI_QILI = {
    2: [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5,
        4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3],  # 水二局
    3: [2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11,
        10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9],  # 木三局
    4: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7,
        6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5],  # 金四局
    5: [6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3,
        2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],  # 土五局
    6: [2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11,
        10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9],  # 火六局
}

# 紫微星系排列顺序和间距（紫微落宫后，其他星依此排列）
ZIWEI_SERIES = [
    ("紫微", 0),
    ("天机", 1),
    ("太阳", 3),
    ("武曲", 4),
    ("天同", 5),
    ("廉贞", 8),
]

# 天府星系（天府与紫微对称）
TIANFU_SERIES = [
    ("天府", 0),
    ("太阴", 1),
    ("贪狼", 2),
    ("巨门", 3),
    ("天相", 4),
    ("天梁", 5),
    ("七杀", 6),
    ("破军", 10),
]

# 四化表（依年干查化禄、化权、化科、化忌）
SIHUA_TABLE = {
    "甲": {"化禄": "廉贞", "化权": "破军", "化科": "武曲", "化忌": "太阳"},
    "乙": {"化禄": "天机", "化权": "天梁", "化科": "紫微", "化忌": "太阴"},
    "丙": {"化禄": "天同", "化权": "天机", "化科": "文昌", "化忌": "廉贞"},
    "丁": {"化禄": "太阴", "化权": "天同", "化科": "天机", "化忌": "巨门"},
    "戊": {"化禄": "贪狼", "化权": "太阴", "化科": "右弼", "化忌": "天机"},
    "己": {"化禄": "武曲", "化权": "贪狼", "化科": "天梁", "化忌": "文曲"},
    "庚": {"化禄": "太阳", "化权": "武曲", "化科": "太阴", "化忌": "天同"},
    "辛": {"化禄": "巨门", "化权": "太阳", "化科": "文曲", "化忌": "文昌"},
    "壬": {"化禄": "天梁", "化权": "紫微", "化科": "左辅", "化忌": "武曲"},
    "癸": {"化禄": "破军", "化权": "巨门", "化科": "太阴", "化忌": "贪狼"},
}

# 左辅右弼安星表
ZUOFU_TABLE = [3, 3, 3, 6, 6, 6, 9, 9, 9, 12, 12, 12]  # 按月份+时辰
YOUYI_TABLE = [4, 4, 4, 7, 7, 7, 10, 10, 10, 1, 1, 1]

# 文昌文曲安星
WENCHANG_TABLE = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 按时辰
WENQU_TABLE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]

# 禄存安星（按年干）
LUCUN_TABLE = {
    "甲": 2, "乙": 3, "丙": 5, "丁": 6, "戊": 5,
    "己": 6, "庚": 8, "辛": 9, "壬": 11, "癸": 12,
}

# 特殊格局列表
SPECIAL_PATTERNS = [
    {"name": "紫府同宫", "desc": "紫微天府同在一宫，主贵"},
    {"name": "机月同梁", "desc": "天机太阴天同天梁会合，宜公职"},
    {"name": "杀破狼", "desc": "七杀破军贪狼三星会合，主变动"},
    {"name": "明珠出海", "desc": "安命在子午，紫微在子，主贵显"},
    {"name": "日照雷门", "desc": "太阳在卯宫坐命，主光明磊落"},
    {"name": "月朗天门", "desc": "太阴在亥宫坐命，主清雅聪明"},
    {"name": "武贪同宫", "desc": "武曲贪狼同宫，主才兼文武"},
    {"name": "廉贞文武", "desc": "廉贞与文昌文曲会合"},
]


def calculate_ziwei(lunar_month, lunar_day, hour_zhi, year_stem, gender="男"):
    """
    紫微斗数安星主入口

    参数:
        lunar_month: 农历月份 (1-12)
        lunar_day: 农历日 (1-30)
        hour_zhi: 时辰地支序号 (0=子 ... 11=亥)
        year_stem: 年干 (如 "甲")
        gender: "男" / "女"

    返回:
        dict 紫微斗数完整数据
    """
    # 1. 确定命宫位置
    minggong_idx = MINGGONG_TABLE[hour_zhi][lunar_month - 1]

    # 2. 身宫位置
    shengong_idx = (MINGGONG_TABLE[hour_zhi][lunar_month - 1] + SHENGONG_OFFSETS[hour_zhi]) % 12

    # 3. 确定五行局（简化：根据命宫和年干推算）
    wuxing_ju = _calc_wuxing_ju(year_stem, lunar_month, lunar_day, minggong_idx)

    # 4. 安十四主星
    palaces = _init_palaces(minggong_idx)
    _place_main_stars(palaces, wuxing_ju, lunar_day, year_stem)

    # 5. 安辅星
    _place_sub_stars(palaces, year_stem, lunar_month, hour_zhi)

    # 6. 安四化
    sihua = _place_sihua(palaces, year_stem)

    # 7. 检测特殊格局
    patterns = _detect_special_patterns(palaces)

    # 8. 组织输出
    all_palaces = {}
    for i in range(12):
        palace_data = palaces[i]
        all_palaces[str(i + 1)] = {
            "name": palace_data["name"],
            "position": DIZHI[palace_data["position"]],
            "main_stars": palace_data["main_stars"],
            "sub_stars": palace_data["sub_stars"],
            "sihua": palace_data["sihua"],
        }

    # 找命宫主星
    ming_gong_data = palaces[0]
    ming_main_star = ming_gong_data["main_stars"][0] if ming_gong_data["main_stars"] else "空宫"

    return {
        "ming_gong": {
            "palace": minggong_idx + 1,
            "position": DIZHI[minggong_idx],
            "main_star": ming_main_star,
            "sub_stars": ming_gong_data["sub_stars"],
        },
        "sheng_gong": {
            "palace": shengong_idx + 1,
            "position": DIZHI[shengong_idx],
        },
        "wuxing_ju": wuxing_ju,
        "all_palaces": all_palaces,
        "special_patterns": patterns,
        "sihua_summary": sihua,
    }


def _init_palaces(minggong_idx):
    """初始化十二宫"""
    palaces = []
    for i in range(12):
        pos = (minggong_idx + i) % 12
        palaces.append({
            "name": PALACE_NAMES[i],
            "position": pos,
            "main_stars": [],
            "sub_stars": [],
            "sihua": {},
        })
    return palaces


def _calc_wuxing_ju(year_stem, lunar_month, lunar_day, minggong_idx):
    """
    计算五行局（简化算法）
    实际应根据命宫天干和纳音五行来确定
    """
    # 简化：根据年干五行属性分配
    wuxing_map = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
                  "戊": "土", "己": "土", "庚": "金", "辛": "金",
                  "壬": "水", "癸": "水"}
    wx = wuxing_map.get(year_stem, "土")
    ju_map = {"水": 2, "木": 3, "金": 4, "土": 5, "火": 6}
    return ju_map.get(wx, 5)


def _place_main_stars(palaces, wuxing_ju, lunar_day, year_stem):
    """安十四主星"""
    # 紫微星系
    ziwei_idx = ZIWEI_QILI[wuxing_ju][(lunar_day - 1) % 30]
    _place_ziwei_series(palaces, ziwei_idx)

    # 天府星系（与紫微对称）
    tianfu_idx = (4 - ziwei_idx) % 12
    _place_tianfu_series(palaces, tianfu_idx)


def _place_ziwei_series(palaces, ziwei_idx):
    """安紫微星系"""
    for star, offset in ZIWEI_SERIES:
        pos = (ziwei_idx + offset) % 12
        palace = _find_palace_by_position(palaces, pos)
        if palace:
            palace["main_stars"].append(star)


def _place_tianfu_series(palaces, tianfu_idx):
    """安天府星系"""
    for star, offset in TIANFU_SERIES:
        pos = (tianfu_idx + offset) % 12
        palace = _find_palace_by_position(palaces, pos)
        if palace:
            palace["main_stars"].append(star)


def _find_palace_by_position(palaces, position):
    """根据地支位置找到宫位"""
    for p in palaces:
        if p["position"] == position:
            return p
    return None


def _place_sub_stars(palaces, year_stem, lunar_month, hour_zhi):
    """安辅星"""
    # 文昌
    wenchang_pos = WENCHANG_TABLE[hour_zhi] - 1
    p = _find_palace_by_position(palaces, wenchang_pos)
    if p:
        p["sub_stars"].append("文昌")

    # 文曲
    wenqu_pos = WENQU_TABLE[hour_zhi] - 1
    p = _find_palace_by_position(palaces, wenqu_pos)
    if p:
        p["sub_stars"].append("文曲")

    # 左辅
    zuofu_pos = (ZUOFU_TABLE[(lunar_month - 1) % 12] + hour_zhi - 1) % 12
    p = _find_palace_by_position(palaces, zuofu_pos)
    if p:
        p["sub_stars"].append("左辅")

    # 右弼
    youbi_pos = (YOUYI_TABLE[(lunar_month - 1) % 12] + hour_zhi - 1) % 12
    p = _find_palace_by_position(palaces, youbi_pos)
    if p:
        p["sub_stars"].append("右弼")

    # 禄存
    lucun_pos = LUCUN_TABLE.get(year_stem, 5) - 1
    p = _find_palace_by_position(palaces, lucun_pos)
    if p:
        p["sub_stars"].append("禄存")

    # 天魁
    tiangkui_pos = _calc_tiankui_position(year_stem)
    p = _find_palace_by_position(palaces, tiangkui_pos)
    if p:
        p["sub_stars"].append("天魁")

    # 天钺
    tianyue_pos = _calc_tianyue_position(year_stem)
    p = _find_palace_by_position(palaces, tianyue_pos)
    if p:
        p["sub_stars"].append("天钺")


def _calc_tiankui_position(year_stem):
    """天魁安星（按年干）"""
    table = {"甲": 0, "乙": 1, "丙": 2, "丁": 3, "戊": 4,
             "己": 5, "庚": 6, "辛": 7, "壬": 8, "癸": 9}
    return table.get(year_stem, 0)


def _calc_tianyue_position(year_stem):
    """天钺安星（按年干）"""
    table = {"甲": 6, "乙": 5, "丙": 4, "丁": 3, "戊": 2,
             "己": 1, "庚": 0, "辛": 11, "壬": 10, "癸": 9}
    return table.get(year_stem, 6)


def _place_sihua(palaces, year_stem):
    """安四化"""
    sihua_info = SIHUA_TABLE.get(year_stem, {})
    summary = {}

    for hua_type, star_name in sihua_info.items():
        summary[hua_type] = star_name
        # 找到该星所在的宫位
        for palace in palaces:
            if star_name in palace["main_stars"] or star_name in palace["sub_stars"]:
                palace["sihua"][hua_type] = star_name
                break

    return summary


def _detect_special_patterns(palaces):
    """检测特殊格局"""
    patterns_found = []

    # 获取各宫主星集合
    all_stars_map = {}
    for i, palace in enumerate(palaces):
        all_stars_map[i] = set(palace["main_stars"])

    # 紫府同宫
    for pos, stars in all_stars_map.items():
        if "紫微" in stars and "天府" in stars:
            patterns_found.append("紫府同宫")
            break

    # 杀破狼（三颗星分布在命三方）
    has_qisha = any("七杀" in s for s in all_stars_map.values())
    has_pojun = any("破军" in s for s in all_stars_map.values())
    has_tanlang = any("贪狼" in s for s in all_stars_map.values())
    if has_qisha and has_pojun and has_tanlang:
        patterns_found.append("杀破狼")

    # 日照雷门（太阳在卯宫）
    for pos, stars in all_stars_map.items():
        palace_pos = palaces[pos]["position"]
        if "太阳" in stars and palace_pos == 3:  # 卯
            patterns_found.append("日照雷门")
            break

    # 月朗天门（太阴在亥宫）
    for pos, stars in all_stars_map.items():
        palace_pos = palaces[pos]["position"]
        if "太阴" in stars and palace_pos == 11:  # 亥
            patterns_found.append("月朗天门")
            break

    return patterns_found
