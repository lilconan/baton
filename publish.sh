#!/usr/bin/env bash
# 비공개 작업 레포에서 뼈대만 골라 공개 레포로 발행
#
# 사용법:
#   bash publish.sh --dry-run          # 올라갈 파일 목록만 출력
#   bash publish.sh ["커밋 메시지"]    # 실제 발행
#
# 동작:
#   작업 레포(비공개)에는 뼈대와 프로젝트 산출물이 함께 있다.
#   HEAD 트리에서 산출물(output/, docs/ 아래 프로젝트 폴더)을 뺀 트리를
#   임시 인덱스로 만들고, 공개 레포 main 위에 커밋 하나로 얹어 push 한다.
#
# 왜 부모를 공개 레포 HEAD 하나만 두는가:
#   작업 레포 커밋을 부모로 넣으면 그 히스토리(산출물 포함)가 통째로
#   공개 레포에 딸려 간다. 공개 레포에는 발행 스냅샷만 쌓는다.

set -e

PUBLIC_URL="https://github.com/lilconan/baton.git"
REMOTE_NAME="public"
BRANCH="main"

# docs/ 아래에서 공개하는 폴더 (나머지 폴더는 프로젝트 산출물로 보고 뺀다)
DOCS_KEEP="_TEMPLATE"
# 통째로 빼는 경로
EXCLUDE=("output")

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

DRY_RUN=0
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=1
  shift
fi

# ── 공개용 트리 만들기 (임시 인덱스, 작업 트리는 건드리지 않음) ──
TMP_INDEX="$(mktemp)"
trap 'rm -f "$TMP_INDEX"' EXIT
export GIT_INDEX_FILE="$TMP_INDEX"
git read-tree HEAD

for p in "${EXCLUDE[@]}"; do
  git rm -r --cached -q --ignore-unmatch -- "$p"
done

# docs/ 바로 아래 폴더 중 DOCS_KEEP 이외는 전부 뺀다 (docs/*.md 파일은 유지)
git -c core.quotePath=false ls-files -- docs | awk -F/ 'NF>2 {print $2}' | sort -u | while read -r d; do
  [ "$d" = "$DOCS_KEEP" ] && continue
  git rm -r --cached -q -- "docs/$d"
done

# hanlint 기준선에는 산출물 문장이 인용돼 있으므로 공개 트리에 남은 파일 항목만 남긴다
if git ls-files --error-unmatch .hanlint-baseline.json >/dev/null 2>&1; then
  BLOB="$(git -c core.quotePath=false ls-files | python3 -c '
import json, subprocess, sys
kept = set(sys.stdin.read().splitlines())
raw = subprocess.run(["git", "cat-file", "blob", "HEAD:.hanlint-baseline.json"],
                     capture_output=True, check=True).stdout
d = json.loads(raw)
d["files"] = {k: v for k, v in d["files"].items() if k in kept}
sys.stdout.write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
' | git hash-object -w --stdin)"
  git update-index --cacheinfo "100644,$BLOB,.hanlint-baseline.json"
fi

TREE="$(git write-tree)"

if [ "$DRY_RUN" = 1 ]; then
  echo ""
  KEPT="$(git ls-files | wc -l | tr -d ' ')"
  ALL="$(git ls-tree -r --name-only HEAD | wc -l | tr -d ' ')"
  echo "  공개 레포에 올라갈 파일 (${KEPT}개, 빠지는 파일 $((ALL - KEPT))개):"
  echo ""
  git -c core.quotePath=false ls-files | sed 's/^/    /'
  echo ""
  exit 0
fi

# ── 커밋 안 된 변경 안내 — 발행은 HEAD 기준이다 ─────────
if ! GIT_INDEX_FILE= git diff --quiet HEAD; then
  echo ""
  echo "  참고: 커밋되지 않은 변경은 발행에 들어가지 않습니다 (HEAD 기준)."
fi

# ── 리모트 등록 (없을 때만) ────────────────────────────
if ! git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  echo "  리모트 등록: $REMOTE_NAME → $PUBLIC_URL"
  git remote add "$REMOTE_NAME" "$PUBLIC_URL"
fi

echo "  원격 상태 확인: $REMOTE_NAME/$BRANCH"
PARENT_ARGS=()
if git fetch -q "$REMOTE_NAME" "$BRANCH" 2>/dev/null; then
  REMOTE_HEAD="$(git rev-parse FETCH_HEAD)"
  if [ "$TREE" = "$(git rev-parse "$REMOTE_HEAD^{tree}")" ]; then
    echo ""
    echo "  변경 없음: 원격이 이미 최신입니다. ($REMOTE_HEAD)"
    echo ""
    exit 0
  fi
  PARENT_ARGS=(-p "$REMOTE_HEAD")
else
  echo "  원격 $BRANCH 브랜치가 없어 첫 커밋으로 발행합니다."
fi

MSG="${1:-publish: 뼈대 발행 ($(git rev-parse --short HEAD))}"
COMMIT="$(git commit-tree "$TREE" "${PARENT_ARGS[@]}" -m "$MSG")"

echo ""
echo "  발행 중: $COMMIT → $REMOTE_NAME/$BRANCH"
git push "$REMOTE_NAME" "$COMMIT:refs/heads/$BRANCH"

echo ""
echo "  발행 완료: $PUBLIC_URL"
echo ""
