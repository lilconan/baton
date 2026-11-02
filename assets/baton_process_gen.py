"""baton 풀프로세스 순서도 생성기 — 표준 순서도 기호 + baton-mono 팔레트."""
from pathlib import Path

INK, MUTED, SOFT_LINE, FILL2, FOCAL, PAPER = "#1a1a1a", "#555555", "#aaaaaa", "#f4f4f4", "#ebebeb", "#ffffff"
SANS = "'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"


class Canvas:
    def __init__(self):
        self.arrows, self.labels, self.nodes = [], [], []

    # ── text ─────────────────────────────────────────────
    def _text(self, cx, cy, name, sub=None, mono_sub=False, weight=600):
        out = []
        if sub:
            out.append(f'<text x="{cx}" y="{cy - 3}" fill="{INK}" font-size="13" font-weight="{weight}" font-family="{SANS}" text-anchor="middle">{name}</text>')
            fam, size, col = (MONO, 10, MUTED) if mono_sub else (SANS, 12, MUTED)
            out.append(f'<text x="{cx}" y="{cy + 14}" fill="{col}" font-size="{size}" font-weight="500" font-family="{fam}" text-anchor="middle">{sub}</text>')
        else:
            out.append(f'<text x="{cx}" y="{cy + 5}" fill="{INK}" font-size="13" font-weight="{weight}" font-family="{SANS}" text-anchor="middle">{name}</text>')
        return out

    def _node(self, shape, cx, cy, name, sub=None, mono_sub=False, fill=PAPER, sw=1):
        mask = shape.replace('fill="FILL"', f'fill="{PAPER}"').replace('stroke="STROKE"', 'stroke="none"')
        styled = shape.replace('fill="FILL"', f'fill="{fill}"').replace('stroke="STROKE"', f'stroke="{INK}" stroke-width="{sw}"')
        self.nodes += [mask, styled] + self._text(cx, cy, name, sub, mono_sub)

    # ── shapes (centered) ────────────────────────────────
    def terminal(self, cx, cy, name, sub=None, w=180, h=48, **k):
        x, y = cx - w / 2, cy - h / 2
        self._node(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def process(self, cx, cy, name, sub=None, w=220, h=56, **k):
        x, y = cx - w / 2, cy - h / 2
        self._node(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def subroutine(self, cx, cy, name, sub=None, w=220, h=56, **k):
        x, y = cx - w / 2, cy - h / 2
        self.process(cx, cy, name, sub, w, h, **k)
        sw = k.get("sw", 1)
        self.nodes += [f'<line x1="{x + 12}" y1="{y}" x2="{x + 12}" y2="{y + h}" stroke="{INK}" stroke-width="{sw}"/>',
                       f'<line x1="{x + w - 12}" y1="{y}" x2="{x + w - 12}" y2="{y + h}" stroke="{INK}" stroke-width="{sw}"/>']

    def decision(self, cx, cy, name, sub=None, w=220, h=88, **k):
        pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def prep(self, cx, cy, name, sub=None, w=240, h=56, **k):
        x, y, d = cx - w / 2, cy - h / 2, 20
        pts = f"{x + d},{y} {x + w - d},{y} {x + w},{cy} {x + w - d},{y + h} {x + d},{y + h} {x},{cy}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def document(self, cx, cy, name, sub=None, w=200, h=56, **k):
        x, y = cx - w / 2, cy - h / 2
        b = y + h - 8
        d = f"M{x} {y} H{x + w} V{b} C{x + w * 0.75} {b - 16} {x + w * 0.25} {b + 16} {x} {b} Z"
        self._node(f'<path d="{d}" fill="FILL" stroke="STROKE"/>', cx, cy - 4, name, sub, **k)

    def manual(self, cx, cy, name, sub=None, w=200, h=56, **k):
        x, y = cx - w / 2, cy - h / 2
        pts = f"{x},{y + 14} {x + w},{y} {x + w},{y + h} {x},{y + h}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy + 4, name, sub, **k)

    def display(self, cx, cy, name, sub=None, w=200, h=56, **k):
        x, y = cx - w / 2, cy - h / 2
        d = f"M{x + 20} {y} H{x + w - 20} Q{x + w} {cy} {x + w - 20} {y + h} H{x + 20} L{x} {cy} Z"
        self._node(f'<path d="{d}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def offpage(self, cx, cy, name, sub=None, w=140, h=52, **k):
        x, y = cx - w / 2, cy - h / 2
        pts = f"{x},{y} {x + w},{y} {x + w},{y + h - 16} {cx},{y + h} {x},{y + h - 16}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy - 6, name, sub, **k)

    def onpage(self, cx, cy, letter, r=14):
        self.nodes += [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>',
                       f'<text x="{cx}" y="{cy + 5}" fill="{INK}" font-size="13" font-weight="700" font-family="{SANS}" text-anchor="middle">{letter}</text>']

    def merge(self, cx, cy):
        self.nodes.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{INK}"/>')

    # ── connectors ───────────────────────────────────────
    def path(self, d, dashed=False, arrow=True):
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        mk = ' marker-end="url(#arrow)"' if arrow else ""
        self.arrows.append(f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1"{dash}{mk}/>')

    def label(self, x, y, text, anchor="middle"):
        """y = 글자 기준선. 마스크는 12px 한글 기준 16px 높이."""
        w = sum(12 if ord(ch) > 0x2E80 else 7.2 for ch in text) + 8
        w = int((w + 3) // 4 * 4)
        rx = {"middle": x - w / 2, "start": x - 4, "end": x - w + 4}[anchor]
        self.labels += [f'<rect x="{rx}" y="{y - 12}" width="{w}" height="16" rx="2" fill="{PAPER}"/>',
                        f'<text x="{x}" y="{y}" fill="{MUTED}" font-size="12" font-weight="500" font-family="{SANS}" text-anchor="{anchor}">{text}</text>']

    def svg(self, slug, title, desc, w, h, legend):
        defs = (f'<defs><marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                f'<polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker></defs>')
        body = "\n        ".join(self.arrows + self.labels + self.nodes + legend)
        return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">\n'
                f'        <title id="{slug}-title">{title}</title>\n        <desc id="{slug}-desc">{desc}</desc>\n        {defs}\n'
                f'        <rect width="100%" height="100%" fill="{PAPER}"/>\n        {body}\n      </svg>')


def legend(items, y, w):
    """items: (kind, label). 기호를 작게 그려 가로 줄로 놓는다."""
    out = [f'<line x1="32" y1="{y - 24}" x2="{w - 32}" y2="{y - 24}" stroke="{FOCAL}" stroke-width="0.8"/>',
           f'<text x="32" y="{y + 4}" fill="{MUTED}" font-size="8" font-family="{MONO}" letter-spacing="0.14em">LEGEND</text>']
    x, row_y = 100, y
    for kind, text in items:
        tw = sum(12 if ord(ch) > 0x2E80 else 7.2 for ch in text)
        need = 36 + 8 + tw + 24
        if x + need > w - 32:
            x, row_y = 100, row_y + 32
        sx, sy = x, row_y - 8
        s = {
            "terminal": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="8" fill="{PAPER}" stroke="{INK}"/>',
            "process": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{PAPER}" stroke="{INK}"/>',
            "subroutine": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{PAPER}" stroke="{INK}"/><line x1="{sx + 5}" y1="{sy}" x2="{sx + 5}" y2="{sy + 16}" stroke="{INK}"/><line x1="{sx + 27}" y1="{sy}" x2="{sx + 27}" y2="{sy + 16}" stroke="{INK}"/>',
            "decision": f'<polygon points="{sx + 16},{sy - 2} {sx + 32},{sy + 8} {sx + 16},{sy + 18} {sx},{sy + 8}" fill="{PAPER}" stroke="{INK}"/>',
            "prep": f'<polygon points="{sx + 6},{sy} {sx + 26},{sy} {sx + 32},{sy + 8} {sx + 26},{sy + 16} {sx + 6},{sy + 16} {sx},{sy + 8}" fill="{PAPER}" stroke="{INK}"/>',
            "document": f'<path d="M{sx} {sy} H{sx + 32} V{sy + 13} C{sx + 24} {sy + 8} {sx + 8} {sy + 20} {sx} {sy + 13} Z" fill="{PAPER}" stroke="{INK}"/>',
            "manual": f'<polygon points="{sx},{sy + 5} {sx + 32},{sy} {sx + 32},{sy + 16} {sx},{sy + 16}" fill="{PAPER}" stroke="{INK}"/>',
            "display": f'<path d="M{sx + 6} {sy} H{sx + 26} Q{sx + 32} {sy + 8} {sx + 26} {sy + 16} H{sx + 6} L{sx} {sy + 8} Z" fill="{PAPER}" stroke="{INK}"/>',
            "offpage": f'<polygon points="{sx + 4},{sy - 2} {sx + 28},{sy - 2} {sx + 28},{sy + 10} {sx + 16},{sy + 18} {sx + 4},{sy + 10}" fill="{PAPER}" stroke="{INK}"/>',
            "onpage": f'<circle cx="{sx + 16}" cy="{sy + 8}" r="8" fill="{PAPER}" stroke="{INK}"/>',
            "merge": f'<circle cx="{sx + 16}" cy="{sy + 8}" r="4" fill="{INK}"/>',
            "focal": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{FOCAL}" stroke="{INK}" stroke-width="2"/>',
            "dashed": f'<line x1="{sx}" y1="{sy + 8}" x2="{sx + 32}" y2="{sy + 8}" stroke="{MUTED}" stroke-dasharray="5,4"/>',
        }[kind]
        out += [s, f'<text x="{x + 42}" y="{row_y + 4}" fill="{MUTED}" font-size="12" font-weight="500" font-family="{SANS}">{text}</text>']
        x += need
    return out, row_y


def page(slug, eyebrow, title, svg, w):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --color-paper: #ffffff;
      --color-ink:   #1a1a1a;
      --color-muted: #555555;
      --font-sans:   {SANS};
      --font-mono:   {MONO};
    }}
    body {{ font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink); min-height: 100vh; display: flex; align-items: flex-start; justify-content: center; padding: 3rem 2rem; }}
    .frame {{ max-width: {w + 40}px; width: 100%; }}
    .diagram-container {{ width: 100%; overflow-x: auto; }}
    .eyebrow {{ font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }}
    h1 {{ font-family: var(--font-sans); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 1.5rem; }}
    svg {{ width: 100%; min-width: {w}px; display: block; }}
    @media print {{ .diagram-container {{ overflow-x: visible; }} svg {{ min-width: 0; }} }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    <div class="diagram-container">
      {svg}
    </div>
  </div>
</body>
</html>
"""


OUT = Path(__file__).resolve().parent  # assets/
CX, RX, LX = 420, 760, 250   # 가운데 줄, 오른쪽 열, 왼쪽 되돌림 통로
W = 960

# ════════════════ 1쪽: 전체 흐름 ════════════════
c = Canvas()
rows = {"start": 50, "has": 150, "s0": 270, "s1q": 390, "mg": 470, "s2": 540, "ok2": 650, "s3": 780, "ok3": 890, "s4": 1020, "ok4": 1130, "s5": 1250, "end": 1350}
r = rows
# 오른쪽 산출물 연결 (점선, 노드 오른쪽 → 문서 왼쪽)
for key, doc in [("s0", None), ("s2", None), ("s3", None), ("s4", None), ("s5", None)]:
    c.path(f"M{CX + 110} {r[key]} H{RX - 102}", dashed=True)
# 주 흐름
c.path(f"M{CX} {r['start'] + 24} V{r['has'] - 46}")
c.path(f"M{CX} {r['has'] + 44} V{r['s0'] - 30}")
c.label(CX + 8, r['has'] + 72, "예", "start")
c.path(f"M{CX + 110} {r['has']} H{RX - 102}")
c.label((CX + 110 + RX - 112) / 2, r['has'] - 8, "아니오")
c.path(f"M{CX} {r['s0'] + 28} V{r['s1q'] - 46}")
c.path(f"M{CX + 110} {r['s1q']} H{RX - 102}")
c.label((CX + 110 + RX - 112) / 2, r['s1q'] - 8, "예")
c.path(f"M{RX} {r['s1q'] + 28} V{r['mg'] - 8} A8 8 0 0 1 {RX - 8} {r['mg']} H{CX + 6}")
c.path(f"M{CX} {r['s1q'] + 44} V{r['mg'] - 6}", arrow=False)
c.label(CX - 8, r['s1q'] + 66, "아니오", "end")
c.path(f"M{CX} {r['mg'] + 4} V{r['s2'] - 30}")
for s, ok, back, fwd in [("s2", "ok2", "재해석·보강", "OK"), ("s3", "ok3", "수정 요청", "A·B·C·전부"), ("s4", "ok4", "예", None)]:
    c.path(f"M{CX} {r[s] + 28} V{r[ok] - 46}")
    c.path(f"M{CX - 110} {r[ok]} H{LX + 8} A8 8 0 0 1 {LX} {r[ok] - 8} V{r[s] + 8} A8 8 0 0 1 {LX + 8} {r[s]} H{CX - 112}")
    c.label(LX + 10, (r[s] + r[ok]) / 2 + 4, back, "start")
nxt = {"ok2": "s3", "ok3": "s4", "ok4": "s5"}
for ok, lab in [("ok2", "OK"), ("ok3", "A·B·C·전부"), ("ok4", "아니오")]:
    c.path(f"M{CX} {r[ok] + 44} V{r[nxt[ok]] - 30}")
    c.label(CX + 8, r[ok] + 70, lab, "start")
c.path(f"M{CX} {r['s5'] + 28} V{r['end'] - 26}")
# 재작업 요청 (수동 입력)
c.path(f"M{230} {r['s0']} H{CX - 112}", dashed=True)
# 노드
c.terminal(CX, r['start'], "기획 입력", "아이디어 한 줄 ~ 기획서")
c.decision(CX, r['has'], "기획 문서가 있나?")
c.subroutine(RX, r['has'], "wireframe 스킬", "baton 밖에서 처리", w=200)
c.subroutine(CX, r['s0'], "STEP 0 입력 게이트", "상세는 2쪽 · 생략 불가", fill=FOCAL, sw=2)
c.manual(140, r['s0'], "문서 재작업 요청", "STEP 2~4 중 언제든", w=180)
c.document(RX, r['s0'], "기획 문서 14개", "docs/{project}/", mono_sub=True)
c.decision(CX, r['s1q'], "STEP 1 요청했나?")
c.process(RX, r['s1q'], "STEP 1 화면 껍데기", "A/B/C 탭 + 화면 전환", w=200)
c.merge(CX, r['mg'])
c.subroutine(CX, r['s2'], "STEP 2 기획 해석", "baton-interpreter", mono_sub=True)
c.document(RX, r['s2'], "해석 리포트", "interpretation.html", mono_sub=True)
c.decision(CX, r['ok2'], "해석 확인")
c.subroutine(CX, r['s3'], "STEP 3 화면 구조 3안", "baton-designer", mono_sub=True)
c.document(RX, r['s3'], "3안 미리보기", "screens-proposal.html", mono_sub=True)
c.decision(CX, r['ok3'], "안 선택")
c.subroutine(CX, r['s4'], "STEP 4 프로토타입 빌드", "baton-builder", mono_sub=True)
c.document(RX, r['s4'], "프로토타입 · 시나리오", "prototype · scenario-flow", mono_sub=True)
c.decision(CX, r['ok4'], "수정 요청이 있나?")
c.process(CX, r['s5'], "STEP 5 마감", "작동 확인 · 변경 내역 종합")
c.document(RX, r['s5'], "마감 보고", "원본 대비 변경 내역 표")
c.terminal(CX, r['end'], "완료")
leg, last = legend([("terminal", "시작·끝"), ("process", "처리"), ("subroutine", "다른 에이전트·스킬이 처리"),
                    ("decision", "판단·사용자 확인"), ("document", "산출물"), ("manual", "사용자 요청"),
                    ("merge", "결합"), ("focal", "건너뛸 수 없는 단계"), ("dashed", "산출물·요청 연결")], r['end'] + 80, W)
H1 = last + 32
svg1 = c.svg("baton-process-1", "Baton 풀프로세스 — 전체 흐름",
             "기획 입력에서 STEP 0 입력 게이트, 선택적인 STEP 1, STEP 2 해석, STEP 3 3안, STEP 4 프로토타입을 거쳐 STEP 5 마감까지 가는 흐름과, 각 단계의 사용자 확인 분기와 산출물을 보여 준다.",
             W, H1, leg)
(OUT / "baton-process-1.html").write_text(page("baton-process-1", "Flowchart · 1/2", "Baton 풀프로세스 — 전체 흐름", svg1, W), encoding="utf-8")

# ════════════════ 2쪽: STEP 0 상세 ════════════════
c = Canvas()
r = {"inp": 46, "prep": 150, "split": 260, "fx": 380, "d1": 510, "ca": 630, "d2": 760, "cb": 880, "d3": 1010, "cc": 1130, "docs": 1250, "out": 1350}
c.path(f"M{CX} {r['inp'] + 20} V{r['prep'] - 30}")
c.path(f"M{CX} {r['prep'] + 28} V{r['split'] - 30}")
c.path(f"M{CX} {r['split'] + 28} V{r['fx'] - 46}")
c.path(f"M{CX + 110} {r['fx']} H{RX - 102}")
c.label((CX + 110 + RX - 102) / 2, r['fx'] - 8, "예")
c.path(f"M{RX} {r['fx'] - 28} V{r['split'] + 8} A8 8 0 0 0 {RX - 8} {r['split']} H{CX + 112}")
c.label(RX + 10, (r['split'] + r['fx']) / 2 + 4, "답을 받고 다시", "start")
c.path(f"M{CX} {r['fx'] + 44} V{r['d1'] - 30}")
c.label(CX + 8, r['fx'] + 70, "아니오", "start")
for d, ck, back, dashed in [("d1", "ca", "후보 추가", False), ("d2", "cb", "리서치 보강", False), ("d3", "cc", "지침에 없음", True)]:
    c.path(f"M{CX} {r[d] + 28} V{r[ck] - 46}")
    c.path(f"M{CX - 110} {r[ck]} H{LX + 8} A8 8 0 0 1 {LX} {r[ck] - 8} V{r[d] + 8} A8 8 0 0 1 {LX + 8} {r[d]} H{CX - 112}", dashed=dashed)
    c.label(LX + 10, (r[d] + r[ck]) / 2 + 4, back, "start")
for ck, nx in [("ca", "d2"), ("cb", "d3"), ("cc", "docs")]:
    c.path(f"M{CX} {r[ck] + 44} V{r[nx] - 30}")
    c.label(CX + 8, r[ck] + 70, "OK", "start")
c.path(f"M{CX} {r['docs'] + 24} V{r['out'] - 28}")
# 되돌아가기(재진입) — 페이지 내 연결자 R
for d in ("d2", "d3"):
    c.path(f"M{CX + 110} {r[d]} H{RX - 16}", dashed=True, arrow=False)
c.path(f"M{RX - 16} {r['d1']} H{CX + 112}", dashed=True)
c.label(RX + 22, r['d1'] + 5, "근거와 어긋나면 되돌아감", "start")
# 노드
c.offpage(CX, r['inp'], "1쪽에서")
c.prep(CX, r['prep'], "문서 틀 복사 · 목표 한 줄", "docs/_TEMPLATE → docs/{project}/", mono_sub=True, w=280)
c.process(CX, r['split'], "입력 나누기", "고정 조건 / 검증 대상")
c.decision(CX, r['fx'], "고정 조건끼리 모순?")
c.display(RX, r['fx'], "사용자에게 확인", "STEP 0의 유일한 질문", w=200)
c.process(CX, r['d1'], "1차 · 문제 찾기", "1-1 ~ 1-4 · 빈틈은 리서치 → 추론")
c.decision(CX, r['ca'], "확인 A", "문제 후보 10개+")
c.process(CX, r['d2'], "1차 · 문제 좁히기", "2-1 ~ 2-3 · 문제 정의")
c.decision(CX, r['cb'], "확인 B", "문제 정의 1문장")
c.process(CX, r['d3'], "2차 · 해법 찾기", "3-1 ~ 4-3 · 화면 목록")
c.decision(CX, r['cc'], "확인 C", "화면 목록 · 플로우")
c.document(CX, r['docs'], "기획 문서 14개", "변경 내역 표 포함", w=220)
c.offpage(CX, r['out'], "1쪽으로")
for d in ("d1", "d2", "d3"):
    c.onpage(RX, r[d], "R")
leg, last = legend([("offpage", "페이지 간 연결"), ("prep", "준비"), ("process", "처리"), ("decision", "판단·사용자 확인"),
                    ("display", "사용자에게 보여 줌"), ("document", "산출물"), ("onpage", "페이지 내 연결"),
                    ("dashed", "되돌아감·지침 미정")], r['out'] + 80, W)
H2 = last + 32
svg2 = c.svg("baton-process-2", "Baton 풀프로세스 — STEP 0 상세",
             "STEP 0 입력 게이트에서 문서 틀을 복사하고 입력을 나눈 뒤, 고정 조건 모순 확인과 문제 찾기·좁히기·해법 찾기를 거치며 확인 A·B·C에서 사용자 확인을 받고, 근거와 어긋나면 앞 단계로 되돌아가는 흐름을 보여 준다.",
             W, H2, leg)
(OUT / "baton-process-2.html").write_text(page("baton-process-2", "Flowchart · 2/2", "Baton 풀프로세스 — STEP 0 상세", svg2, W), encoding="utf-8")
print("written", H1, H2)
