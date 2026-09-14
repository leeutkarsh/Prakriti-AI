import math
import json
import random
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Prakriti-AI • Plant-to-Plant Risk",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Synthetic demo data
# -----------------------------
random.seed(42)
ROWS, COLS = 13, 22
plants = []
centers = [
    (7.1, 5.2, 0.99, "Rice Blast", "Disease"),
    (15.7, 9.4, 0.93, "Stem Borer", "Pest"),
    (18.2, 3.5, 0.84, "Bacterial Blight", "Disease"),
    (4.0, 10.6, 0.78, "Brown Spot", "Disease"),
]

for r in range(ROWS):
    for c in range(COLS):
        x = c * 34 + 30
        y = r * 31 + 28
        risk = 0.04 + random.random() * 0.07
        causes = []
        for cx, cy, strength, label, kind in centers:
            d = math.sqrt((c - cx) ** 2 + (r - cy) ** 2)
            influence = strength * math.exp(-(d * d) / (2 * 2.8 ** 2))
            risk += influence
            if influence > 0.18:
                causes.append(label)
        risk = min(0.99, risk)
        if risk >= 0.78:
            status = "Affected"
        elif risk >= 0.40:
            status = "At Risk"
        else:
            status = "Healthy"
        primary = causes[0] if causes else "Low exposure"
        if status == "Affected" and not causes:
            primary = random.choice(["Rice Blast", "Stem Borer", "Bacterial Blight"])
        plants.append({
            "id": f"P-{r+1:02d}-{c+1:02d}",
            "row": r + 1,
            "col": c + 1,
            "x": x,
            "y": y,
            "risk": round(risk, 3),
            "status": status,
            "cause": primary,
            "kind": "Pest" if primary == "Stem Borer" else "Disease",
            "confidence": round(min(0.98, 0.72 + risk * 0.24), 2),
        })

# A few explicit anchor affected plants make the story obvious in the demo.
for p in plants:
    d1 = math.hypot((p["col"] - 8.1), (p["row"] - 6.2))
    d2 = math.hypot((p["col"] - 16.7), (p["row"] - 10.4))
    d3 = math.hypot((p["col"] - 19.2), (p["row"] - 4.5))
    if d1 < 1.05:
        p.update(risk=0.97, status="Affected", cause="Rice Blast", kind="Disease", confidence=0.94)
    elif d2 < 1.05:
        p.update(risk=0.95, status="Affected", cause="Stem Borer", kind="Pest", confidence=0.92)
    elif d3 < 1.05:
        p.update(risk=0.91, status="Affected", cause="Bacterial Blight", kind="Disease", confidence=0.90)

stats = {
    "total": len(plants),
    "healthy": sum(p["status"] == "Healthy" for p in plants),
    "risk": sum(p["status"] == "At Risk" for p in plants),
    "affected": sum(p["status"] == "Affected" for p in plants),
}

payload = json.dumps({"plants": plants, "stats": stats})

# -----------------------------
# App chrome
# -----------------------------
st.markdown(
    """
    <style>
    .stApp { background: #071018; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .block-container { padding: 1.2rem 1.5rem 1.2rem; max-width: 1600px; }
    </style>
    """,
    unsafe_allow_html=True,
)

