# baton-shell — 공유 JS 유틸리티 (createMobileApp + 플로우뷰)

> **역할:** 이 파일은 JS 유틸리티 라이브러리다. 레이아웃 셸(HTML 골격)은 **baton-builder.md** 참고.
> **모노크롬 팔레트:** baton-tokens.md 준수. 유채색 일체 금지.

포함 내용:
- `createMobileApp` 팩토리 (라우팅 격리)
- 플로우 뷰 CSS + HTML + JS 전체
- 슬라이드 애니메이션 CSS

## 모바일앱 팩토리 (라우팅 격리 핵심)

### ★ data-attribute 라우팅 방식 (권장)
HTML에서 직접 라우팅 지시 — onMount에서 onclick 바인딩 불필요:
```html
<button data-push="screen-key">다음 화면으로</button>   <!-- 스택 추가 -->
<button data-pop>뒤로가기</button>                      <!-- 스택 제거 -->
<button data-goto="screen-key">교체 이동</button>       <!-- 현재 화면 교체 -->
<button data-tab="tab-key">탭 전환</button>             <!-- 스택 리셋 후 이동 -->
<button data-toast="저장됐어요">토스트</button>          <!-- 토스트 메시지 -->
```
복잡한 로직(타이머, 상태 계산, 조건 분기)만 `onMount`에서 추가 처리.

```js
function createMobileApp(rootEl, flow){
  // flow = { initial, screens:{key:(app)=>htmlString}, onMount:{key:(rootEl,app)=>{}} }
  const state = { stack:[flow.initial], data:{} };
  const app = {
    push(k)   { _cl(app); state.stack.push(k);                    _render('in'); },
    replace(k){ _cl(app); state.stack[state.stack.length-1]=k;    _render('in'); },
    pop()     { if(state.stack.length>1){ _cl(app); state.stack.pop(); _render('back'); } },
    tab(k)    { _cl(app); state.stack=[k];                        _render('in'); },
    set(k,v)  { state.data[k]=v; },
    get(k)    { return state.data[k]; },
    cur()     { return state.stack[state.stack.length-1]; },
    toast(msg){
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
    wrap.innerHTML = flow.screens[key](app);
    rootEl.querySelectorAll(':scope>div').forEach(n=>n.remove());
    rootEl.appendChild(wrap);
    window.__refreshIcons?.();  // Lucide 재렌더 필수

    // ★ data-attribute 자동 바인딩
    wrap.querySelectorAll('[data-push]').forEach(el=>el.onclick=()=>app.push(el.dataset.push));
    wrap.querySelectorAll('[data-pop]').forEach(el=>el.onclick=()=>app.pop());
    wrap.querySelectorAll('[data-goto]').forEach(el=>el.onclick=()=>app.replace(el.dataset.goto));
    wrap.querySelectorAll('[data-tab]').forEach(el=>el.onclick=()=>app.tab(el.dataset.tab));
    wrap.querySelectorAll('[data-toast]').forEach(el=>el.onclick=()=>app.toast(el.dataset.toast));

    flow.onMount?.[key]?.(wrap, app);
  }
  _render('in');
  return app;
}
```
- 각 프레임이 자기 `state.stack`을 가지므로 A의 클릭이 B/C에 영향 없음.
- 이벤트는 `wrap.querySelector` 범위 안에서만 바인딩. 전역 id 금지.
- 슬라이드 CSS: `.slide-in{animation:slideIn .2s ease-out}` `.slide-back{animation:slideBack .2s ease-out}`

## 주의
- 전역 변수/전역 id 쓰지 말 것. 모든 상태는 팩토리 클로저 안에.
- 화면 전환은 reload 없이 innerHTML 교체. 슬라이드 트랜지션은 .scr 클래스로.
- innerHTML 교체 직후 반드시 __refreshIcons() — 안 하면 Lucide 아이콘이 빈 칸으로 남음.

---

## 플로우 뷰 (Flow View) 보일러플레이트 ★ STEP 4 필수

모든 prototype.html에 반드시 포함해야 한다.
각 frame-wrap 아래에 "플로우 보기" 버튼을 추가하고, body 끝에 오버레이 HTML을 삽입한다.

