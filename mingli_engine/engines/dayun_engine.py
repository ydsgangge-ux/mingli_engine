"""
大运流年引擎 - 纯算法实现
包含：起运岁数、大运天干地支、流年叠加
"""
from datetime import datetime, timedelta
from .bazi_engine import TIANGAN, DIZHI, WUXING_GAN, WUXING_ZHI, WUXING_SHENG, CANGGAN


def calculate_dayun(bazi_data, birth_year, birth_month, birth_day, birth_hour, longitude=116.4):
    """
    计算大运流年
    
    规则：
    - 阳男阴女：顺推（从出生日到下一个节气的天数 ÷ 3 = 起运岁数）
    - 阴男阳女：逆推（从出生日到上一个节气的天数 ÷ 3 = 起运岁数）
    - 每步大运 10 年
    """
    year_yinyang = bazi_data["year_yinyang"]
    gender_yinyang = bazi_data["gender_yinyang"]
    month_stem = TIANGAN.index(bazi_data["month_stem"])
    month_branch_idx = bazi_data.get("month_branch_idx")
    if month_branch_idx is None:
        month_branch_idx = DIZHI.index(bazi_data["month_branch"])
    day_master_idx = TIANGAN.index(bazi_data["day_master"])

    # 判断顺推/逆推
    # 阳年男命或阴年女命：顺推
    # 阴年男命或阳年女命：逆推
    is_forward = (year_yinyang == "阳" and gender_yinyang == "阳") or \
                 (year_yinyang == "阴" and gender_yinyang == "阴")

    # 计算起运岁数
    start_age = _calc_start_age(
        birth_year, birth_month, birth_day, birth_hour,
        month_branch_idx, is_forward, longitude
    )

    # 生成大运序列
    cycles = _generate_cycles(month_stem, month_branch_idx, is_forward, start_age, birth_year)

    # 找到当前大运
    current_year = datetime.now().year
    current_cycle_index = 0
    for i, cycle in enumerate(cycles):
        age_start = int(cycle["age_range"].split("-")[0])
        birth_plus_age = birth_year + age_start
        if birth_plus_age <= current_year < birth_plus_age + 10:
            current_cycle_index = i
            break

    return {
        "start_age": start_age,
        "is_forward": is_forward,
        "cycles": cycles,
        "current_cycle_index": current_cycle_index,
    }


def _calc_start_age(year, month, day, hour, month_branch_idx, is_forward, longitude):
    """
    计算起运岁数
    顺推：出生日到下一个节气的天数 ÷ 3
    逆推：出生日到上一个节气的天数 ÷ 3
    """
    # 节气日期表（简化版 - 使用近似值）
    # 每月两个节气，此处使用12个"节"（立春、惊蛰、清明...）
    jieqi_approx = _get_approx_jieqi_dates(year)

    birth_dt = datetime(year, month, day, hour, 0)

    # 月支对应的节
    branch_to_jie = {
        2: "立春", 3: "惊蛰", 4: "清明", 5: "立夏",
        6: "芒种", 7: "小暑", 8: "立秋", 9: "白露",
        10: "寒露", 11: "立冬", 0: "大雪", 1: "小寒",
    }

    # 找当前月支对应的节气和下一个/上一个节气
    jie_name = branch_to_jie.get(month_branch_idx, "立春")
    jie_names_ordered = [
        "小寒", "立春", "惊蛰", "清明", "立夏", "芒种",
        "小暑", "立秋", "白露", "寒露", "立冬", "大雪",
    ]

    current_jie_idx = jie_names_ordered.index(jie_name)

    if is_forward:
        # 顺推：找下一个节气
        next_jie_idx = (current_jie_idx + 1) % 12
        next_jie_name = jie_names_ordered[next_jie_idx]

        # 获取下一个节气日期
        next_dt = jieqi_approx.get(next_jie_name)
        if next_dt is None:
            next_year_jieqi = _get_approx_jieqi_dates(year + 1)
            next_dt = next_year_jieqi.get(next_jie_name)

        if next_dt and birth_dt < next_dt:
            days = (next_dt - birth_dt).days
        else:
            days = 30  # fallback
    else:
        # 逆推：找上一个节气
        prev_jie_idx = (current_jie_idx - 1) % 12
        prev_jie_name = jie_names_ordered[prev_jie_idx]

        prev_dt = jieqi_approx.get(prev_jie_name)
        if prev_dt is None:
            prev_year_jieqi = _get_approx_jieqi_dates(year - 1)
            prev_dt = prev_year_jieqi.get(prev_jie_name)

        if prev_dt and birth_dt > prev_dt:
            days = (birth_dt - prev_dt).days
        else:
            days = 30  # fallback

    # 起运岁数 = 天数 ÷ 3，四舍五入
    start_age = max(1, round(days / 3))
    return start_age


