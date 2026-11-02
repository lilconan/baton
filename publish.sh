#!/usr/bin/env bash
# 비공개 작업 레포에서 뼈대만 골라 공개 레포로 발행
#
# 사용법:
#   bash publish.sh --dry-run          # 올라갈 파일 목록만 출력
#   bash publish.sh ["커밋 메시지"]    # 실제 발행
#
# 동작:
#   작업 레포(비공개)에는 뼈대와 프로젝트 산출물이 함께 있다.
#   HEAD 트리에서 PUBLISH 목록에 적힌 경로만 골라 임시 인덱스로 트리를 만들고,
#   공개 레포 main 위에 커밋 하나로 얹어 push 한다.
#
# 왜 허용 목록인가:
#   "뺄 목록" 방식은 산출물이 예상 밖 위치에 생기면 그대로 공개된다.
#   허용 목록은 새 뼈대 파일을 빠뜨릴 수는 있어도 산출물을 내보내지는 않는다.
#   빠진 뼈대 후보는 발행할 때마다 아래에 따로 알려 준다.
#
# 왜 부모를 공개 레포 HEAD 하나만 두는가:
#   작업 레포 커밋을 부모로 넣으면 그 히스토리(산출물 포함)가 통째로
#   공개 레포에 딸려 간다. 공개 레포에는 발행 스냅샷만 쌓는다.

set -eo pipefail

PUBLIC_URL="https://github.com/lilconan/baton.git"
REMOTE_NAME="public"
BRANCH="main"

# 공개하는 경로 (폴더는 하위 전체). 새 뼈대 파일을 만들면 여기에 추가한다.
PUBLISH=(
  ".claude/agents" ".claude/skills" ".claude/hooks" ".claude/settings.json"
  ".codex"
  ".gitignore" ".hanlint-baseline.json" "hanlint.toml"
  "AGENTS.md" "BACKLOG.md" "CLAUDE.md" "CONTEXT.md"
  "PROCESS.md" "PROCESS_CHANGELOG.md" "README.md" "RUNBOOK.md" "START_HERE.md"
  "docs/_TEMPLATE" "docs/핵심-설계-규칙.md" "docs/한국어-카피-가드레일.md"
  "assets" "install.sh" "publish.sh" "shell.html"
  "memory" "tools"
)

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
git read-tree --empty
git ls-tree -r -z HEAD -- "${PUBLISH[@]}" | git update-index -z --index-info

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

# output/·docs/ 프로젝트 폴더가 아닌데 PUBLISH 목록에도 없는 파일 = 빠뜨린 뼈대일 수 있다
UNLISTED="$(git -c core.quotePath=false ls-tree -r --name-only HEAD \
  | grep -vE '^(output/|docs/[^/]+/)' \
  | grep -vxF -f <(git -c core.quotePath=false ls-files) || true)"
if [ -n "$UNLISTED" ]; then
  echo ""
  echo "  참고: 공개 목록(PUBLISH)에 없어 빠지는 파일입니다. 뼈대라면 publish.sh에 추가하세요."
  echo "$UNLISTED" | sed 's/^/    /'
fi

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
