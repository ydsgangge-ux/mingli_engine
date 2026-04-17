"""
报告组装器 - 将各轮LLM输出合并为八模块完整报告
输出 Markdown 格式
"""
import json
from pathlib import Path
from typing import Dict


REPORT_TEMPLATE = """# {name} 的命理分析报告

> 生成时间：{generated_at} | 引擎版本：{engine_version}

---

## M1 · 八字基因图谱

### 四柱八字

|  | 年柱 | 月柱 | 日柱 | 时柱 |
|---|---|---|---|---|
| **天干** | {ys} | {ms} | **{ds}** | {hs} |
| **地支** | {yb} | {mb} | {db} | {hb} |
| **十神** | {ysg} | {msg} | 日主 | {hsg} |

- **日主**：{day_master}（{day_master_wx}）· {strength}
- **纳音**：{nayin}
- **喜用神**：{xi_shen}
- **忌神**：{ji_shen}
- **五行得分**：金 {fe_jin} | 木 {fe_mu} | 水 {fe_shui} | 火 {fe_huo} | 土 {fe_tu}

### 格局定性

**格局**：{pattern_name}

{pattern_reasoning}

### 日主分析

{day_master_analysis}

### 喜用神推理

{xi_shen_reasoning}

### 性格特征

{character_traits}

### 人生风险提示

{life_risks}

---

## M2 · 紫微斗数命盘

{ziwei_section}

---

## M3 · 婚姻感情与家道

{marriage_portrait}

---

## M4 · 事业财务与时代机遇

### 适合行业方向

{career_sectors}

### 关键流年分析

{key_years_section}

---

## M5 · 奇门遁甲终身局

{qimen_section}

---

## M6 · 流年热力图

### 季度能量热力图

{heatmap_section}

---

## M7 · 心性决策参数

### θ 参数报告

| 参数 | 分值 | 类型标签 |
|---|---|---|
| θᵣ（风险偏好） | {theta_r} | {theta_r_type} |
| θₛ（人际依赖） | {theta_s} | {theta_s_type} |

### 心性盲点预警

{blind_spots}

---

## M8 · 路径推演

### 关键流年分叉路径

{paths_section}

### 重大决策框架

- **婚姻**：{marriage_decision}
- **职业转换**：{career_decision}
- **投资理财**：{investment_decision}

### 命运评分

| 维度 | 得分 |
|---|---|
| 基础分（base） | {fate_base} |
| 环境系数（k_env） | {fate_k_env} |
| 时代系数（k_era） | {fate_k_era} |
| 综合命运指数（F） | {fate_final} |

---

> **免责声明**：本报告基于传统命理框架与现代系统思维构建，旨在提供趋势分析与自我认知的多元视角。命运由先天基础、后天选择和随机事件共同塑造。报告揭示的是可能性框架而非必然结论，所有重大人生决策请结合现实情况、专业建议和内心指引综合判断。
"""


