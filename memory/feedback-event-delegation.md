---
name: feedback-event-delegation
description: shell.html에서 인라인 onclick="app.xxx()" 대신 data 속성 기반 이벤트 위임을 써야 한다
metadata:
  type: feedback
---

data-push/pop/toast/reset 속성 + rootEl.onclick 위임 패턴이 확정된 표준이다.

**Why:** createMobileApp 팩토리의 `app` 객체는 클로저 내부 변수라 전역 스코프에서 접근 불가. 인라인 `onclick="app.push('screen')"` 은 클릭해도 아무 동작 안 함.

**How to apply:** 화면 HTML 문자열에서 네비게이션/액션이 필요한 버튼에는 반드시 아래 속성 사용:
- `data-push="screenKey"` → app.push(key)
- `data-pop` → app.pop()
- `data-toast="메시지"` → app.toast(msg)
- `data-reset` → app.reset()

순수 DOM 시각 토글(칩 선택 등)은 `this.style.xxx` 인라인 onclick 사용 가능 (app 참조 없으므로).
