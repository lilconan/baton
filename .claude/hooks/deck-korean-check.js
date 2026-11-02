#!/usr/bin/env node
/*
 * deck-korean-check — baton 덱/프로토타입 HTML의 한국어 카피를 hanlint로 검사한다.
 *
 * PostToolUse(Edit|Write) 훅으로 붙는다. 저장된 파일이 output/**.html 일 때만 동작.
 * <style>·<script>·주석·태그·속성(onclick 등)을 걷어내고 한글이 든 카피 줄만 추린 뒤
 * `hanlint - --preset chat` 에 파이프한다. chat 프리셋은 구조 규칙(headingSkip·factListParagraph 등)을
 * 꺼서 단편 UI 카피에 생기는 오탐을 없애고, 문장 단위 규칙(번역투·이중피동·cliche·dash)만 남긴다.
 * 항상 exit 0(비차단). 발견이 있으면 hookSpecificOutput.additionalContext 로 사실만 되먹인다.
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

function readStdin() {
  try { return fs.readFileSync(0, 'utf8'); } catch (e) { return ''; }
}

let data;
try { data = JSON.parse(readStdin()); } catch (e) { process.exit(0); }

const fp = (data && data.tool_input && data.tool_input.file_path) || '';
if (!/\/output\/.*\.html$/.test(fp)) process.exit(0);

let html;
try { html = fs.readFileSync(fp, 'utf8'); } catch (e) { process.exit(0); }

// 1) 카피가 아닌 블록 제거 (head·style·script·주석)
html = html
  .replace(/<head[\s\S]*?<\/head>/i, '\n')
  .replace(/<style[\s\S]*?<\/style>/gi, '\n')
  .replace(/<script[\s\S]*?<\/script>/gi, '\n')
  .replace(/<!--[\s\S]*?-->/g, '\n');

// 2) 줄바꿈 태그 처리 + 인라인 태그는 공백으로(단어 붙음 방지), 나머지 태그는 줄 경계로
html = html.replace(/<br\s*\/?>/gi, '\n');
const INLINE = 'b|i|em|strong|span|a|code|mark|small|sub|sup|u|s';
html = html.replace(new RegExp('</?(?:' + INLINE + ')(?:\\s[^>]*)?>', 'gi'), ' ');
html = html.replace(/<[^>]+>/g, '\n');

// 3) 엔티티 일부 복원
html = html
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#0?39;/g, "'")
  .replace(/&middot;/g, '·');

// 4) 한글이 든 줄만, 공백 정리 + 연속 중복 제거
const HANGUL = /[가-힣]/;
const lines = [];
for (let raw of html.split('\n')) {
  const s = raw.replace(/\s+/g, ' ').trim();
  if (!s || !HANGUL.test(s)) continue;
  if (lines[lines.length - 1] !== s) lines.push(s);
}
// 조각마다 빈 줄로 분리해 서로 다른 카피가 한 문장으로 합쳐지지 않게 한다
const text = lines.join('\n\n');
if (!text.trim()) process.exit(0);

// 5) hanlint - --preset chat 로 검사
const label = path.basename(fp) + '.md';
let findings = '';
try {
  findings = execFileSync('hanlint', ['-', '--path', label, '--preset', 'chat', '--no-color', '--quiet'],
    { input: text, encoding: 'utf8' });
} catch (e) {
  findings = ((e.stdout || '') + (e.stderr || ''));
}
findings = findings.trim();
if (!findings) process.exit(0);

// 컨텍스트 과부하 방지: 6000자에서 자른다
const CAP = 6000;
if (findings.length > CAP) {
  findings = findings.slice(0, CAP) + '\n…(생략 — hanlint ' + path.basename(fp) + '.md 로 전체 확인)';
}

const ctx = 'hanlint가 방금 저장한 덱/프로토타입 HTML의 한국어 카피에서 센 Finding입니다(구조 규칙은 chat 프리셋으로 끔). 카피를 고쳐 다시 저장하면 다시 셉니다.\n' + findings;
process.stdout.write(JSON.stringify({
  hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: ctx }
}));
process.exit(0);