### 1. CSS (style 블록에 추가)
```css
/* ── 플로우 뷰 ── */
#flow-overlay{position:fixed;inset:0;background:#1a1a1a;z-index:9999;display:none}
#fl-header{position:absolute;top:0;left:0;right:0;height:52px;background:#1a1a1a;
  border-bottom:1px solid #333333;display:flex;align-items:center;padding:0 20px;gap:12px;z-index:10}
#fl-wrap{position:absolute;top:52px;left:0;right:0;bottom:40px;overflow:hidden;cursor:default}
#fl-canvas{position:absolute;top:0;left:0;transform-origin:0 0;will-change:transform}
.fl-frame{position:absolute;cursor:pointer}
.fl-label{font:600 13px/1 "Pretendard";color:#ccc;text-align:center;margin-bottom:8px;pointer-events:none;white-space:nowrap}
.fl-device{width:390px;height:844px;border-radius:28px;border:2px solid #555555;overflow:hidden;background:#fff;pointer-events:none;transition:border-color .2s,box-shadow .2s}
.fl-frame:hover .fl-device{border-color:#888}
.fl-frame.fl-active .fl-device{border:3px solid #fff;box-shadow:0 0 0 4px rgba(255,255,255,.15)}
.fl-frame.fl-nav .fl-device{animation:fl-pulse .7s ease-out}
@keyframes fl-pulse{0%{box-shadow:0 0 0 0 rgba(255,255,255,.55)}100%{box-shadow:0 0 0 24px rgba(255,255,255,0)}}
#fl-hint{position:absolute;bottom:0;left:0;right:0;height:40px;display:flex;align-items:center;
  justify-content:center;gap:24px;background:#1a1a1a;border-top:1px solid #333333;
  font:400 12px/1 "Pretendard";color:#555}
#fl-hint b{color:#888}
.fl-btn{background:none;border:1.5px solid #333;border-radius:7px;color:#888;font:500 12px/1 "Pretendard";padding:5px 12px;cursor:pointer}
.fl-btn:hover{border-color:#aaa;color:#fff}
#fl-zoom-pct{font:600 12px/1 "Pretendard";color:#888;min-width:38px;text-align:center}
.flow-open-btn{margin-top:10px;padding:6px 14px;border:1.5px solid #cccccc;border-radius:8px;
  background:#fff;font:500 12px/1 "Pretendard";color:#555;cursor:pointer;
  display:flex;align-items:center;gap:6px;justify-content:center}
.flow-open-btn:hover{background:#1a1a1a;color:#fff;border-color:#1a1a1a}
```

### 2. 셸 골격 (플로우 버튼 포함)
```html
<div class="frame-wrap">
  <div class="frame-label">A안 · 탭바 중심</div>
  <!-- 플로우 보기 버튼 — 단일 안은 openFlowView(), 복수 안은 openFlowView('a') -->
  <button class="flow-open-btn" onclick="openFlowView('a')">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="3" y="14" width="7" height="7"/><line x1="17.5" y1="17.5" x2="21" y2="21"/>
    </svg>
    플로우 보기
  </button>
  <div class="device"><div class="notch"></div><div class="screen" id="app-A"></div></div>
</div>
```

### 3. body 끝 오버레이 HTML
```html
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
    <span>핀치 투 줌 지원</span>
    <span><b>Esc</b>: 닫기</span>
  </div>
</div>
```

### 4. 플로우 데이터 구조 (에이전트가 화면마다 채운다)
```js
// x 간격 = SW(390) + 120 = 510, y 간격 = SH(844) + 120 = 964
// 음수 y 없도록 FL_OY로 오프셋 조정
const FL_OX = 100, FL_OY = 100;   // 음수 없으면 FL_OY=100으로 충분
const SW = 390, SH = 844;
const INIT_SCALE = 0.35;

const FL_POS = {
  'screen_key': { x: 0,   y: 0   },   // 1열 1행
  'screen_key2':{ x: 510, y: 0   },   // 1열 2행
  'screen_key3':{ x: 0,   y: 964 },   // 2열 1행 (분기)
};
const FL_LABEL = { 'screen_key': '화면 표시명', ... };
const FL_ARROWS = [
  ['from_key', 'to_key'],              // 단순 연결
  ['from_key', 'to_key', '레이블'],    // 레이블 있는 연결
];

// 복수 안(A/B/C)은 FL_DATA로 묶어서 관리
const FL_DATA = {
  a: { pos:{...}, label:{...}, arrows:[...], title:'A안 · 위저드형', initScreen:'a_splash' },
  b: { pos:{...}, label:{...}, arrows:[...], title:'B안 · 원페이지형', initScreen:'b_splash' },
};
```