def _get_approx_jieqi_dates(year):
    """
    近似节气日期表（简化版）
    实际生产环境应使用精确天文历数据
    """
    # 简化的节气近似日期 (月, 日)
    jieqi_day_map = {
        "小寒": (1, 6), "立春": (2, 4), "惊蛰": (3, 6),
        "清明": (4, 5), "立夏": (5, 6), "芒种": (6, 6),
        "小暑": (7, 7), "立秋": (8, 7), "白露": (9, 8),
        "寒露": (10, 8), "立冬": (11, 7), "大雪": (12, 7),
    }

    result = {}
    for name, (m, d) in jieqi_day_map.items():
        result[name] = datetime(year, m, d, 0, 0)
    return result


def _generate_cycles(month_stem, month_branch, is_forward, start_age, birth_year):
    """生成大运序列（一般取8-10步）"""
    cycles = []
    num_cycles = 8

    for i in range(num_cycles):
        step = i + 1 if is_forward else -(i + 1)

        new_stem = (month_stem + step) % 10
        new_branch = (month_branch + step) % 12

        age_start = start_age + i * 10
        age_end = age_start + 10

        # 流年列表
        years = []
        for j in range(10):
            dy_year = birth_year + age_start + j
            dy_stem = (dy_year - 4) % 10
            dy_branch = (dy_year - 4) % 12
            years.append(f"{dy_year}{TIANGAN[dy_stem]}{DIZHI[dy_branch]}")

        cycles.append({
            "cycle_index": i,
            "age_range": f"{age_start}-{age_end}",
            "stem": TIANGAN[new_stem],
            "branch": DIZHI[new_branch],
            "stem_wuxing": WUXING_GAN[new_stem],
            "branch_wuxing": WUXING_ZHI[new_branch],
            "years": years,
        })

    return cycles


def get_current_liunian(day_master_idx, current_year, bazi_data, dayun_data):
    """
    获取当前流年详细信息
    """
    stem = (current_year - 4) % 10
    branch = (current_year - 4) % 12

    # 与日主的关系
    from .bazi_engine import SHISHEN_TABLE
    shishen = SHISHEN_TABLE[day_master_idx][stem]

    # 与大运的关系
    dayun_stem = ""
    dayun_branch = ""
    if dayun_data and dayun_data.get("cycles"):
        for cycle in dayun_data["cycles"]:
            age_start = int(cycle["age_range"].split("-")[0])
            if age_start <= (current_year - int(bazi_data.get("birth_year", 1990))) < age_start + 10:
                dayun_stem = cycle["stem"]
                dayun_branch = cycle["branch"]
                break

    return {
        "year": current_year,
        "stem": TIANGAN[stem],
        "branch": DIZHI[branch],
        "ganzhi": f"{TIANGAN[stem]}{DIZHI[branch]}",
        "stem_wuxing": WUXING_GAN[stem],
        "branch_wuxing": WUXING_ZHI[branch],
        "shishen_to_daymaster": shishen,
        "dayun_stem": dayun_stem,
        "dayun_branch": dayun_branch,
        "hidden_stems": CANGGAN.get(DIZHI[branch], []),
    }
