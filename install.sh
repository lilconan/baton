#!/usr/bin/env bash
# Baton — Claude Code 에이전트·스킬 설치 스크립트
#
# 원격 설치:
#   curl -fsSL https://raw.githubusercontent.com/moonbo-debug/baton/main/install.sh | bash
#
# 로컬 설치 (레포 clone 후):
#   bash install.sh

set -e

# ── 설치 경로 ──────────────────────────────────────────
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
AGENTS_DIR="$CLAUDE_DIR/agents"
SKILLS_DIR="$CLAUDE_DIR/skills"

# ── 소스 경로 (원격 or 로컬) ───────────────────────────
REMOTE_BASE="https://raw.githubusercontent.com/moonbo-debug/baton/main"

# 에이전트·스킬 원본 위치 (레포 루트 기준)
SRC_AGENTS=".claude/agents"
SRC_SKILLS=".claude/skills"

# 스크립트가 로컬 파일로 실행되면 로컬 경로 사용
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/$SRC_AGENTS/baton.md" ]; then
  USE_LOCAL=true
  LOCAL_BASE="$SCRIPT_DIR"
else
  USE_LOCAL=false
fi

# ── 유틸 함수 ──────────────────────────────────────────
download() {
  local src="$1"
  local dst="$2"
  if [ "$USE_LOCAL" = true ]; then
    cp "$LOCAL_BASE/$src" "$dst"
  else
    curl -fsSL "$REMOTE_BASE/$src" -o "$dst"
  fi
}

# ── 설치 ───────────────────────────────────────────────
echo ""
echo "  Baton 설치 중..."
echo ""

mkdir -p "$AGENTS_DIR" "$SKILLS_DIR"

AGENTS=(
  "baton"
  "baton-interpreter"
  "baton-designer"
  "baton-builder"
)
for name in "${AGENTS[@]}"; do
  echo "  → agents/$name.md"
  download "$SRC_AGENTS/$name.md" "$AGENTS_DIR/$name.md"
done

SKILLS=("baton-tokens" "baton-shell")
for name in "${SKILLS[@]}"; do
  echo "  → skills/$name.md"
  download "$SRC_SKILLS/$name.md" "$SKILLS_DIR/$name.md"
done

echo ""
echo "  설치 완료!"
echo ""
echo "  사용 방법:"
echo "  1. 새 프로젝트 루트에 CLAUDE.md + PROCESS.md 복사"
echo "     (PROCESS.md 는 STEP 0 입력 게이트가 참조하는 필수 파일 —"
echo "      없으면 FIXED/OPEN 분해 기준을 못 읽습니다)"
if [ "$USE_LOCAL" = true ]; then
  echo "     cp $LOCAL_BASE/CLAUDE.md ./CLAUDE.md"
  echo "     cp $LOCAL_BASE/PROCESS.md ./PROCESS.md"
else
  echo "     curl -fsSL $REMOTE_BASE/CLAUDE.md -o CLAUDE.md"
  echo "     curl -fsSL $REMOTE_BASE/PROCESS.md -o PROCESS.md"
fi
echo "  2. Claude Code 실행 후 '와이어프레임 만들어줘' 또는 '/baton'"
echo ""
