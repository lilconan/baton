# BACKLOG

> 단일 진실 소스 (Single Source of Truth)
>
> 마지막 업데이트: (자동 갱신)
>
> **EPIC 기반 워크플로우**: 백로그 → EPIC → User Story → Acceptance Criteria

## Project Vision

> (PO 세션에서 설정됨)

## Goals & OKR

| # | Objective | Key Results | 상태 | Phase | 관련 백로그 |
|---|-----------|-------------|------|-------|-----------|

## Phase Gate Log

| Phase | 목표 | 시작일 | 종료일 | Sprints | Gate 결과 | 비고 |
|-------|------|--------|--------|---------|----------|------|

## Current Sprint

> Sprint 미설정. `/ha:po`로 첫 Sprint를 구성하세요.

## Sprint History (최근 3회)

> Sprint Close 시 자동 갱신됩니다. 4회차 이전은 `docs/archive/sprint-archive-YYYY.md`로 이관됩니다.
> Automatically updated on Sprint Close. Sprints older than 3 are archived to `docs/archive/sprint-archive-YYYY.md`.

<!-- 예시 형식 / Example format:
### S1 (P1) — 2026-01-15 완료
> Goal: Sprint Goal 설명
> 완료: 5건 | AC: 20 | 소요: ~3h
> 주요 성과: 주요 달성 내용 요약
-->

---

## Velocity Log

| Sprint | 완료 | AC | 복잡도 합 | 소요 시간 | QA 회전 | OKR 정렬 | 비고 |
|--------|------|-----|----------|----------|---------|---------|------|

---

## Inbox

> 새 아이디어, 피드백, 버그 리포트가 여기에 쌓입니다.
> - `/ha:idea <설명>` - 추가 후 자동으로 `/ha:po` 체이닝
> - `/ha:po B-XXX` - 특정 항목 분석 (EPIC/Story/AC 생성 → Ready 전환)

| ID | 제목 | 상태 | 임팩트 | 노력 | 우선순위 | 의존성 | 문서 | 담당 | 생성일 |
|----|------|------|--------|------|----------|--------|------|------|--------|

---

## Ready

> 작업 준비 완료, EPIC/Stories/AC 문서 완성됨
> - `/ha:pick` - Ready 목록에서 직접 선택하여 시작
> - `/ha:next` - AI가 최우선 항목 자동 선택 + 실행

| ID | 제목 | 우선순위 | Phase | Sprint | EPIC | Stories | AC | 예상공수 | 선행 | 문서 |
|----|------|----------|-------|--------|------|---------|-----|----------|------|------|

---

## In Progress

> 현재 진행 중인 작업
> 워커 세션에서 개발 중, AC 기준으로 완료 판단

| ID | 제목 | 상태 | Sprint | EPIC | Stories | AC 진행 | 담당 | 시작일 |
|----|------|------|--------|------|---------|--------|------|--------|


---

## Done (최근 20개)

> 완료된 작업
> `/ha:done` 명령어로 완료 처리
> 20개 초과 시 오래된 항목은 `docs/archive/backlog-archive-YYYY.md`로 자동 이관

| ID | 제목 | Sprint | 완료일 | 담당 | 요약 |
|----|------|--------|--------|------|------|

---

## Backlog Channels

### VoC (사용자/시장 피드백)

| 출처 | 내용 | 등록일 | 상태 | 연결된 백로그 |
|------|------|--------|------|-------------|

### Tech Debt (기술부채)

| 출처 | 내용 | 심각도 | 상태 | 연결된 백로그 |
|------|------|--------|------|-------------|

### Stakeholder (경영진/외부 요구)

| 출처 | 내용 | 긴급도 | 상태 | 연결된 백로그 |
|------|------|--------|------|-------------|

---

## 참고

### 상태 흐름

```
Inbox → Ready → In Progress → Done
  │       │                     │
  │       │                     └─ Sprint Close → Phase Gate 체크
  │       └─ /ha:pick, /ha:next
  └─ /ha:idea → /ha:po 자동 체이닝
```

