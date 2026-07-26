// AlgoForge 解題儀表板前端邏輯
const API = ''; // 與後端同源（FastAPI 直接 serve）

let problems = [];
let activePattern = null;
let activeId = null;

const $ = (sel) => document.querySelector(sel);

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
}

async function loadProblems() {
  try {
    const res = await fetch(`${API}/api/problems`);
    const data = await res.json();
    problems = data.problems || [];
    renderStats();
    renderChips();
    renderList();
  } catch (e) {
    toast('讀取題目失敗，後端有開嗎？');
  }
}

function renderStats() {
  const total = problems.length;
  const solved = problems.filter(p => p.status === 'solved').length;
  const patterns = new Set(problems.flatMap(p => p.patterns || []));
  $('#stats').innerHTML = `
    <div class="stat-card"><div class="num">${total}</div><div class="lbl">題數</div></div>
    <div class="stat-card"><div class="num">${solved}</div><div class="lbl">已解</div></div>
    <div class="stat-card"><div class="num">${patterns.size}</div><div class="lbl">模式</div></div>`;
}

function renderChips() {
  const patterns = [...new Set(problems.flatMap(p => p.patterns || []))].sort();
  $('#patternChips').innerHTML = patterns.map(p =>
    `<span class="chip ${p === activePattern ? 'active' : ''}" data-p="${p}">${p}</span>`
  ).join('');
  document.querySelectorAll('.chip').forEach(c => {
    c.onclick = () => {
      activePattern = (activePattern === c.dataset.p) ? null : c.dataset.p;
      renderChips();
      renderList();
    };
  });
}

function renderList() {
  const q = $('#search').value.trim().toLowerCase();
  let list = problems;
  if (activePattern) list = list.filter(p => (p.patterns || []).includes(activePattern));
  if (q) list = list.filter(p => `${p.id} ${p.title}`.toLowerCase().includes(q));

  $('#problemList').innerHTML = list.map(p => `
    <li class="problem-item ${p.id === activeId ? 'active' : ''}" data-id="${p.id}">
      <div class="pid">#${p.id}</div>
      <div class="ptitle">${p.title}</div>
      <div class="meta">
        <span class="badge d-${p.difficulty}">${p.difficulty}</span>
        <span class="badge s-${p.status}">${p.status}</span>
        ${(p.patterns || []).slice(0,2).map(t => `<span class="tag">${t}</span>`).join('')}
      </div>
    </li>`).join('') || '<p class="muted" style="padding:10px">沒有符合的題目。</p>';

  document.querySelectorAll('.problem-item').forEach(el => {
    el.onclick = () => openNote(el.dataset.id);
  });
}

// 取出 YAML frontmatter 區塊文字
function frontmatterBlock(md) {
  if (!md.startsWith('---')) return '';
  const end = md.indexOf('\n---', 3);
  return end === -1 ? '' : md.slice(3, end);
}

// 讀 frontmatter 的單一純量欄位
function fmField(fm, key) {
  const m = fm.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
  return m ? m[1].trim() : null;
}

// 去掉 YAML frontmatter（--- ... ---），不要渲染成內文
function stripFrontmatter(md) {
  if (!md.startsWith('---')) return md;
  const end = md.indexOf('\n---', 3);
  return end === -1 ? md : md.slice(end + 4).replace(/^\s+/, '');
}

// 從筆記抽出時間/空間複雜度「結論」（取該段最後一個 O()，即加總結果）
function extractComplexity(md) {
  const grab = (heading) => {
    const re = new RegExp(`##\\s*\\d*\\.?\\s*${heading}([\\s\\S]*?)(?=\\n##|$)`);
    const m = md.match(re);
    if (!m) return null;
    const all = [...m[1].matchAll(/O\(([^)]+)\)/g)];
    return all.length ? `O(${all[all.length - 1][1]})` : null;
  };
  return { time: grab('時間複雜度'), space: grab('空間複雜度') };
}

async function openNote(id) {
  activeId = id;
  renderList();
  const reader = $('#reader');
  reader.innerHTML = '<p class="muted">載入中…</p>';
  try {
    const res = await fetch(`${API}/api/problems/${id}/note`);
    if (!res.ok) throw new Error();
    const { markdown } = await res.json();
    const fm = frontmatterBlock(markdown);
    const body = stripFrontmatter(markdown);
    const fallback = extractComplexity(body);
    // 優先用 frontmatter 結構化欄位，沒有才退回 regex 猜測
    const cx = {
      time: fmField(fm, 'time_complexity') || fallback.time,
      space: fmField(fm, 'space_complexity') || fallback.space,
    };
    const cxBar = (cx.time || cx.space) ? `
      <div class="cx-bar">
        ${cx.time ? `<div class="cx-pill"><div class="k">時間複雜度</div><div class="v">${cx.time}</div></div>` : ''}
        ${cx.space ? `<div class="cx-pill"><div class="k">空間複雜度</div><div class="v">${cx.space}</div></div>` : ''}
      </div>` : '';
    reader.innerHTML = `<article class="note">${cxBar}${marked.parse(body)}</article>`;
    reader.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));
    reader.scrollTop = 0;
  } catch (e) {
    reader.innerHTML = '<p class="muted">讀取筆記失敗。</p>';
  }
}

