"""과정 준수 결정적 검사 8개 (goal.md R3). 저장된 기록만 보므로 다시 돌려도 같은 결과가 나온다."""
import re

from ..events import content_text, has_question

GOAL_IN_DOTGOAL = re.compile(r"^\.goal/[^/]+/goal\.md$", re.I)
SECTIONS = {   # 스킬이 정한 이름 + 한국어 동의어
    "Objective": ["objective", "목표", "목적"],
    "Deliverable": ["deliverable", "산출물", "결과물"],
    "Requirements": ["requirements", "requirement", "요구사항", "요구 사항"],
    "Constraints": ["constraints", "constraint", "제약", "제약사항", "제약 조건"],
    "Out of scope": ["out of scope", "out-of-scope", "범위 밖", "범위 제외", "제외 범위", "하지 않을 것"],
    "Evaluation": ["evaluation", "평가", "평가 기준"],
}
MARKS = {
    "합의": r"(\[|\*\*|^|\s)(합의|확정|agreed|decided|confirmed)(\]|\*\*|\s|:|$| Q)",
    "미결정": r"(\[|\*\*|^|\s)(미결정|미정|열린 질문|open question|undecided|tbd)(\]|\*\*|\s|:|$| Q)",
    "가정": r"(\[|\*\*|^|\s)(가정|assumption|assumed)(\]|\*\*|\s|:|$)",
}
# Evaluation을 절 대신 요구사항·제약 항목 아래에 적은 줄 ("- Evaluation — Criteria: ...", "- 평가: ...")
INLINE_EVAL = re.compile(r"^\s*(?:[-*]|\d+[.)])\s*(?:\*\*)?\s*(?:evaluation|평가(?:\s*기준)?)\b", re.I | re.M)
NUMBERED = re.compile(r"^\s*(?:[-*>]\s*)?(?:\*\*)?\s*(?:Q\s*\d+|\d+[.)]|\(\d+\))", re.I)
RECOMMEND = re.compile(r"➡️|추천|권장|제안|recommend", re.I)
READONLY_BASH = re.compile(r"^\s*(cd\s+\S+\s*&&\s*)?(ls|cat|head|tail|grep|rg|find|wc|pwd|tree|sed -n|git (status|log|diff|show))\b")

CHECKS = ["c1_goal_location", "c2_six_sections", "c3_numbered_recommended", "c4_one_round_wait",
          "c5_goal_updated_each_round", "c6_status_marks", "c7_no_edit_outside_goal", "c8_confirm_before_finish"]
LABELS = {
    "c1_goal_location": "1 goal.md가 .goal/<이름>/ 아래",
    "c2_six_sections": "2 여섯 절",
    "c3_numbered_recommended": "3 질문 번호·추천 답",
    "c4_one_round_wait": "4 한 턴에 한 라운드, 묻고 기다림",
    "c5_goal_updated_each_round": "5 라운드마다 goal.md 갱신",
    "c6_status_marks": "6 합의·미결정·가정 표기",
    "c7_no_edit_outside_goal": "7 .goal/ 밖 수정 없음",
    "c8_confirm_before_finish": "8 끝내기 전 사용자 확인",
}


def _res(ok, detail):
    return {"pass": bool(ok), "detail": detail}


def c1_goal_location(r):
    p = r.meta.get("goal_path")
    return _res(p and GOAL_IN_DOTGOAL.match(p), p or "goal.md 없음")


def headings(text: str) -> list:
    return [re.sub(r"[#*`]|^\d+[.)]\s*", "", m.group(1)).strip().lower()
            for m in re.finditer(r"^#{1,6}\s+(.+)$", text or "", re.M)]


def c2_six_sections(r):
    """스킬은 Evaluation을 "Requirements와 Constraints 항목마다" 적으라고만 해서, 항목 아래에 적은 것도 인정한다(2026-10-23 결정)."""
    hs = headings(r.goal_text or "")
    missing = [k for k, names in SECTIONS.items() if not any(any(n in h for n in names) for h in hs)]
    inline = "Evaluation" in missing and bool(INLINE_EVAL.search(r.goal_text or ""))
    if inline:
        missing.remove("Evaluation")
    detail = f"빠진 절: {missing}" if missing else "6개 모두" + (" (Evaluation은 항목 아래)" if inline else "")
    return _res(r.goal_text and not missing, detail)


def question_turns(r) -> list:
    """질문 턴: 그 턴에 모의 사용자가 질문을 하나 이상 읽어 낸 턴(마무리 확인만 있는 턴은 제외).
    대답이 없는 마지막 턴은 물음표 기준."""
    out = []
    for d in r.assistant_turns:
        rep = r.reply_after(d["n"])
        if rep is not None:
            if rep.get("items"):
                out.append(d)
        elif d.get("has_question"):
            out.append(d)
    return out


