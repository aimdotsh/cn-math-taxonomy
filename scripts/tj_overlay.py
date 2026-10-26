#!/usr/bin/env python3
"""生成天津卷叠加层 data/regions/tianjin-physics.json。

逐题考点来自 research/tj_exam.json（2020–2025 天津卷物理，部分题为考生回忆版，见各题 uncertain），
这里人工把每道题映射到章节层 key（phy_hs_plan.py）和模型层 key（"M:" 前缀，tj_plan.py）。
每个知识点得到：出现年数、出现次数、累计分值、题目列表、频度等级（高频 ≥4 年 / 中频 2–3 年 / 低频 1 年 / 近年未考）。
用法：python3 scripts/tj_overlay.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phy_hs_lib as HL  # noqa: E402
import phy_hs_plan as HP  # noqa: E402
import tj_lib as TL  # noqa: E402
import tj_plan as TP  # noqa: E402

# (年, 题号, 题型, 分值, 回忆版?, [key, ...])
MAP = [
    (2020, "1", "单选", 5, False, ["rutherford"]),
    (2020, "2", "单选", 5, False, ["satellite_orbit"]),
    (2020, "3", "单选", 5, False, ["em_spectrum", "polarization"]),
    (2020, "4", "单选", 5, False, ["wave_graph", "wave_formation"]),
    (2020, "5", "单选", 5, False, ["boyle", "first_law", "M:m_cylinder_piston"]),
    (2020, "6", "多选", 5, False, ["self_inductance", "transformer"]),
    (2020, "7", "多选", 5, False, ["charge_circular", "M:m_bounded_field"]),
    (2020, "8", "多选", 5, False, ["power", "work_energy_theorem", "M:m_vehicle_start"]),
    (2020, "9(1)", "实验", 6, False, ["exp_projectile"]),
    (2020, "9(2)", "实验", 6, False, ["exp_emf", "M:m_circuit_choice"]),
    (2020, "10", "计算", 14, False, ["faraday", "ampere_force", "electric_work"]),
    (2020, "11", "计算", 16, False, ["circular_apply", "momentum_theorem", "collision", "M:m_vertical_circle", "M:m_momentum_energy_combo"]),
    (2020, "12", "计算", 18, False, ["particle_accel", "mass_spectrometer", "M:m_combined_field"]),
    (2021, "1", "单选", 5, False, ["newton1"]),
    (2021, "2", "单选", 5, False, ["refraction"]),
    (2021, "3", "单选", 5, False, ["ac_describe"]),
    (2021, "4", "单选", 5, False, ["wave_formation", "wave_graph"]),
    (2021, "5", "单选", 5, False, ["kepler", "satellite_orbit", "M:m_orbit_change"]),
    (2021, "6", "多选", 5, False, ["first_law", "boyle", "M:m_cylinder_piston"]),
    (2021, "7", "多选", 5, False, ["recoil", "momentum_theorem"]),
    (2021, "8", "多选", 5, False, ["equipotential", "potential"]),
    (2021, "9(1)", "实验", 6, False, ["exp_vt"]),
    (2021, "9(2)", "实验", 6, False, ["exp_emf"]),
    (2021, "10", "计算", 14, False, ["recoil", "projectile", "momentum_conservation", "M:m_momentum_energy_combo"]),
    (2021, "11", "计算", 16, False, ["induction_dynamics", "emf_cutting", "M:m_single_rod", "M:m_induction_momentum"]),
    (2021, "12", "计算", 18, False, ["lorentz_force", "M:m_superposed_field"]),
    (2022, "1", "单选", 5, False, ["fission_fusion", "binding_energy", "M:m_nuclear_energy"]),
    (2022, "2", "单选", 5, True, ["potential", "e_field"]),
    (2022, "3", "单选", 5, True, ["satellite_orbit"]),
    (2022, "5", "单选", 5, False, ["wave_interference", "wave_formation"]),
    (2022, "6", "多选", 5, False, ["first_law", "charles", "M:m_cylinder_piston"]),
    (2022, "7", "多选", 5, False, ["em_spectrum", "bohr", "einstein_photo", "light_interference", "diffraction", "M:m_level_photo"]),
    (2022, "8", "多选", 5, False, ["transformer", "power_transmission", "M:m_transformer_dynamic"]),
    (2022, "9(1)", "实验", 6, False, ["exp_momentum", "exp_length"]),
    (2022, "9(2)", "实验", 6, False, ["exp_emf", "M:m_circuit_choice"]),
    (2022, "10", "计算", 14, False, ["kinetic_friction", "collision", "M:m_momentum_energy_combo"]),
    (2022, "11", "计算", 16, False, ["particle_accel", "charge_circular", "M:m_combined_field", "M:m_bounded_field"]),
    (2022, "12", "计算", 18, False, ["ampere_force", "resistance", "equilibrium"]),
    (2023, "1", "单选", 5, False, ["satellite_orbit"]),
    (2023, "2", "单选", 5, False, ["charles", "first_law", "M:m_cylinder_piston"]),
    (2023, "3", "单选", 5, False, ["fission_fusion", "binding_energy", "M:m_nuclear_energy"]),
    (2023, "4", "单选", 5, False, ["polarization"]),
    (2023, "5", "单选", 5, False, ["newton2", "impulse", "power"]),
    (2023, "6", "多选", 5, False, ["power_transmission", "transformer", "M:m_transformer_dynamic"]),
    (2023, "7", "多选", 5, False, ["wave_params", "wave_graph"]),
    (2023, "8", "多选", 5, False, ["equipotential", "potential_diff"]),
    (2023, "9(1)", "实验", 6, False, ["exp_energy", "connected"]),
    (2023, "9(2)", "实验", 6, False, ["exp_multimeter", "exp_resistivity", "M:m_circuit_choice"]),
    (2023, "10", "计算", 14, True, ["faraday", "ampere_force"]),
    (2023, "11", "计算", 16, True, ["free_fall", "collision", "M:m_chase", "M:m_momentum_energy_combo"]),
    (2023, "12", "计算", 18, True, ["charge_circular", "lorentz_force", "M:m_bounded_field"]),
    (2024, "1", "单选", 5, True, ["photoelectric", "total_reflection", "light_interference"]),
    (2024, "2", "单选", 5, True, ["first_law", "boyle", "M:m_cylinder_piston"]),
    (2024, "3", "单选", 5, False, ["wave_graph"]),
    (2024, "4", "单选", 5, False, ["induction_dynamics", "M:m_single_rod"]),
    (2024, "5", "单选", 5, True, ["newton2", "connected"]),
    (2024, "6", "多选", 5, False, ["decay", "half_life", "M:m_nuclear_energy"]),
    (2024, "7", "多选", 5, False, ["satellite_orbit", "M:m_equator_sync"]),
    (2024, "8", "多选", 5, False, ["potential", "electric_pe", "M:m_field_graph"]),
    (2024, "9(1)", "实验", 6, False, ["circuit_dynamic", "exp_emf"]),
    (2024, "9(2)", "实验", 6, False, ["exp_newton2"]),
    (2024, "10", "计算", 14, False, ["momentum_theorem", "energy_conservation", "collision", "M:m_vertical_circle", "M:m_momentum_energy_combo"]),
    (2024, "11", "计算", 16, False, ["lorentz_force", "particle_deflect", "charge_circular", "M:m_superposed_field", "M:m_bounded_field"]),
    (2024, "12", "计算", 18, False, ["ac_generate", "M:m_rotating_cut"]),
    (2025, "1", "单选", 5, False, ["satellite_orbit"]),
    (2025, "2", "单选", 5, False, ["decay", "binding_energy", "half_life", "M:m_nuclear_energy"]),
    (2025, "3", "单选", 5, False, ["momentum", "impulse", "momentum_theorem"]),
    (2025, "4", "单选", 5, False, ["ideal_gas", "first_law", "M:m_cylinder_piston"]),
    (2025, "5", "单选", 5, False, ["diffraction", "light_interference", "quantum", "wave_particle"]),
    (2025, "6", "多选", 5, False, ["transformer", "M:m_transformer_dynamic"]),
    (2025, "7", "多选", 5, False, ["wave_graph"]),
    (2025, "8", "多选", 5, False, ["electric_pe", "e_field", "potential"]),
    (2025, "9(1)", "实验", 6, False, ["exp_projectile"]),
    (2025, "9(2)", "实验", 6, False, ["exp_resistivity", "M:m_circuit_choice"]),
    (2025, "10", "计算", 14, False, ["momentum_conservation", "work_energy_theorem", "energy_conservation", "M:m_momentum_energy_combo"]),
    (2025, "11", "计算", 16, False, ["particle_deflect", "charge_circular", "M:m_combined_field"]),
    (2025, "12", "计算", 18, False, ["emf_cutting", "M:m_rotating_cut"]),
]
YEARS = sorted({m[0] for m in MAP})


def tid(key):
    if key.startswith("M:"):
        return TL.tid_of(key[2:])
    assert key in HP.PLAN_BY_KEY, key
    return HL.tid_of(key)


def level(n_years):
    return "高频" if n_years >= 4 else "中频" if n_years >= 2 else "低频" if n_years == 1 else "近年未考"


def main():
    stats = {}
    for year, no, typ, score, recalled, keys in MAP:
        for k in keys:
            t = tid(k)
            s = stats.setdefault(t, {"years": set(), "hits": [], "score": 0.0})
            s["years"].add(year)
            s["hits"].append({"year": year, "no": no, "type": typ, "score": score, "recalled": recalled})
            # 一道题的分值平均摊给它映射到的章节层知识点（模型层不参与分摊，单独计）
            ch = [x for x in keys if not x.startswith("M:")]
            if not k.startswith("M:"):
                s["score"] += score / len(ch)
    topics = {}
    all_ids = [HL.tid_of(r["key"]) for r in HP.PLAN] + [TL.tid_of(r["key"]) for r in TP.PLAN]
    for t in all_ids:
        s = stats.get(t)
        n = len(s["years"]) if s else 0
        entry = {"level": level(n), "years": n}
        if s:
            entry.update(hits=len(s["hits"]), avgScorePerYear=round(s["score"] / len(YEARS), 2) if not t.startswith("cnp_m") else None,
                         papers=s["hits"])
            if entry["avgScorePerYear"] is None:
                del entry["avgScorePerYear"]
        topics[t] = entry
    out = {
        "region": "天津",
        "subject": "physics",
        "exam": "天津市普通高中学业水平等级性考试·物理（天津卷，自主命题）",
        "textbook": "人教版 2019（必修第一至三册、选择性必修第一至三册），天津高中物理使用人教版",
        "structure": {
            "total": 100, "minutes": 60,
            "sections": [
                {"name": "单项选择题", "numbers": "1–5", "count": 5, "score_each": 5},
                {"name": "多项选择题", "numbers": "6–8", "count": 3, "score_each": 5},
                {"name": "实验题", "numbers": "9(1)(2)", "count": 2, "score_each": 6, "note": "固定一力一电"},
                {"name": "计算题", "numbers": "10–12", "count": 3, "scores": [14, 16, 18]},
            ],
            "note": "2025 年逐题分值已确认；2020–2024 实验、计算题分值按惯例推定。",
        },
        "years": YEARS,
        "features": [
            "选择题模块基本固定：卫星、机械波、气体＋热力学第一定律、原子或光、变压器、静电场，每年各约 1 题。",
            "第 1 题常考物理学史或研究方法。",
            "实验题固定一力一电：电学在测电源电动势和内阻与伏安法测电阻之间轮换。",
            "计算第 10 题多为动量＋能量综合；第 11 题电磁场中的粒子或力学碰撞；第 12 题压轴多是现代科技装置＋电磁规律。",
            "情境贴近国家科技成就：北斗、天问一号、空间站、光刻机、复兴号等。",
        ],
        "sources_note": ("逐题考点综合网络整卷与考生回忆版整理（2022 年第 4 题缺失；2022 年第 2、3 题，2023 年全卷，2024 年第 1、2、5 题为回忆版，"
                         "papers 里 recalled = true）。2026 年只查到压轴题零散信息，未计入。题目到知识点的映射为人工判断，AI 初稿，待教师审核。"),
        "topics": topics,
    }
    path = os.path.join(ROOT, "data", "regions", "tianjin-physics.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    by = {}
    for t, e in topics.items():
        by.setdefault(e["level"], 0)
        by[e["level"]] += 1
    print("写入 %s：%d 个知识点；%s" % (path, len(topics), by))


if __name__ == "__main__":
    main()