// ===== S4：統計視圖 =====
function bars(title, obj, classPrefix) {
  const entries = Object.entries(obj);
  if (!entries.length) return '';
  const max = Math.max(...entries.map(([, n]) => n), 1);
  const rows = entries.map(([k, n]) => `
    <div class="bar-row">
      <div class="bl">${k}</div>
      <div class="bar-track"><div class="bar-fill ${classPrefix ? classPrefix + k : ''}" style="width:${(n / max) * 100}%"></div></div>
      <div class="bn">${n}</div>
    </div>`).join('');
  return `<h2>${title}</h2>${rows}`;
}

async function showStats() {
  activeId = null; renderList();
  const reader = $('#reader');
  reader.innerHTML = '<p class="muted">統計載入中…</p>';
  try {
    const s = await (await fetch(`${API}/api/stats`)).json();
    reader.innerHTML = `<div class="panel">
      <h1><img src="/assets/icons/chart-column.svg" width="22" height="22" alt="" style="vertical-align:-4px"> 刷題統計</h1>
      <p class="muted">已累積 <strong>${s.total}</strong> 題。</p>
      ${bars('依難度', s.by_difficulty, 'fill-')}
      ${bars('依狀態', s.by_status, 'fill-')}
      ${bars('依解題模式', s.by_pattern, '')}
    </div>`;
    reader.scrollTop = 0;
  } catch (e) { reader.innerHTML = '<p class="muted">統計讀取失敗。</p>'; }
}

// ===== S4：複習視圖 =====
function reviewItem(it, isDue) {
  return `<div class="review-card ${isDue ? 'due' : ''}" data-id="${it.id}">
    <span class="badge d-${it.difficulty}">${it.difficulty}</span>
    <div>
      <div style="font-weight:600">#${it.id} ${it.title}</div>
      <div style="font-size:12px;color:var(--muted)">${(it.patterns || []).join(' · ')}</div>
    </div>
    <span class="rdate">${isDue ? '<img src="/assets/icons/alarm-clock.svg" width="13" height="13" alt="" style="vertical-align:-2px"> ' : ''}${it.revisit}</span>
  </div>`;
}

async function showReview() {
  activeId = null; renderList();
  const reader = $('#reader');
  reader.innerHTML = '<p class="muted">複習佇列載入中…</p>';
  try {
    const r = await (await fetch(`${API}/api/review`)).json();
    const dueHtml = r.due.length ? r.due.map(it => reviewItem(it, true)).join('')
      : '<p class="section-empty"><img src="/assets/icons/circle-check-big.svg" width="14" height="14" alt="" style="vertical-align:-2px"> 目前沒有到期的複習題</p>';
    const upHtml = r.upcoming.length ? r.upcoming.map(it => reviewItem(it, false)).join('')
      : '<p class="section-empty">尚無排定的複習。</p>';
    reader.innerHTML = `<div class="panel">
      <h1><img src="/assets/icons/repeat.svg" width="22" height="22" alt="" style="vertical-align:-4px"> 複習佇列</h1>
      <p class="muted">今天：${r.today}（題目筆記 frontmatter 的 <code>revisit</code> 日期到了就出現在「到期」）</p>
      <h2>到期（該複習了）</h2>${dueHtml}
      <h2>即將複習</h2>${upHtml}
    </div>`;
    reader.querySelectorAll('.review-card').forEach(el => el.onclick = () => openNote(el.dataset.id));
    reader.scrollTop = 0;
  } catch (e) { reader.innerHTML = '<p class="muted">複習佇列讀取失敗。</p>'; }
}

$('#showStats').addEventListener('click', showStats);
$('#showReview').addEventListener('click', showReview);
$('#search').addEventListener('input', renderList);

$('#fetchDaily').addEventListener('click', async () => {
  toast('抓取今日題中…');
  try {
    const res = await fetch(`${API}/api/daily`);
    const data = await res.json();
    if (data.id) {
      toast(`已抓：${data.id}. ${data.title}`);
      await loadProblems();
      openNote(String(data.id));
    } else {
      toast('抓取失敗');
    }
  } catch (e) {
    toast('抓取失敗，後端有開嗎？');
  }
});

loadProblems();