html = r'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
:root{
 --bg:#071018;--panel:#0d1923;--panel2:#101f2c;--line:rgba(170,205,220,.11);
 --text:#e9f1f6;--muted:#8fa6b6;--green:#47db7d;--yellow:#f2ba45;--red:#ff4e55;--blue:#56b7ff;
}
*{box-sizing:border-box} body{margin:0;background:transparent;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;color:var(--text)}
.shell{display:flex;min-height:840px;border:1px solid var(--line);border-radius:22px;overflow:hidden;background:linear-gradient(140deg,#09131d,#071018 55%,#0a141f);box-shadow:0 30px 80px rgba(0,0,0,.34)}
.sidebar{width:205px;border-right:1px solid var(--line);padding:22px 16px;display:flex;flex-direction:column;background:rgba(6,14,21,.7)}
.brand{display:flex;align-items:center;gap:10px;font-size:17px;font-weight:750;margin:2px 7px 28px}.logo{width:31px;height:31px;border-radius:10px;background:linear-gradient(145deg,#2fe677,#138e55);display:grid;place-items:center;box-shadow:0 10px 30px rgba(47,230,119,.25)}
.nav{display:grid;gap:7px}.nav div{padding:11px 12px;border-radius:11px;color:#8ea4b3;font-size:13px}.nav .active{color:#eaf6f2;background:linear-gradient(90deg,rgba(40,194,127,.18),rgba(40,194,127,.06));box-shadow:inset 2px 0 #39d47a}
.sideNote{margin-top:auto;padding:12px 8px;color:#607a89;font-size:11px;line-height:1.55}.sideNote b{color:#a9c1cc}
.main{flex:1;min-width:0;padding:22px 22px 18px}.top{display:flex;justify-content:space-between;gap:15px;align-items:flex-start;margin-bottom:16px}.title{font-size:28px;font-weight:780;letter-spacing:-.03em}.subtitle{font-size:12px;color:var(--muted);margin-top:6px}.chips{display:flex;gap:8px;align-items:center}.chip{background:#0c1b27;border:1px solid var(--line);padding:8px 11px;border-radius:10px;color:#aac0cd;font-size:11px}.chip strong{color:#e8f1f6}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:16px;align-items:start}.fieldCard{background:#09141e;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.22)}
.toolbar{height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#0d1a26,#09141e)}
.toolbar .left,.toolbar .right{display:flex;gap:8px;align-items:center}.toolbar button{border:1px solid var(--line);background:#0d1b27;color:#a8bfca;border-radius:9px;padding:7px 9px;font-size:11px;cursor:pointer}.toolbar button:hover{border-color:rgba(90,185,220,.33);color:#e7f3f7}.statusDot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px rgba(71,219,125,.7)}
#viewport{height:610px;position:relative;overflow:hidden;background:#0a1510;cursor:grab}.map{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);transform-origin:center center;transition:transform .08s linear}.field{position:relative;width:820px;height:545px;border-radius:18px;overflow:hidden;border:1px solid rgba(190,230,200,.16);background:linear-gradient(145deg,#183d2b,#10321f 45%,#0b2819);box-shadow:inset 0 0 0 1px rgba(255,255,255,.03),inset 0 0 90px rgba(0,0,0,.18)}
.field:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 28% 18%,rgba(75,177,90,.18),transparent 22%),radial-gradient(circle at 80% 70%,rgba(46,153,82,.14),transparent 24%),repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 27px),repeating-linear-gradient(90deg,rgba(255,255,255,.018) 0 1px,transparent 1px 35px);pointer-events:none}
.ridge{position:absolute;left:0;right:0;height:18px;background:linear-gradient(180deg,rgba(98,154,86,.16),transparent);border-top:1px solid rgba(134,191,111,.08);opacity:.55}.water{position:absolute;right:20px;bottom:15px;width:108px;height:76px;border-radius:48% 52% 45% 55%;background:radial-gradient(circle at 35% 35%,#2b7d95,#0f4557 65%,#092a39);opacity:.85;box-shadow:0 0 0 5px rgba(4,24,30,.2)}
.plant{position:absolute;width:31px;height:28px;transform:translate(-50%,-50%);cursor:pointer;transition:filter .12s,transform .12s}.plant:hover{filter:brightness(1.28) drop-shadow(0 0 7px rgba(255,255,255,.25));z-index:20}.plant.selected{transform:translate(-50%,-50%) scale(1.18);z-index:30}.plant svg{width:100%;height:100%;overflow:visible}.halo{position:absolute;inset:-12px;border-radius:50%;pointer-events:none;opacity:0;transition:opacity .12s}.plant.hover .halo{opacity:1;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 62%)}
.risk{filter:drop-shadow(0 3px 4px rgba(0,0,0,.25))}.heat{position:absolute;border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;mix-blend-mode:screen}.heat.red{background:radial-gradient(circle,rgba(255,62,68,.43),rgba(255,62,68,.16) 34%,transparent 70%)}.heat.yellow{background:radial-gradient(circle,rgba(242,186,69,.25),rgba(242,186,69,.08) 38%,transparent 72%)}
.scan{position:absolute;width:112px;height:112px;border-radius:50%;border:1px solid rgba(95,231,164,.45);box-shadow:0 0 0 1px rgba(95,231,164,.1),0 0 35px rgba(50,221,137,.11) inset;pointer-events:none;transform:translate(-50%,-50%);opacity:0;transition:opacity .12s}.scan.on{opacity:1}.scan:after{content:"";position:absolute;inset:17px;border-radius:50%;border:1px dashed rgba(89,219,166,.28)}
.legendBar{height:44px;border-top:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 14px;color:#7e96a5;font-size:10px}.legend{display:flex;gap:15px}.legend span{display:flex;align-items:center;gap:6px}.dot{width:8px;height:8px;border-radius:50%}.g{background:#35da78}.y{background:#f3bc47}.r{background:#ff4d54}
.panel{display:grid;gap:12px}.card{background:linear-gradient(180deg,#0d1923,#0a151f);border:1px solid var(--line);border-radius:16px;padding:14px}.card h3{margin:0;font-size:13px}.card .muted{color:var(--muted);font-size:10px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:12px}.metric{border-radius:12px;padding:10px 8px;background:#0d1d28;text-align:center}.metric b{display:block;font-size:18px}.metric small{color:#91a8b5;font-size:9px}.metric.green b{color:#43de7b}.metric.yellow b{color:#f0b53f}.metric.red b{color:#ff5960}
.bar{height:6px;background:#10222d;border-radius:8px;overflow:hidden;margin-top:8px}.bar i{display:block;height:100%;border-radius:8px}.riskrow{display:flex;justify-content:space-between;font-size:10px;color:#8ea5b2;margin-top:8px}.details{display:grid;gap:9px;margin-top:12px}.kv{display:flex;justify-content:space-between;gap:12px;font-size:10px}.kv span:first-child{color:#6f8796}.kv span:last-child{color:#dce7ed;text-align:right}.pill{padding:3px 7px;border-radius:999px;font-size:9px;border:1px solid rgba(255,255,255,.08)}.pill.high{color:#ff777c;background:rgba(255,78,85,.1)}.pill.mid{color:#f1c76a;background:rgba(242,186,69,.1)}.pill.low{color:#69dd95;background:rgba(71,219,125,.08)}
.callout{display:flex;gap:9px;align-items:flex-start;padding:10px;border-radius:11px;background:rgba(54,170,255,.055);border:1px solid rgba(86,183,255,.12);color:#8eacbd;font-size:10px;line-height:1.45}.callout b{color:#cfe6f1}.btn{width:100%;margin-top:12px;border:1px solid rgba(60,225,146,.35);color:#64e9a5;background:rgba(49,209,127,.05);border-radius:10px;padding:9px;font-size:10px;cursor:pointer}.btn:hover{background:rgba(49,209,127,.10)}
.footer{font-size:9px;color:#566f7e;margin-top:12px;text-align:right}
@media (max-width:1050px){.sidebar{width:175px}.grid{grid-template-columns:1fr}.panel{grid-template-columns:1fr 1fr}.field{transform:scale(.9);transform-origin:center}.top{flex-direction:column}.chips{justify-content:flex-start}}
</style>
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <div class="brand"><div class="logo">🌱</div><span>Prakriti-AI</span></div>
    <div class="nav"><div>⌂ &nbsp; Overview</div><div class="active">◈ &nbsp; Field Health</div><div>✥ &nbsp; Disease & Pest</div><div>◌ &nbsp; Soil & Fertilizer</div><div>☁ &nbsp; Weather</div><div>▤ &nbsp; Reports</div></div>
    <div class="sideNote"><b>Demo field</b><br>Top-down risk propagation prototype<br><br>Hover a plant to scan its neighborhood. Click to inspect.</div>
  </aside>
  <main class="main">
    <div class="top">
      <div><div class="title">Plant-to-Plant Disease / Pest Risk</div><div class="subtitle">Visualizing how disease and pest risk propagates between neighboring plants.</div></div>
      <div class="chips"><div class="chip">● <strong>Field Analysis</strong></div><div class="chip">Crop&nbsp; <strong>Rice</strong></div><div class="chip">View&nbsp; <strong>Top</strong></div></div>
    </div>
    <div class="grid">
      <section class="fieldCard">
        <div class="toolbar"><div class="left"><span class="statusDot"></span><span style="font-size:11px;color:#b6c9d3">Live field risk map</span><span style="font-size:9px;color:#687e8b">• synthetic demo</span></div><div class="right"><button id="reset">Reset View</button><button id="minus">−</button><button id="plus">＋</button></div></div>
        <div id="viewport"><div id="map" class="map"><div id="field" class="field"><div class="water"></div><div class="ridge" style="top:95px"></div><div class="ridge" style="top:280px"></div><div class="ridge" style="top:455px"></div><div id="heats"></div><div id="plants"></div><div id="scan" class="scan"></div></div></div></div>
        <div class="legendBar"><div class="legend"><span><i class="dot g"></i>Healthy</span><span><i class="dot y"></i>At Risk</span><span><i class="dot r"></i>Affected</span></div><div>Scroll to zoom • drag to pan • hover/click a plant</div></div>
      </section>
      <aside class="panel">
        <div class="card"><h3>Field Statistics</h3><div class="muted" style="margin-top:3px">1,248 plants monitored</div><div class="metrics"><div class="metric green"><b id="healthyPct">86%</b><small>Healthy</small></div><div class="metric yellow"><b id="riskPct">11%</b><small>At Risk</small></div><div class="metric red"><b id="affectedPct">3%</b><small>Affected</small></div></div></div>
        <div class="card"><h3>Risk Distribution</h3><div class="riskrow"><span>Healthy</span><span id="hcount">—</span></div><div class="bar"><i id="hbar" style="width:86%;background:#35da78"></i></div><div class="riskrow"><span>At Risk</span><span id="rcount">—</span></div><div class="bar"><i id="rbar" style="width:11%;background:#f3bc47"></i></div><div class="riskrow"><span>Affected</span><span id="acount">—</span></div><div class="bar"><i id="abar" style="width:3%;background:#ff4d54"></i></div></div>
        <div class="card"><h3>Selected Plant</h3><div class="muted" style="margin-top:3px" id="selHint">Move your cursor over the field.</div><div class="details" id="details"><div class="kv"><span>Plant ID</span><span>—</span></div><div class="kv"><span>Risk Level</span><span>—</span></div><div class="kv"><span>Disease / Pest</span><span>—</span></div><div class="kv"><span>Confidence</span><span>—</span></div><div class="kv"><span>Nearby at risk</span><span>—</span></div></div><button class="btn" id="inspect">Inspect Plant Report</button></div>
        <div class="callout">ⓘ <div><b>Risk propagation</b><br>Risk intensity is estimated from the distance to nearby affected plants. The red/yellow halos visually communicate the spread zone.</div></div>
      </aside>
    </div>
    <div class="footer">Prakriti-AI • Plant-to-Plant Risk • presentation prototype</div>
  </main>
</div>
<script>
const DATA = __PAYLOAD__;
const plants = DATA.plants;
const stats = DATA.stats;
const field = document.getElementById('field');
const plantLayer = document.getElementById('plants');
const heatLayer = document.getElementById('heats');
const scan = document.getElementById('scan');
const viewport = document.getElementById('viewport');
const map = document.getElementById('map');
const detail = document.getElementById('details');
const hint = document.getElementById('selHint');
let scale = 1, panX = 0, panY = 0, selected = null, hover = null;
let dragging = false, lastX = 0, lastY = 0;

function statusClass(s){return s==='Affected'?'high':s==='At Risk'?'mid':'low'}
function plantSvg(status){
 const c = status==='Affected'?'#ff4f58':status==='At Risk'?'#f4bf4e':'#48d97b';
 const c2 = status==='Affected'?'#b32634':status==='At Risk'?'#9f7420':'#179b59';
 return `<svg viewBox="0 0 36 32" aria-hidden="true"><path d="M18 28 C17 22 16 17 13 12" stroke="${c2}" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M17 19 C10 20 6 16 5 10 C11 9 16 12 17 19Z" fill="${c}"/><path d="M19 18 C22 11 27 8 32 9 C31 16 27 20 19 18Z" fill="${c2}"/><path d="M17 24 C11 25 8 22 7 18 C12 17 16 19 17 24Z" fill="${c2}" opacity=".95"/><path d="M19 23 C24 20 29 21 31 25 C26 28 22 27 19 23Z" fill="${c}" opacity=".9"/></svg>`;
}
function render(){
 heatLayer.innerHTML=''; plantLayer.innerHTML='';
 const clusters = [
  {x:274,y:190,s:175,c:'red'}, {x:568,y:346,s:168,c:'red'}, {x:653,y:118,s:145,c:'red'}, {x:132,y:354,s:132,c:'yellow'}
 ];
 clusters.forEach(z=>{const e=document.createElement('div');e.className='heat '+z.c;e.style.left=z.x+'px';e.style.top=z.y+'px';e.style.width=z.s+'px';e.style.height=z.s+'px';heatLayer.appendChild(e)});
 plants.forEach((p,i)=>{
   const el=document.createElement('div'); el.className='plant'; el.dataset.i=i; el.style.left=p.x+'px'; el.style.top=p.y+'px';
   el.innerHTML=`<div class="halo"></div><div class="risk">${plantSvg(p.status)}</div>`;
   el.addEventListener('mouseenter',()=>{hover=i; el.classList.add('hover'); showHover(i)});
   el.addEventListener('mouseleave',()=>{el.classList.remove('hover'); hover=null; scan.classList.remove('on')});
   el.addEventListener('click',e=>{e.stopPropagation(); select(i)});
   plantLayer.appendChild(el);
 });
 updateStats(); updateTransform();
}
function updateStats(){
 const total=plants.length; const hp=Math.round(stats.healthy/total*100), rp=Math.round(stats.risk/total*100), ap=100-hp-rp;
 document.getElementById('healthyPct').textContent=hp+'%';document.getElementById('riskPct').textContent=rp+'%';document.getElementById('affectedPct').textContent=ap+'%';
 document.getElementById('hcount').textContent=stats.healthy+' plants';document.getElementById('rcount').textContent=stats.risk+' plants';document.getElementById('acount').textContent=stats.affected+' plants';
 document.getElementById('hbar').style.width=hp+'%';document.getElementById('rbar').style.width=rp+'%';document.getElementById('abar').style.width=ap+'%';
}
function riskPill(status){return `<span class="pill ${statusClass(status)}">${status}</span>`}
function nearbyCount(i){const p=plants[i]; return plants.filter(q=>Math.hypot(q.x-p.x,q.y-p.y)<78 && q.status!=='Healthy').length}
function updateDetails(i){
 const p=plants[i]; hint.textContent='Plant '+p.id+' selected';
 detail.innerHTML=`<div class="kv"><span>Plant ID</span><span>${p.id}</span></div><div class="kv"><span>Risk Level</span><span>${riskPill(p.status)}</span></div><div class="kv"><span>Disease / Pest</span><span>${p.cause}</span></div><div class="kv"><span>Confidence</span><span>${Math.round(p.confidence*100)}%</span></div><div class="kv"><span>Nearby at risk</span><span>${nearbyCount(i)} plants</span></div><div class="kv"><span>Field position</span><span>R${p.row} · C${p.col}</span></div>`;
}
function showHover(i){
 const p=plants[i]; updateDetails(i); scan.style.left=p.x+'px';scan.style.top=p.y+'px';scan.classList.add('on');
}
function select(i){
 selected=i; document.querySelectorAll('.plant.selected').forEach(e=>e.classList.remove('selected')); const el=document.querySelector(`.plant[data-i="${i}"]`); if(el) el.classList.add('selected'); updateDetails(i); }
function updateTransform(){ map.style.transform=`translate(calc(-50% + ${panX}px),calc(-50% + ${panY}px)) scale(${scale})`; }
function zoom(delta, cx=viewport.clientWidth/2, cy=viewport.clientHeight/2){
 const old=scale; scale=Math.max(.62,Math.min(1.48,scale+delta));
 // Keep cursor approximately anchored.
 panX += (cx-viewport.clientWidth/2)*(1-scale/old); panY += (cy-viewport.clientHeight/2)*(1-scale/old); updateTransform();
}

document.getElementById('plus').onclick=()=>zoom(.1);
document.getElementById('minus').onclick=()=>zoom(-.1);
document.getElementById('reset').onclick=()=>{scale=1;panX=0;panY=0;selected=null;document.querySelectorAll('.plant.selected').forEach(e=>e.classList.remove('selected'));updateTransform()};
viewport.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY<0?.08:-.08,e.offsetX,e.offsetY)},{passive:false});
viewport.addEventListener('mousedown',e=>{dragging=true;lastX=e.clientX;lastY=e.clientY;viewport.style.cursor='grabbing'});
window.addEventListener('mouseup',()=>{dragging=false;viewport.style.cursor='grab'});
window.addEventListener('mousemove',e=>{if(!dragging)return;panX+=e.clientX-lastX;panY+=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;updateTransform()});
viewport.addEventListener('mousemove',e=>{if(hover!==null){const p=plants[hover]; const rect=field.getBoundingClientRect(); scan.style.left=(e.clientX-rect.left)/scale+'px';scan.style.top=(e.clientY-rect.top)/scale+'px'}});

document.getElementById('inspect').onclick=()=>{ if(selected===null) return alert('Click a plant first to inspect its demo report.'); const p=plants[selected]; alert(`Plant ${p.id}\n${p.cause} • ${p.status}\nConfidence: ${Math.round(p.confidence*100)}%\nNearby plants at risk: ${nearbyCount(selected)}`); };
render();
</script>
</body></html>'''.replace('__PAYLOAD__', payload)

components.html(html, height=900, scrolling=False)