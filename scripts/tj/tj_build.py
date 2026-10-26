#!/usr/bin/env python3
"""编译天津卷物理专题层 → data/tianjin/physics_tj.json，并做校验。

用法：python3 scripts/tj/tj_build.py
输入：scripts/tj/tj_content.py（模型、易错概念、真题映射）、data/tianjin/tj_exam_raw.json（真题考点调研）、data/topics.json（上游章节点）
输出：data/tianjin/physics_tj.json；校验失败时非 0 退出。
"""
import hashlib, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)
import tj_content as T  # noqa: E402
from verify_questions import safe_eval, compare_numeric, compare_choice  # noqa: E402

errs = []
topics = json.load(open(os.path.join(ROOT, "data", "topics.json"), encoding="utf-8"))
hs = {t["id"]: t for t in topics if t["id"].startswith("cnp_h")}
raw = json.load(open(os.path.join(ROOT, "data", "tianjin", "tj_exam_raw.json"), encoding="utf-8"))

mid = {m["key"]: "cnp_tjm%s" % m["key"][1:] for m in T.MODELS}
eid = {e["key"]: "cnp_tje%s" % e["key"][1:] for e in T.MISCONCEPTIONS}


def slot(key, i, n=4):
    return int(hashlib.md5(("%s#%d" % (key, i)).encode()).hexdigest(), 16) % n


def build_choice(qid, topic, q, mis_text=None):
    opts = list(q["wrongs"])
    pos = slot(qid, 0, len(opts) + 1)
    opts.insert(pos, q["right"])
    keys = "ABCD"
    choices = [{"key": keys[i], "text": t} for i, t in enumerate(opts)]
    out = {"id": qid, "topicId": topic, "type": "choice", "difficulty": q.get("diff", "basic"), "prompt": q["prompt"],
           "choices": choices, "answer": keys[pos], "explanation": q["expl"],
           "verify": q.get("verify") or json.dumps(q["right"], ensure_ascii=False)}
    if mis_text:
        out["misconception_choice"] = keys[opts.index(mis_text)]
    return out


def check_q(q):
    try:
        res = safe_eval(q["verify"])
        ok, why = (compare_numeric if q["type"] == "numeric" else compare_choice)(q, res)
    except Exception as ex:  # noqa: BLE001
        ok, why = False, "verify 出错：%s" % ex
    if not ok:
        errs.append("%s 核验失败：%s" % (q["id"], why))


nodes, edges, questions = [], [], []
# ---------------- 模型层
for m in T.MODELS:
    nid = mid[m["key"]]
    for h, s in m["links"]:
        if h not in hs:
            errs.append("%s 链接的章节点 %s 不存在" % (nid, h))
        edges.append({"topicId": nid, "prerequisiteId": h, "strength": s, "kind": "applies", "reason": "模型用到「%s」" % hs.get(h, {}).get("name", h)})
    for p, s in m["pre"]:
        if p not in mid:
            errs.append("%s 先修模型 %s 不存在" % (nid, p))
            continue
        edges.append({"topicId": nid, "prerequisiteId": mid[p], "strength": s, "kind": "model_pre",
                      "reason": "先掌握模型「%s」" % next(x["name"] for x in T.MODELS if x["key"] == p)})
    if len(m["qs"]) != 2:
        errs.append("%s 题数不是 2" % nid)
    for i, q in enumerate(m["qs"], 1):
        qid = "%s_q%d" % (nid, i)
        if q["kind"] == "numeric":
            qq = {"id": qid, "topicId": nid, "type": "numeric", "difficulty": q["diff"], "prompt": q["prompt"],
                  "answer": q["answer"], "explanation": q["expl"], "verify": q["verify"]}
        else:
            qq = build_choice(qid, nid, q)
        check_q(qq)
        questions.append(qq)
    nodes.append({"id": nid, "layer": "model", "name": m["name"], "kind": m["kind"], "slot": m["slot"],
                  "description": m["desc"], "key_steps": m["steps"],
                  "misconceptions": [eid[k] for k in m["mis"]]})

# ---------------- 易错概念层
for e in T.MISCONCEPTIONS:
    nid = eid[e["key"]]
    for h, s in e["links"]:
        if h not in hs:
            errs.append("%s 链接的章节点 %s 不存在" % (nid, h))
        edges.append({"topicId": nid, "prerequisiteId": h, "strength": s, "kind": "misconception_of",
                      "reason": "「%s」中的常见误区" % hs.get(h, {}).get("name", h)})
    for mk in e["models"]:
        if mk not in mid:
            errs.append("%s 关联模型 %s 不存在" % (nid, mk))
    q = dict(e["q"]); q["diff"] = "basic"
    qq = build_choice(nid + "_q1", nid, q, mis_text=q["mis"])
    check_q(qq)
    questions.append(qq)
    nodes.append({"id": nid, "layer": "misconception", "name": e["name"], "wrong_idea": e["wrong_idea"],
                  "correct": e["correct"], "models": [mid[k] for k in e["models"] if k in mid]})

