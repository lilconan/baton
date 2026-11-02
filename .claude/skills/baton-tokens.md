# baton-tokens — 와이어프레임 디자인 토큰 & 컴포넌트 규칙

## ★ 모노크롬 전용 — 유채색 금지

와이어프레임은 레이아웃·플로우 검증 도구다. 어떤 유채색도 사용하지 않는다.
CLAUDE.md의 "절대 규칙 1"을 항상 따른다.

---

## 확정 스택 (단일 HTML, 빌드 없음)

```html
<!-- Tailwind Play CDN v4 -->
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

<!-- Lucide 아이콘 (ESM) -->
<script type="module">
  import { createIcons, icons } from 'https://cdn.jsdelivr.net/npm/lucide@latest/dist/esm/lucide.js';
  window.__refreshIcons = () => createIcons({ icons });
  window.__refreshIcons(); // 모듈은 deferred 실행이라 DOM 파싱 후 호출됨 — DOMContentLoaded 불필요
</script>

<!-- Pretendard 폰트 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@latest/dist/web/static/pretendard.min.css">
```

> innerHTML 교체 시마다 반드시 `window.__refreshIcons()` 호출 — 안 하면 Lucide 아이콘 빈 칸.

---

## 모노크롬 팔레트 (허용 목록 — 이것만)

```css
<style type="text/tailwindcss">
@theme {
  /* ─── 모노크롬 팔레트 ─── */
  --color-wf-black:  #1a1a1a;   /* Primary 텍스트, Primary 버튼 */
  --color-wf-dark:   #333333;   /* 진한 회색 */
  --color-wf-mid:    #555555;   /* Secondary 텍스트 */
  --color-wf-muted:  #888888;   /* Muted, 비활성 */
  --color-wf-faint:  #aaaaaa;   /* 더 옅은 회색 */
  --color-wf-light:  #cccccc;   /* 비활성 테두리 */
  --color-wf-line:   #d8d8d8;   /* 구분선, 테두리 */
  --color-wf-divid:  #ebebeb;   /* 밝은 구분선 */
  --color-wf-surf:   #f4f4f4;   /* 배경 */
  --color-wf-white:  #ffffff;   /* 흰 배경 */

  /* ─── 타이포 ─── */
  --font-sans: "Pretendard", -apple-system, system-ui, sans-serif;
}
</style>
```

**절대 정의하지 않는 것**: brand color, accent color, primary color 등 유채색 토큰.

---

## 타이포 스케일

| 역할 | 클래스 | 실제 값 |
|---|---|---|
| 타이틀 | `text-xl font-bold` | 20px, 700 |
| 섹션 헤더 | `text-base font-semibold` | 16px, 600 |
| 본문 | `text-sm` | 14px, 400 |
| 보조 | `text-xs` | 12px, 400 |

색상: 기본 `#1a1a1a`, 보조 `#555`, Muted `#888`, 비활성 `#aaa`

---

## 컴포넌트 정의 (모노크롬)

### StatusBar
```html
<div style="height:36px;display:flex;align-items:center;justify-content:space-between;padding:4px 20px 0;flex-shrink:0">
  <span style="font:600 12px Pretendard;color:#1a1a1a">9:41</span>
  <div style="display:flex;gap:4px;align-items:center">
    <i data-lucide="signal" style="width:13px;height:13px;color:#1a1a1a"></i>
    <i data-lucide="battery-full" style="width:13px;height:13px;color:#1a1a1a"></i>
  </div>
</div>
```

### AppBar
```html
<div style="height:50px;display:flex;align-items:center;padding:0 8px;border-bottom:1px solid #ebebeb;flex-shrink:0">
  <!-- 뒤로가기 버튼 (있을 때) -->
  <button class="back-btn" style="width:44px;height:44px;display:flex;align-items:center;justify-content:center;border:none;background:transparent;cursor:pointer">
    <i data-lucide="chevron-left" style="width:22px;height:22px;color:#1a1a1a"></i>
  </button>
  <span style="flex:1;font:700 17px Pretendard;color:#1a1a1a;text-align:center">타이틀</span>
  <div style="width:44px"></div>
</div>
```

### Button Primary
```html
<button style="width:100%;height:52px;border-radius:12px;border:none;background:#1a1a1a;color:#fff;font:700 16px Pretendard;cursor:pointer">
  레이블
</button>
```

### Button Outline
```html
<button style="width:100%;height:52px;border-radius:12px;border:1.5px solid #1a1a1a;background:transparent;color:#1a1a1a;font:600 16px Pretendard;cursor:pointer">
  레이블
</button>
```

### Button Ghost
```html
<button style="height:40px;padding:0 16px;border-radius:8px;border:1px solid #d8d8d8;background:transparent;color:#555;font:500 13px Pretendard;cursor:pointer">
  레이블
</button>
```

### Input
```html
<!-- 기본 -->
<div style="border:1.5px solid #d8d8d8;border-radius:12px;padding:14px 16px;background:#fff;font:400 15px Pretendard;color:#1a1a1a">
  플레이스홀더 또는 값
</div>

<!-- 포커스 (강조) — border #1a1a1a 로 변경, 파란색 금지 -->
<div style="border:1.5px solid #1a1a1a;border-radius:12px;padding:14px 16px;background:#fff;font:400 15px Pretendard;color:#1a1a1a">
  포커스 상태
</div>
```

