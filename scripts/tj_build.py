#!/usr/bin/env python3
"""把「模型与方法」层草稿（tj_m01 … tj_m03）编译进 data/，并生成天津卷叠加层。

可重复运行：只删掉 cnp_m 知识点、它们的边和题目再重写；数学、英语、初中物理、高中章节层（cnp_h）一概不动。
另外写：
  data/physics-misconceptions.json   易错概念（模型层登记的 mc_*）以及选择题错误选项 → 易错概念的对应
  data/regions/tianjin-physics.json  天津卷叠加层（由 tj_overlay.py 生成；这里只在它存在时检查引用）

用法：python3 scripts/tj_build.py            # 编译并写入
      python3 scripts/tj_build.py --check m01  # 只检查一份草稿，不写文件
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phy_hs_plan as HP  # noqa: E402
import phy_hs_lib as HL  # noqa: E402
import phy_hs_std as HS  # noqa: E402
import tj_lib as L  # noqa: E402
import tj_plan as P  # noqa: E402
from verify_questions import verify_all  # noqa: E402

DRAFTS = ("m01", "m02", "m03")
VALID_STD = {c[0] for c in HS.CLAUSES} | {e[0] for e in HS.EXPERIMENTS}
KEYS = "ABCD"


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def dump(name, data):
    path = os.path.join(ROOT, "data", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def compile_models(only=None):
    errs = []
    for d in DRAFTS:
        if only and d != only:
            continue
        try:
            importlib.import_module("tj_" + d)
        except ModuleNotFoundError as e:
            if only:
                raise
            errs.append("缺少草稿 tj_%s.py（%s）" % (d, e))
    topics, deps, qs, tags = [], [], [], {}
    mcs = []
    for r in P.PLAN:
        key = r["key"]
        t = L.MS.get(key)
        if t is None:
            if not only:
                errs.append("缺少模型 %s（%s）" % (key, r["name"]))
            continue
        tid = L.tid_of(key)
        for tail, _ in t["std"]:
            if tail not in VALID_STD:
                errs.append("%s 引用了不存在的课标 %s" % (key, tail))
        q1 = t["qs"][0]
        topic = {
            "id": tid, "name": r["name"], "domain": t["domain"], "grade": r["grade"], "semester": "上",
            "chapter": r["chapter"], "type": t["type"], "description": t["description"],
            "mastery_criteria": t["mastery"],
            "diagnostic_question": {"question": q1["prompt"],
                                    "answer": q1["right"] if q1["kind"] == "choice" else q1["answer"]},
            "external": False, "subject": "physics", "layer": r["kind"],
            "standards": [{"id": HL.std_id(c), "confidence": conf} for c, conf in t["std"]],
            "misconceptions": [{"id": mk, "text": text, "fix": fix} for mk, text, fix in t["mcs"]],
        }
        if t["math"]:
            topic["mathLinks"] = [{"id": m, "reason": why} for m, why in t["math"]]
        topics.append(topic)
        for mk, text, fix in t["mcs"]:
            mcs.append({"id": mk, "topicId": tid, "text": text, "fix": fix})
        for pk, strength in t["pre"]:
            if pk.startswith("M:"):
                pid, pname, pgrade = L.tid_of(pk[2:]), P.PLAN_BY_KEY[pk[2:]]["name"], P.PLAN_BY_KEY[pk[2:]]["grade"]
            else:
                pid, pname, pgrade = HL.tid_of(pk), HP.PLAN_BY_KEY[pk]["name"], HP.PLAN_BY_KEY[pk]["grade"]
            if pgrade > r["grade"]:
                errs.append("%s（%s）的先修 %s 在更晚的册（grade %d > %d）" % (key, r["book"], pk, pgrade, r["grade"]))
            reason = ("用「%s」要先会「%s」。" if strength == "hard" else "「%s」会用到「%s」。") % (r["name"], pname)
            deps.append({"topicId": tid, "prerequisiteId": pid, "strength": strength, "reason": reason})
        for i, q in enumerate(t["qs"], 1):
            qid = "%s_q%d" % (tid, i)
            if q["kind"] == "numeric":
                obj = {"id": qid, "topicId": tid, "difficulty": q["diff"], "type": "numeric", "prompt": q["prompt"],
                       "answer": q["answer"], "explanation": q["expl"], "verify": q["verify"]}
            else:
                texts = [str(w) for w in q["wrongs"]]
                if len(set(texts + [q["right"]])) != len(texts) + 1:
                    errs.append("%s 选项重复" % qid)
                pos = q["pos"] if q["pos"] is not None else HL._slot(key, i) % (len(texts) + 1)
                texts.insert(pos, q["right"])
                obj = {"id": qid, "topicId": tid, "difficulty": q["diff"], "type": "choice", "prompt": q["prompt"],
                       "choices": [{"key": KEYS[j], "text": x} for j, x in enumerate(texts)],
                       "answer": KEYS[pos], "explanation": q["expl"],
                       "verify": q["verify"] if q["verify"] else json.dumps(q["right"], ensure_ascii=False)}
                tag = {}
                for w in q["wrongs"]:
                    mc = getattr(w, "mc", None)
                    if mc:
                        if mc not in L.MC_KEYS:
                            errs.append("%s 的错误选项标了不存在的易错概念 %s" % (qid, mc))
                        tag[KEYS[texts.index(str(w))]] = mc
                if tag:
                    tags[qid] = tag
            if q.get("figure"):
                obj["figure"] = q["figure"]
            qs.append(obj)
    res = verify_all(qs)
    for m in res["mismatch"]:
        errs.append("核验不通过 %s：%s" % (m["id"], m.get("detail")))
    return dict(topics=topics, deps=deps, qs=qs, mcs=mcs, tags=tags, errs=errs, verified=len(res["auto_verified"]))


def main():
    if "--check" in sys.argv:
        only = sys.argv[sys.argv.index("--check") + 1]
        out = compile_models(only)
        for e in out["errs"]:
            print("ERROR", e)
        print("模型 %d，边 %d，题 %d（自动核验 %d），易错概念 %d" % (len(out["topics"]), len(out["deps"]), len(out["qs"]),
                                                       out["verified"], len(out["mcs"])))
        if "--show" in sys.argv:
            for q in out["qs"]:
                print(q["id"], q["prompt"], q.get("choices") or "", "→", q["answer"])
        sys.exit(1 if out["errs"] else 0)
    out = compile_models()
    if out["errs"]:
        for e in out["errs"]:
            print("ERROR", e)
        sys.exit(1)
    rx = re.compile(r"^cnp_m\d")
    topics = [t for t in load("topics.json") if not rx.match(t["id"])] + out["topics"]
    deps = [d for d in load("dependencies.json") if not rx.match(d["topicId"])] + out["deps"]
    qs = [q for q in load("questions.json") if not rx.match(q.get("topicId", ""))] + out["qs"]
    dump("topics.json", topics)
    dump("dependencies.json", deps)
    dump("questions.json", qs)
    dump("physics-misconceptions.json", {
        "note": "高中物理易错概念（模型与方法层登记）。choiceTags：题目 id → {错误选项字母: 易错概念 id}，诊断答错时可直接定位易错概念。AI 初稿，未经教师审核。",
        "misconceptions": out["mcs"], "choiceTags": out["tags"]})
    print("写入：模型 %d，边 %d，题 %d（自动核验 %d），易错概念 %d" % (len(out["topics"]), len(out["deps"]), len(out["qs"]),
                                                    out["verified"], len(out["mcs"])))


if __name__ == "__main__":
    main()
