"""실행 기록 요약 한 줄 (goal.md R6). 점수 계산에는 쓰지 않는다."""
from collections import Counter

from .events import first_user_text, messages, split_turns, system_sections, tool_calls

USAGE_KEYS = ("input", "output", "cacheRead", "cacheWrite", "reasoning")


def usage_sum(events: list) -> dict:
    tot = {k: 0 for k in USAGE_KEYS}
    cost = 0.0
    max_ctx = 0
    for m in messages(events, "assistant"):
        u = m.get("usage") or {}
        for k in USAGE_KEYS:
            tot[k] += u.get(k) or 0
        cost += (u.get("cost") or {}).get("total") or 0
        max_ctx = max(max_ctx, (u.get("input") or 0) + (u.get("cacheRead") or 0) + (u.get("cacheWrite") or 0))
    return {**tot, "cost": round(cost, 6), "max_input": max_ctx}


TESTED_SKILLS = ".pi/agent/skills/"


def _path_of(c):
    return str(c["args"].get("path") or c["args"].get("file_path") or "")


def summarize_candidate(records: list, context_window: int, arm: dict | None = None) -> dict:
    turns = split_turns(records)
    events = [e for t in turns for e in t["events"]]
    calls = tool_calls(events)
    u = usage_sum(events)
    read = [_path_of(c) for c in calls if c["name"] == "read"]
    written = [_path_of(c) for c in calls if c["name"] in ("write", "edit")]
    skill_reads = sorted({p for p in read if p.endswith("SKILL.md")} |
                         {str(c["args"].get("command"))[:200] for c in calls
                          if c["name"] == "bash" and "SKILL.md" in str(c["args"].get("command", ""))})
    first = turns[0]["events"] if turns else []
    sections = system_sections(first)
    cmd = (turns[0]["end"] or {}).get("cmd", []) if turns else []
    return {
        "turns": len(turns),
        "tokens": {k: u[k] for k in USAGE_KEYS},
        "cost": u["cost"],
        "max_context_ratio": round(u["max_input"] / context_window, 4) if context_window else None,
        "compactions": sum(e.get("type") == "compaction_start" for e in events),
        "retries": sum(e.get("type") == "auto_retry_start" for e in events),
        "tool_calls": dict(Counter(c["name"] for c in calls)),
        "tool_calls_total": len(calls),
        "failed_calls": sum(bool(c.get("isError")) for c in calls),
        "files_read": sorted(set(read)),
        "files_written": sorted(set(written)),
        "skill_md_read": skill_reads,
        # 시험 대상 스킬은 실행별 설정 폴더(.pi/agent/skills/)에 있다. 과제 3 작업 폴더의 옛 스킬은 과제 내용이다
        "tested_skill_md_read": [s for s in skill_reads if TESTED_SKILLS in s],
        "duration_s": round(sum((t["end"] or {}).get("duration_s") or 0 for t in turns), 1),
        # C4 스킬 로드 확인용 (점수 아님)
        "skill_load": {
            "first_user_starts_with_skill": first_user_text(first).startswith("<skill name="),
            "first_user_skill_name": first_user_text(first)[13:40].split('"')[0]
            if first_user_text(first).startswith("<skill name=") else None,
            "grill_skill_md_read": any("workflow-grill/SKILL.md" in s for s in skill_reads if TESTED_SKILLS in s),
            "sections_skills_count": sections.get("skills", "").count("<name>") if sections.get("skills") else 0,
            "sections_has_skills": bool(sections.get("skills")),
            "sections_project_context": bool(sections.get("project_context")),
            "project_context_paths": _context_paths(sections.get("project_context") or ""),
            "cmd_no_skills": "--no-skills" in cmd,
            "cmd_no_context_files": "--no-context-files" in cmd,
            "cmd_no_extensions": "--no-extensions" in cmd,
            "cmd_no_approve": "--no-approve" in cmd,
        },
    }


def _context_paths(s: str) -> list:
    import re
    return re.findall(r'path="([^"]+)"', s)


def summarize_mock(records: list) -> dict:
    events = [r for r in records if not r.get("_runner")]
    u = usage_sum(events)
    calls = sum(1 for r in records if r.get("_runner") == "call_start")
    return {"calls": calls, "tokens": {k: u[k] for k in USAGE_KEYS}, "cost": u["cost"]}