### 우선순위 계산
- **P1**: 임팩트 H + 노력 L/M (빠르게 큰 효과)
- **P2**: 임팩트 H + 노력 H 또는 임팩트 M + 노력 L/M
- **P3**: 임팩트 L 또는 임팩트 M + 노력 H

### EPIC 기반 계층 구조

```
백로그 (B-XXX)
  └── EPIC (기능 그룹)
        └── User Story (사용자 관점)
              └── Acceptance Criteria (완료 기준)
```

### 핵심 명령어

| 명령어 | 설명 | 언제 쓰나요? | 체이닝 |
|--------|------|-------------|--------|
| `/ha:idea <설명>` | Inbox에 새 아이디어 추가 | 아이디어가 떠올랐을 때 | → `/ha:po` 자동 |
| `/ha:po` | 상황 인식형 PO 에이전트. Goal/Phase 설정, Phase Gate 리뷰, 백로그 분석을 자동 판별 | 프로젝트 초기 설정, Inbox 정리, Phase 전환 시 | 조건부 → `/ha:okr`, `/ha:health` |
| `/ha:next` | AI가 Ready에서 최우선 항목 자동 선택 → Scout → 구현 → AC 검증 → 완료 | 뭘 할지 고민할 때. AI에게 맡기기 | → `/ha:done` 자동 |
| `/ha:pick` | Ready에서 직접 골라서 구현 시작. Scout → 구현 → AC 검증 → 완료 | 특정 작업을 직접 선택하고 싶을 때 | → `/ha:done` 자동 |
| `/ha:done <요약>` | 진행 중 작업 완료 처리. AC 자동 검증 → Done 이동 + Git 커밋 | 작업 끝났을 때 (pick/next에서 자동 호출됨) | 자동 호출됨 |
| `/ha:auto-loop [N]` | Ready 작업을 N개 자동 순차 처리. Build/QA/Code 3모드 | 자리 비울 때. 여러 작업 자동 처리 | 내부 pick → done 반복 |
| `/ha:night-shift [시간]` | 시간 기반 자율 루프. 지정 시간 동안 반복 + 마무리 | 밤새 작업 맡길 때 | 내부 pick → done 반복 |
| `/ha:wrap` | 세션 분석 + 학습 추출 + 워크플로우 강화 | 세션 마무리 시 | - |

### 전략/자문 명령어

| 명령어 | 설명 | 언제 쓰나요? | 모드 |
|--------|------|-------------|------|
| `/ha:counsel` | 시니어 전략 자문. 프로젝트 상태 자동 분석 후 최적 모드 선택 | 방향이 불확실할 때 | 자동 감지 |
| `/ha:counsel --strategic` | DO/STOP/WATCH 전략 가이드 | 뭘 해야 할지 / 뭘 멈춰야 할지 | Strategic |
| `/ha:counsel --stuck` | 막힌 문제 돌파구 제시 | 문제 해결이 안 될 때 | Stuck |
| `/ha:counsel --council` | 4관점 독립 분석 → 교차 검증 → 종합 판정 | 중대한 기술/아키텍처 결정 | Council |
| `/ha:counsel --brainstorm <주제>` | 코드 전 설계. 6단계 체크리스트 + YAGNI 검증 | 새 기능 설계 시 | Brainstorm |
| `/ha:counsel --focus` | 우선순위 혼란 시 하나에 집중 | 할 일이 너무 많을 때 | Focus |
| `/ha:counsel <자유 텍스트>` | 소크라테스식 3라운드 심층 대화 | 구체적 고민이 있을 때 | Interactive |

### 관찰/분석 명령어

