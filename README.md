# Baton — Claude Code 에이전트 패키지

기획서 한 장으로 풀 플로우 프로토타입(prototype.html) + 시나리오 플로우 문서(scenario-flow.html)를 자동 생성하는 Claude Code 에이전트 시스템.

---

## 설치

### 원격 설치 (GitHub에서 직접)

```bash
curl -fsSL https://raw.githubusercontent.com/moonbo-debug/baton/main/install.sh | bash
```

### 로컬 설치 (레포 clone 후)

```bash
git clone https://github.com/moonbo-debug/baton.git
bash baton/install.sh
```

설치 위치: `~/.claude/agents/` + `~/.claude/skills/`

---

## 프로젝트에 적용

새 프로젝트 루트에 CLAUDE.md와 PROCESS.md를 복사하면 Claude Code가 자동으로 규칙을 적용합니다.
`PROCESS.md`는 STEP 0 입력 게이트가 참조하는 필수 파일이므로 함께 복사해야 합니다.

```bash
BASE=https://raw.githubusercontent.com/moonbo-debug/baton/main
curl -fsSL $BASE/CLAUDE.md  -o CLAUDE.md
curl -fsSL $BASE/PROCESS.md -o PROCESS.md
```

---

## 워크플로우

```
입력 (아이디어 한 줄 ~ 완성된 기획서)
  ↓
STEP 0: docs/{프로젝트}/ 기획 문서       → 컨펌   ★생략 금지
        (FIXED/OPEN 분해 + 필수기능 근거 추적)
  ↓
STEP 2: interpretation.html  (기획 해석 리포트)       → 컨펌
  ↓
STEP 3: screens-proposal.html (A/B/C 레이아웃 3안)    → 안 선택
  ↓
STEP 4: prototype.html        (A/B/C 탭 통합 프로토타입)
        scenario-flow.html    (시나리오 기반 플로우 문서)
```

**입력이 아무리 상세해도 STEP 0을 건너뛰지 않습니다.** 기획서가 자세하다는 것은
검증되지 않은 결론이 많다는 뜻이므로, 와이어프레임을 그리기 전에 먼저
`docs/{프로젝트}/`에 기획 문서를 남깁니다. → `PROCESS.md` §2, R9

---

## 포함 파일

| 파일 | 역할 |
|---|---|
| `.claude/agents/baton.md` | 오케스트레이터 (STEP 0→2→3→4 관리) |
| `.claude/agents/baton-interpreter.md` | STEP 2: 기획서 해석 |
| `.claude/agents/baton-designer.md` | STEP 3: A/B/C 레이아웃 설계 |
| `.claude/agents/baton-builder.md` | STEP 4: 프로토타입 빌드 |
| `.claude/skills/baton-tokens.md` | 모노크롬 팔레트·컴포넌트 정의 |
| `.claude/skills/baton-shell.md` | createMobileApp + 플로우뷰 JS |
| `CLAUDE.md` | 프로젝트 규칙 (설치 시 템플릿으로 복사) |
| `PROCESS.md` | 기획 프로세스 표준 — 더블 다이아몬드, 출처 등급, FIXED 처리 (**STEP 0 필수 참조**) |
| `RUNBOOK.md` | 단계별 프롬프트 모음 (사람이 읽는 것) |
| `START_HERE.md` | 온보딩 가이드 |
| `CONTEXT.md` | 프로젝트 컨텍스트 |
| `shell.html` | 온다 레퍼런스 구현체 (모노크롬 참고) |
| `docs/{프로젝트}/` | 기획서 원본 |
| `output/{프로젝트}/` | STEP 2~4 산출물 |
| `publish.sh` | 이 레포로 발행 (git subtree push) |

---

## 출력 규칙

- **모노크롬 전용** — 유채색 없음, #1a1a1a ~ #ffffff
- **단일 HTML** — 빌드 없음, CDN만 (Tailwind v4 + Lucide + Pretendard)
- **A/B/C 탭 통합** — 한 파일에 3개 안 탭 전환
