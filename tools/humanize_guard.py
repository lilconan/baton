#!/usr/bin/env python3
"""윤문 보호 장치 — 원문 인용·ID·링크·코드를 윤문 엔진에서 지킨다

humanize-korean(im-not-ai) 같은 윤문 엔진은 "말했다·밝혔다" 표지가 붙은 인용만 보호한다.
baton 문서의 인용은 `"원문" [출처 · 열람일]` 형태라 표지가 없어 윤문 대상이 될 수 있다.
CLAUDE.md 규칙 7(인용은 원문 그대로)을 지키려고, 윤문 전에 보호 대상을 자리표시자로 바꾸고
윤문 뒤에 되돌린 다음, 원본과 결과를 대조한다.

  # 1) 보호 대상을 ⟦P001⟧ 자리표시자로 바꾼 사본 + 대응표
  python3 tools/humanize_guard.py mask output/foo.md --run-dir _workspace/run1

  # 2) 윤문본의 자리표시자를 원래 문자열로 되돌림
  python3 tools/humanize_guard.py unmask _workspace/run1/final.md --run-dir _workspace/run1 --out _workspace/run1/restored.md

  # 3) 원본과 결과 대조 (하나라도 다르면 exit 1)
  python3 tools/humanize_guard.py verify output/foo.md _workspace/run1/restored.md

★ 보호 대상
  코드 블록, 인라인 코드, 마크다운 링크 대상(URL), 맨 URL, 큰따옴표 인용("…" “…”),
  인용 ID(Q-01, V-31, PN-1, U-12 …), 열람일 표기([열람 2026-10-26])

★ verify 가 보는 것
  보호 대상 전부가 같은 횟수로 남았는가 / 숫자 집합 / 표 행 수 / 제목(#) 줄 수
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

# 순서가 중요하다. 넓은 것(코드 블록)부터 잡아야 안쪽 패턴이 겹쳐 잡히지 않는다.
PATTERNS = [
    ("codeblock", re.compile(r"```.*?```", re.S)),
    ("code", re.compile(r"`[^`\n]+`")),
    ("linktarget", re.compile(r"\]\([^)\s]+\)")),
    ("url", re.compile(r"https?://[^\s)\]|>]+")),
    ("quote", re.compile(r"\"[^\"\n]+\"|“[^”\n]+”")),
    ("viewed", re.compile(r"\[?열람 \d{4}-\d{2}-\d{2}\]?")),
    ("id", re.compile(r"(?<![A-Za-z0-9-])[A-Z]{1,3}-\d{1,3}(?![0-9])")),
]
PH = "⟦P{:03d}⟧"
PH_RE = re.compile(r"⟦P(\d{3})⟧")


def protected_spans(text):
    """겹치지 않는 보호 구간 목록 [(start, end, kind)]."""
    taken = []
    for kind, pat in PATTERNS:
        for m in pat.finditer(text):
            s, e = m.span()
            if any(s < te and ts < e for ts, te, _ in taken):
                continue
            taken.append((s, e, kind))
    return sorted(taken)


def mask(src, run_dir):
    text = Path(src).read_text(encoding="utf-8")
    spans = protected_spans(text)
    out, table, pos = [], {}, 0
    for i, (s, e, kind) in enumerate(spans, 1):
        out.append(text[pos:s])
        key = PH.format(i)
        out.append(key)
        table[key] = {"kind": kind, "text": text[s:e]}
        pos = e
    out.append(text[pos:])
    run = Path(run_dir)
    run.mkdir(parents=True, exist_ok=True)
    (run / "masked.md").write_text("".join(out), encoding="utf-8")
    (run / "mask_table.json").write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    kinds = collections.Counter(v["kind"] for v in table.values())
    print(f"보호 {len(table)}곳: " + " · ".join(f"{k} {n}" for k, n in kinds.most_common()))
    print(f"저장: {run / 'masked.md'}, {run / 'mask_table.json'}")
    return 0


def unmask(src, run_dir, out):
    text = Path(src).read_text(encoding="utf-8")
    table = json.loads((Path(run_dir) / "mask_table.json").read_text(encoding="utf-8"))
    seen = set(PH_RE.findall(text))
    missing = [k for k in table if k[2:5] not in seen]
    text = PH_RE.sub(lambda m: table.get(m.group(0), {"text": m.group(0)})["text"], text)
    Path(out).write_text(text, encoding="utf-8")
    print(f"복원: {out}")
    if missing:
        print(f"⚠ 윤문본에서 사라진 자리표시자 {len(missing)}개: " + ", ".join(missing[:10]), file=sys.stderr)
        for k in missing[:10]:
            print(f"   {k} = {table[k]['text'][:80]}", file=sys.stderr)
        return 1
    return 0


def _profile(text):
    return {
        "protected": collections.Counter(text[s:e] for s, e, _ in protected_spans(text)),
        "numbers": collections.Counter(re.findall(r"\d+(?:[.,]\d+)?", text)),
        "table_rows": sum(1 for l in text.splitlines() if l.lstrip().startswith("|")),
        "headings": sum(1 for l in text.splitlines() if re.match(r"#{1,6} ", l)),
    }


def verify(before, after):
    a = _profile(Path(before).read_text(encoding="utf-8"))
    b = _profile(Path(after).read_text(encoding="utf-8"))
    problems = []
    lost = a["protected"] - b["protected"]
    added = b["protected"] - a["protected"]
    if lost:
        problems.append(f"보호 대상이 사라지거나 바뀜 {sum(lost.values())}곳: " + " | ".join(t[:60] for t in list(lost)[:8]))
    if added:
        problems.append(f"원본에 없던 보호 대상이 생김 {sum(added.values())}곳: " + " | ".join(t[:60] for t in list(added)[:8]))
    if a["numbers"] != b["numbers"]:
        diff = (a["numbers"] - b["numbers"]) + (b["numbers"] - a["numbers"])
        problems.append("숫자가 달라짐: " + ", ".join(list(diff)[:12]))
    for k, label in (("table_rows", "표 행 수"), ("headings", "제목 줄 수")):
        if a[k] != b[k]:
            problems.append(f"{label} {a[k]} → {b[k]}")
    if problems:
        print("❌ 검증 실패")
        for p in problems:
            print(" - " + p)
        return 1
    print(f"✅ 검증 통과 — 보호 대상 {sum(a['protected'].values())}곳 · 숫자 {sum(a['numbers'].values())}개 · "
          f"표 행 {a['table_rows']} · 제목 {a['headings']} 모두 원본과 같음")
    return 0


def main():
    ap = argparse.ArgumentParser(description="윤문 보호 장치 (CLAUDE.md 규칙 7)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mask", help="보호 대상을 자리표시자로 바꾼 사본 만들기")
    m.add_argument("src")
    m.add_argument("--run-dir", required=True)
    u = sub.add_parser("unmask", help="자리표시자를 원래 문자열로 되돌리기")
    u.add_argument("src")
    u.add_argument("--run-dir", required=True)
    u.add_argument("--out", required=True)
    v = sub.add_parser("verify", help="원본과 결과 대조")
    v.add_argument("before")
    v.add_argument("after")
    a = ap.parse_args()
    if a.cmd == "mask":
        return mask(a.src, a.run_dir)
    if a.cmd == "unmask":
        return unmask(a.src, a.run_dir, a.out)
    return verify(a.before, a.after)


if __name__ == "__main__":
    sys.exit(main())
