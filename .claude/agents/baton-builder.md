---
name: baton-builder
description: >
  선택된 UX 안(A/B/C)을 하나의 파일에 탭 스위처로 묶은
  완전 작동 풀 플로우 프로토타입(prototype.html)과
  시나리오 기반 화면 플로우 문서(scenario-flow.html)를 동시에 빌드한다.
  STEP 4 전담. "프로토타입 만들어줘", "풀빌드", 안 선택 직후 사용.
  baton 오케스트레이터가 STEP 4에서 호출한다.
tools: Read, Write, Edit
model: sonnet
skills:
  - korean-copy-guardrail
---

# baton-builder — 풀 플로우 프로토타입 빌더

## 와이어프레임 vs 프로토타입 — 이 에이전트의 역할

| | 와이어프레임 풀빌드 | **풀 플로우 프로토타입 (이것)** |
|---|---|---|
| 목적 | 화면 레이아웃·컴포넌트 검증 | **사용자 플로우 체험 검증** |
| 화면 디테일 | 높음 (컴포넌트 정밀) | 낮아도 됨 (구조만 전달) |
| 인터랙션 | 일부 | **모든 버튼·링크 작동** |
| 출력 | wireframe.html (안별 분리) | **prototype.html (A/B/C 탭 통합)** |

**핵심 기준**: "이 프로토타입으로 처음부터 끝까지 서비스를 체험할 수 있는가?"

---

## 작업 전 필수 (순서대로)

1. `CLAUDE.md` 읽기 — 모노크롬 규칙, 품질 체크리스트
2. `.claude/skills/baton-tokens.md` 읽기 — 팔레트, 컴포넌트 정의
3. `.claude/skills/baton-shell.md` 읽기 — **createMobileApp 팩토리만** 참조.
   baton-shell.md의 `openFlowView`는 단일 플로우(FL_POS/FL_LABEL/FL_ARROWS)용 예시다.
   A/B/C 탭 통합 prototype.html에서는 반드시 이 파일(baton-builder.md) 아래 "프로토타입 셸
   구조"에 있는 `openFlowView`(FL_DATA 다중 플로우 버전)를 그대로 쓴다 — baton-shell.md 버전을
   복수 안(A/B/C)용으로 확장한 것이며, 단일 플로우 폴백이 없고 `#sf-overlay` Esc 처리가
   추가돼 있다.
   prototype.html 레이아웃 전체는 이 파일(baton-builder.md)의 탭 스위처 셸 템플릿을 따른다.
4. `output/{프로젝트명}/interpretation.html` + `screens-proposal.html` 확인 — **없으면 STEP 4를
   시작하지 않는다.** baton 오케스트레이터에 STEP 2/3부터 실행하도록 되돌려 보낸다.

---