### 5. 플로우 뷰 JS (전체 — script 블록에 포함)
```js
function flAbsPos(pos, id) {
  const p = pos[id];
  return p ? { x: p.x + FL_OX, y: p.y + FL_OY } : null;
}
let flT={x:0,y:0,scale:INIT_SCALE}, flFlowId=null, flActive='', flHistory=[];
let flSpace=false, flPan=false, flMouse=null, flPinchD=0;

function openFlowView(flowId) {
  // 단일 플로우 예시 버전. A/B/C 탭 통합 prototype.html에서는 이 버전을 쓰지 않고
  // baton-builder.md의 openFlowView(FL_DATA 다중 플로우 버전)를 쓴다.
  // 단일 안이면 flowId 없이 호출 가능. FL_DATA 또는 직접 FL_POS/FL_LABEL/FL_ARROWS 사용.
  const d = (typeof FL_DATA!=='undefined') ? FL_DATA[flowId]
          : { pos:FL_POS, label:FL_LABEL, arrows:FL_ARROWS, title:'플로우 맵', initScreen:Object.keys(FL_POS)[0] };
  flFlowId=flowId||''; flActive=d.initScreen; flHistory=[];
  document.getElementById('fl-title').textContent = d.title + '  —  플로우 맵';

  // mock app (화면 렌더용)
  const mock={get:()=>null,set:()=>{},push:()=>{},pop:()=>{},replace:()=>{},tab:()=>{},toast:()=>{},cur:()=>''};

  // 캔버스 크기 자동 계산
  const xs=Object.values(d.pos).map(p=>p.x+FL_OX), ys=Object.values(d.pos).map(p=>p.y+FL_OY);
  const cW=Math.max(...xs)+SW+FL_OX+100, cH=Math.max(...ys)+SH+FL_OY+100;

  // SVG 화살표
  let svg=`<svg style="position:absolute;top:0;left:0;width:${cW}px;height:${cH}px;overflow:visible;pointer-events:none">
    <defs><marker id="flarr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <polygon points="0 0,10 4,0 8" fill="rgba(255,255,255,0.75)"/></marker></defs>`;
  for(const [from,to,lbl] of d.arrows){
    const fp=flAbsPos(d.pos,from), tp=flAbsPos(d.pos,to);
    if(!fp||!tp) continue;
    const fcx=fp.x+SW/2,fcy=fp.y+SH/2,tcx=tp.x+SW/2,tcy=tp.y+SH/2;
    const dx=tcx-fcx,dy=tcy-fcy,adx=Math.abs(dx),ady=Math.abs(dy);
    let fx,fy,tx,ty,horiz;
    if(adx>ady*1.2){
      horiz=true;
      if(dx>0){fx=fp.x+SW+8;fy=fcy;tx=tp.x-8;ty=tcy}
      else{fx=fp.x-8;fy=fcy;tx=tp.x+SW+8;ty=tcy}
    } else {
      horiz=false;
      if(dy>0){fx=fcx;fy=fp.y+SH+18;tx=tcx;ty=tp.y-18}
      else{fx=fcx;fy=fp.y-18;tx=tcx;ty=tp.y+SH+18}
    }
    const hw=Math.abs(tx-fx)/2;
    const path=horiz?`M${fx},${fy} C${fx+hw},${fy} ${tx-hw},${ty} ${tx},${ty}`
                    :`M${fx},${fy} C${fx},${(fy+ty)/2} ${tx},${(fy+ty)/2} ${tx},${ty}`;
    svg+=`<path d="${path}" fill="none" stroke="rgba(255,255,255,0.75)" stroke-width="2" marker-end="url(#flarr)"/>`;
    if(lbl) svg+=`<text x="${(fx+tx)/2}" y="${(fy+ty)/2-8}" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.55)" font-family="Pretendard,sans-serif">${lbl}</text>`;
  }
  svg+=`</svg>`;

  // 스크린 프레임 렌더
  // FLOW_SRC: 에이전트가 각 안의 screens 객체를 반환하는 함수로 정의한다.
  // 예) const FLOW_SRC = { a: ()=>FLOW_A.screens, b: ()=>FLOW_B.screens }
  let frames='';
  const screens = (typeof FLOW_SRC!=='undefined'&&FLOW_SRC[flowId]) ? FLOW_SRC[flowId]()
                : (typeof FLOW!=='undefined') ? FLOW.screens : {};
  for(const [sid] of Object.entries(d.pos)){
    const p=flAbsPos(d.pos,sid);
    const html=screens[sid]?screens[sid](mock):'';
    frames+=`<div class="fl-frame ${sid===flActive?'fl-active':''}" data-sid="${sid}"
      style="left:${p.x}px;top:${p.y}px;width:${SW}px">
      <div class="fl-label">${d.label[sid]||sid}</div>
      <div class="fl-device">${html}</div>
    </div>`;
  }
  const canvas=document.getElementById('fl-canvas');
  canvas.style.width=cW+'px'; canvas.style.height=cH+'px';
  canvas.innerHTML=svg+frames;
  window.__refreshIcons?.();
  canvas.onclick=(e)=>{
    if(e.target.closest('[data-pop]')){flBack();return;}
    const dest=[e.target.closest('[data-push]')?.dataset.push,
                e.target.closest('[data-goto]')?.dataset.goto,
                e.target.closest('.fl-frame')?.dataset.sid]
      .find(k=>k&&d.pos[k]);
    if(dest) flGoTo(d.pos,dest);
  };
  document.getElementById('flow-overlay').style.display='block';
  flT={x:0,y:0,scale:INIT_SCALE}; flApply();
  setTimeout(()=>flCenterOn(d.pos,d.initScreen,false),60);
}
function closeFlowView(){document.getElementById('flow-overlay').style.display='none';}
function flBack(){if(flHistory.length>0)flGoTo(null,flHistory.pop(),false);}
function flGoTo(pos,sid,push=true){
  const d=(typeof FL_DATA!=='undefined')&&flFlowId ? FL_DATA[flFlowId] : {pos:FL_POS||pos};
  if(!d.pos[sid]) return;
  if(push&&flActive&&flActive!==sid) flHistory.push(flActive);
  flActive=sid;
  document.querySelectorAll('.fl-frame').forEach(f=>{
    const t=f.dataset.sid===sid;
    f.classList.toggle('fl-active',t);
    if(t){f.classList.remove('fl-nav');void f.offsetWidth;f.classList.add('fl-nav');setTimeout(()=>f.classList.remove('fl-nav'),750);}
  });
  flCenterOn(d.pos,sid,true);
}
function flCenterOn(pos,sid,anim){
  const d=(typeof FL_DATA!=='undefined')&&flFlowId ? FL_DATA[flFlowId].pos : (pos||FL_POS);
  const p=flAbsPos(d,sid); if(!p) return;
  const wrap=document.getElementById('fl-wrap');
  const nx=wrap.clientWidth/2-(p.x+SW/2)*flT.scale, ny=wrap.clientHeight/2-(p.y+SH/2)*flT.scale;
  const canvas=document.getElementById('fl-canvas');
  if(anim){canvas.style.transition='transform .48s cubic-bezier(.4,0,.2,1)';setTimeout(()=>canvas.style.transition='',520);}
  flT.x=nx; flT.y=ny; flApply();
}
function flApply(){
  const c=document.getElementById('fl-canvas'); if(!c) return;
  c.style.transform=`translate(${flT.x}px,${flT.y}px) scale(${flT.scale})`;
  document.getElementById('fl-zoom-pct').textContent=Math.round(flT.scale*100)+'%';
}
function flZoomAt(cx,cy,f){
  const ns=Math.max(0.12,Math.min(2.5,flT.scale*f)),r=ns/flT.scale;
  flT.x=cx-r*(cx-flT.x); flT.y=cy-r*(cy-flT.y); flT.scale=ns; flApply();
}
function flZoom(f){const w=document.getElementById('fl-wrap');if(w)flZoomAt(w.clientWidth/2,w.clientHeight/2,f);}
function flFit(){
  const wrap=document.getElementById('fl-wrap'); if(!wrap) return;
  const d=(typeof FL_DATA!=='undefined')&&flFlowId ? FL_DATA[flFlowId].pos : FL_POS;
  const xs=Object.values(d).map(p=>p.x+FL_OX), ys=Object.values(d).map(p=>p.y+FL_OY);
  const minX=Math.min(...xs),maxX=Math.max(...xs)+SW,minY=Math.min(...ys),maxY=Math.max(...ys)+SH;
  const vw=wrap.clientWidth-80,vh=wrap.clientHeight-80;
  flT.scale=Math.min(2.5,Math.min(vw/(maxX-minX),vh/(maxY-minY)));
  flT.x=(wrap.clientWidth-(maxX-minX)*flT.scale)/2-minX*flT.scale;
  flT.y=(wrap.clientHeight-(maxY-minY)*flT.scale)/2-minY*flT.scale;
  flApply();
}
// 키보드
document.addEventListener('keydown',e=>{
  if(document.getElementById('flow-overlay')?.style.display==='none') return;
  if(e.code==='Space'&&!e.target.matches('input,textarea')){e.preventDefault();flSpace=true;const w=document.getElementById('fl-wrap');if(w)w.style.cursor='grab';}
  if(e.ctrlKey&&(e.key==='='||e.key==='+')){e.preventDefault();flZoom(1.25);}
  if(e.ctrlKey&&e.key==='-'){e.preventDefault();flZoom(0.8);}
  if(e.key==='0'&&e.ctrlKey){e.preventDefault();flFit();}
  if(e.key==='Escape') closeFlowView();
});
document.addEventListener('keyup',e=>{if(e.code==='Space'){flSpace=false;const w=document.getElementById('fl-wrap');if(w&&!flPan)w.style.cursor='default';}});
// 마우스 팬
document.addEventListener('mousedown',e=>{const w=document.getElementById('fl-wrap');if(!w?.contains(e.target))return;if(flSpace||e.button===1){e.preventDefault();flPan=true;flMouse={x:e.clientX,y:e.clientY};w.style.cursor='grabbing';}});
document.addEventListener('mousemove',e=>{if(!flPan||!flMouse)return;flT.x+=e.clientX-flMouse.x;flT.y+=e.clientY-flMouse.y;flMouse={x:e.clientX,y:e.clientY};flApply();});
document.addEventListener('mouseup',()=>{if(flPan){flPan=false;const w=document.getElementById('fl-wrap');if(w)w.style.cursor=flSpace?'grab':'default';}});
// 휠
document.addEventListener('wheel',e=>{const w=document.getElementById('fl-wrap');if(!w?.contains(e.target))return;if(e.ctrlKey){e.preventDefault();const r=w.getBoundingClientRect();flZoomAt(e.clientX-r.left,e.clientY-r.top,e.deltaY>0?0.9:1.1);}else{e.preventDefault();flT.x-=e.deltaX*1.2;flT.y-=e.deltaY*1.2;flApply();}},{passive:false});
// 터치 핀치
document.addEventListener('touchstart',e=>{if(!document.getElementById('fl-wrap')?.contains(e.target))return;if(e.touches.length===2)flPinchD=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);},{passive:false});
document.addEventListener('touchmove',e=>{const w=document.getElementById('fl-wrap');if(!w?.contains(e.target)||e.touches.length!==2)return;e.preventDefault();const d2=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);const cx=(e.touches[0].clientX+e.touches[1].clientX)/2,cy=(e.touches[0].clientY+e.touches[1].clientY)/2;const r=w.getBoundingClientRect();if(flPinchD>0)flZoomAt(cx-r.left,cy-r.top,d2/flPinchD);flPinchD=d2;},{passive:false});
```
