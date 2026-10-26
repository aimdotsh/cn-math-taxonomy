"""高中物理「模型与方法」层（L3）计划：天津版第一版。

这一层不是教材的节，而是高考（天津卷）里反复出现的典型物理模型和解题方法。每个模型挂在它最晚用到的那一册，
先修边只指向人教版 2019 章节层（cnp_h，phy_hs_plan.py 的 key）或更早的模型（"M:" 前缀）。
id 按这里的顺序编号 cnp_m001 起；草稿（tj_m01.py … tj_m03.py）只用 key 登记内容。

kind: model（物理模型）/ method（思想方法）
"""
from __future__ import annotations

from phy_hs_plan import BOOKS

# (key, 名称, 册, kind)
_RAW = [
    # ---------- 必修一 ----------
    ("m_graph_motion", "运动图像法（x-t、v-t、a-t 图像）", "必修一", "method"),
    ("m_chase", "追及与相遇模型", "必修一", "model"),
    ("m_dynamic_eq", "动态平衡（图解法、相似三角形法）", "必修一", "method"),
    ("m_incline", "斜面模型（含摩擦的受力与运动）", "必修一", "model"),
    ("m_spring_instant", "弹簧、轻绳的瞬时加速度（突变）问题", "必修一", "model"),
    ("m_conveyor", "传送带模型", "必修一", "model"),
    ("m_board_block", "板块模型（滑块—木板）", "必修一", "model"),
    # ---------- 必修二 ----------
    ("m_incline_projectile", "斜面与平抛的结合", "必修二", "model"),
    ("m_vertical_circle", "竖直面内圆周运动（绳模型与杆模型）", "必修二", "model"),
    ("m_turntable", "水平面圆周运动的临界问题（转盘、圆锥摆）", "必修二", "model"),
    ("m_double_star", "双星与多星模型", "必修二", "model"),
    ("m_orbit_change", "卫星变轨与对接", "必修二", "model"),
    ("m_equator_sync", "赤道上的物体、近地卫星与同步卫星的比较", "必修二", "model"),
    ("m_vehicle_start", "机车启动模型（恒定功率与恒定加速度）", "必修二", "model"),
    ("m_multi_process_energy", "多过程问题的能量分析（动能定理与机械能守恒的选用）", "必修二", "method"),
    # ---------- 必修三 ----------
    ("m_field_graph", "电场中的图像问题（φ-x、E-x、Ep-x）", "必修三", "method"),
    ("m_capacitor_dynamic", "电容器的动态分析（Q 不变与 U 不变）", "必修三", "model"),
    ("m_ac_field_particle", "带电粒子在交变电场中的运动", "必修三", "model"),
    ("m_circuit_choice", "测量电路的选择（内接外接、限流分压、器材选取）", "必修三", "method"),
    ("m_resistance_special", "电阻测量的特殊方法（半偏法、等效替代、电桥）", "必修三", "method"),
    # ---------- 选必一 ----------
    ("m_bullet_block", "子弹打木块与摩擦生热（动量与能量）", "选必一", "model"),
    ("m_spring_collision", "含弹簧的碰撞模型", "选必一", "model"),
    ("m_man_boat", "人船模型", "选必一", "model"),
    ("m_momentum_energy_combo", "动量与能量的多过程综合", "选必一", "method"),
    ("m_wave_multi", "机械波的多解问题", "选必一", "model"),
    ("m_glass_brick", "玻璃砖中的折射与全反射（光路几何）", "选必一", "model"),
    # ---------- 选必二 ----------
    ("m_bounded_field", "带电粒子在有界磁场中的运动（找圆心、半径与临界）", "选必二", "model"),
    ("m_combined_field", "带电粒子在组合场中的运动", "选必二", "model"),
    ("m_superposed_field", "叠加场的应用（速度选择器、磁流体发电机、霍尔效应、电磁流量计）", "选必二", "model"),
    ("m_single_rod", "单杆切割模型（动力学与能量）", "选必二", "model"),
    ("m_double_rod", "双杆模型", "选必二", "model"),
    ("m_frame_cross", "线框穿越磁场", "选必二", "model"),
    ("m_rotating_cut", "导体棒转动切割与线框转动发电", "选必二", "model"),
    ("m_induction_momentum", "电磁感应中的动量定理（求电荷量、位移、时间）", "选必二", "method"),
    ("m_transformer_dynamic", "理想变压器的动态分析与远距离输电", "选必二", "model"),
    # ---------- 选必三 ----------
    ("m_cylinder_piston", "气缸活塞模型（气体实验定律与热力学第一定律）", "选必三", "model"),
    ("m_liquid_column", "玻璃管液柱模型", "选必三", "model"),
    ("m_level_photo", "能级跃迁与光电效应综合", "选必三", "model"),
    ("m_nuclear_energy", "核反应方程与核能计算", "选必三", "model"),
]

PLAN = []
for i, (key, name, book, kind) in enumerate(_RAW):
    PLAN.append(dict(key=key, name=name, book=book, grade=BOOKS[book]["grade"], kind=kind,
                     chapter="%s %s %s" % (book, "高考模型" if kind == "model" else "思想方法", name.split("（")[0])))
PLAN_BY_KEY = {r["key"]: r for r in PLAN}
ORDER = {r["key"]: i for i, r in enumerate(PLAN)}
assert len(PLAN_BY_KEY) == len(PLAN)
