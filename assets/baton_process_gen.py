"""baton 풀프로세스 순서도 생성기 — 표준 순서도 기호 + baton-mono 팔레트.

diagram-design 스킬의 slide-16x9 기준을 따른다.
- 화면 1280×720, 발표용 글자 크기: 노드 이름 16px, 보조 글자·화살표 라벨 12px
- 노드 높이 64px 이상, 노드 간격 40px 이상, 좌표와 크기는 4px 격자
- 노드 9개를 넘는 그림은 구역(zone)으로 나눈다

실행: python3 assets/baton_process_gen.py → assets/baton-process.html
"""
import re
from pathlib import Path

INK, MUTED, RULE, RULE_SOLID, FOCAL, PAPER, SOFT = "#1a1a1a", "#555555", "#ebebeb", "#d8d8d8", "#ebebeb", "#ffffff", "#aaaaaa"
SANS = "'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"
VW, VH = 1280, 720
NODE_H, DEC_H = 64, 96          # 발표용 최소 노드 높이, 마름모 높이


class Canvas:
    def __init__(self):
        self.zones, self.arrows, self.labels, self.nodes = [], [], [], []

    # ── 글자 ─────────────────────────────────────────────
    def _text(self, cx, cy, name, sub=None, mono_sub=False):
        if not sub:
            return [f'<text x="{cx}" y="{cy + 6}" fill="{INK}" font-size="16" font-weight="600" font-family="{SANS}" text-anchor="middle">{name}</text>']
        fam = MONO if mono_sub else SANS
        return [f'<text x="{cx}" y="{cy - 2}" fill="{INK}" font-size="16" font-weight="600" font-family="{SANS}" text-anchor="middle">{name}</text>',
                f'<text x="{cx}" y="{cy + 16}" fill="{MUTED}" font-size="12" font-weight="500" font-family="{fam}" text-anchor="middle">{sub}</text>']

    def _node(self, shape, cx, cy, name, sub=None, mono_sub=False, fill=PAPER, sw=1, text_dy=0, dashed=False):
        mask = shape.replace('fill="FILL"', f'fill="{PAPER}"').replace('stroke="STROKE"', 'stroke="none"')
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        styled = shape.replace('fill="FILL"', f'fill="{fill}"').replace('stroke="STROKE"', f'stroke="{INK}" stroke-width="{sw}"{dash}')
        self.nodes += [mask, styled] + self._text(cx, cy + text_dy, name, sub, mono_sub)

    # ── 순서도 기호 (모두 중심 좌표) ─────────────────────
    def terminal(self, cx, cy, name, sub=None, w=160, h=NODE_H, **k):
        self._node(f'<rect x="{cx - w // 2}" y="{cy - h // 2}" width="{w}" height="{h}" rx="20" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def process(self, cx, cy, name, sub=None, w=160, h=NODE_H, **k):
        self._node(f'<rect x="{cx - w // 2}" y="{cy - h // 2}" width="{w}" height="{h}" rx="4" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def subroutine(self, cx, cy, name, sub=None, w=160, h=NODE_H, **k):
        self.process(cx, cy, name, sub, w, h, **k)
        x, y, sw = cx - w // 2, cy - h // 2, k.get("sw", 1)
        self.nodes += [f'<line x1="{x + 12}" y1="{y}" x2="{x + 12}" y2="{y + h}" stroke="{INK}" stroke-width="{sw}"/>',
                       f'<line x1="{x + w - 12}" y1="{y}" x2="{x + w - 12}" y2="{y + h}" stroke="{INK}" stroke-width="{sw}"/>']

    def decision(self, cx, cy, name, sub=None, w=160, h=DEC_H, **k):
        pts = f"{cx},{cy - h // 2} {cx + w // 2},{cy} {cx},{cy + h // 2} {cx - w // 2},{cy}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def prep(self, cx, cy, name, sub=None, w=192, h=NODE_H, **k):
        x, y = cx - w // 2, cy - h // 2
        pts = f"{x + 20},{y} {x + w - 20},{y} {x + w},{cy} {x + w - 20},{y + h} {x + 20},{y + h} {x},{cy}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def document(self, cx, cy, name, sub=None, w=192, h=NODE_H, **k):
        x, y = cx - w // 2, cy - h // 2
        b = y + h - 8
        d = f"M{x} {y} H{x + w} V{b} C{x + w * 3 // 4} {b - 16} {x + w // 4} {b + 16} {x} {b} Z"
        self._node(f'<path d="{d}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, text_dy=-4, **k)

    def manual(self, cx, cy, name, sub=None, w=176, h=NODE_H, **k):
        x, y = cx - w // 2, cy - h // 2
        pts = f"{x},{y + 16} {x + w},{y} {x + w},{y + h} {x},{y + h}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, text_dy=4, **k)

    def display(self, cx, cy, name, sub=None, w=192, h=NODE_H, **k):
        x, y = cx - w // 2, cy - h // 2
        d = f"M{x + 20} {y} H{x + w - 20} Q{x + w} {cy} {x + w - 20} {y + h} H{x + 20} L{x} {cy} Z"
        self._node(f'<path d="{d}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, **k)

    def offpage(self, cx, cy, name, sub=None, w=160, h=NODE_H, **k):
        x, y = cx - w // 2, cy - h // 2
        pts = f"{x},{y} {x + w},{y} {x + w},{y + h - 16} {cx},{y + h} {x},{y + h - 16}"
        self._node(f'<polygon points="{pts}" fill="FILL" stroke="STROKE"/>', cx, cy, name, sub, text_dy=-6, **k)

    def merge(self, cx, cy):
        self.nodes.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{INK}"/>')

    def zone(self, x, y, w, h, name, label_at="top", focal=False):
        """구역: 노드가 9개를 넘는 그림을 읽는 단위로 나눈다. 연결선보다 먼저 그린다.
        위에서 연결선이 들어오는 구역은 이름을 아래 모서리(label_at="bottom")에 둔다."""
        ty = y + 20 if label_at == "top" else y + h - 12
        stroke, sw, col = (INK, 2, INK) if focal else (RULE_SOLID, 1, MUTED)
        self.zones += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="{stroke}" stroke-width="{sw}"/>',
                       f'<text x="{x + 16}" y="{ty}" fill="{col}" font-size="12" font-weight="600" font-family="{SANS}">{name}</text>']

    def note(self, x, y, text):
        self.nodes.append(f'<text x="{x}" y="{y}" fill="{MUTED}" font-size="12" font-weight="500" font-family="{SANS}">{text}</text>')

    # ── 연결선 ───────────────────────────────────────────
    def path(self, d, dashed=False, arrow=True):
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        mk = ' marker-end="url(#arrow)"' if arrow else ""
        self.arrows.append(f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1"{dash}{mk}/>')

    def label(self, x, y, text, anchor="middle"):
        """화살표 라벨. y는 글자 기준선, 마스크는 16px 높이(한글 12px 기준)."""
        w = sum(12 if ord(ch) > 0x2E80 else 7.2 for ch in text) + 8
        w = int((w + 3) // 4 * 4)
        rx = {"middle": x - w // 2, "start": x - 4, "end": x - w + 4}[anchor]
        self.labels += [f'<rect x="{rx}" y="{y - 12}" width="{w}" height="16" rx="2" fill="{PAPER}"/>',
                        f'<text x="{x}" y="{y}" fill="{MUTED}" font-size="12" font-weight="500" font-family="{SANS}" text-anchor="{anchor}">{text}</text>']

    def loop_above(self, dx, dy, tx, ty, text, dashed=False, up=40):
        """마름모 위 꼭짓점(dx, dy) → 위로 → 왼쪽 → 단계 윗변(tx, ty)."""
        top = dy - up
        self.path(f"M{dx} {dy} V{top + 8} A8 8 0 0 0 {dx - 8} {top} H{tx + 8} A8 8 0 0 0 {tx} {top + 8} V{ty - 2}", dashed=dashed)
        self.label((dx + tx) // 2, top - 10, text)

    def loop_below(self, dx, dy, tx, ty, text, dashed=False, down=40):
        """마름모 아래 꼭짓점(dx, dy) → 아래로 → 왼쪽 → 단계 아랫변(tx, ty)."""
        bot = dy + down
        self.path(f"M{dx} {dy} V{bot - 8} A8 8 0 0 1 {dx - 8} {bot} H{tx + 8} A8 8 0 0 1 {tx} {bot - 8} V{ty + 2}", dashed=dashed)
        self.label((dx + tx) // 2, bot + 20, text)

    def self_loop(self, cx, edge_y, text, side="top", reach=48, spread=40):
        """단계 노드의 한 변에서 나갔다가 같은 변으로 돌아오는 화살표. 확인에서 다시 하는 길."""
        a, b = cx + spread, cx - spread
        if side == "top":
            y = edge_y - reach
            self.path(f"M{a} {edge_y} V{y + 8} A8 8 0 0 0 {a - 8} {y} H{b + 8} A8 8 0 0 0 {b} {y + 8} V{edge_y - 2}")
            self.label(cx, y - 10, text)
        else:
            y = edge_y + reach
            self.path(f"M{a} {edge_y} V{y - 8} A8 8 0 0 1 {a - 8} {y} H{b + 8} A8 8 0 0 1 {b} {y - 8} V{edge_y + 2}")
            self.label(cx, y + 20, text)

    def svg(self, slug, title, desc, legend):
        defs = (f'<defs><marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                f'<polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker></defs>')
        body = "\n        ".join(self.zones + self.arrows + self.labels + self.nodes + legend)
        return (f'<svg viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">\n'
                f'        <title id="{slug}-title">{title}</title>\n        <desc id="{slug}-desc">{desc}</desc>\n        {defs}\n'
                f'        <rect width="100%" height="100%" fill="{PAPER}"/>\n        {body}\n      </svg>')


def legend(items, y=664):
    """범례: 그림 아래 가로 한 줄. items = (기호 종류, 설명)."""
    out = [f'<line x1="32" y1="{y - 28}" x2="{VW - 32}" y2="{y - 28}" stroke="{RULE}" stroke-width="1"/>',
           f'<text x="32" y="{y + 4}" fill="{MUTED}" font-size="8" font-family="{MONO}" letter-spacing="0.14em">LEGEND</text>']
    x = 104
    for kind, text in items:
        sx, sy = x, y - 8
        s = {
            "terminal": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="8" fill="{PAPER}" stroke="{INK}"/>',
            "process": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{PAPER}" stroke="{INK}"/>',
            "subroutine": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{PAPER}" stroke="{INK}"/><line x1="{sx + 6}" y1="{sy}" x2="{sx + 6}" y2="{sy + 16}" stroke="{INK}"/><line x1="{sx + 26}" y1="{sy}" x2="{sx + 26}" y2="{sy + 16}" stroke="{INK}"/>',
            "decision": f'<polygon points="{sx + 16},{sy - 4} {sx + 32},{sy + 8} {sx + 16},{sy + 20} {sx},{sy + 8}" fill="{PAPER}" stroke="{INK}"/>',
            "prep": f'<polygon points="{sx + 8},{sy} {sx + 24},{sy} {sx + 32},{sy + 8} {sx + 24},{sy + 16} {sx + 8},{sy + 16} {sx},{sy + 8}" fill="{PAPER}" stroke="{INK}"/>',
            "document": f'<path d="M{sx} {sy} H{sx + 32} V{sy + 12} C{sx + 24} {sy + 8} {sx + 8} {sy + 20} {sx} {sy + 12} Z" fill="{PAPER}" stroke="{INK}"/>',
            "manual": f'<polygon points="{sx},{sy + 4} {sx + 32},{sy} {sx + 32},{sy + 16} {sx},{sy + 16}" fill="{PAPER}" stroke="{INK}"/>',
            "display": f'<path d="M{sx + 8} {sy} H{sx + 24} Q{sx + 32} {sy + 8} {sx + 24} {sy + 16} H{sx + 8} L{sx} {sy + 8} Z" fill="{PAPER}" stroke="{INK}"/>',
            "offpage": f'<polygon points="{sx + 4},{sy - 4} {sx + 28},{sy - 4} {sx + 28},{sy + 8} {sx + 16},{sy + 20} {sx + 4},{sy + 8}" fill="{PAPER}" stroke="{INK}"/>',
            "merge": f'<circle cx="{sx + 16}" cy="{sy + 8}" r="4" fill="{INK}"/>',
            "focal": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{FOCAL}" stroke="{INK}" stroke-width="2"/>',
            "zone": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="4" fill="none" stroke="{RULE_SOLID}"/>',
            "focalzone": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="4" fill="none" stroke="{INK}" stroke-width="2"/>',
            "loop": f'<path d="M{sx + 24} {sy + 16} V{sy + 4} H{sx + 8} V{sy + 14}" fill="none" stroke="{MUTED}"/><polygon points="{sx + 5},{sy + 11} {sx + 8},{sy + 16} {sx + 11},{sy + 11}" fill="{MUTED}"/>',
            "optional": f'<rect x="{sx}" y="{sy}" width="32" height="16" rx="2" fill="{PAPER}" stroke="{INK}" stroke-dasharray="4,3"/>',
            "dashed": f'<line x1="{sx}" y1="{sy + 8}" x2="{sx + 32}" y2="{sy + 8}" stroke="{MUTED}" stroke-dasharray="5,4"/>',
        }[kind]
        out += [s, f'<text x="{x + 40}" y="{y + 4}" fill="{MUTED}" font-size="12" font-weight="500" font-family="{SANS}">{text}</text>']
        x += 40 + int(sum(12 if ord(ch) > 0x2E80 else 7.2 for ch in text)) + 28
    assert x < VW, "범례가 한 줄을 넘는다"
    return out


def channel(c, x_from, y_from, x_to, y_to, y_mid, x_right=1176):
    """한 줄의 끝에서 오른쪽 통로로 내려가, 다음 줄 첫 노드의 윗변으로 들어간다."""
    c.path(f"M{x_from} {y_from} H{x_right - 8} A8 8 0 0 1 {x_right} {y_from + 8} V{y_mid - 8} "
           f"A8 8 0 0 1 {x_right - 8} {y_mid} H{x_to + 8} A8 8 0 0 0 {x_to} {y_mid + 8} V{y_to - 2}")


def drop(c, x_from, y_from, x_to, y_to, y_mid):
    """마름모 아래 꼭짓점에서 바로 내려가, 왼쪽으로 꺾어 다음 줄 첫 노드의 윗변으로 들어간다."""
    c.path(f"M{x_from} {y_from} V{y_mid - 8} A8 8 0 0 1 {x_from - 8} {y_mid} H{x_to + 8} A8 8 0 0 0 {x_to} {y_mid + 8} V{y_to - 2}")


# ════════════════ 전체 흐름 (14개 노드 · 구역 2개) ════════════════
c = Canvas()
Y1, Y1S, Y2 = 136, 272, 448          # 1줄 본선, 1줄 곁가지, 2줄 본선
c.zone(16, 56, 1248, 264, "시작 · STEP 0~1")
c.zone(16, 384, 1248, 216, "화면 만들기 · STEP 2~5", label_at="bottom")
# 1줄 본선: 기획 입력 → 기획 문서? → STEP 0 → STEP 1? → 결합
c.path(f"M176 {Y1} H214")
c.path(f"M376 {Y1} H430")
c.label(404, Y1 - 10, "네")
c.path(f"M608 {Y1} H654")
c.path(f"M832 {Y1} H900", arrow=False)
c.label(866, Y1 - 10, "아니요")
# 1줄 곁가지
c.path(f"M296 {Y1 + 48} V{Y1S - 34}")
c.label(304, Y1 + 76, "아니요", "start")
c.path(f"M520 {Y1S - 24} V{Y1 + 34}", dashed=True)
c.path(f"M744 {Y1 + 48} V{Y1S - 34}")
c.label(752, Y1 + 76, "네", "start")
c.path(f"M832 {Y1S} H896 A8 8 0 0 0 904 {Y1S - 8} V{Y1 + 4}", arrow=False)
# 결합 → 오른쪽 통로 → 2줄 STEP 2
channel(c, 908, Y1, 104, Y2 - 32, 352, x_right=1240)
# 2줄: STEP 2 → 해석 확인 → STEP 3 → 안 선택 → STEP 4 → 수정 요청? → STEP 5
xs = [104, 284, 464, 644, 824, 1004, 1184]       # 노드 폭 144, 마름모 폭 136, 간격 40
half = [72, 68, 72, 68, 72, 68, 72]
for (a, ha), (b, hb) in zip(zip(xs, half), zip(xs[1:], half[1:])):
    c.path(f"M{a + ha} {Y2} H{b - hb - 2}")
c.label(372, Y2 - 10, "네")
c.label(732, Y2 - 10, "선택")
c.label(1090, Y2 - 10, "아니요")
for d, s, text in [(284, 104, "다시"), (644, 464, "다시 제안"), (1004, 824, "네")]:
    c.loop_below(d, Y2 + 48, s, Y2 + 32, text)
c.terminal(104, Y1, "기획 입력", "아이디어 ~ 기획서", w=144)
c.decision(296, Y1, "기획서 있나요?", w=160)
c.subroutine(520, Y1, "STEP 0 기획 검증", "건너뛸 수 없음", w=176, fill=FOCAL, sw=2)
c.decision(744, Y1, "화면 틀 먼저?", "STEP 1 요청", w=176)
c.merge(904, Y1)
c.subroutine(296, Y1S, "빠른 스케치", "wireframe 스킬로", w=176)
c.manual(520, Y1S, "기획 다시 요청", "STEP 2~4 중 언제든", w=176)
c.process(744, Y1S, "STEP 1 화면 틀", "요청할 때만", w=176)
c.subroutine(104, Y2, "STEP 2 해석", "결과: 해석 리포트", w=144)
c.decision(284, Y2, "해석 맞나요?", w=136)
c.subroutine(464, Y2, "STEP 3 화면 3안", "결과: 3안 비교", w=144)
c.decision(644, Y2, "어느 안으로?", w=136)
c.subroutine(824, Y2, "STEP 4 시안 제작", "결과: 클릭되는 시안", w=144)
c.decision(1004, Y2, "더 고칠까요?", w=136)
c.process(1184, Y2, "STEP 5 마감", "변경 내역 정리", w=144)
svg1 = c.svg("overview", "Baton 풀프로세스 — 전체 흐름",
             "기획 입력에서 STEP 0 기획 검증과 요청할 때만 하는 STEP 1을 거쳐 STEP 2 해석, STEP 3 화면 3안, STEP 4 시안 제작, STEP 5 마감까지 가는 흐름과, 단계마다 사람이 답하는 질문에서 되돌아가는 길을 두 구역으로 나눠 보여 준다.",
             legend([("terminal", "시작"), ("process", "baton이 하는 일"), ("subroutine", "baton 단계"), ("decision", "사람이 답하는 질문"),
                     ("manual", "사람이 요청"), ("merge", "합류"), ("focal", "건너뛸 수 없음"), ("zone", "구역")]))

# ════════════════ STEP 0 상세 (11개 노드 · 구역 3개) ════════════════
c = Canvas()
Y1, Y2 = 152, 448
c.zone(16, 40, 1248, 200, "준비")
c.zone(16, 384, 696, 216, "1차 · 문제", label_at="bottom")
c.zone(728, 384, 536, 216, "2차 · 해법", label_at="bottom")
c.path(f"M192 {Y1} H230")
c.path(f"M408 {Y1} H446")
c.path(f"M624 {Y1} H670")
c.path(f"M880 {Y1} H942")
c.label(912, Y1 - 10, "네")
c.path(f"M1040 {Y1 - 32} V92 A8 8 0 0 0 1032 84 H544 A8 8 0 0 0 536 92 V{Y1 - 34}")
c.label(788, 74, "답을 받고 다시")
drop(c, 776, Y1 + 48, 104, Y2 - 32, 320)
c.label(784, 272, "아니요", "start")
xs = [104, 280, 456, 632, 824, 1000, 1176]        # 노드·마름모·연결자 모두 폭 144
half = [72] * 7
for (a, ha), (b, hb) in zip(zip(xs, half), zip(xs[1:], half[1:])):
    c.path(f"M{a + ha} {Y2} H{b - hb - 2}")
for x in (368, 728, 1088):
    c.label(x, Y2 - 10, "네")
c.loop_below(280, Y2 + 48, 104, Y2 + 32, "더 찾기")
c.loop_below(632, Y2 + 48, 456, Y2 + 32, "더 다듬기")
c.loop_below(1000, Y2 + 48, 824, Y2 + 32, "거절 시 (미정)", dashed=True)
c.offpage(112, Y1, "전체 흐름에서", w=160)
c.prep(320, Y1, "문서 틀 준비", "목표 한 줄 쓰기", w=176)
c.process(536, Y1, "입력 나누기", "고정할 것 / 검증할 것", w=176)
c.decision(776, Y1, "모순 있나요?", "고정 조건끼리", w=208)
c.display(1040, Y1, "사람에게 질문", "STEP 0의 유일한 질문", w=192)
c.process(104, Y2, "문제 찾기", "리서치 · 문서 4개", w=144)
c.decision(280, Y2, "문제 맞나요?", "확인 A", w=144)
c.process(456, Y2, "문제 정의", "문서 3개", w=144)
c.decision(632, Y2, "정의 맞나요?", "확인 B", w=144)
c.process(824, Y2, "해법·화면 목록", "문서 5개", w=144)
c.decision(1000, Y2, "목록 맞나요?", "확인 C", w=144)
c.offpage(1176, Y2, "전체 흐름으로", "기획 문서 14개", w=144)
c.note(32, 624, "확인 B·C 단계에서 리서치 근거가 결론과 어긋나면 문제 찾기로 되돌아갑니다.")
svg2 = c.svg("step0", "Baton 풀프로세스 — STEP 0 상세",
             "STEP 0 기획 검증에서 문서 틀을 준비하고 입력을 나눠 고정 조건끼리 모순이 있는지 본 뒤, 1차 구역에서 문제를 찾고 정의하며 2차 구역에서 해법과 화면 목록을 정하고, 확인 A·B·C에서 사람의 답을 받는 흐름을 보여 준다.",
             legend([("offpage", "다른 그림으로 이어짐"), ("prep", "준비"), ("process", "baton이 하는 일"), ("decision", "사람이 답하는 질문"),
                     ("display", "사람에게 묻기"), ("zone", "구역"), ("dashed", "아직 정해지지 않은 길")], y=672))

# ════════════════ 전체 흐름 심플 (9개 노드) ════════════════
c = Canvas()
Y1, Y2 = 200, 460
c.path(f"M216 {Y1} H302")
c.path(f"M528 {Y1} H586")
c.path(f"M796 {Y1} H862")
channel(c, 1072, Y1, 144, Y2 - 32, 328, x_right=1180)
c.label(1188, 268, "네", "start")
c.loop_above(968, Y1 - 48, 692, Y1 - 32, "다시")
c.path(f"M248 {Y2} H294")
c.path(f"M472 {Y2} H526")
c.label(500, Y2 - 10, "선택")
c.path(f"M752 {Y2} H790")
c.path(f"M1016 {Y2} H1078")
c.label(1048, Y2 - 10, "아니요")
# 2줄 되돌아가는 길은 위로 돈다(아래는 결과물 자리). STEP 3 윗변 가운데는 통로 화살표가 쓰므로 오른쪽으로 비켜 꽂는다
c.loop_above(384, Y2 - 48, 200, Y2 - 32, "다시 제안")
c.loop_above(904, Y2 - 48, 640, Y2 - 32, "네")
# 단계가 남기는 결과물 (점선 화살표 + 문서 기호)
for x, y0, yd, name in [(416, Y1 + 32, 288, "기획 문서 14개"), (692, Y1 + 32, 288, "해석 리포트"),
                        (144, Y2 + 32, 560, "화면 3안 비교"), (640, Y2 + 32, 560, "클릭되는 시안")]:
    c.path(f"M{x} {y0} V{yd - 26}", dashed=True)
    c.document(x, yd, name, w=176, h=48)
c.terminal(128, Y1, "기획 입력", "아이디어 ~ 기획서", w=176)
c.subroutine(416, Y1, "STEP 0 기획 검증", "확인 3번 · 건너뛸 수 없음", w=224, fill=FOCAL, sw=2)
c.subroutine(692, Y1, "STEP 2 기획 해석", w=208)
c.decision(968, Y1, "해석 맞나요?", w=208)
c.subroutine(144, Y2, "STEP 3 화면 3안", w=208)
c.decision(384, Y2, "어느 안으로?", w=176)
c.subroutine(640, Y2, "STEP 4 시안 제작", w=224)
c.decision(904, Y2, "더 고칠까요?", w=224)
c.terminal(1160, Y2, "마감", "STEP 5", w=160)
svg_s = c.svg("overview-simple", "Baton 풀프로세스 — 심플",
              "기획 입력에서 STEP 0 기획 검증을 거쳐 STEP 2 해석, STEP 3 화면 3안, STEP 4 시안 제작을 지나 마감까지 두 줄로 이어지며, 각 단계 뒤 사람이 답하는 질문에서 다시 하겠다고 하면 그 단계로 돌아가고, 단계마다 남는 결과물을 함께 보여 준다.",
              legend([("terminal", "시작·끝"), ("subroutine", "baton 단계"), ("decision", "사람이 답하는 질문"),
                      ("focal", "건너뛸 수 없는 단계"), ("document", "단계가 남기는 결과물")]))

# ════════════════ STEP 0 심플 (9개 노드) ════════════════
c = Canvas()
c.path(f"M232 {Y1} H278")
c.path(f"M456 {Y1} H510")
c.path(f"M672 {Y1} H726")
c.label(700, Y1 - 10, "네")
c.path(f"M904 {Y1} H950")
c.loop_above(592, Y1 - 48, 368, Y1 - 32, "더 찾기")
c.loop_above(1032, Y1 - 48, 816, Y1 - 32, "더 다듬기")
channel(c, 1112, Y1, 144, Y2 - 32, 328, x_right=1180)
c.label(1188, 268, "네", "start")
c.path(f"M248 {Y2} H310")
c.path(f"M472 {Y2} H534")
c.label(504, Y2 - 10, "네")
c.path(f"M744 {Y2} H806")
c.loop_below(392, Y2 + 48, 144, Y2 + 32, "거절 시 (미정)", dashed=True)
c.prep(136, Y1, "문서 틀 준비", "목표 한 줄 · 입력 나누기", w=192)
c.process(368, Y1, "문제 찾기", "리서치 · 문서 4개", w=176)
c.decision(592, Y1, "문제 맞나요?", "확인 A", w=160)
c.process(816, Y1, "문제 정의", "문서 3개", w=176)
c.decision(1032, Y1, "정의 맞나요?", "확인 B", w=160)
c.process(144, Y2, "해법·화면 목록", "문서 5개", w=208)
c.decision(392, Y2, "목록 맞나요?", "확인 C", w=160)
c.document(640, Y2, "기획 문서 14개", "변경 내역 표 포함", w=208)
c.terminal(896, Y2, "STEP 1·2로", w=176)
svg_s0 = c.svg("step0-simple", "Baton STEP 0 — 심플",
               "문서 틀을 준비하고 입력을 나눈 뒤 문제 찾기, 문제 정의, 해법과 화면 목록을 두 줄로 이어 가며 확인 A·B·C에서 사람의 답을 받고 기획 문서 14개를 남기는 STEP 0 기획 검증의 흐름을 보여 준다.",
               legend([("prep", "준비"), ("process", "baton이 하는 일"), ("decision", "사람이 답하는 질문"), ("document", "결과물"),
                       ("terminal", "끝"), ("dashed", "아직 정해지지 않은 길")]))


# ════════════════ 전체 통합 (22개 노드 · 구역 4개 · faithful) ════════════════
c = Canvas()
Y1, Y2, Y3, DH = 160, 304, 504, 80     # 세 줄, 마름모 높이 80 (노드 높이 64는 유지)
c.zone(16, 8, 368, 208, "시작")
c.zone(400, 8, 864, 208, "STEP 0 기획 검증 · 준비 (건너뛸 수 없음)", focal=True)
c.zone(16, 240, 1052, 172, "STEP 0 · 문제·해법", label_at="bottom", focal=True)
c.zone(16, 444, 1248, 168, "화면 · STEP 2~5", label_at="bottom")
# 1줄: 기획 입력 → 기획 문서? → 문서 틀 복사 → 입력 나누기 → 고정 조건 모순? → 사용자에게 확인
c.path(f"M176 {Y1} H206")
c.path(f"M288 {Y1 - 40} V90")
c.label(296, 112, "아니요", "start")
c.path(f"M368 {Y1} H422")
c.label(396, Y1 - 10, "네")
c.path(f"M584 {Y1} H622")
c.path(f"M784 {Y1} H822")
c.path(f"M1000 {Y1} H1054")
c.label(1028, Y1 - 10, "네")
c.path(f"M1144 {Y1 - 32} V104 A8 8 0 0 0 1136 96 H712 A8 8 0 0 0 704 104 V{Y1 - 34}")
c.label(924, 86, "답을 받고 다시")
drop(c, 912, Y1 + 40, 104, Y2 - 32, 232)
c.label(920, 218, "아니요", "start")
# 2줄: 문제 찾기 → 확인 A → 문제 정의 → 확인 B → 해법·화면 목록 → 확인 C → STEP 1(요청 시)
xs = [104, 280, 456, 632, 808, 984, 1160]
half = [72] * 7                          # 마름모도 폭 144 (질문 글자가 들어가도록)
for (a, ha), (b, hb) in zip(zip(xs, half), zip(xs[1:], half[1:])):
    c.path(f"M{a + ha} {Y2} H{b - hb - 2}")
for x in (368, 720, 1072):
    c.label(x, Y2 - 10, "네")
c.loop_below(280, Y2 + 40, 104, Y2 + 32, "더 찾기", down=32)
c.loop_below(632, Y2 + 40, 456, Y2 + 32, "더 다듬기", down=32)
c.loop_below(984, Y2 + 40, 808, Y2 + 32, "거절 시 (미정)", dashed=True, down=32)
channel(c, 1232, Y2, 104, Y3 - 32, 428, x_right=1264)
# 3줄: STEP 2 → 해석 확인 → STEP 3 → 안 선택 → STEP 4 → 수정 요청? → STEP 5
xs3 = [104, 284, 464, 644, 824, 1004, 1184]
half3 = [72] * 7
for (a, ha), (b, hb) in zip(zip(xs3, half3), zip(xs3[1:], half3[1:])):
    c.path(f"M{a + ha} {Y3} H{b - hb - 2}")
c.label(374, Y3 - 10, "네")
c.label(734, Y3 - 10, "선택")
c.label(1094, Y3 - 10, "아니요")
for d, t, text in [(284, 104, "다시"), (644, 464, "다시 제안"), (1004, 824, "네")]:
    c.loop_below(d, Y3 + 40, t, Y3 + 32, text, down=32)
# 노드
c.terminal(104, Y1, "기획 입력", "아이디어 ~ 기획서", w=144)
c.decision(288, Y1, "기획서 있나요?", w=160, h=DH)
c.subroutine(288, 56, "빠른 스케치", "wireframe 스킬로", w=160)
c.prep(504, Y1, "문서 틀 준비", "목표 한 줄 쓰기", w=160)
c.process(704, Y1, "입력 나누기", "고정할 것 / 검증할 것", w=160)
c.decision(912, Y1, "모순 있나요?", "고정 조건끼리", w=176, h=DH)
c.display(1144, Y1, "사람에게 질문", "유일한 질문", w=176)
c.process(104, Y2, "문제 찾기", "리서치 · 문서 4개", w=144)
c.decision(280, Y2, "문제 맞나요?", "확인 A", w=144, h=DH)
c.process(456, Y2, "문제 정의", "문서 3개", w=144)
c.decision(632, Y2, "정의 맞나요?", "확인 B", w=144, h=DH)
c.process(808, Y2, "해법·화면 목록", "문서 5개", w=144)
c.decision(984, Y2, "목록 맞나요?", "확인 C", w=144, h=DH)
c.process(1160, Y2, "STEP 1 화면 틀", "요청할 때만", w=144, dashed=True)
c.subroutine(104, Y3, "STEP 2 해석", "결과: 해석 리포트", w=144)
c.decision(284, Y3, "해석 맞나요?", w=144, h=DH)
c.subroutine(464, Y3, "STEP 3 화면 3안", "결과: 3안 비교", w=144)
c.decision(644, Y3, "어느 안으로?", w=144, h=DH)
c.subroutine(824, Y3, "STEP 4 시안 제작", "결과: 클릭되는 시안", w=144)
c.decision(1004, Y3, "더 고칠까요?", w=144, h=DH)
c.process(1184, Y3, "STEP 5 마감", "변경 내역 정리", w=144)
c.note(32, 640, "STEP 2~4 중 기획을 다시 요청하면 STEP 0으로 돌아갑니다. 확인 B·C에서 근거가 결론과 어긋나면 문제 찾기로 되돌아갑니다.")
svg_all = c.svg("all", "Baton 풀프로세스 — 전체 통합",
                "기획 입력에서 STEP 0 기획 검증의 준비, 문제 찾기와 정의, 해법과 화면 목록, 요청할 때만 하는 STEP 1을 거쳐 STEP 2 해석, STEP 3 화면 3안, STEP 4 시안 제작, STEP 5 마감까지 가는 전체 흐름을 세 줄로 이어 보여 주며, 사람이 답하는 질문마다 되돌아가는 길을 함께 그린다.",
                legend([("terminal", "시작"), ("prep", "준비"), ("process", "baton이 하는 일"), ("subroutine", "baton 단계"),
                        ("decision", "사람이 답하는 질문"), ("display", "사람에게 묻기"), ("optional", "요청할 때만"),
                        ("focalzone", "STEP 0 (건너뛸 수 없음)")], y=688))


# ════════════════ 전체 통합 심플: 열 3개 순서도 (포트폴리오 첫머리에도 쓴다) ════════════════
def ortho(c, pts, dashed=False, r=8):
    """직각으로 꺾이는 점 목록을 모서리가 둥근 경로로 바꾼다. 마지막 점에 화살촉이 붙는다."""
    d = [f"M{pts[0][0]} {pts[0][1]}"]
    for (x0, y0), (x1, y1), (x2, y2) in zip(pts, pts[1:], pts[2:]):
        ax, ay = (x1 - x0) // max(abs(x1 - x0), 1) if x1 != x0 else 0, (y1 - y0) // max(abs(y1 - y0), 1) if y1 != y0 else 0
        bx, by = (x2 - x1) // max(abs(x2 - x1), 1) if x2 != x1 else 0, (y2 - y1) // max(abs(y2 - y1), 1) if y2 != y1 else 0
        sweep = 1 if ax * by - ay * bx > 0 else 0
        d.append(f"L{x1 - ax * r} {y1 - ay * r} A{r} {r} 0 0 {sweep} {x1 + bx * r} {y1 + by * r}")
    d.append(f"L{pts[-1][0]} {pts[-1][1]}")
    c.path(" ".join(d), dashed=dashed)


c = Canvas()
H, DH = 56, 80
c.zone(40, 40, 240, 616, "STEP 0 기획 검증", label_at="bottom")

# ── 연결선 ──
# STEP 0 열: 위에서 아래로, 끝에 기획 문서
for y0, y1 in ((108, 156), (212, 252), (308, 348), (404, 444), (500, 546)):
    c.path(f"M160 {y0} V{y1 - 2}")
ortho(c, [(248, 576), (400, 576), (400, 72), (542, 72)])                             # 기획 문서 → STEP 2
# STEP 2~4 열
for y0, y1, t in ((108, 144, None), (224, 260, "네"), (316, 352, None), (432, 468, "선택")):
    c.path(f"M640 {y0} V{y1 - 2}")
    if t:
        c.label(648, y1 - 12, t, "start")
ortho(c, [(560, 184), (520, 184), (520, 88), (542, 88)])                             # 해석 다시
c.label(512, 140, "아니요", "end")
ortho(c, [(560, 392), (520, 392), (520, 288), (542, 288)])                           # 다른 안 다시
c.label(512, 344, "다시 제안", "end")
c.path("M736 80 H822", dashed=True)
c.path("M736 288 H822", dashed=True)
c.path("M640 524 V578", dashed=True)
# 수정 루프
c.path("M736 496 H822")
c.path("M984 496 H1050")
c.label(1016, 486, "아니요")
ortho(c, [(904, 456), (904, 440), (704, 440), (704, 466)])                           # 고칠 것 있음 → STEP 4
c.label(804, 430, "네 · 다시 고침")

# ── 노드 ──
c.terminal(160, 80, "기획 입력", w=176, h=H)
c.process(160, 184, "입력 나누기", "고정할 것 · 검증할 것", w=176, h=H)
c.process(160, 280, "문제 찾기", "리서치 · 확인 A", w=176, h=H)
c.process(160, 376, "문제 정의", "확인 B", w=176, h=H)
c.process(160, 472, "해법 · 화면 목록", "확인 C", w=176, h=H)
c.document(160, 576, "기획 문서 14개", w=176, h=56)

c.subroutine(640, 80, "STEP 2 기획 해석", "기획서를 화면 언어로", w=192, h=H)
c.decision(640, 184, "해석 맞나요?", w=160, h=DH)
c.subroutine(640, 288, "STEP 3 화면 3안", "구조가 다른 세 안", w=192, h=H)
c.decision(640, 392, "어느 안으로?", w=160, h=DH)
c.subroutine(640, 496, "STEP 4 시안 제작", "A·B·C 탭 프로토타입", w=192, h=H, fill=FOCAL, sw=2)
c.document(904, 80, "해석 리포트", w=160, h=56)
c.document(904, 288, "화면 3안 비교", w=160, h=56)
c.document(640, 604, "클릭되는 시안", w=176, h=48)

c.decision(904, 496, "더 고칠까요?", w=160, h=DH)
c.terminal(1120, 496, "마감", "변경 내역 정리", w=136, h=H)

svg_all_s = c.svg("all-simple", "Baton 풀프로세스 — 전체 통합 심플",
            "기획 입력을 고정할 것과 검증할 것으로 나눈 뒤 문제 찾기, 문제 정의, 해법과 화면 목록을 확인 A, B, C를 거쳐 정해 기획 문서 14개를 남긴다. 이어 STEP 2 해석, STEP 3 화면 3안, STEP 4 시안 제작마다 사람이 확인하고, 고칠 것이 있으면 STEP 4로 돌아가며, 없으면 마감한다.",
            legend([("terminal", "시작·끝"), ("process", "baton이 하는 일"), ("subroutine", "baton 단계"),
                    ("decision", "사람이 답하는 질문"), ("document", "결과물"), ("focal", "핵심 단계")], y=696))


# ════════════════ 한 파일로 묶기: 메뉴로 오간다 ════════════════
def scoped(svg, slug):
    """여러 SVG를 한 문서에 넣을 때 marker id가 겹치지 않게 슬러그를 붙인다."""
    return re.sub(r'(id="|url\(#)(arrow[\w-]*)', rf"\g<1>{slug}-\2", svg)


# (hash, 메뉴 이름, 제목, 이 그림에서 볼 것, svg). 처음 보는 사람이 쉬운 그림부터 보도록 심플 3장을 앞에 둔다
VIEWS = [
    ("all-simple", "전체 통합 심플", "풀프로세스 — 전체 통합 심플",
     "왼쪽 열은 기획을 검증하는 STEP 0, 가운데 열은 화면을 만드는 STEP 2~4입니다. 마름모는 사람이 답하는 질문이고, ‘아니요’면 화살표를 따라 그 단계를 다시 합니다.", svg_all_s),
    ("overview-simple", "전체 흐름 심플", "풀프로세스 — 심플",
     "기획서를 넣으면 마감까지 어떤 순서로 가는지 보여 줍니다. 마름모는 사람이 답하는 질문이고, STEP 1은 요청할 때만 해서 이 그림에서는 뺐습니다.", svg_s),
    ("step0-simple", "STEP 0 상세 심플", "STEP 0 — 심플",
     "가장 오래 걸리는 STEP 0 기획 검증의 안쪽입니다. 리서치로 문제를 찾고, 정의하고, 해법과 화면 목록을 정하며 그때마다 사람이 확인합니다.", svg_s0),
    ("all", "전체 통합", "풀프로세스 — 전체 통합",
     "STEP 0 안쪽까지 모든 갈래를 한 장에 넣은 지도입니다. 처음이라면 왼쪽의 심플 그림부터 보는 편이 쉽습니다.", svg_all),
    ("overview", "전체 흐름", "풀프로세스 — 전체 흐름",
     "STEP 0을 한 덩어리로 접고, 요청할 때만 하는 STEP 1과 기획 다시 요청 같은 곁가지까지 보여 줍니다.", svg1),
    ("step0", "STEP 0 상세", "STEP 0 — 상세",
     "STEP 0 기획 검증의 모든 갈래입니다. 바꾸면 안 되는 조건끼리 부딪힐 때만 사람에게 묻고, 나머지 빈칸은 리서치로 채웁니다.", svg2),
]
tabs = [f'      <a class="tab" href="#{h}">{name}</a>' for h, name, *_ in VIEWS]
nav = "\n".join(['      <span class="group">처음이라면</span>', *tabs[:3],
                 '      <span class="sep" aria-hidden="true"></span>', '      <span class="group">자세히</span>', *tabs[3:]])
sections = "\n".join(f'    <section id="{h}" class="view" aria-label="{title}">\n      <p class="guide">{guide}</p>\n      {scoped(svg, h)}\n    </section>'
                     for h, _, title, guide, svg in VIEWS)
active = "\n".join(
    f'    .frame:has(#{h}:target) .tab[href="#{h}"]' + (f', .frame:not(:has(.view:target)) .tab[href="#{h}"]' if i == 0 else "")
    + " { background: var(--ink); color: var(--paper); border-color: var(--ink); }"
    for i, (h, *_rest) in enumerate(VIEWS))
combined = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Baton 풀프로세스 순서도</title>
  <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{ --paper: #ffffff; --ink: #1a1a1a; --muted: #555555; --line: #d8d8d8; --font-sans: {SANS}; }}
    html, body {{ height: 100%; }}
    body {{ font-family: var(--font-sans); background: var(--paper); color: var(--ink); }}
    /* 16:9 화면 한 장: 위에 메뉴, 아래에 1280×720 그림을 화면 높이에 맞춰 넣는다 */
    .frame {{ height: 100vh; display: flex; flex-direction: column; padding: 12px 16px; gap: 8px; }}
    header {{ text-align: center; }}
    h1 {{ font-size: 20px; font-weight: 700; }}
    .intro {{ font-size: 14px; color: var(--muted); margin-top: 2px; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; align-items: center; }}
    .group {{ font-size: 12px; font-weight: 600; color: var(--muted); padding: 0 4px; }}
    .sep {{ width: 1px; height: 24px; background: var(--line); margin: 0 8px; }}
    .guide {{ font-size: 14px; color: var(--ink); text-align: center; max-width: 960px; line-height: 1.5; }}
    .tab {{ display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border: 1px solid var(--line); border-radius: 22px; color: var(--muted); background: var(--paper); font-size: 14px; font-weight: 500; text-decoration: none; }}
{active}
    .view {{ display: none; flex: 1; min-height: 0; }}
    .view:target, .frame:not(:has(.view:target)) .view:first-of-type {{ display: flex; flex-direction: column; align-items: center; gap: 4px; }}
    .view svg {{ width: 100%; flex: 1; min-height: 0; max-width: 1280px; aspect-ratio: 16 / 9; display: block; }}
  </style>
</head>
<body>
  <div class="frame">
    <header>
      <h1>baton 풀프로세스</h1>
      <p class="intro">기획서 한 장을 받아, 단계마다 사람의 확인을 거쳐 클릭되는 화면 시안까지 만드는 과정입니다.</p>
    </header>
    <nav aria-label="순서도 고르기">
{nav}
    </nav>
{sections}
  </div>
</body>
</html>
"""
OUT = Path(__file__).resolve().parent  # assets/
(OUT / "baton-process.html").write_text(combined, encoding="utf-8")
print("written", OUT / "baton-process.html")
