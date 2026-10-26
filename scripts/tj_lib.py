"""高中物理「模型与方法」层（cnp_m）草稿用的登记函数。名称、册次来自 tj_plan.py；草稿里只写内容。

M(key, domain, typ, desc, mastery, std, pre, misconceptions, qs, math=())
  key             tj_plan.py 里登记的模型 key
  domain          物质 / 运动和相互作用 / 能量 / 跨学科实践
  typ             conceptual / procedural / reasoning / application / modeling（模型多用 modeling 或 application）
  desc            40–200 字：模型是什么、典型情境、关键突破口
  mastery         2–3 条掌握标准
  std             [("B1.2.3", "inferred"), ...]  cps-hs-2017: 课标条目尾部，1–3 条（模型一般是 inferred）
  pre             [("newton2", "hard"), ("M:m_incline", "soft")]  章节层 key（phy_hs_plan.py）或更早的模型（"M:" 前缀）
  misconceptions  [("mc_key", "易错概念的一句话描述", "纠正要点一句话"), ...]  2–3 条，mc_key 全局唯一，用 mc_ 开头
  qs              恰好 4 道题（C 选择 / N 数值，与 phy_lib 相同）；至少 2 道 basic，第 1 道必须 basic；
                  选择题可在 wrongs 里用 W("错误选项文字", "mc_key") 标出它对应的易错概念
  math            [("cnm_h012", "理由")]  可选
"""
from __future__ import annotations

from phy_lib import C, N, PHY_DOMAINS  # noqa: F401
import phy_hs_plan as HP
import tj_plan as P

MS = {}      # key -> 草稿
MC_KEYS = {}  # mc_key -> model key


class W(str):
    """带易错概念标签的错误选项。用法：W("错误选项", "mc_key")。"""

    def __new__(cls, text, mc):
        obj = str.__new__(cls, text)
        obj.mc = mc
        return obj


def M(key, domain, typ, desc, mastery, std, pre, misconceptions, qs, math=()):
    assert key in P.PLAN_BY_KEY, "tj_plan.py 里没有这个 key：%s" % key
    assert key not in MS, "重复登记：%s" % key
    assert domain in PHY_DOMAINS, (key, domain)
    assert 2 <= len(mastery) <= 3, key
    assert 1 <= len(std) <= 3, key
    assert pre, "%s 没有先修" % key
    assert 2 <= len(misconceptions) <= 3, key
    for mk, text, fix in misconceptions:
        assert mk.startswith("mc_"), mk
        assert mk not in MC_KEYS, "易错概念 key 重复：%s" % mk
        MC_KEYS[mk] = key
    for pk, s in pre:
        assert s in ("hard", "soft"), (key, pk, s)
        if pk.startswith("M:"):
            assert pk[2:] in P.ORDER and P.ORDER[pk[2:]] < P.ORDER[key], "%s 的模型先修 %s 不存在或不在前面" % (key, pk)
        else:
            assert pk in HP.PLAN_BY_KEY, "%s 的章节先修 %s 不存在" % (key, pk)
    assert len(qs) == 4, "%s 必须恰好 4 道题" % key
    assert qs[0]["diff"] == "basic", "%s 第 1 道必须 basic" % key
    assert sum(q["diff"] == "basic" for q in qs) >= 2, "%s 至少 2 道 basic" % key
    MS[key] = dict(key=key, domain=domain, type=typ, description=desc, mastery=list(mastery), std=list(std),
                   pre=list(pre), mcs=list(misconceptions), qs=list(qs), math=list(math))
    return MS[key]


def tid_of(key):
    return "cnp_m%03d" % (P.ORDER[key] + 1)
