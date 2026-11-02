#!/usr/bin/env bash
# baton/ 를 공개 레포(baton) 루트로 발행
#
# 사용법:
#   bash baton/publish.sh ["커밋 메시지"]
#
# 동작:
#   모노레포의 baton/ 서브트리를 잘라내(split) 공개 레포
#   main 브랜치 루트로 발행한다. dist/ 사본을 두던 구 sync.sh 대체 —
#   중복 사본이 없고 원본이 유일한 진실이다.
#
# 왜 subtree push 를 그냥 안 쓰는가:
#   공개 레포 히스토리는 구 dist 커밋과 서브트리 히스토리를 접목한 것이라
#   `git subtree push` 가 만드는 split 커밋의 조상이 아니다. 그래서 매번
#   거부된다. 대신 split 트리를 그대로 담은 머지 커밋을 만들어 push 한다.

set -e

REMOTE_URL="https://github.com/moonbo-debug/baton.git"
REMOTE_NAME="baton"
PREFIX="baton"
BRANCH="main"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ── 리모트 등록 (없을 때만) ────────────────────────────
if ! git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  echo "  리모트 등록: $REMOTE_NAME"
  git remote add "$REMOTE_NAME" "$REMOTE_URL"
fi

# ── 커밋 안 된 변경 확인 — split 은 커밋된 내용만 본다 ──
if ! git diff --quiet -- "$PREFIX" || ! git diff --cached --quiet -- "$PREFIX"; then
  echo ""
  echo "  중단: $PREFIX/ 에 커밋되지 않은 변경이 있습니다."
  echo "  먼저 커밋하세요 — 발행은 커밋된 내용만 반영합니다."
  echo ""
  git status --short -- "$PREFIX"
  exit 1
fi

echo ""
echo "  서브트리 분리 중: $PREFIX/"
SPLIT="$(git subtree split --prefix="$PREFIX")"
TREE="$(git rev-parse "$SPLIT^{tree}")"

echo "  원격 상태 확인: $REMOTE_NAME/$BRANCH"
git fetch -q "$REMOTE_NAME" "$BRANCH"
REMOTE_HEAD="$(git rev-parse FETCH_HEAD)"
REMOTE_TREE="$(git rev-parse "$REMOTE_HEAD^{tree}")"

# ── 내용이 같으면 빈 커밋을 만들지 않는다 ──────────────
if [ "$TREE" = "$REMOTE_TREE" ]; then
  echo ""
  echo "  변경 없음 — 원격이 이미 최신입니다. ($REMOTE_HEAD)"
  echo ""
  exit 0
fi

MSG="${1:-publish: baton 서브트리 발행}"

# 트리는 split 결과 그대로, 부모는 원격 HEAD + split 팁.
# → 공개 레포 히스토리가 이어지고(fast-forward) force push 가 필요 없다.
MERGE="$(git commit-tree "$TREE" -p "$REMOTE_HEAD" -p "$SPLIT" -m "$MSG")"

echo ""
echo "  발행 중: $MERGE → $REMOTE_NAME/$BRANCH"
git push "$REMOTE_NAME" "$MERGE:refs/heads/$BRANCH"

echo ""
echo "  발행 완료: $REMOTE_URL"
echo ""