## 프로토타입 셸 구조 (A/B/C 탭 통합)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>프로토타입 — {프로젝트명}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@latest/dist/web/static/pretendard.min.css">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <script type="module">
    import { createIcons, icons } from 'https://cdn.jsdelivr.net/npm/lucide@latest/dist/esm/lucide.js';
    window.__refreshIcons = () => createIcons({ icons });
    window.__refreshIcons(); // 모듈은 DOM 파싱 후 실행되므로 즉시 호출
  </script>
  <style>
    /* ── 기본 ── */
    *, *::before, *::after { box-sizing: border-box; }
    body { margin:0; background:#f4f4f4; font-family:"Pretendard",system-ui,sans-serif; }

    /* ── 프로토타입 컨테이너 ── */
    .proto-wrap { min-height:100vh; display:flex; flex-direction:column; align-items:center; padding:32px 24px 60px; }

    /* ── 탭 스위처 ── */
    .proto-tabs { display:flex; gap:6px; background:#fff; border:1px solid #ebebeb; border-radius:12px; padding:4px; margin-bottom:8px; }
    .proto-tab { padding:8px 20px; border-radius:8px; border:none; background:transparent; color:#888; font:500 13px Pretendard; cursor:pointer; transition:all .15s; white-space:nowrap; }
    .proto-tab.active { background:#1a1a1a; color:#fff; font-weight:600; }

    /* ── 안 설명 ── */
    .proto-desc { font:400 12px Pretendard; color:#888; margin-bottom:14px; text-align:center; max-width:390px; line-height:1.5; }

    /* ── 플로우 버튼 ── */
    .flow-open-btn { margin-bottom:16px; padding:7px 16px; border:1.5px solid #cccccc; border-radius:8px; background:#fff; font:500 12px Pretendard; color:#555; cursor:pointer; display:inline-flex; align-items:center; gap:6px; }
    .flow-open-btn:hover { background:#1a1a1a; color:#fff; border-color:#1a1a1a; }

    /* ── 디바이스 ── */
    .device { width:390px; height:844px; background:#fff; border-radius:46px; border:11px solid #1a1a1a;
      box-shadow:0 18px 50px rgba(26,26,26,.18); overflow:hidden; position:relative; flex:none; }
    .notch { position:absolute; top:0; left:50%; transform:translateX(-50%); width:150px; height:30px;
      background:#1a1a1a; border-radius:0 0 18px 18px; z-index:50; }
    .screen { position:absolute; inset:0; overflow:hidden; }

    /* ── 슬라이드 트랜지션 ── */
    @keyframes slideIn   { from{transform:translateX(100%)} to{transform:translateX(0)} }
    @keyframes slideBack { from{transform:translateX(-30%)} to{transform:translateX(0)} }
    @keyframes sheetUp   { from{transform:translateY(100%)} to{transform:translateY(0)} }
    .slide-in   { animation:slideIn .2s ease-out; }
    .slide-back { animation:slideBack .2s ease-out; }

    /* ── 시나리오 플로우 오버레이 ── */
    #sf-overlay { position:fixed; inset:0; z-index:9997; display:none; background:#f4f4f4; overflow-y:auto; }
    #sf-overlay-hd { position:sticky; top:0; left:0; right:0; height:52px; background:#1a1a1a; display:flex; align-items:center; padding:0 20px; gap:12px; z-index:10; border-bottom:1px solid #333333; }
    .sf-doc-header { margin-bottom:56px; padding-bottom:32px; border-bottom:1.5px solid #d8d8d8; }
    .sf-doc-label { font:700 11px Pretendard; color:#888; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:12px; }
    .sf-doc-title { font:700 28px Pretendard; color:#1a1a1a; margin-bottom:8px; }
    .sf-doc-meta { font:400 13px Pretendard; color:#888; }
    .sf-page { padding:56px 64px 96px; max-width:1600px; margin:0 auto; }
    .sf-scenario { margin-bottom:64px; }
    .sf-header { display:flex; align-items:center; gap:14px; margin-bottom:6px; }
    .sf-num { width:30px;height:30px;background:#1a1a1a;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 13px Pretendard;flex-shrink:0; }
    .sf-scenario-title { font:700 20px Pretendard; color:#1a1a1a; }
    .sf-path { font:400 12px Pretendard; color:#888; margin-left:44px; margin-bottom:28px; }
    .sf-divider { border:none; border-top:1px solid #d8d8d8; margin-bottom:72px; }
    .sf-row { display:flex; align-items:flex-start; gap:0; overflow-x:auto; padding-bottom:16px; }
    .sf-screen-wrap { display:flex; flex-direction:column; align-items:center; flex-shrink:0; }
    .sf-screen-label { font:600 12px Pretendard; color:#1a1a1a; margin-bottom:8px; text-align:center; }
    .sf-device { width:200px; height:432px; background:#fff; border-radius:24px; border:6px solid #1a1a1a; overflow:hidden; position:relative; flex:none; }
    .sf-device-inner { position:absolute; top:0; left:0; width:390px; height:844px; transform:scale(0.512); transform-origin:0 0; pointer-events:none; overflow:hidden; }
    .sf-note { font:400 11px Pretendard; color:#888; margin-top:10px; text-align:center; max-width:200px; line-height:1.5; }
    .sf-connector { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:0 12px; margin-top:220px; flex-shrink:0; }
    .sf-conn-arrow { display:flex; align-items:center; }
    .sf-conn-line { width:36px; height:2px; background:#d8d8d8; }
    .sf-conn-head { width:0; height:0; border-top:5px solid transparent; border-bottom:5px solid transparent; border-left:7px solid #d8d8d8; }
    .sf-conn-label { font:400 10px Pretendard; color:#aaa; margin-top:4px; white-space:nowrap; text-align:center; }
    .sf-diamond-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:0 8px; margin-top:210px; flex-shrink:0; }
    .sf-diamond-label { font:500 10px Pretendard; color:#555; margin-top:4px; text-align:center; white-space:nowrap; }

    /* ── 플로우 뷰 ── */
    #flow-overlay { position:fixed; inset:0; background:#1a1a1a; z-index:9999; display:none; }
    #fl-header { position:absolute; top:0; left:0; right:0; height:52px; background:#1a1a1a;
      border-bottom:1px solid #333333; display:flex; align-items:center; padding:0 20px; gap:12px; z-index:10; }
    #fl-wrap { position:absolute; top:52px; left:0; right:0; bottom:40px; overflow:hidden; cursor:default; }
    #fl-canvas { position:absolute; top:0; left:0; transform-origin:0 0; will-change:transform; }
    .fl-frame { position:absolute; cursor:pointer; }
    .fl-label { font:600 13px/1 "Pretendard"; color:#ccc; text-align:center; margin-bottom:8px; pointer-events:none; white-space:nowrap; }
    .fl-device { width:390px; height:844px; border-radius:28px; border:2px solid #555555; overflow:hidden; background:#fff; pointer-events:none; transition:border-color .2s,box-shadow .2s; display:flex; flex-direction:column; }
    .fl-frame:hover .fl-device { border-color:#888; }
    .fl-frame.fl-active .fl-device { border:3px solid #fff; box-shadow:0 0 0 4px rgba(255,255,255,.15); }
    .fl-frame.fl-nav .fl-device { animation:fl-pulse .7s ease-out; }
    @keyframes fl-pulse { 0%{box-shadow:0 0 0 0 rgba(255,255,255,.55)} 100%{box-shadow:0 0 0 24px rgba(255,255,255,0)} }
    #fl-hint { position:absolute; bottom:0; left:0; right:0; height:40px; display:flex; align-items:center;
      justify-content:center; gap:24px; background:#1a1a1a; border-top:1px solid #333333;
      font:400 12px/1 "Pretendard"; color:#555; }
    #fl-hint b { color:#888; }
    .fl-btn { background:none; border:1.5px solid #333; border-radius:7px; color:#888; font:500 12px/1 "Pretendard"; padding:5px 12px; cursor:pointer; }
    .fl-btn:hover { border-color:#aaa; color:#fff; }
    #fl-zoom-pct { font:600 12px/1 "Pretendard"; color:#888; min-width:38px; text-align:center; }
  </style>
</head>
<body>
<div class="proto-wrap">

  <!-- ★ 탭 스위처 -->
  <div class="proto-tabs">
    <button class="proto-tab active" onclick="switchProto('a')">A안 · {A안 이름}</button>
    <button class="proto-tab"        onclick="switchProto('b')">B안 · {B안 이름}</button>
    <button class="proto-tab"        onclick="switchProto('c')">C안 · {C안 이름}</button>
  </div>

  <!-- 안 설명 (탭 전환 시 바뀜) -->
  <div class="proto-desc" id="desc-a">{A안 한 줄 설명}</div>
  <div class="proto-desc" id="desc-b" style="display:none">{B안 한 줄 설명}</div>
  <div class="proto-desc" id="desc-c" style="display:none">{C안 한 줄 설명}</div>

  <!-- ★ 버튼 2개: 플로우 보기 + 시나리오 보기 -->
  <div style="display:flex;gap:8px;margin-bottom:16px">
    <button class="flow-open-btn" style="margin-bottom:0" onclick="openFlowView(currentProto)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/><line x1="17.5" y1="17.5" x2="21" y2="21"/>
      </svg>
      플로우 보기
    </button>
    <button class="flow-open-btn" style="margin-bottom:0" onclick="openSfOverlay()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
        <rect x="9" y="3" width="6" height="4" rx="1"/>
        <line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/>
      </svg>
      시나리오 보기
    </button>
  </div>

  <!-- ★ 단일 디바이스 — 3개 screen이 겹쳐 있고 하나만 표시 -->
  <div class="device">
    <div class="notch"></div>
    <div class="screen" id="app-A"></div>
    <div class="screen" id="app-B" style="display:none"></div>
    <div class="screen" id="app-C" style="display:none"></div>
  </div>

</div><!-- /proto-wrap -->

<!-- ★ 시나리오 플로우 오버레이 (Cursor IDE 호환: 새 탭 없이 인라인 표시) -->
<!-- 에이전트: scenario-flow.html과 동일한 시나리오 HTML을 여기에 embed -->
<!-- sf-device-inner id는 "s01-{키}", "s02-{키}" 등 고유 id 부여 -->
<div id="sf-overlay">
  <div id="sf-overlay-hd">
    <button class="fl-btn" onclick="closeSfOverlay()">← 돌아가기</button>
    <span style="font:600 14px/1 'Pretendard';color:#ccc">시나리오 플로우 — {서비스명}</span>
  </div>
  <div class="sf-page">
    <div class="sf-doc-header">
      <div class="sf-doc-label">Scenario Flow Document</div>
      <div class="sf-doc-title">{서비스명} — 시나리오 플로우</div>
      <div class="sf-doc-meta">{안 이름} · {페르소나} · {날짜}</div>
    </div>
    <!-- 시나리오 1 -->
    <div class="sf-scenario">
      <div class="sf-header"><div class="sf-num">01</div><div class="sf-scenario-title">{시나리오 제목}</div></div>
      <div class="sf-path">{화면A} → {화면B} → ...</div>
      <div class="sf-row">
        <div class="sf-screen-wrap">
          <div class="sf-screen-label">{화면 레이블}</div>
          <div class="sf-device"><div class="sf-device-inner" id="s01-{키}"></div></div>
          <div class="sf-note">{주석}</div>
        </div>
        <div class="sf-connector"><div class="sf-conn-arrow"><div class="sf-conn-line"></div><div class="sf-conn-head"></div></div><div class="sf-conn-label">{액션}</div></div>
        <div class="sf-screen-wrap">
          <div class="sf-screen-label">{화면 레이블}</div>
          <div class="sf-device"><div class="sf-device-inner" id="s01-{키2}"></div></div>
          <div class="sf-note">{주석}</div>
        </div>
      </div>
    </div>
    <hr class="sf-divider">
    <!-- 시나리오 02~N: 동일 패턴 반복 -->
  </div>
</div>

<!-- ★ 플로우 뷰 오버레이 -->
<div id="flow-overlay">
  <div id="fl-header">
    <button class="fl-btn" onclick="closeFlowView()">← 돌아가기</button>
    <span id="fl-title" style="font:600 14px/1 'Pretendard';color:#ccc"></span>
    <div style="margin-left:auto;display:flex;align-items:center;gap:6px">
      <button class="fl-btn" onclick="flZoom(0.8)">−</button>
      <span id="fl-zoom-pct">42%</span>
      <button class="fl-btn" onclick="flZoom(1.25)">+</button>
      <button class="fl-btn" style="margin-left:8px" onclick="flFit()">전체 보기</button>
    </div>
  </div>
  <div id="fl-wrap"><div id="fl-canvas"></div></div>
  <div id="fl-hint">
    <span><b>Space</b> + 드래그: 이동</span>
    <span><b>Ctrl</b> + 스크롤 · <b>+−</b>: 확대·축소</span>
    <span><b>Esc</b>: 닫기</span>
  </div>
</div>

<script>
// ─────────────────────────────────────────────
// 0. 탭 스위처
// ─────────────────────────────────────────────
let currentProto = 'a';
function switchProto(id) {
  ['a','b','c'].forEach((k, i) => {
    document.getElementById('app-' + k.toUpperCase()).style.display = k===id ? 'block' : 'none';
    document.getElementById('desc-' + k).style.display = k===id ? 'block' : 'none';
    document.querySelectorAll('.proto-tab')[i].classList.toggle('active', k===id);
  });
  currentProto = id;
}

// ─────────────────────────────────────────────
// 1. createMobileApp 팩토리 (라우팅 격리)
// ─────────────────────────────────────────────
function createMobileApp(rootEl, flow) {
  const state = { stack:[flow.initial], data:{} };
  const app = {
    push(k)    { _cl(app); state.stack.push(k);                 _render('in'); },
    replace(k) { _cl(app); state.stack[state.stack.length-1]=k; _render('in'); },
    pop()      { if(state.stack.length>1){ _cl(app); state.stack.pop(); _render('back'); } },
    tab(k)     { _cl(app); state.stack=[k];                     _render('in'); },
    set(k,v)   { state.data[k]=v; },
    get(k)     { return state.data[k]; },
    cur()      { return state.stack[state.stack.length-1]; },
    toast(msg) {
      const t=document.createElement('div');
      t.style.cssText='position:absolute;bottom:80px;left:50%;transform:translateX(-50%);background:#1a1a1a;color:#fff;font:500 13px Pretendard;padding:10px 20px;border-radius:100px;z-index:99;white-space:nowrap;opacity:0;transition:opacity .18s';
      t.textContent=msg; rootEl.appendChild(t);
      requestAnimationFrame(()=>t.style.opacity=1);
      setTimeout(()=>{t.style.opacity=0;setTimeout(()=>t.remove(),220);},2200);
    },
  };
  function _cl(a){ const f=a.get('__cleanup'); if(f){f();a.set('__cleanup',null);} }
  function _render(dir){
    const key=state.stack[state.stack.length-1];
    const wrap=document.createElement('div');
    wrap.style.cssText='position:absolute;inset:0;overflow:hidden;display:flex;flex-direction:column';
    wrap.classList.add(dir==='back'?'slide-back':'slide-in');
    wrap.innerHTML=flow.screens[key](app);
    rootEl.querySelectorAll(':scope>div').forEach(n=>n.remove());
    rootEl.appendChild(wrap);
    window.__refreshIcons?.();
    wrap.querySelectorAll('[data-push]').forEach(el=>el.onclick=()=>app.push(el.dataset.push));
    wrap.querySelectorAll('[data-pop]').forEach(el=>el.onclick=()=>app.pop());
    wrap.querySelectorAll('[data-goto]').forEach(el=>el.onclick=()=>app.replace(el.dataset.goto));
    wrap.querySelectorAll('[data-tab]').forEach(el=>el.onclick=()=>app.tab(el.dataset.tab));
    wrap.querySelectorAll('[data-toast]').forEach(el=>el.onclick=()=>app.toast(el.dataset.toast));
    flow.onMount?.[key]?.(wrap,app);
  }
  _render('in');
  return app;
}

// ─────────────────────────────────────────────
// 2. 공통 헬퍼
// ─────────────────────────────────────────────
const SB = `<div style="height:36px;display:flex;align-items:center;justify-content:space-between;padding:4px 22px 0;flex-shrink:0">
  <span style="font:600 12px Pretendard;color:#1a1a1a">9:41</span>
  <div style="display:flex;gap:4px"><i data-lucide="signal" style="width:13px;height:13px;color:#1a1a1a"></i><i data-lucide="battery-full" style="width:13px;height:13px;color:#1a1a1a"></i></div>
</div>`;

const AB = (title, back=false, right='') => `<div style="height:50px;display:flex;align-items:center;padding:0 8px;border-bottom:1px solid #ebebeb;flex-shrink:0">
  ${back?`<button data-pop style="width:44px;height:44px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;cursor:pointer"><i data-lucide="chevron-left" style="width:22px;height:22px;color:#1a1a1a"></i></button>`:`<div style="width:44px"></div>`}
  <span style="flex:1;font:700 17px Pretendard;color:#1a1a1a;text-align:center">${title}</span>
  ${right?`<button style="width:44px;height:44px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;cursor:pointer"><i data-lucide="${right}" style="width:20px;height:20px;color:#555"></i></button>`:`<div style="width:44px"></div>`}
</div>`;

const BTN_P = 'width:100%;height:52px;border-radius:12px;border:none;background:#1a1a1a;color:#fff;font:700 16px Pretendard;cursor:pointer;flex-shrink:0';
const BTN_O = 'width:100%;height:52px;border-radius:12px;border:1.5px solid #1a1a1a;background:transparent;color:#1a1a1a;font:600 16px Pretendard;cursor:pointer;flex-shrink:0';

const TABBAR = (tabs, active) => `<div style="height:64px;background:#fff;border-top:1.5px solid #ebebeb;display:flex;padding-bottom:8px;flex-shrink:0">
  ${tabs.map(t=>`<button data-tab="${t.key}" style="flex:1;border:none;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;padding-top:8px">
    <i data-lucide="${t.icon}" style="width:20px;height:20px;color:${active===t.key?'#1a1a1a':'#aaa'}"></i>
    <span style="font:${active===t.key?700:500} 10px Pretendard;color:${active===t.key?'#1a1a1a':'#aaa'}">${t.label}</span>
  </button>`).join('')}
</div>`;

function openSheet(root, content) {
  const bd=document.createElement('div');
  bd.style.cssText='position:absolute;inset:0;background:rgba(0,0,0,0.45);z-index:60;display:flex;align-items:flex-end';
  bd.innerHTML=`<div style="background:#fff;border-radius:20px 20px 0 0;width:100%;padding:8px 20px 36px;animation:sheetUp .25s ease-out">
    <div style="width:36px;height:4px;background:#d8d8d8;border-radius:2px;margin:12px auto 20px"></div>${content}</div>`;
  root.appendChild(bd);
  window.__refreshIcons?.();
  bd.addEventListener('click',e=>{if(e.target===bd)bd.remove();});
  return bd;
}

// ─────────────────────────────────────────────
// 3. 플로우 데이터 (에이전트가 채운다)
// ─────────────────────────────────────────────
// x 간격: SW(390)+120=510, y 간격: SH(844)+120=964
const FL_OX=100, FL_OY=100;
const SW=390, SH=844;
const INIT_SCALE=0.35;

const FL_DATA = {
  a: { title:'A안 · {A안 이름}', initScreen:'a_home', pos:{}, label:{}, arrows:[] },
  b: { title:'B안 · {B안 이름}', initScreen:'b_home', pos:{}, label:{}, arrows:[] },
  c: { title:'C안 · {C안 이름}', initScreen:'c_home', pos:{}, label:{}, arrows:[] },
};
// 렌더 소스 (플로우 뷰에서 화면 미리보기용)
const FLOW_SRC = {
  a: () => FLOW_A.screens,
  b: () => FLOW_B.screens,
  c: () => FLOW_C.screens,
};

// ─────────────────────────────────────────────
// 4. A/B/C 플로우 정의 (에이전트가 채운다)
// ─────────────────────────────────────────────
const FLOW_A = { initial:'a_home', screens:{ 'a_home': (app)=>`...` }, onMount:{} };
const FLOW_B = { initial:'b_home', screens:{ 'b_home': (app)=>`...` }, onMount:{} };
const FLOW_C = { initial:'c_home', screens:{ 'c_home': (app)=>`...` }, onMount:{} };

// ─────────────────────────────────────────────
// 5. 초기화
// ─────────────────────────────────────────────
createMobileApp(document.getElementById('app-A'), FLOW_A);
createMobileApp(document.getElementById('app-B'), FLOW_B);
createMobileApp(document.getElementById('app-C'), FLOW_C);

// ─────────────────────────────────────────────
// 5-b. 시나리오 플로우 오버레이 JS
// ─────────────────────────────────────────────
let _sfInited = false;
function openSfOverlay(){
  document.getElementById('sf-overlay').style.display='block';
  document.body.style.overflow='hidden';
  if(!_sfInited){ _sfInitAll(); _sfInited=true; }
}
function closeSfOverlay(){
  document.getElementById('sf-overlay').style.display='none';
  document.body.style.overflow='';
}
function _sfInitAll(){
  const MOCK={push:()=>{},pop:()=>{},replace:()=>{},tab:()=>{},toast:()=>{},set:()=>{},get:()=>null,cur:()=>''};
  // 에이전트: sf-device-inner id → FLOW_A/B/C.screens 키 매핑
  // a_ → FLOW_A.screens, b_ → FLOW_B.screens, c_ → FLOW_C.screens
  const MAP={
    's01-{키}':'a_{screen}',
    // ... scenario-flow.html의 모든 id:screenKey 쌍을 여기에 열거
  };
  const FLOWS={a:FLOW_A,b:FLOW_B,c:FLOW_C};
  for(const [elId,screenKey] of Object.entries(MAP)){
    const el=document.getElementById(elId); if(!el)continue;
    const prefix=screenKey[0];
    const fn=FLOWS[prefix]?.screens[screenKey]; if(!fn)continue;
    el.innerHTML=fn(MOCK);
    el.querySelectorAll('[data-push],[data-pop],[data-tab],[data-replace]')
      .forEach(b=>b.style.pointerEvents='none');
  }
  if(window.__refreshIcons)window.__refreshIcons();
}

// ─────────────────────────────────────────────
// 6. 플로우 뷰 JS (baton-shell.md의 단일 플로우 버전을 A/B/C 다중 플로우용으로 확장)
// ─────────────────────────────────────────────
function flAbsPos(pos,id){const p=pos[id];return p?{x:p.x+FL_OX,y:p.y+FL_OY}:null;}
let flT={x:0,y:0,scale:INIT_SCALE},flFlowId=null,flActive='',flHistory=[];
let flSpace=false,flPan=false,flMouse=null,flPinchD=0;
function openFlowView(flowId){
  const d=FL_DATA[flowId];if(!d)return;
  flFlowId=flowId;flActive=d.initScreen;flHistory=[];
  document.getElementById('fl-title').textContent=d.title+'  —  플로우 맵';
  const mock={get:()=>null,set:()=>{},push:()=>{},pop:()=>{},replace:()=>{},tab:()=>{},toast:()=>{},cur:()=>''};
  const xs=Object.values(d.pos).map(p=>p.x+FL_OX),ys=Object.values(d.pos).map(p=>p.y+FL_OY);
  const cW=Math.max(...xs)+SW+FL_OX+100,cH=Math.max(...ys)+SH+FL_OY+100;
  let svg=`<svg style="position:absolute;top:0;left:0;width:${cW}px;height:${cH}px;overflow:visible;pointer-events:none">
    <defs><marker id="flarr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0,10 4,0 8" fill="rgba(255,255,255,0.75)"/></marker></defs>`;
  for(const [from,to,lbl] of d.arrows){
    const fp=flAbsPos(d.pos,from),tp=flAbsPos(d.pos,to);if(!fp||!tp)continue;
    const fcx=fp.x+SW/2,fcy=fp.y+SH/2,tcx=tp.x+SW/2,tcy=tp.y+SH/2;
    const dx=tcx-fcx,dy=tcy-fcy,adx=Math.abs(dx),ady=Math.abs(dy);
    let fx,fy,tx,ty,horiz;
    if(adx>ady*1.2){horiz=true;if(dx>0){fx=fp.x+SW+8;fy=fcy;tx=tp.x-8;ty=tcy}else{fx=fp.x-8;fy=fcy;tx=tp.x+SW+8;ty=tcy}}
    else{horiz=false;if(dy>0){fx=fcx;fy=fp.y+SH+18;tx=tcx;ty=tp.y-18}else{fx=fcx;fy=fp.y-18;tx=tcx;ty=tp.y+SH+18}}
    const hw=Math.abs(tx-fx)/2;
    const path=horiz?`M${fx},${fy} C${fx+hw},${fy} ${tx-hw},${ty} ${tx},${ty}`:`M${fx},${fy} C${fx},${(fy+ty)/2} ${tx},${(fy+ty)/2} ${tx},${ty}`;
    svg+=`<path d="${path}" fill="none" stroke="rgba(255,255,255,0.75)" stroke-width="2" marker-end="url(#flarr)"/>`;
    if(lbl)svg+=`<text x="${(fx+tx)/2}" y="${(fy+ty)/2-8}" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.55)" font-family="Pretendard,sans-serif">${lbl}</text>`;
  }
  svg+=`</svg>`;
  const screens=FLOW_SRC[flowId]?FLOW_SRC[flowId]():{};
  let frames='';
  for(const [sid] of Object.entries(d.pos)){
    const p=flAbsPos(d.pos,sid);
    const html=screens[sid]?screens[sid](mock):'';
    frames+=`<div class="fl-frame ${sid===flActive?'fl-active':''}" data-sid="${sid}" style="left:${p.x}px;top:${p.y}px;width:${SW}px">
      <div class="fl-label">${d.label[sid]||sid}</div>
      <div class="fl-device">${html}</div></div>`;
  }
  const canvas=document.getElementById('fl-canvas');
  canvas.style.width=cW+'px';canvas.style.height=cH+'px';
  canvas.innerHTML=svg+frames;
  window.__refreshIcons?.();
  canvas.onclick=(e)=>{
    if(e.target.closest('[data-pop]')){flBack();return;}
    const dest=[e.target.closest('[data-push]')?.dataset.push,e.target.closest('[data-goto]')?.dataset.goto,e.target.closest('.fl-frame')?.dataset.sid].find(k=>k&&d.pos[k]);
    if(dest)flGoTo(d.pos,dest);
  };
  document.getElementById('flow-overlay').style.display='block';
  flT={x:0,y:0,scale:INIT_SCALE};flApply();
  setTimeout(()=>flCenterOn(d.pos,d.initScreen,false),60);
}
function closeFlowView(){document.getElementById('flow-overlay').style.display='none';}
function flBack(){if(flHistory.length>0)flGoTo(null,flHistory.pop(),false);}
function flGoTo(pos,sid,push=true){
  const d=FL_DATA[flFlowId];if(!d||!d.pos[sid])return;
  if(push&&flActive&&flActive!==sid)flHistory.push(flActive);
  flActive=sid;
  document.querySelectorAll('.fl-frame').forEach(f=>{
    const t=f.dataset.sid===sid;f.classList.toggle('fl-active',t);
    if(t){f.classList.remove('fl-nav');void f.offsetWidth;f.classList.add('fl-nav');setTimeout(()=>f.classList.remove('fl-nav'),750);}
  });
  flCenterOn(d.pos,sid,true);
}
function flCenterOn(pos,sid,anim){
  const d=FL_DATA[flFlowId];const p=flAbsPos(d?d.pos:pos,sid);if(!p)return;
  const wrap=document.getElementById('fl-wrap');
  const nx=wrap.clientWidth/2-(p.x+SW/2)*flT.scale,ny=wrap.clientHeight/2-(p.y+SH/2)*flT.scale;
  const canvas=document.getElementById('fl-canvas');
  if(anim){canvas.style.transition='transform .48s cubic-bezier(.4,0,.2,1)';setTimeout(()=>canvas.style.transition='',520);}
  flT.x=nx;flT.y=ny;flApply();
}
function flApply(){const c=document.getElementById('fl-canvas');if(!c)return;c.style.transform=`translate(${flT.x}px,${flT.y}px) scale(${flT.scale})`;document.getElementById('fl-zoom-pct').textContent=Math.round(flT.scale*100)+'%';}
function flZoomAt(cx,cy,f){const ns=Math.max(0.12,Math.min(2.5,flT.scale*f)),r=ns/flT.scale;flT.x=cx-r*(cx-flT.x);flT.y=cy-r*(cy-flT.y);flT.scale=ns;flApply();}
function flZoom(f){const w=document.getElementById('fl-wrap');if(w)flZoomAt(w.clientWidth/2,w.clientHeight/2,f);}
function flFit(){
  const wrap=document.getElementById('fl-wrap');if(!wrap)return;
  const d=FL_DATA[flFlowId];if(!d)return;
  const xs=Object.values(d.pos).map(p=>p.x+FL_OX),ys=Object.values(d.pos).map(p=>p.y+FL_OY);
  const minX=Math.min(...xs),maxX=Math.max(...xs)+SW,minY=Math.min(...ys),maxY=Math.max(...ys)+SH;
  const vw=wrap.clientWidth-80,vh=wrap.clientHeight-80;
  flT.scale=Math.min(2.5,Math.min(vw/(maxX-minX),vh/(maxY-minY)));
  flT.x=(wrap.clientWidth-(maxX-minX)*flT.scale)/2-minX*flT.scale;
  flT.y=(wrap.clientHeight-(maxY-minY)*flT.scale)/2-minY*flT.scale;
  flApply();
}
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    if(document.getElementById('sf-overlay')?.style.display!=='none') closeSfOverlay();
    else if(document.getElementById('flow-overlay')?.style.display!=='none') closeFlowView();
    return;
  }
  if(document.getElementById('flow-overlay')?.style.display==='none')return;
  if(e.code==='Space'&&!e.target.matches('input,textarea')){e.preventDefault();flSpace=true;const w=document.getElementById('fl-wrap');if(w)w.style.cursor='grab';}
  if(e.ctrlKey&&(e.key==='='||e.key==='+'))  {e.preventDefault();flZoom(1.25);}
  if(e.ctrlKey&&e.key==='-')                  {e.preventDefault();flZoom(0.8);}
  if(e.key==='0'&&e.ctrlKey)                  {e.preventDefault();flFit();}
});
document.addEventListener('keyup',e=>{if(e.code==='Space'){flSpace=false;const w=document.getElementById('fl-wrap');if(w&&!flPan)w.style.cursor='default';}});
document.addEventListener('mousedown',e=>{const w=document.getElementById('fl-wrap');if(!w?.contains(e.target))return;if(flSpace||e.button===1){e.preventDefault();flPan=true;flMouse={x:e.clientX,y:e.clientY};w.style.cursor='grabbing';}});
document.addEventListener('mousemove',e=>{if(!flPan||!flMouse)return;flT.x+=e.clientX-flMouse.x;flT.y+=e.clientY-flMouse.y;flMouse={x:e.clientX,y:e.clientY};flApply();});
document.addEventListener('mouseup',()=>{if(flPan){flPan=false;const w=document.getElementById('fl-wrap');if(w)w.style.cursor=flSpace?'grab':'default';}});
document.addEventListener('wheel',e=>{const w=document.getElementById('fl-wrap');if(!w?.contains(e.target))return;if(e.ctrlKey){e.preventDefault();const r=w.getBoundingClientRect();flZoomAt(e.clientX-r.left,e.clientY-r.top,e.deltaY>0?0.9:1.1);}else{e.preventDefault();flT.x-=e.deltaX*1.2;flT.y-=e.deltaY*1.2;flApply();}},{passive:false});
document.addEventListener('touchstart',e=>{if(!document.getElementById('fl-wrap')?.contains(e.target))return;if(e.touches.length===2)flPinchD=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);},{passive:false});
document.addEventListener('touchmove',e=>{const w=document.getElementById('fl-wrap');if(!w?.contains(e.target)||e.touches.length!==2)return;e.preventDefault();const d2=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);const cx=(e.touches[0].clientX+e.touches[1].clientX)/2,cy=(e.touches[0].clientY+e.touches[1].clientY)/2;const r=w.getBoundingClientRect();if(flPinchD>0)flZoomAt(cx-r.left,cy-r.top,d2/flPinchD);flPinchD=d2;},{passive:false});
</script>
</body>
</html>
```

---

## 핵심 원칙 (와이어프레임과 다른 것들)

### 1. 플로우 완결이 최우선
- 모든 버튼은 실제로 어딘가로 이동한다 (막힌 버튼 없음)
- 핵심 시나리오를 처음부터 끝까지 체험할 수 있어야 한다
- 화면이 불완전하더라도 전환은 반드시 작동한다

### 2. 화면 디테일보다 인터랙션
- 컴포넌트 픽셀 정밀도 < 모든 인터랙션 작동
- 레이아웃은 단순해도 되지만 탭·슬라이더·타이머는 실제로 동작해야 함
- 더미 데이터는 서비스 맥락에 맞는 한국어 (절대 placeholder/Lorem 금지)

### 3. 모노크롬 절대 준수
허용: `#1a1a1a #333 #555 #888 #aaa #ccc #d8d8d8 #ebebeb #f4f4f4 #fff`
금지: 어떤 유채색도. 쉐딩 구간 음영 = `#ebebeb` 또는 사선 해칭 CSS.

### 4. A/B/C 완전 격리
- 각 앱은 독립적 `createMobileApp` 인스턴스
- A 탭 클릭이 B/C 상태에 영향 없음
- 전역 id/변수 금지 — 화면 key는 `a_`, `b_`, `c_` 접두사로 구분

### 5. 자연스러운 한국어 (번역투·AI 티 제거)
**korean-copy-guardrail 스킬**을 따른다. 이 에이전트는 그 스킬을 frontmatter `skills:`로 선적재하므로 canonical 7 규칙이 이미 컨텍스트에 있다. 더미 텍스트·버튼·타이틀·안내 문구를 쓴 뒤 별도 pass로 다시 읽으며 잡고, 레포의 `hanlint` 훅이 저장 때 한 번 더 센다.

---

## data-attribute 라우팅 우선

```html
<button data-push="a_next">다음 화면</button>   <!-- 스택 추가 -->
<button data-pop>뒤로가기</button>              <!-- 스택 제거 -->
<button data-goto="a_home">홈으로</button>      <!-- 현재 화면 교체 -->
<button data-tab="a_timeline">탭 전환</button>  <!-- 스택 리셋 + 이동 -->
<button data-toast="저장됐어요">토스트</button>  <!-- 토스트 메시지 -->
```
복잡한 로직(타이머, 조건 분기, 바텀시트)만 `onMount`에서 처리.

---

## 빌드 체크리스트 (완료 전 반드시 확인)

### 플로우 완결 (최우선)
- [ ] **모든 버튼이 어딘가로 이동**한다 — 막힌 버튼 없음
- [ ] **핵심 시나리오 1개 이상** 처음부터 끝까지 체험 가능
- [ ] 뒤로가기/탭 전환 작동
- [ ] 타이머·슬라이더·토스트 등 핵심 인터랙션 실제 동작

### 품질
- [ ] **유채색 0개** — 허용 팔레트 외 색상 없음
- [ ] `__refreshIcons()` innerHTML 교체 직후 호출
- [ ] A/B/C 화면 key에 각각 `a_` `b_` `c_` 접두사
- [ ] 더미 텍스트 = 서비스 맥락 한국어
- [ ] 한국어 카피 번역투·AI 티 없음 (korean-copy-guardrail 스킬 기준, §5 별도 pass + hanlint 훅)
- [ ] **플로우 뷰** 버튼 작동, FL_DATA 3개 안 모두 채워짐
- [ ] **시나리오 보기** 버튼 → `#sf-overlay` 인라인 오버레이 열기 (Cursor IDE 호환)

---

---

## 시나리오 플로우 ★ STEP 4 필수 (2중 출력)

**prototype.html 빌드 직후 두 가지를 동시에 처리한다:**

1. **prototype.html 내 `#sf-overlay`** — 인라인 embed (Cursor IDE 호환, "시나리오 보기" 버튼 동작)
2. **`scenario-flow.html`** — 별도 파일 (직접 브라우저 열기용, 변경 없이 계속 생성)

두 파일의 시나리오 내용은 동일해야 한다.

### 목적
시나리오 서사 중심의 정적 화면 플로우 문서. "사용자가 이 서비스를 어떻게 경험하는가"를
시나리오 단위로 읽을 수 있는 스펙 문서.

### 시나리오 추출 (interpretation.html 기반)
interpretation.html의 핵심 플로우에서 3~5개 시나리오 추출:
- 온보딩 / 복약 알림 정상 완료 / 쉐딩 예보 수신 / 경과 타임라인 확인 등

### prototype.html sf-overlay 내 화면 렌더링 (인라인 패턴)

sf-overlay HTML의 `.sf-device-inner`에 고유 id를 부여하고,
`_sfInitAll()`에서 `FLOW_A/B/C.screens[screenKey](MOCK)`를 직접 호출한다:

```js
function _sfInitAll(){
  const MOCK={push:()=>{},pop:()=>{},replace:()=>{},tab:()=>{},toast:()=>{},set:()=>{},get:()=>null,cur:()=>''};
  // sf-device-inner id → FLOW_.screens 키 (a_→FLOW_A, b_→FLOW_B, c_→FLOW_C)
  const MAP={'s01-home':'a_home', 's02-camera':'a_camera', ...};
  const FLOWS={a:FLOW_A,b:FLOW_B,c:FLOW_C};
  for(const [elId,screenKey] of Object.entries(MAP)){
    const el=document.getElementById(elId); if(!el)continue;
    const fn=FLOWS[screenKey[0]]?.screens[screenKey]; if(!fn)continue;
    el.innerHTML=fn(MOCK);
    el.querySelectorAll('[data-push],[data-pop],[data-tab],[data-replace]')
      .forEach(b=>b.style.pointerEvents='none');
  }
  if(window.__refreshIcons)window.__refreshIcons();
}
```

### scenario-flow.html 화면 렌더링 (별도 파일 패턴)

별도 파일은 FLOW_A 화면을 복사한 독립 SCREENS 객체를 사용한다:

```html
<div class="sf-device">
  <div class="sf-device-inner" id="{고유ID}"></div>
</div>
```
```js
const SCREENS = { 'a_home': () => `...같은 내용...` };
const MAP = {'s01-home':'a_home', ...};
window.addEventListener('DOMContentLoaded', () => {
  for(const [id, key] of Object.entries(MAP)){
    const el = document.getElementById(id);
    if(el && SCREENS[key]) el.innerHTML = SCREENS[key]();
  }
  window.__refreshIcons?.();
});
```

CSS (두 파일 공통 — sf-overlay는 이미 prototype.html style에 포함):
- `.sf-device` : width:200px; height:432px; border-radius:24px; border:6px solid #1a1a1a
- `.sf-device-inner` : width:390px; height:844px; transform:scale(0.512); transform-origin:0 0

### 분기 다이아몬드 HTML
```html
<div class="sf-diamond-wrap">
  <svg width="64" height="42"><polygon points="32,2 62,21 32,40 2,21" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/></svg>
  <div class="sf-diamond-label">분기 레이블</div>
</div>
```

### 완성 체크
- [ ] 시나리오 3~5개: 번호·제목·경로 한 줄·화면 열
- [ ] `#sf-overlay` 내 sf-device-inner id와 _sfInitAll MAP이 1:1 매칭
- [ ] 미니 화면이 FLOW_A/B/C 실제 화면 내용 표시
- [ ] 화살표·분기 다이아몬드 연결
- [ ] 모노크롬 준수, `__refreshIcons()` 호출

---

## 완료 조건

- `prototype.html` 저장 완료 — A/B/C 탭 전환, 핵심 플로우 체험 가능
- `scenario-flow.html` 저장 완료 — 시나리오 3~5개, 미니 화면 렌더
- 플로우 보기 버튼 → 해당 안의 화면 맵 확인 가능
- **원본 기획안 대비 전체 변경/추가/제안 내역 종합 표 포함** (STEP 0~3에서 쌓인 내역 + STEP 4 자체 추가분)
- 사용자에게 두 파일 경로 + 각 안 주요 플로우 요약 전달