def assemble_report(
    chart_data: Dict,
    round1: Dict,
    round2: Dict,
    round3: Dict,
    round4: Dict,
) -> str:
    """组装完整报告"""
    user = chart_data.get("user", {})
    bazi = chart_data.get("bazi", {})
    personality = chart_data.get("personality", {})
    meta = chart_data.get("meta", {})

    # M1 - 八字基因图谱
    nayin = bazi.get("nayin", "")
    nayin_str = f"{nayin[0]} / {nayin[1]}" if isinstance(nayin, (list, tuple)) and len(nayin) == 2 else str(nayin)

    fe = bazi.get("five_elements_score", {})
    character_traits = "\n".join(f"- {t}" for t in round1.get("character_traits", []))
    life_risks = "\n".join(f"- {t}" for t in round1.get("life_risks", []))

    # M2 - 紫微斗数
    ziwei_section = _build_ziwei_section(chart_data.get("ziwei"), round2)

    # M4 - 事业 + 流年
    career_sectors = "\n".join(f"- {s}" for s in round2.get("career_sectors", []))
    key_years_section = _build_key_years_section(round3)

    # M5 - 奇门
    qimen_section = _build_qimen_section(chart_data.get("qimen"), round2)

    # M6 - 热力图
    heatmap_section = _build_heatmap_section(round3)

    # M7 - 心性参数
    blind_spots = "\n".join(f"- {b}" for b in personality.get("blind_spots", []))

    # M8 - 路径
    paths_section = _build_paths_section(round4)

    # 重大决策
    major = round4.get("major_decisions", {})
    fate = round4.get("fate_score", {})

    report = REPORT_TEMPLATE.format(
        name=user.get("name", "用户"),
        generated_at=meta.get("generated_at", ""),
        engine_version=meta.get("engine_version", ""),
        # 四柱
        ys=bazi.get("year_stem", ""), yb=bazi.get("year_branch", ""),
        ms=bazi.get("month_stem", ""), mb=bazi.get("month_branch", ""),
        ds=bazi.get("day_stem", ""), db=bazi.get("day_branch", ""),
        hs=bazi.get("hour_stem", ""), hb=bazi.get("hour_branch", ""),
        # 十神
        ysg=bazi.get("ten_gods", {}).get("year", {}).get("stem", ""),
        msg=bazi.get("ten_gods", {}).get("month", {}).get("stem", ""),
        hsg=bazi.get("ten_gods", {}).get("hour", {}).get("stem", ""),
        # 核心
        day_master=bazi.get("day_master", ""),
        day_master_wx=bazi.get("day_master_wuxing", ""),
        strength=bazi.get("day_master_strength", ""),
        nayin=nayin_str,
        xi_shen="、".join(bazi.get("xi_yong_shen", [])),
        ji_shen="、".join(bazi.get("ji_shen", [])),
        fe_jin=fe.get("金", 0), fe_mu=fe.get("木", 0), fe_shui=fe.get("水", 0),
        fe_huo=fe.get("火", 0), fe_tu=fe.get("土", 0),
        # R1
        pattern_name=round1.get("pattern_name", ""),
        pattern_reasoning=round1.get("pattern_reasoning", ""),
        day_master_analysis=round1.get("day_master_analysis", ""),
        xi_shen_reasoning=round1.get("xi_shen_reasoning", ""),
        character_traits=character_traits,
        life_risks=life_risks,
        # M2-M8
        ziwei_section=ziwei_section,
        marriage_portrait=round2.get("marriage_portrait", ""),
        career_sectors=career_sectors,
        key_years_section=key_years_section,
        qimen_section=qimen_section,
        heatmap_section=heatmap_section,
        theta_r=personality.get("theta_r", 0),
        theta_r_type=personality.get("theta_r_type", ""),
        theta_s=personality.get("theta_s", 0),
        theta_s_type=personality.get("theta_s_type", ""),
        blind_spots=blind_spots,
        paths_section=paths_section,
        marriage_decision=major.get("marriage", ""),
        career_decision=major.get("career_change", ""),
        investment_decision=major.get("investment", ""),
        fate_base=fate.get("base", 0),
        fate_k_env=fate.get("k_env", 0),
        fate_k_era=fate.get("k_era", 0),
        fate_final=fate.get("final_F", 0),
    )

    return report


