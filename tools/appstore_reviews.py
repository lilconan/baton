#!/usr/bin/env python3
"""P0 1차 VOC 수집기 — Apple App Store 공개 리뷰 RSS

PROCESS.md §4 "P0 긁는 순서"의 실행 도구.
인증·API 키 불필요. Apple 공개 RSS(itunes.apple.com/.../rss/customerreviews)만 사용한다.

  # 1) 경쟁앱 ID 찾기
  python3 tools/appstore_reviews.py search "다이어트" --country kr

  # 2) 리뷰 수집 → 인용 표 (2년 이내 · 1~2★)
  python3 tools/appstore_reviews.py pull 634598719 --country kr

  # 3) 여러 앱을 한 번에
  python3 tools/appstore_reviews.py pull 634598719 347184248 981460948 --out docs/foo/p0.md

★ 왜 10페이지를 전부 받아 로컬에서 거르는가
  `sortby=mostrecent` 가 실제로는 최신순이 아니다. 2026-09-09 실측(4개 앱, 각 500건):
  전체의 78~94%가 2년 초과였고, `sortby=mostcritical` 은 HTTP 500 으로 죽어 있다.
  따라서 "저평점만" 또는 "최신만" 골라 받는 방법이 없다. 전량을 받아 여기서 거른다.

★ 실측 수율 (2026-09-09, 한국 스토어)
  앱당 500건 수집 → 2년 이내 1~2★ 는 4~15건.
  §4-2 포화 하한(12건 / 세그먼트 2개 이상이면 16건)을 채우려면
  §4-1이 요구하는 대로 **경쟁앱 3개 이상**을 돌려야 한다.

★ Google Play 는 공개 리뷰 피드가 없다 (§4 한계로 기록할 것).
"""
import argparse
import datetime
import json
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (research; PROCESS.md §4)"}
TODAY = datetime.date.today()


def _get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except (OSError, ValueError) as e:  # 네트워크·HTTP 오류 / JSON·인코딩 오류
            if i == retries - 1:
                return {"__error__": str(e)}
            time.sleep(1.5 * (i + 1))  # Apple 은 egress IP 단위로 강하게 스로틀한다


def search(term, country, limit):
    q = urllib.parse.urlencode({"term": term, "country": country,
                                "entity": "software", "limit": limit})
    d = _get(f"https://itunes.apple.com/search?{q}")
    if "__error__" in d:
        print(f"검색 실패: {d['__error__']}", file=sys.stderr)
        return 1
    print(f"{'trackId':>12}  {'평점':>5}  {'리뷰수':>7}  앱 이름")
    for r in d.get("results", []):
        print(f"{r['trackId']:>12}  {r.get('averageUserRating', 0):>5.2f}  "
              f"{r.get('userRatingCount', 0):>7}  {r['trackName'][:52]}")
    return 0


def app_name(app_id, country):
    """lookup API로 앱 이름을 받는다. RSS feed title은 앱 이름이 아니다."""
    d = _get(f"https://itunes.apple.com/lookup?id={app_id}&country={country}")
    try:
        return d["results"][0]["trackName"]
    except (KeyError, IndexError, TypeError):
        return None


PAGE_SIZE = 50
EMPTY_RETRIES = 3


def _entries(d):
    e = d.get("feed", {}).get("entry", [])
    return [e] if isinstance(e, dict) else e


def pull_app(app_id, country, pages):
    """10페이지 전량 수집. (rows, meta) 반환.

    2026-10-22부터 RSS가 간헐적으로 빈 피드를 준다. 같은 페이지를 다시 받으면 대체로 채워지므로
    빈 페이지는 재시도하고, 그래도 비면 "데이터 끝"인지 "장애로 잘림"인지 구분해 meta에 남긴다.
    """
    rows, name, err = [], app_name(app_id, country), None
    prev_count = PAGE_SIZE
    for p in range(1, pages + 1):
        url = (f"https://itunes.apple.com/{country}/rss/customerreviews/"
               f"page={p}/id={app_id}/sortby=mostrecent/json")
        for attempt in range(EMPTY_RETRIES):
            d = _get(url)
            if "__error__" in d or _entries(d):
                break
            time.sleep(2 * (attempt + 1))
        if "__error__" in d:
            err = f"{p}페이지 요청 실패: {d['__error__']}"
            break
        e = _entries(d)
        if not e:
            # 앞 페이지가 꽉 찼는데 비었다면 데이터 끝이 아니라 빈 피드 장애로 본다
            if prev_count >= PAGE_SIZE:
                err = f"{p}페이지가 재시도 {EMPTY_RETRIES}회 뒤에도 빈 피드"
            break
        prev_count = len(e)
        for x in e:
            rows.append({
                "rating": int(x["im:rating"]["label"]),
                "title": x["title"]["label"],
                "body": x["content"]["label"],
                "date": x.get("updated", {}).get("label", "")[:10],
                "author": x.get("author", {}).get("name", {}).get("label", ""),
                "version": x.get("im:version", {}).get("label", ""),
            })
        time.sleep(0.4)
    return rows, {"name": name or f"app {app_id}", "id": app_id,
                  "country": country, "error": err}