### Chip
```html
<!-- 기본 -->
<button style="padding:8px 16px;border-radius:100px;border:1px solid #d8d8d8;background:#fff;color:#555;font:500 13px Pretendard;cursor:pointer">
  칩 레이블
</button>

<!-- 선택됨 -->
<button style="padding:8px 16px;border-radius:100px;border:none;background:#1a1a1a;color:#fff;font:600 13px Pretendard;cursor:pointer">
  칩 레이블
</button>
```

### Card
```html
<div style="background:#fff;border:1px solid #ebebeb;border-radius:16px;padding:16px">
  <!-- 카드 내용 -->
</div>
```

### ListRow
```html
<div style="display:flex;align-items:center;padding:14px 20px;background:#fff;border-bottom:1px solid #ebebeb;gap:12px;cursor:pointer">
  <!-- 아이콘 플레이스홀더 -->
  <div style="width:40px;height:40px;background:#f4f4f4;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0">
    <i data-lucide="circle" style="width:18px;height:18px;color:#888"></i>
  </div>
  <div style="flex:1">
    <div style="font:500 15px Pretendard;color:#1a1a1a">항목 제목</div>
    <div style="font:400 12px Pretendard;color:#888;margin-top:2px">보조 텍스트</div>
  </div>
  <i data-lucide="chevron-right" style="width:14px;height:14px;color:#ccc"></i>
</div>
```

### TabBar
```html
<div style="height:64px;background:#fff;border-top:1.5px solid #ebebeb;display:flex;padding-bottom:8px;flex-shrink:0">
  <!-- active 탭 -->
  <button style="flex:1;border:none;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;padding-top:8px">
    <i data-lucide="home" style="width:20px;height:20px;color:#1a1a1a"></i>
    <span style="font:700 10px Pretendard;color:#1a1a1a">홈</span>
  </button>
  <!-- inactive 탭 -->
  <button style="flex:1;border:none;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;padding-top:8px">
    <i data-lucide="user" style="width:20px;height:20px;color:#aaa"></i>
    <span style="font:500 10px Pretendard;color:#aaa">프로필</span>
  </button>
</div>
```

### BottomSheet
```html
<!-- backdrop -->
<div style="position:absolute;inset:0;background:rgba(0,0,0,0.45);z-index:60;display:flex;align-items:flex-end">
  <div style="background:#fff;border-radius:20px 20px 0 0;width:100%;padding:8px 20px 36px;animation:sheetUp .25s ease-out">
    <!-- 드래그 핸들 -->
    <div style="width:36px;height:4px;background:#d8d8d8;border-radius:2px;margin:12px auto 20px"></div>
    <!-- 시트 내용 -->
  </div>
</div>
```

### Toast (2.2초 자동)
```javascript
function showToast(rootEl, msg) {
  const t = document.createElement('div');
  t.style.cssText = 'position:absolute;bottom:80px;left:50%;transform:translateX(-50%);background:#1a1a1a;color:#fff;font:500 13px Pretendard;padding:10px 20px;border-radius:100px;z-index:99;white-space:nowrap;opacity:0;transition:opacity .18s';
  t.textContent = msg;
  rootEl.appendChild(t);
  requestAnimationFrame(() => t.style.opacity = 1);
  setTimeout(() => { t.style.opacity = 0; setTimeout(() => t.remove(), 220); }, 2200);
}
```

### EmptyState (빈 상태)
```html
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 24px;text-align:center">
  <div style="width:64px;height:64px;background:#f4f4f4;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:16px">
    <i data-lucide="inbox" style="width:28px;height:28px;color:#aaa"></i>
  </div>
  <div style="font:600 16px Pretendard;color:#1a1a1a;margin-bottom:6px">아직 내용이 없어요</div>
  <div style="font:400 14px Pretendard;color:#888">설명 텍스트</div>
</div>
```

### Skeleton (로딩 상태)
```html
<style>
@keyframes shimmer { from{background-position:200% 0} to{background-position:-200% 0} }
.skeleton { background:linear-gradient(90deg,#ebebeb 25%,#f4f4f4 50%,#ebebeb 75%);
  background-size:200% 100%; animation:shimmer 1.4s infinite; border-radius:6px; }
</style>

<div class="skeleton" style="height:18px;width:60%;margin-bottom:8px"></div>
<div class="skeleton" style="height:14px;width:80%"></div>
```

---

## 이미지 플레이스홀더

실사 이미지 사용 금지. Lucide 글리프 + 회색 박스로:

```html
<!-- 일반 이미지 -->
<div style="background:#f4f4f4;display:flex;align-items:center;justify-content:center;color:#aaa;border-radius:8px">
  <i data-lucide="image" style="width:24px;height:24px;color:#ccc"></i>
</div>

<!-- 아바타 / 프로필 -->
<div style="background:#ebebeb;border-radius:50%;display:flex;align-items:center;justify-content:center">
  <i data-lucide="user" style="width:20px;height:20px;color:#888"></i>
</div>
```

---

## "있어 보이게" 체크리스트

- [ ] 유채색 없음 — #1a1a1a/#333333/#555555/#888888/#aaaaaa/#cccccc/#d8d8d8/#ebebeb/#f4f4f4/#ffffff 이외 색상 없음
- [ ] 더미 데이터가 서비스 맥락에 맞는 한국어 (제목1, Lorem 금지)
- [ ] 간격이 일관적 (8pt 배수)
- [ ] 로딩 스켈레톤 최소 1개
- [ ] 빈 상태(EmptyState) 최소 1개
- [ ] 화면 전환 슬라이드 트랜지션
- [ ] 터치 타깃 ≥ 44px

---

## 접근성·터치

포커스 가능한 요소는 실제 클릭 작동 보장. 최소 터치 타깃 44×44px.