def _build_ziwei_section(ziwei_data, round2):
    if not ziwei_data or ziwei_data.get("error"):
        return "（紫微斗数数据未生成）"

    mg = ziwei_data.get("ming_gong", {})
    sg = ziwei_data.get("sheng_gong", {})
    sp = ziwei_data.get("special_patterns", [])

    lines = [
        f"**命宫**：{mg.get('position', '')}宫 · 主星 {mg.get('main_star', '')} · 辅星 {'、'.join(mg.get('sub_stars', []))}",
        f"**身宫**：{sg.get('position', '')}宫",
        f"**五行局**：{ziwei_data.get('wuxing_ju', '')}局",
    ]

    if sp:
        lines.append(f"\n**特殊格局**：{'、'.join(sp)}")

    # 十二宫概要
    palaces = ziwei_data.get("all_palaces", {})
    if palaces:
        lines.append("\n### 十二宫位概要\n")
        lines.append("| 宫位 | 位置 | 主星 | 四化 |")
        lines.append("|---|---|---|---|")
        for idx, palace in palaces.items():
            name = palace.get("name", "")
            pos = palace.get("position", "")
            stars = "、".join(palace.get("main_stars", [])) or "空宫"
            sihua = "、".join(f"{k}:{v}" for k, v in palace.get("sihua", {}).items()) or "-"
            lines.append(f"| {name} | {pos} | {stars} | {sihua} |")

    return "\n".join(lines)


def _build_qimen_section(qimen_data, round2):
    if not qimen_data:
        return "（奇门遁甲数据未生成）"

    summary = qimen_data.get("summary", {})
    lines = [
        f"**遁局类型**：{summary.get('dun_type', '')}",
        f"**局数**：{qimen_data.get('ju_shu', '')}局",
        f"**值符**：{summary.get('zhifu', '')}",
        f"**值使**：{summary.get('zhishi', '')}",
        f"\n{summary.get('brief', '')}",
    ]

    # 九宫概要
    palaces = qimen_data.get("palaces", {})
    if palaces:
        lines.append("\n### 九宫排布\n")
        lines.append("| 宫位 | 三奇六仪 | 九星 | 八门 | 八神 |")
        lines.append("|---|---|---|---|---|")
        for gong, data in palaces.items():
            lines.append(f"| {data.get('name', '')} | {data.get('sanqi_liuyi', '')} | {data.get('star', '')} | {data.get('men', '')} | {data.get('shen', '')} |")

    return "\n".join(lines)


def _build_key_years_section(round3):
    key_years = round3.get("key_years", [])
    if not key_years:
        return "（无流年数据）"

    lines = []
    for ky in key_years:
        lines.append(f"#### {ky.get('year', '')}")
        lines.append(f"- **核心主题**：{ky.get('core_theme', '')}")
        lines.append(f"- **天干地支分析**：{ky.get('stem_branch_analysis', '')}")
        lines.append(f"- **大运交互**：{ky.get('dayun_interaction', '')}")
        lines.append("")

    return "\n".join(lines)


def _build_heatmap_section(round3):
    heatmap = round3.get("quarterly_heatmap", [])
    if not heatmap:
        return "（无热力图数据）"

    lines = ["| 季度 | 能量等级 | 优势 | 风险 | 建议 |",
             "|---|---|---|---|---|"]
    for q in heatmap:
        energy_bar = "★" * q.get("energy_level", 0) + "☆" * (5 - q.get("energy_level", 0))
        lines.append(f"| {q.get('period', '')} | {energy_bar} | {q.get('advantage', '')} | {q.get('risk', '')} | {q.get('advice', '')} |")

    return "\n".join(lines)


def _build_paths_section(round4):
    paths_by_year = round4.get("paths_by_year", {})
    if not paths_by_year:
        return "（无路径数据）"

    lines = []
    for year, paths in paths_by_year.items():
        lines.append(f"### {year}")
        for p in paths:
            recommended = "⭐ **推荐**" if p.get("recommended_for_user") else ""
            lines.append(f"\n#### {p.get('path_name', '')} {recommended}")
            lines.append(f"- **适合人群**：{p.get('trigger_profile', '')}")
            lines.append(f"- **发展轨迹**：{p.get('trajectory', '')}")
            lines.append(f"- **命运契合度**：{p.get('fate_alignment', '')}")
            lines.append(f"- **优化建议**：{p.get('optimization', '')}")
        lines.append("")

    return "\n".join(lines)


def save_report(report_md: str, output_dir: str = "output", name: str = "report") -> str:
    """保存报告到文件"""
    from datetime import datetime
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{name}_{timestamp}.md"
    filepath = out_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_md)

    return str(filepath)