def render(app_id, country, pages, max_age_days, max_rating):
    rows, meta = pull_app(app_id, country, pages)
    if not rows:
        return f"\n## {meta['name']} (id={app_id})\n\n> ❌ 수집 실패 — {meta['error']}\n", None

    cut = TODAY - datetime.timedelta(days=max_age_days)
    def d(r):
        try:
            return datetime.date(*map(int, r["date"].split("-")))
        except (ValueError, TypeError):
            return None

    low = [r for r in rows if r["rating"] <= max_rating]
    fresh = [r for r in low if d(r) and d(r) >= cut]
    stale = [r for r in low if d(r) and d(r) < cut]
    years = {}
    for r in rows:
        years[r["date"][:4]] = years.get(r["date"][:4], 0) + 1

    out = [f"\n## {meta['name']}  ·  App Store {country.upper()}  ·  id={app_id}\n",
           f"- 수집 {len(rows)}건 (RSS 최대 {pages}페이지)",
           f"- 저평점 1~{max_rating}★ **{len(low)}건**  ·  그중 {max_age_days//365}년 이내 **{len(fresh)}건** (↓시점 강등 대상 {len(stale)}건)",
           "- 연도 분포: " + " · ".join(f"{y} {c}" for y, c in sorted(years.items()) if y),
           *([f"- ⚠ 수집이 중간에 끊김: {meta['error']}. 위 수치는 일부 표본이다 (§4-3 ↓편향에 기록)"]
             if meta["error"] else []),
           f"- 열람 {TODAY.isoformat()}\n",
           "| # | 인용 원문 | 별점 | 작성일 | 버전 | 등급 |",
           "|---|---|---|---|---|---|"]
    for i, r in enumerate(fresh, 1):
        body = " ".join(r["body"].split())
        if len(body) > 160:
            body = body[:160] + "…"
        out.append(f"| {i} | \"{body}\" | {r['rating']}★ | {r['date']} | {r['version']} | ✅ P0 |")
    if not fresh:
        out.append("| — | (2년 이내 저평점 없음) | | | | |")
    if stale:
        out.append(f"\n> ↓시점 강등 {len(stale)}건은 2년 초과라 제외했다. "
                   f"쓰려면 `✅ P0 ↓시점` 으로 표기하고 등급 집계에서 한 칸 낮춘다 (§4-3).")
    return "\n".join(out) + "\n", {"total": len(rows), "low": len(low),
                                   "fresh": len(fresh), "stale": len(stale)}


def main():
    ap = argparse.ArgumentParser(description="P0 1차 VOC 수집기 (PROCESS.md §4)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="앱 이름으로 trackId 찾기")
    s.add_argument("term")
    s.add_argument("--country", default="kr")
    s.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("pull", help="리뷰 수집 → 인용 표")
    p.add_argument("app_ids", nargs="+")
    p.add_argument("--country", default="kr")
    p.add_argument("--pages", type=int, default=10)
    p.add_argument("--max-age-days", type=int, default=730, help="기본 730일(2년) — §4-3 ↓시점 기준")
    p.add_argument("--max-rating", type=int, default=2, help="기본 2★ 이하 — §4 P0 긁는 순서")
    p.add_argument("--out", help="마크다운 저장 경로")

    a = ap.parse_args()
    if a.cmd == "search":
        return search(a.term, a.country, a.limit)

    chunks = [(f"# P0 1차 VOC 수집 결과\n\n> 수집: `tools/appstore_reviews.py` · Apple 공개 리뷰 RSS\n"
               f"> 기준: {a.max_rating}★ 이하 · 최근 {a.max_age_days//365}년 이내 · 열람 {TODAY.isoformat()}\n")]
    tot = {"total": 0, "low": 0, "fresh": 0, "stale": 0}
    for aid in a.app_ids:
        md, st = render(aid, a.country, a.pages, a.max_age_days, a.max_rating)
        chunks.append(md)
        if st:
            for k in tot:
                tot[k] += st[k]

    chunks.append(f"\n---\n\n## 합계\n\n"
                  f"| 항목 | 값 |\n|---|---|\n"
                  f"| 앱 수 | {len(a.app_ids)} |\n"
                  f"| 총 수집 | {tot['total']}건 |\n"
                  f"| 저평점 | {tot['low']}건 |\n"
                  f"| **P0 인용 가능 (강등 없음)** | **{tot['fresh']}건** |\n"
                  f"| ↓시점 강등 대상 | {tot['stale']}건 |\n\n"
                  f"§4-2 포화 하한: 12건(단일 세그먼트) / 16건(세그먼트 2개 이상) → "
                  f"{'✅ 충족' if tot['fresh'] >= 12 else '⚠ 미달 — 경쟁앱을 더 돌린다'}\n\n"
                  f"### 반드시 함께 기록할 표본 편향 (§4-3 ↓편향)\n"
                  f"- Apple 공개 RSS는 스토어별 **최근 약 500건**만 노출한다. 전체 리뷰 모수가 아니다.\n"
                  f"- **Google Play 는 공개 리뷰 피드가 없다.** iOS 편향이 남는다.\n"
                  f"- `sortby=mostcritical` 은 현재 HTTP 500 (2026-09-09 확인). 저평점만 골라 받을 수 없다.\n")

    md = "".join(chunks)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"저장: {a.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
