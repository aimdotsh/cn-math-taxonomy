/* 天津卷高中物理专题页：读 data/topics.json（上游章节点）+ data/tianjin/physics_tj.json（专题层） */
(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const TIER = { '必考': 't-must', '高频': 't-high', '常考': 't-some', '未考': 't-none' };
  const BOOKS = ['必修一', '必修二', '必修三', '选必一', '选必二', '选必三'];
  let TJ, CH = {}, NODE = {}, QS = {}, cy = null;

  Promise.all([
    fetch('../data/topics.json').then(r => r.json()),
    fetch('../data/tianjin/physics_tj.json').then(r => r.json())
  ]).then(([topics, tj]) => {
    TJ = tj;
    topics.filter(t => /^cnp_h\d+$/.test(t.id)).forEach(t => { CH[t.id] = t; });
    tj.nodes.forEach(n => { NODE[n.id] = n; });
    tj.questions.forEach(q => { (QS[q.topicId] = QS[q.topicId] || []).push(q); });
    renderStats(); renderHeat(); renderModelList(); renderPapers(); bindTabs();
    const h = location.hash.slice(1);
    if (NODE[h]) { openTab('models'); select(h); } else { select(firstModel()); }
  }).catch(e => { document.querySelector('.tj').insertAdjacentHTML('afterbegin', '<p class="pop">数据加载失败：' + esc(e) + '。请用 python3 -m http.server 在仓库根目录打开。</p>'); });

  const W = id => TJ.weights[id] || { n_years: 0, avg_score: 0, tier: '未考', years: [] };
  const models = () => TJ.nodes.filter(n => n.layer === 'model');
  const firstModel = () => models().slice().sort((a, b) => W(b.id).n_years - W(a.id).n_years)[0].id;
  const nameOf = id => (NODE[id] && NODE[id].name) || (CH[id] && CH[id].name) || id;

  function renderStats() {
    const m = models().length, e = TJ.nodes.length - m;
    const covered = Object.keys(CH).filter(id => W(id).n_years > 0).length;
    const yrs = new Set(TJ.papers.map(p => p.year));
    $('#stats').innerHTML = [
      [Object.keys(CH).length, '教材章节点（人教 2019）'], [covered, '被天津卷考到的章节点'], [m, '模型与方法'], [e, '易错概念'],
      [TJ.questions.length, '专题练习题（全部自动核验）'], [TJ.papers.length, '真题逐题映射（' + Math.min(...yrs) + '–' + Math.max(...yrs) + '）']
    ].map(([n, l]) => '<div class="stat"><b>' + n + '</b><span>' + l + '</span></div>').join('');
    const s = TJ.meta.exam || {};
    const d = s.default_2020_2025 || {};
    const txt = Object.entries(d).filter(([k]) => k !== '第II卷').map(([k, v]) => k + ' ' + v).join('；') + (s.full_score ? '。满分 ' + s.full_score + '，' + s.duration_min + ' 分钟。' : '');
    $('#exam').innerHTML = '<b>天津卷结构：</b>' + esc(txt || '单选 5×5 + 多选 3×5 + 实验 2 小题 + 计算 14/16/18，满分 100，60 分钟');
  }

  // ---------------- 热力图：册 → 章 → 节点
  function renderHeat() {
    const byBook = {};
    Object.values(CH).forEach(t => {
      const [book, chap, chapName] = t.chapter.split(' ');
      ((byBook[book] = byBook[book] || {})[chap + ' ' + chapName] = byBook[book][chap + ' ' + chapName] || []).push(t);
    });
    let html = '';
    BOOKS.forEach(b => {
      if (!byBook[b]) return;
      html += '<h3 class="book">' + b + '</h3>';
      Object.entries(byBook[b]).forEach(([chap, list]) => {
        const yrs = new Set(); let sc = 0;
        list.forEach(t => { W(t.id).years.forEach(y => yrs.add(y)); sc += W(t.id).avg_score; });
        html += '<div class="chapter"><h4>' + esc(chap) + '<em>章出现 ' + yrs.size + '/6 年 · 年均约 ' + sc.toFixed(1) + ' 分</em></h4><div class="cells">' +
          list.map(t => { const w = W(t.id); return '<button class="cell ' + TIER[w.tier] + '" data-id="' + t.id + '">' + esc(t.name) + (w.n_years ? '<small>' + w.n_years + '年</small>' : '') + '</button>'; }).join('') +
          '</div><div class="popwrap"></div></div>';
      });
    });
    $('#heat').innerHTML = html;
    $('#heat').addEventListener('click', ev => {
      const b = ev.target.closest('.cell'); if (!b) return;
      const id = b.dataset.id, w = W(id), wrap = b.closest('.chapter').querySelector('.popwrap');
      const ms = TJ.edges.filter(e => e.prerequisiteId === id && e.kind === 'applies').map(e => e.topicId);
      const es = TJ.edges.filter(e => e.prerequisiteId === id && e.kind === 'misconception_of').map(e => e.topicId);
      const ps = TJ.papers.filter(p => p.topics.includes(id));
      wrap.innerHTML = '<div class="pop"><b>' + esc(CH[id].name) + '</b> <span class="meta">' + esc(CH[id].chapter) + ' · ' + w.tier + '（' + (w.years.join('、') || '未出现') + '）</span>' +
        (ms.length ? '<div>相关模型：' + ms.map(m => '<a data-go="' + m + '">' + esc(nameOf(m)) + '</a>').join('、') + '</div>' : '') +
        (es.length ? '<div>易错：' + es.map(m => '<a data-go="' + m + '">' + esc(nameOf(m)) + '</a>').join('、') + '</div>' : '') +
        (ps.length ? '<div>真题：' + ps.map(p => p.year + ' 第' + p.no + '题（' + esc(p.topic.slice(0, 26)) + '…）').join('；') + '</div>' : '') +
        '<div><a href="../explore/?subject=physics#' + id + '" target="_blank">在全国通用图谱中查看先修 →</a></div></div>';
    });
    document.addEventListener('click', ev => { const a = ev.target.closest('[data-go]'); if (a) { ev.preventDefault(); openTab('models'); select(a.dataset.go); } });
  }

  // ---------------- 模型列表
  function group(n) {
    const k = +n.id.replace(/\D/g, '');
    if (n.layer === 'misconception') return '易错概念';
    if (n.kind === '实验') return '实验';
    if (n.kind === '方法' && k === 44) return '方法';
    if (k <= 15 || k === 45) return '力学';
    if (k <= 33) return '电磁学';
    return '光学与近代物理';
  }
  function renderModelList() {
    const groups = { '力学': [], '电磁学': [], '光学与近代物理': [], '实验': [], '方法': [], '易错概念': [] };
    TJ.nodes.forEach(n => groups[group(n)].push(n));
    let html = '';
    Object.entries(groups).forEach(([g, list]) => {
      if (g !== '易错概念') list.sort((a, b) => W(b.id).n_years - W(a.id).n_years || b.id < a.id);
      html += '<h5>' + g + '（' + list.length + '）</h5>' + list.map(n => {
        const w = W(n.id);
        const badge = n.layer === 'model' ? '<span class="n ' + TIER[w.tier] + '">' + w.n_years + '/6</span>' : '';
        return '<button class="mitem" data-id="' + n.id + '"><span>' + esc(n.name) + '</span>' + badge + '</button>';
      }).join('');
    });
    $('#mlist').innerHTML = html;
    $('#mlist').addEventListener('click', ev => { const b = ev.target.closest('.mitem'); if (b) select(b.dataset.id); });
    $('#fit').addEventListener('click', () => cy && cy.fit(undefined, 30));
  }

  // ---------------- 选中：局部图 + 详情
  function select(id) {
    document.querySelectorAll('.mitem').forEach(b => b.classList.toggle('on', b.dataset.id === id));
    history.replaceState(null, '', '#' + id);
    drawGraph(id); renderDetail(id);
  }

  function drawGraph(id) {
    const keep = new Set([id]);
    TJ.edges.forEach(e => {
      if (e.topicId === id) keep.add(e.prerequisiteId);
      if (e.prerequisiteId === id) keep.add(e.topicId);
    });
    // 模型的误区也带上
    const n = NODE[id];
    if (n && n.misconceptions) n.misconceptions.forEach(m => keep.add(m));
    if (n && n.models) n.models.forEach(m => keep.add(m));
    const els = [];
    keep.forEach(k => {
      const kind = /^cnp_tjm/.test(k) ? 'model' : /^cnp_tje/.test(k) ? 'mis' : 'ch';
      els.push({ data: { id: k, label: nameOf(k), kind, focus: k === id ? 1 : 0 } });
    });
    TJ.edges.forEach((e, i) => { if (keep.has(e.topicId) && keep.has(e.prerequisiteId)) els.push({ data: { id: 'e' + i, source: e.topicId, target: e.prerequisiteId, s: e.strength } }); });
    if (n && n.misconceptions) n.misconceptions.forEach((m, i) => els.push({ data: { id: 'm' + i, source: m, target: id, s: 'soft' } }));
    if (cy) cy.destroy();
    cy = cytoscape({
      container: $('#cy'), elements: els, wheelSensitivity: 0.2, maxZoom: 1.4,
      layout: { name: 'dagre', rankDir: 'BT', nodeSep: 18, rankSep: 60 },
      style: [
        { selector: 'node', style: { label: 'data(label)', 'text-wrap': 'wrap', 'text-max-width': 120, 'font-size': 12, 'text-valign': 'center', shape: 'round-rectangle', width: 'label', height: 'label', padding: 8, 'border-width': 1.5 } },
        { selector: 'node[kind="model"]', style: { 'background-color': '#e0e7ff', 'border-color': '#6366f1', color: '#312e81' } },
        { selector: 'node[kind="ch"]', style: { 'background-color': '#fae8ff', 'border-color': '#c026d3', color: '#701a75' } },
        { selector: 'node[kind="mis"]', style: { 'background-color': '#fee2e2', 'border-color': '#ef4444', color: '#7f1d1d' } },
        { selector: 'node[focus=1]', style: { 'border-width': 4, 'font-weight': 700 } },
        { selector: 'edge', style: { width: 1.6, 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'line-color': '#94a3b8', 'target-arrow-color': '#94a3b8' } },
        { selector: 'edge[s="soft"]', style: { 'line-style': 'dashed' } }
      ]
    });
    cy.on('tap', 'node', ev => { const k = ev.target.id(); if (NODE[k]) select(k); else window.open('../explore/?subject=physics#' + k, '_blank'); });
    $('#gtitle').textContent = nameOf(id);
  }

  function renderDetail(id) {
    const n = NODE[id], w = W(id);
    let h = '<h3>' + esc(n.name) + '</h3>';
    if (n.layer === 'model') {
      h += '<div class="meta">' + esc(n.kind) + ' · 天津卷位置：' + esc(n.slot) + ' · ' + w.tier + '（' + (w.years.join('、') || '2020–2025 未直接出现') + '）</div>';
      h += '<p>' + esc(n.description) + '</p><h4>解题要点</h4><ul>' + n.key_steps.map(s => '<li>' + esc(s) + '</li>').join('') + '</ul>';
      const ch = TJ.edges.filter(e => e.topicId === id && e.kind === 'applies');
      h += '<h4>用到的教材知识点</h4>' + ch.map(e => '<a class="tag" href="../explore/?subject=physics#' + e.prerequisiteId + '" target="_blank">' + esc(nameOf(e.prerequisiteId)) + (e.strength === 'hard' ? '' : '（软）') + '</a>').join('');
      const pre = TJ.edges.filter(e => e.topicId === id && e.kind === 'model_pre');
      if (pre.length) h += '<h4>先掌握的模型</h4>' + pre.map(e => '<span class="tag" data-go="' + e.prerequisiteId + '">' + esc(nameOf(e.prerequisiteId)) + '</span>').join('');
      if (n.misconceptions.length) h += '<h4>相关易错</h4>' + n.misconceptions.map(m => '<span class="tag" data-go="' + m + '">' + esc(nameOf(m)) + '</span>').join('');
      const ps = TJ.papers.filter(p => p.models.includes(id));
      if (ps.length) h += '<h4>天津卷真题</h4><ul>' + ps.map(p => '<li>' + p.year + ' 第' + esc(p.no) + '题（' + esc(p.type) + (p.score ? ' ' + p.score + '分' : '') + '）' + (p.uncertain ? '※' : '') + '：' + esc(p.topic) + '</li>').join('') + '</ul>';
    } else {
      h += '<div class="meta">易错概念</div><p><b>错误想法：</b>' + esc(n.wrong_idea) + '</p><p><b>正确认识：</b>' + esc(n.correct) + '</p>';
      const ch = TJ.edges.filter(e => e.topicId === id);
      h += '<h4>出现在</h4>' + ch.map(e => '<a class="tag" href="../explore/?subject=physics#' + e.prerequisiteId + '" target="_blank">' + esc(nameOf(e.prerequisiteId)) + '</a>').join('') +
        (n.models || []).map(m => '<span class="tag" data-go="' + m + '">' + esc(nameOf(m)) + '</span>').join('');
    }
    h += '<h4>练一练</h4>' + (QS[id] || []).map(renderQ).join('');
    $('#detail').innerHTML = h;
    $('#detail').querySelectorAll('.q').forEach(bindQ);
  }

  function renderQ(q) {
    let h = '<div class="q" data-qid="' + q.id + '"><div>' + esc(q.prompt) + '</div>';
    if (q.type === 'choice') h += '<div class="opts">' + q.choices.map(c => '<button class="opt" data-k="' + c.key + '">' + c.key + '. ' + esc(c.text) + '</button>').join('') + '</div>';
    else h += '<div class="num"><input type="text" inputmode="decimal" placeholder="填数值"><button type="button">提交</button></div>';
    return h + '<div class="fb"></div></div>';
  }
  const QBY = id => TJ.questions.find(q => q.id === id);
  function bindQ(el) {
    const q = QBY(el.dataset.qid), fb = el.querySelector('.fb');
    const show = (ok, extra) => { fb.className = 'fb ' + (ok ? 'ok' : 'bad'); fb.innerHTML = (ok ? '✓ 正确。' : '✗ 不对。') + esc(q.explanation) + (extra || ''); };
    if (q.type === 'choice') {
      el.querySelectorAll('.opt').forEach(b => b.addEventListener('click', () => {
        const ok = b.dataset.k === q.answer;
        el.querySelectorAll('.opt').forEach(x => { x.classList.remove('ok', 'bad'); if (x.dataset.k === q.answer) x.classList.add('ok'); });
        if (!ok) b.classList.add('bad');
        let extra = '';
        if (!ok && q.misconception_choice === b.dataset.k) {
          const m = NODE[q.topicId];
          extra = '<span class="mis">这正是典型误区「' + esc(m.name) + '」：' + esc(m.correct) + '</span>';
        }
        show(ok, extra);
      }));
    } else {
      const inp = el.querySelector('input');
      const go = () => { const v = parseFloat(inp.value.replace(/[^\d.\-eE]/g, '')); const a = parseFloat(q.answer); show(Math.abs(v - a) <= 1e-6 * Math.max(1, Math.abs(a)) || Math.abs(v - a) < 0.005, ok => ''); if (!(Math.abs(v - a) < 0.005)) fb.innerHTML += '（参考答案 ' + esc(q.answer) + '）'; };
      el.querySelector('button').addEventListener('click', go);
      inp.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
    }
  }

  // ---------------- 真题表
  function renderPapers() {
    const by = {};
    TJ.papers.forEach(p => (by[p.year] = by[p.year] || []).push(p));
    $('#papers').innerHTML = Object.keys(by).sort().reverse().map(y => '<table class="pp"><caption>' + y + ' 年天津卷物理</caption><tr><th>题号</th><th>题型</th><th>分值</th><th>考点</th><th>模型</th><th>教材知识点</th></tr>' +
      by[y].map(p => '<tr><td>' + esc(p.no) + (p.uncertain ? '※' : '') + '</td><td>' + esc(p.type) + '</td><td>' + esc(p.score || '') + '</td><td>' + esc(p.topic) + '</td><td>' +
        p.models.map(m => '<span class="tag" data-go="' + m + '">' + esc(nameOf(m)) + '</span>').join('') + '</td><td>' +
        p.topics.map(t => '<a class="tag" href="../explore/?subject=physics#' + t + '" target="_blank">' + esc(nameOf(t)) + '</a>').join('') + '</td></tr>').join('') + '</table>').join('');
  }

  function openTab(t) {
    document.querySelectorAll('.tj-tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === t));
    document.querySelectorAll('.tj-tab').forEach(s => s.classList.toggle('on', s.id === 'tab-' + t));
    if (t === 'models' && cy) setTimeout(() => { cy.resize(); cy.fit(undefined, 30); }, 30);
  }
  function bindTabs() { document.querySelectorAll('.tj-tabs button').forEach(b => b.addEventListener('click', () => openTab(b.dataset.tab))); }
})();