def _turn_format_ok(text: str, n_items: int = 0):
    """n_items: 모의 사용자가 이 턴에서 읽어 낸 질문 수(물음표 없는 질문도 센다)."""
    if "❓" in text:
        blocks = [b.split("\n---")[0] for b in text.split("❓")[1:]]
        bad = [i + 1 for i, b in enumerate(blocks) if not (re.search(r"Q\s*\d+", b) and RECOMMEND.search(b))]
        return not bad, f"❓ {len(blocks)}개 중 번호·추천 없음 {bad}" if bad else f"❓ {len(blocks)}개"
    qlines = [l for l in text.splitlines() if has_question(l)]
    if not qlines:
        return False, f"질문 형식 인식 불가(❓·물음표 없음, 모의 사용자가 읽은 질문 {n_items}개)"
    unnumbered = [l.strip()[:40] for l in qlines if not NUMBERED.search(l)]
    recs = len(RECOMMEND.findall(text))
    ok = not unnumbered and recs >= max(len(qlines), n_items)
    return ok, f"물음표 줄 {len(qlines)}개, 번호 없음 {len(unnumbered)}, 추천 표시 {recs}"


def c3_numbered_recommended(r):
    qt = question_turns(r)
    if not qt:
        return _res(False, "질문한 턴 없음")
    details, ok = [], True
    for d in qt:
        rep = r.reply_after(d["n"]) or {}
        good, det = _turn_format_ok(d["text"], len(rep.get("items") or []))
        ok &= good
        details.append(f"{d['n']}턴 {'통과' if good else '실패'}({det})")
    return _res(ok, "; ".join(details))


def _is_doc_write(name, args) -> bool:
    if name in ("write", "edit"):
        p = str(args.get("path") or args.get("file_path") or "")
        return ".goal/" in p or p.lower().endswith("goal.md")
    if name == "bash":
        cmd = str(args.get("command", ""))
        return ".goal" in cmd or "goal.md" in cmd.lower()
    return False


def _allowed_after_question(name, args) -> bool:
    if name == "read" or _is_doc_write(name, args):
        return True
    return name == "bash" and bool(READONLY_BASH.match(str(args.get("command", ""))))


def turn_round_violation(events: list) -> str | None:
    """(i) 질문이 도구 실행을 사이에 두고 두 메시지에 나옴 = 한 턴에 두 라운드
    (ii) 마지막 질문 메시지 뒤에 읽기·문서 쓰기가 아닌 도구 실행 = 묻고 기다리지 않음"""
    q_msgs, tools_between, after_last_q = 0, False, []
    for e in events:
        t = e.get("type")
        if t == "message_end" and (e.get("message") or {}).get("role") == "assistant":
            txt = content_text(e["message"].get("content"))
            if has_question(txt):
                if q_msgs and tools_between:
                    return "질문이 도구 실행을 사이에 두고 두 번 나옴(한 턴에 두 라운드)"
                q_msgs += 1
                tools_between = False
                after_last_q = []
        elif t == "tool_execution_start" and q_msgs:
            tools_between = True
            after_last_q.append((e.get("toolName"), e.get("args") or {}))
    bad = [n for n, a in after_last_q if not _allowed_after_question(n, a)]
    if bad:
        return f"질문 뒤 도구 실행 {bad}"
    return None


def c4_one_round_wait(r):
    viol = []
    for d in r.assistant_turns:
        v = turn_round_violation(r.events_of(d["n"]))
        if v:
            viol.append(f"{d['n']}턴: {v}")
    return _res(not viol, "; ".join(viol) or f"{len(r.assistant_turns)}턴 모두 통과")


def c5_goal_updated_each_round(r):
    bad = []
    for d in r.assistant_turns:
        if d["n"] == 1:
            if not d.get("goal"):
                bad.append("1턴: goal.md 없음")
            continue
        prev = r.reply_before(d["n"])
        if prev and prev.get("kind") == "answer" and not d.get("goal_changed"):
            bad.append(f"{d['n']}턴: 대답을 받고도 goal.md 그대로")
    return _res(not bad, "; ".join(bad) or "모든 라운드 갱신")


def c6_status_marks(r):
    texts = [r.goal_snapshot(d["n"]) or "" for d in r.assistant_turns] + [r.goal_text or ""]
    found = {k: any(re.search(p, t, re.I | re.M) for t in texts) for k, p in MARKS.items()}
    ok = found["합의"] and (found["미결정"] or found["가정"])
    return _res(ok, ", ".join(f"{k} {'있음' if v else '없음'}" for k, v in found.items()))


def _exempt(path: str) -> bool:
    return path.startswith(".goal/") or path.lower().split("/")[-1] == "goal.md"


def c7_no_edit_outside_goal(r):
    fs = r.fs_changes
    out = {k: [p for p in fs.get(k, []) if not _exempt(p)] for k in ("added", "removed", "modified")}
    n = sum(len(v) for v in out.values())
    return _res(n == 0, {k: v for k, v in out.items() if v} if n else "0건")


def c8_confirm_before_finish(r):
    end = r.meta.get("end_reason")
    return _res(end == "closed", f"종료 사유 {end}")


def run_process(r) -> dict:
    res = {c: globals()[c](r) for c in CHECKS}
    return {"checks": res, "passed": sum(v["pass"] for v in res.values()), "total": len(CHECKS)}