# 模型引用的误区必须存在且互相登记
for m in T.MODELS:
    for k in m["mis"]:
        if k not in eid:
            errs.append("%s 引用的误区 %s 不存在" % (m["key"], k))

# ---------------- 真题映射与考频
papers = []
raw_by = {(p["year"], str(q["no"])): q for p in raw["papers"] for q in p["questions"]}
h_years, h_score, m_years, m_score = defaultdict(set), defaultdict(float), defaultdict(set), defaultdict(float)
for (y, no), (hl, ml) in sorted(T.EXAM_MAP.items(), key=lambda kv: (kv[0][0], [int(c) if c.isdigit() else 0 for c in kv[0][1].replace("(", " ").replace(")", "").split()])):
    rq = raw_by.get((y, no))
    if rq is None:
        errs.append("真题 %s 第 %s 题在调研数据里不存在" % (y, no))
        continue
    sc = float(rq.get("score") or 0)
    for h in hl:
        if h not in hs:
            errs.append("真题 %s-%s 映射到不存在的 %s" % (y, no, h))
        if y <= 2025:
            h_years[h].add(y); h_score[h] += sc / len(hl)
    for k in ml:
        if k not in mid:
            errs.append("真题 %s-%s 映射到不存在的模型 %s" % (y, no, k))
            continue
        if y <= 2025:
            m_years[mid[k]].add(y); m_score[mid[k]] += sc / len(ml)
    papers.append({"year": y, "no": no, "type": rq.get("type"), "score": rq.get("score"), "topic": rq.get("topic"),
                   "model": rq.get("model") or "", "uncertain": bool(rq.get("uncertain") or rq.get("uncertain_score")),
                   "source_url": rq.get("source_url", ""), "topics": hl, "models": [mid[k] for k in ml if k in mid]})

YEARS = 6  # 2020–2025 有逐题考点


def weight(years, score):
    n = len(years)
    tier = "必考" if n >= 5 else "高频" if n >= 3 else "常考" if n >= 1 else "未考"
    return {"years": sorted(years), "n_years": n, "avg_score": round(score / YEARS, 1), "tier": tier}


weights = {h: weight(h_years[h], h_score[h]) for h in hs}
for nid in mid.values():
    weights[nid] = weight(m_years[nid], m_score[nid])

# 无环检查（模型层内部）
graph = defaultdict(list)
for e in edges:
    if e["kind"] == "model_pre":
        graph[e["topicId"]].append(e["prerequisiteId"])
state = {}
def dfs(u):
    state[u] = 1
    for v in graph[u]:
        if state.get(v) == 1:
            errs.append("模型先修有环：%s → %s" % (u, v))
        elif v not in state:
            dfs(v)
    state[u] = 2
for u in list(graph):
    if u not in state:
        dfs(u)

out = {
    "meta": {
        "title": "天津卷高中物理专题层（试做版）",
        "textbook": "人教版 2019 必修第一至三册、选择性必修第一至三册（天津使用人教版，章节点沿用上游 cnp_h001–cnp_h177）",
        "exam": raw.get("structure"),
        "exam_notes": raw.get("notes", []),
        "weights_basis": "2020–2025 天津卷逐题考点（部分年份题目为回忆版，见 papers[].uncertain）；n_years 为出现年数，avg_score 为年均分值（一题多点时平分）",
        "status": "AI 生成初稿，未经教师审核",
        "built": "2026-10-26",
    },
    "nodes": nodes, "edges": edges, "questions": questions, "papers": papers, "weights": weights,
}
dst = os.path.join(ROOT, "data", "tianjin", "physics_tj.json")
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

nm = sum(1 for n in nodes if n["layer"] == "model"); ne = len(nodes) - nm
covered = sum(1 for h in hs if weights[h]["n_years"])
print("模型/方法节点 %d，易错概念节点 %d，边 %d，题目 %d，真题条目 %d" % (nm, ne, len(edges), len(questions), len(papers)))
print("被天津卷考到的章节点 %d / %d；必考 %d，高频 %d" % (covered, len(hs),
      sum(1 for h in hs if weights[h]["tier"] == "必考"), sum(1 for h in hs if weights[h]["tier"] == "高频")))
unused = [mid[m["key"]] + m["name"] for m in T.MODELS if not m_years[mid[m["key"]]]]
print("真题中尚未出现的模型 %d 个：%s" % (len(unused), "、".join(unused)))
if errs:
    print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
print("TJ BUILD PASSED")
