# 写「模型与方法」层草稿的说明（tj_m01 / tj_m02 / tj_m03）

仓库根：/workspace/projects/77450b66-8cc4-436d-a19e-5d4c2759834b/cn-math-taxonomy

先读：scripts/tj_lib.py（M、W 的用法）、scripts/tj_plan.py（模型 key、名称、册次）、scripts/phy_hs_plan.py（章节层 key）、
scripts/phy_hs_std.py（课标条目 CLAUSES / EXPERIMENTS 的 id 尾部，如 B1.2.3、S2.1.4）、scripts/phy_lib.py 里 C、N 的签名，
以及一份现成章节草稿 scripts/phy_hs_a04.py 的写法和语气（模仿它）。

## 每个模型写什么
```python
from tj_lib import M, C, N, W

M("m_board_block", "运动和相互作用", "modeling",
  "描述 40–200 字：模型是什么、典型情境、关键突破口（如判断是否相对滑动、临界加速度）。",
  ["掌握标准1", "掌握标准2", "掌握标准3"],
  [("B1.2.3", "inferred")],
  pre=[("newton2", "hard"), ("kinetic_friction", "hard"), ("connected", "hard"), ("M:m_incline", "soft")],
  misconceptions=[("mc_board_same_a", "以为滑块和木板总是一起运动、加速度相同", "先假设相对静止求共同加速度，再与最大静摩擦提供的加速度比较"),
                  ("mc_board_friction_dir", "...", "...")],
  qs=[C("basic", "题干…哪一个？", "正确选项", [W("错误选项1", "mc_board_same_a"), "错误选项2", "错误选项3"], "解析：先给正确思路，再点出错误选项对应的错误。"),
      N("basic", "题干……是多少 m/s²？（只填数值）", "2", "解析……", "（6-2)/2 写成可求值的 Python 表达式"),
      ...])
```

## 硬性规则
- 每个模型恰好 4 题：第 1 题 basic（它就是诊断题），至少 2 道 basic，另有 standard / advanced（建议 2 basic + 1 standard + 1 advanced）。
- 至少 2 道题是选择题，选择题 3 个错误选项，每题至少 1 个错误选项用 W(...) 标到本模型登记的易错概念。
- 数值题：answer 只写数（不带单位），单位写在题干「（只填数值）」前面；verify 是能算出 answer 的纯算术 Python 表达式（只用数字、+-*/**、括号、math 函数如 sqrt、sin、pi 视 verify_questions.py 支持情况，先读它）。g 取 10 m/s²。答案取整洁的数。
- 题目必须条件完整、答案唯一；解析里逐步算，最后点出一个常见错误会得到什么。
- 先修 pre：只用 phy_hs_plan.py 里的 key 或更早模型 "M:key"；**先修所在的册不能晚于本模型所在册**（必修一 < 必修二 < 必修三 < 选必一 < 选必二 < 选必三）。至少 2 条 hard。
- 易错概念 2–3 条，key 用 mc_ 开头、全局唯一（加上模型名前缀避免和别的文件冲突）。
- 不出现「AI 初稿」「免费」字样。题干用中文，问法用「是多少」「哪一个」。
- 风格贴近天津卷：情境化（现代科技、生活、体育、航天）、中等难度为主。
- 不要配图（不写 figure）；需要图的情境用文字说清楚几何关系。

## 自检
写完运行：`cd scripts && python3 tj_build.py --check m01 --show`（把 m01 换成你的文件编号），直到没有 ERROR、核验全过。
再自己逐题重算一遍数值题，检查选择题只有一个正确选项。只改你自己的文件 scripts/tj_mXX.py，不要改其他文件。