| 명령어 | 설명 | 언제 쓰나요? |
|--------|------|-------------|
| `/ha:sprint` | 스프린트 진행률 대시보드 | 현재 진행 상황 파악 |
| `/ha:health` | 빌드/테스트/복잡도/의존성/백로그 5개 카테고리 헬스체크 | 프로젝트 전반 상태 점검 |
| `/ha:retro` | 스프린트 회고. 패턴 감지 + 프로세스 개선 | 스프린트 끝, 작업 패턴 돌아보기 |
| `/ha:compass` | 경량 방향 점검 (~10초). Goal 달성률 + Sprint 진행률 | 빠르게 현위치 확인 |
| `/ha:weekly` | 주간 리포트. 이번 주 실적 + 다음 주 예정 | 주간 정리 |
| `/ha:backlog-detail B-XXX` | 특정 백로그의 EPIC/Story/AC 상세 조회 | 작업 구조 파악 |
| `/ha:okr` | Goal/OKR 관리 (조회, 추가, 정합성 검사) | 목표 확인/수정 |

### 품질/자동화 명령어

| 명령어 | 설명 | 언제 쓰나요? |
|--------|------|-------------|
| `/ha:qa` | 전문 QA 팀 (10개 에이전트). 기능/보안/성능/접근성 종합 | 릴리즈 전 품질 검증 |
| `/ha:review` | 통합 리뷰. UX + 코드 + 다관점 평의회 | 구현 후 리뷰 |
| `/ha:ci` | CI/CD 모니터링. 실패 분석 + 자동 수정 제안 | CI 실패 확인/분석 |
| `/ha:ac-verify [B-XXX]` | AC 검증만 단독 실행 | 완료 전 AC 점검 |

### 초기 설정 명령어

| 명령어 | 설명 |
|--------|------|
| `/ha:init` | 프로젝트 온보딩. 스택 자동감지 + BACKLOG 생성 + TODO/Issues 시딩 |
| `/ha:prd-analysis <파일>` | PRD 문서 → 백로그 일괄 생성 + 의존성 그래프 |

### 자동 체이닝 흐름

```
/ha:idea ─→ /ha:po ─→ Ready에 등록
/ha:pick ─→ [Scout → Plan → 구현 → 평가 → 검증] ─→ /ha:done (자동)
/ha:next ─→ [Scout → Plan → TDD구현 → 평가 → 검증] ─→ /ha:done (자동)
/ha:auto-loop ── 내부에서 pick → done 반복 (N회)
/ha:night-shift ── 내부에서 pick → done 반복 (시간 기반)
/ha:po ── 조건부 → /ha:okr, /ha:health, /ha:prd-analysis
```

> **참고**: `/ha:pick`과 `/ha:next`는 내부적으로 Scout(탐색) → Plan(계획) → 구현 → Evaluator(평가) → Verification(검증) 파이프라인을 거쳐 자동으로 `/ha:done`까지 체이닝합니다. 사용자가 별도로 `/ha:done`을 호출할 필요가 없습니다.

### 스마트 다음 액션 (자동 체이닝 라우터)

스킬 완료 후 프로젝트 상태를 분석하여 최적의 다음 액션을 자동 제안합니다.

```
/ha:done ──────┐
/ha:qa ────────┤
/ha:retro ─────┤
/ha:health ────┼──→ [상태 분석] ──→ 다음 액션 제안
/ha:compass ───┤
/ha:counsel ───┘

에스컬레이션 예시:
  /ha:health → D/F 2개 이상 → /ha:counsel --stuck (전략적 진단)
  /ha:retro  → 개선 3건 이상 → /ha:counsel --strategic (우선순위 정렬)
  /ha:compass → 범위 이탈 30%+ → /ha:counsel --strategic (전략 재정렬)
  /ha:done  → 연속 빌드 3회+ → /ha:qa --smoke (품질 확인)
  /ha:done  → Ready 항목 있음 → /ha:next (다음 작업)
```

> **참고**: 스마트 다음 액션은 사용자에게 추천만 합니다 (자율 루프에서만 자동 실행). 사용자가 3회 연속 거부 시 `/ha:counsel`로 에스컬레이션하여 방향 재정립을 돕습니다.
