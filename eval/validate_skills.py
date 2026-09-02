"""크로스 플랫폼 스킬 검증 — `skills/*/SKILL.md` (실습서 Ch 38).

본편 §29의 검증 절차를 이 저장소용으로 옮긴 것. Agent Skills 개방 표준(SKILL.md +
frontmatter)을 지키는지, 플랫폼 종속 문법이 도메인/범용 스킬에 섞이지 않았는지 본다.

실행::

    python eval/validate_skills.py            # 또는 `just validate-skills`
    echo $?    # WARN/FAIL 있으면 1

검사 항목:
  - frontmatter 파싱 (name·description 존재, 최소 YAML 유효)
  - name 형식 (kebab-case, 디렉토리명과 일치)
  - description 길이 (>= 20자, "언제 쓰는지" 힌트 포함)
  - 본문 H1 (frontmatter 뒤 첫 비어있지 않은 줄이 '# ')
  - references/ 링크 (본문이 가리키는 파일이 실제 존재)
  - 플랫폼 종속 문법 ($ARGUMENTS 등)이 도메인/범용 스킬에 없음
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SKILLS = _ROOT / "skills"

# 절차(procedure) 스킬은 팀 도구 개념을 언급해도 되지만 문법 결합은 지양.
_PROCEDURE_SKILLS = {"gate-chapter-loop"}
_PLATFORM_TOKENS = ("$ARGUMENTS", "$1", "$2", "<<<", "claude_code_hook")
_KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
_WHEN_HINTS = ("사용", "에 쓴다", "when", "할 때", "조정", "온보딩", "작성")


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """아주 얕은 frontmatter 파서 (key: value 한 줄씩). 본문도 함께 반환."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    fm: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def _check(skill_dir: Path) -> list[str]:
    issues: list[str] = []
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return ["SKILL.md 없음"]
    text = md.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)

    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        issues.append("frontmatter에 name 없음")
    if not desc:
        issues.append("frontmatter에 description 없음")
    if name and not _KEBAB.match(name):
        issues.append(f"name '{name}' 이 kebab-case 아님")
    if name and name != skill_dir.name:
        issues.append(f"name '{name}' ≠ 디렉토리명 '{skill_dir.name}'")
    if desc and len(desc) < 20:
        issues.append("description 20자 미만")
    if desc and not any(h in desc for h in _WHEN_HINTS):
        issues.append("description에 '언제 쓰는지' 힌트 없음")

    first_body_line = next((ln for ln in body.splitlines() if ln.strip()), "")
    if not first_body_line.startswith("# "):
        issues.append("본문 첫 줄이 H1('# ...') 아님")

    for ref in re.findall(r"references/[A-Za-z0-9_./-]+", body):
        if not (skill_dir / ref).is_file():
            issues.append(f"references 링크 대상 없음: {ref}")

    if skill_dir.name not in _PROCEDURE_SKILLS:
        for tok in _PLATFORM_TOKENS:
            if tok in body:
                issues.append(f"플랫폼 종속 문법 '{tok}' — 도메인/범용 스킬엔 예시로만")
    return issues


def main() -> int:
    if not _SKILLS.is_dir():
        print("skills/ 디렉토리 없음")
        return 1
    dirs = sorted(p for p in _SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
    if not dirs:
        print("skills/*/SKILL.md 없음")
        return 1
    worst = 0
    width = max(len(f"skills/{p.name}") for p in dirs)
    for d in dirs:
        issues = _check(d)
        label = f"skills/{d.name}".ljust(width)
        if not issues:
            print(f"{label}  OK")
            continue
        worst = 1
        print(f"{label}  WARN")
        for it in issues:
            print(f"{'':{width}}  → {it}")
    return worst


if __name__ == "__main__":
    sys.exit(main())
