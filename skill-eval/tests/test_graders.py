"""T7(과정 검사 8개: 통과 예·위반 예), T8(회수율), T10(누출 검사), T12(다시 판정해도 같은 점수)."""
import json
from pathlib import Path

import pytest
from fixtures.fake_runs import CONFIRM, DONE, GOOD_GOAL, Q_ROUND, good_script, goal_v, make_run, write

from skilleval.grade import grade_run
from skilleval.graders.leak import run_leak
from skilleval.graders.process import run_process
from skilleval.graders.recall import run_recall
from skilleval.record import load_run

FIX = Path(__file__).parent / "fixtures"


def proc(cfg, suite, task, tmp_path, script, arm="skill", **kw):
    d, res = make_run(cfg, suite, task, tmp_path, script, arm=arm, **kw)
    assert res["status"] == "done", res
    return run_process(load_run(d))["checks"], load_run(d)


def test_good_run_passes_all(cfg, suite, task3, tmp_path):
    checks, _ = proc(cfg, suite, task3, tmp_path, good_script())
    assert all(v["pass"] for v in checks.values()), {k: v for k, v in checks.items() if not v["pass"]}


# 위반 예: (검사, 대본) — 해당 검사만 실패해야 한다
def _two_rounds():
    s = good_script()
    s[1] = {"steps": [{"text": Q_ROUND, "tools": [write(".goal/fix/goal.md", goal_v(2))]},
                      {"text": "Q1은 제가 정했습니다.\n\n❓ **Q5** - **다음**: 다음 것도 할까요?\n\n➡️ 네", "tools": []}]}
    return s


def _edit_outside():
    s = good_script()
    s[2] = {"steps": [{"text": CONFIRM, "tools": [write(".goal/fix/goal.md", goal_v(3)),
                                                 write(".agents/skills/workflow-analysis/SKILL.md", "changed")]}]}
    return s


def _no_number():
    s = good_script()
    s[1] = {"steps": [{"text": "범위는 어디까지 할까요?", "tools": [write(".goal/fix/goal.md", goal_v(2))]}]}
    return s


def _no_update():
    s = good_script()
    s[1] = {"steps": [{"text": Q_ROUND.replace("Q1", "Q3"), "tools": []}]}
    return s


def _missing_section():
    s = good_script()
    g = GOOD_GOAL.replace("## Deliverable\n스킬 7개\n", "")
    s[2] = {"steps": [{"text": CONFIRM, "tools": [write(".goal/fix/goal.md", g)]}]}
    return s


def _no_marks():
    clean = lambda i: goal_v(i).replace("[합의]", "").replace("[가정]", "")
    s = good_script()
    for i, t in enumerate(s[:3]):
        for st in t["steps"]:
            for tool in st.get("tools") or []:
                if tool["name"] == "write":
                    tool["args"]["content"] = clean(i + 1)
    return s


def _no_confirm():
    s = good_script()
    s[2] = {"steps": [{"text": "정리했습니다.", "tools": [write(".goal/fix/goal.md", goal_v(3))]}]}
    s[3] = {"steps": [{"text": "끝."}]}
    s.append({"steps": [{"text": "끝났습니다."}]})      # 두 턴 연속 질문·변경 없음 → 자연 종료
    return s


def _question_then_act():
    s = good_script()
    s[1] = {"steps": [{"text": Q_ROUND.replace("Q1", "Q3"), "tools": [write(".goal/fix/goal.md", goal_v(2))]},
                      {"text": "", "tools": [{"name": "bash", "args": {"command": "python3 fix.py"}}]},
                      {"text": "적용했습니다."}]}
    return s


VIOLATIONS = [
    ("c1_goal_location", lambda: good_script("goal.md"), {}),
    ("c2_six_sections", _missing_section, {}),
    ("c3_numbered_recommended", _no_number, {}),
    ("c4_one_round_wait", _two_rounds, {}),
    ("c4_one_round_wait", _question_then_act, {}),
    ("c5_goal_updated_each_round", _no_update, {}),
    ("c6_status_marks", _no_marks, {}),
    ("c7_no_edit_outside_goal", _edit_outside, {}),
    ("c8_confirm_before_finish", _no_confirm, {}),
]


@pytest.mark.parametrize("check,script,kw", VIOLATIONS, ids=[f"{c}-{s.__name__}" for c, s, _ in VIOLATIONS])
def test_violation_fails_its_check(cfg, suite, task3, tmp_path, check, script, kw):
    checks, _ = proc(cfg, suite, task3, tmp_path, script(), **kw)
    assert not checks[check]["pass"], checks[check]
    others = [k for k, v in checks.items() if not v["pass"] and k != check]
    print(check, "→", checks[check]["detail"], "| 함께 실패:", others)


def test_recall_fixtures(task3):
    a = task3.answer
    rate = lambda name: run_recall(a, (FIX / "goals" / name).read_text())["rate"]
    assert rate("workflow-skill-fix.correct.md") >= 0.9
    assert rate("empty.md") == 0
    print("바꿔 쓴 goal.md 회수율:", rate("workflow-skill-fix.paraphrased.md"),
          "/ 크게 바꿔 쓴 goal.md:", rate("workflow-skill-fix.paraphrased-hard.md"))
    assert run_recall(a, "x") == run_recall(a, "x")


def _thief_script():
    s = good_script()
    s[0]["steps"].insert(0, {"text": "", "tools": [
        {"name": "read", "args": {"path": "/Users/sinjaehan/DEV/pi-lab/skill-eval/suites/workflow-define/tasks/"
                                          "workflow-skill-fix/answer.yaml"}, "result": "persona: ..."}]})
    return s


def _network_script():
    s = good_script()
    s[0]["steps"].insert(0, {"text": "", "tools": [{"name": "bash", "args": {"command": "curl -s https://example.com"}}]})
    return s


def _early_fact_script(task3):
    # U3에 누출 패턴을 임시로 두고, 모의 사용자가 말하기 전에 후보가 먼저 쓰게 한다
    s = good_script()
    s[0]["steps"][1]["text"] += "\n\n(사용자는 미니멀 선호 메모를 남겼죠)"
    return s


def test_leak_thief_and_clean(cfg, suite, task3, tmp_path):
    _, r = proc(cfg, suite, task3, tmp_path / "clean", good_script())
    assert run_leak(r, task3.answer)["status"] == "clean"
    _, r = proc(cfg, suite, task3, tmp_path / "thief", _thief_script())
    out = run_leak(r, task3.answer)
    assert out["status"] == "suspect" and "작업 폴더 밖" in out["reasons"][0]
    _, r = proc(cfg, suite, task3, tmp_path / "net", _network_script())
    assert any("네트워크" in x for x in run_leak(r, task3.answer)["reasons"])


def test_leak_fact_before_reveal(cfg, suite, task3, tmp_path):
    from dataclasses import replace
    f = task3.answer.by_id("U3")
    patched = replace(task3.answer, facts=[replace(x, leak_patterns=["미니멀 선호 메모"]) if x is f else x
                                           for x in task3.answer.facts])
    _, r = proc(cfg, suite, task3, tmp_path, _early_fact_script(task3))
    out = run_leak(r, patched)
    assert out["status"] == "suspect" and "U3" in out["reasons"][0]
    # 모의 사용자가 1턴 뒤에 U3를 알려 줬으므로 2턴 이후에 나오는 것은 괜찮다
    s = good_script()
    s[1]["steps"][0]["text"] += "\n(미니멀 선호 메모 반영)"
    _, r = proc(cfg, suite, task3, tmp_path / "late", s)
    assert run_leak(r, patched)["status"] == "clean"


def test_grade_twice_same(cfg, suite, task3, tmp_path):
    d, _ = make_run(cfg, suite, task3, tmp_path, good_script())
    a = grade_run(cfg, suite, d, judge="skip")
    b = grade_run(cfg, suite, d, judge="skip")
    assert a == b
    from skilleval.report import build_report
    rep = build_report(tmp_path, suite).read_text()
    assert "pi 버전" in rep and "스킬 버전" in rep and "모델" in rep
    assert (tmp_path / "summary.csv").exists()


def test_leak_relative_glob_is_not_outside():
    from skilleval.graders.leak import outside_paths
    ws, ag = "/private/var/folders/x/T/abc/pi-lab", "/private/var/folders/x/T/abc/.pi/agent"
    call = lambda cmd: {"name": "bash", "args": {"command": cmd}}
    assert outside_paths(call('for f in .agents/skills/workflow-*/SKILL.md; do wc -l "$f"; done'), ws, ag) == []
    assert outside_paths(call("ls -la; find .goal -maxdepth 3 -type f 2>/dev/null | sort"), ws, ag) == []
    assert outside_paths(call(f"cat {ag}/skills/workflow-grill/SKILL.md"), ws, ag) == []
    assert outside_paths(call("cat /var/folders/x/T/abc/pi-lab/AGENTS.md"), ws, ag) == []
    assert outside_paths(call("cat ~/.pi/agent/auth.json"), ws, ag) == ["~/.pi/agent/auth.json"]
    assert outside_paths(call("ls ../"), ws, ag) == ["../"]
    assert outside_paths(call("grep -r x /Users/someone/DEV"), ws, ag) == ["/Users/someone/DEV"]
    assert outside_paths({"name": "read", "args": {"path": f"{ag}/auth.json"}}, ws, ag) == [f"{ag}/auth.json"]


def test_c3_imperative_unnumbered_fails(cfg, suite, task3, tmp_path):
    s = good_script()
    s[1] = {"steps": [{"text": "범위를 알려 주세요. 조건도 말씀해 주세요.", "tools": [write(".goal/fix/goal.md", goal_v(2))]}]}

    def classify(dia, last):
        if "말씀해 주세요" in last:
            return {"items": [{"label": "범위", "type": "unknown", "fact_ids": []},
                              {"label": "조건", "type": "unknown", "fact_ids": []}]}
        from fixtures.fake_runs import classify_by_text
        return classify_by_text(dia, last)

    checks, _ = proc(cfg, suite, task3, tmp_path, s, classify=classify)
    assert not checks["c3_numbered_recommended"]["pass"]
    assert "인식 불가" in checks["c3_numbered_recommended"]["detail"]


def test_judge_message_has_dialogue_without_arm(cfg, suite, task3, tmp_path):
    from skilleval.grade import judge_dialogue
    from skilleval.graders.judge import build_message
    for arm in ("skill", "control"):
        d, res = make_run(cfg, suite, task3, tmp_path / arm, good_script(), arm=arm)
        assert res["status"] == "done", res
        r = load_run(d)
        msg = build_message(task3.answer, r.goal_text, judge_dialogue(r, task3), "rubric")
        assert task3.start_request in msg
        assert r.assistant_turns[0]["text"].strip() in msg            # 후보 글이 들어간다
        assert r.reply_after(1)["text"].strip() in msg                 # 모의 사용자 대답도
        assert "/skill:" not in msg and "질문해서 목표를 정리하고" not in msg  # 팔이 드러나는 첫 메시지는 뺀다


def test_leak_m2_false_positives():
    """M2에서 오탐이던 것: /skill: 명령, ../로 시험 대상 스킬 읽기, 설정 폴더 AGENTS.md, 자기 컴퓨터·예약 주소."""
    from skilleval.graders.leak import network_hits, outside_paths
    ws, ag = "/private/var/folders/x/T/abc/pi-lab", "/private/var/folders/x/T/abc/.pi/agent"
    call = lambda cmd: {"name": "bash", "args": {"command": cmd}}
    assert outside_paths(call("pi -p '/skill:workflow-define-goal 메모 검색'"), ws, ag) == []
    assert outside_paths(call("find ../.pi/agent/skills -maxdepth 2 -name SKILL.md"), ws, ag) == []
    assert outside_paths({"name": "read", "args": {"path": ag + "/AGENTS.md"}}, ws, ag) == []
    assert outside_paths({"name": "read", "args": {"path": "../.pi/agent/skills/workflow-grill/SKILL.md"}}, ws, ag) == []
    # 회차 폴더 위·설정 폴더의 다른 파일은 여전히 밖이다
    assert outside_paths(call("find .. -maxdepth 2 -type f"), ws, ag) == [".."]
    assert outside_paths(call("ls -la ../.pi/agent"), ws, ag) == ["../.pi/agent"]
    assert outside_paths({"name": "read", "args": {"path": "../.pi/agent/auth.json"}}, ws, ag) == ["../.pi/agent/auth.json"]
    assert network_hits("python3 -c 'requests.get(\"http://127.0.0.1:%d/\" % port)'") == []
    assert network_hits("s.request(method, 'http://example.org/')") == []
    assert network_hits("curl -s https://github.com/psf/requests/issues/2317") == ["curl", "https://github.com"]
    assert network_hits("python3 -c 'import urllib.request; urllib.request.urlopen(\"https://pypi.org/x\")'") == ["https://pypi.org"]
    # T16 첫 회차: uv pip list는 로컬, uv run … --with는 받아 올 수 있다
    assert network_hits("uv cache dir && uv pip list --python /usr/bin/python3 | head -35") == []
    assert network_hits("uv run --no-project --python /usr/bin/python3 --with pytest python -m pytest -q")
    assert network_hits("uv pip install pytest") and network_hits("uvx ruff check .")
    # T16: --offline은 네트워크를 안 쓴다, 점 없는 이름은 인터넷 주소가 아니다, 시스템 위치는 끝 / 없이도 허용
    assert network_hits("uv run --offline --no-project --python python3 --with pytest python -m pytest -q") == []
    assert network_hits("uv run --offline x; uv run --with pytest y")
    assert network_hits("s.get_adapter('http://x').max_retries") == []
    assert outside_paths(call("find /opt/homebrew /usr/local -maxdepth 5 -name pytest"), ws, ag) == []


def test_leak_word_heard_from_other_fact(suite, tmp_path):
    """U6 대답에 나온 "neutronclient"를 후보가 따라 말한 것은 U4가 먼저 나온 것이 아니다. safe_encode_list는 여전히 잡는다."""
    from skilleval.record import RunRecord
    t1 = suite.task("requests-2317")
    def rec(second):
        dlg = [{"role": "user", "n": 0, "kind": "start", "text": t1.start_request},
               {"role": "assistant", "n": 1, "text": "어떤 프로그램에서 쓰시나요?"},
               {"role": "user", "n": 1, "kind": "answer", "text": t1.answer.by_id("U6").say, "revealed_fact_ids": ["U6"]},
               {"role": "assistant", "n": 2, "text": second}]
        return RunRecord(dir=tmp_path, meta={"paths": {"workspace": "/w", "agent_dir": "/a"}}, dialogue=dlg,
                         turns=[], fs_changes={}, goal_text=None)
    assert run_leak(rec("neutronclient 쪽 호출 코드를 볼게요."), t1.answer)["status"] == "clean"
    out = run_leak(rec("neutronclient가 safe_encode_list로 바꾸는 것 같네요."), t1.answer)
    assert out["status"] == "suspect" and out["reasons"][0].startswith("U4")


def test_leak_run_folder_read_allowed():
    """회차 폴더(작업 폴더 + 설정 폴더) 안 읽기는 허용하고 따로 적는다(2026-10-23). 그 위와 쓰기는 여전히 밖."""
    from skilleval.graders.leak import classify_paths
    b = "/private/var/folders/x/T/abc"
    ws, ag = b + "/pi-lab", b + "/.pi/agent"
    call = lambda cmd: {"name": "bash", "args": {"command": cmd}}
    assert classify_paths(call("find .. -maxdepth 2 -type f"), ws, ag, b) == ([], [".."])
    assert classify_paths(call("ls -la ../.pi/agent"), ws, ag, b) == ([], ["../.pi/agent"])
    assert classify_paths({"name": "read", "args": {"path": "../.pi/agent/auth.json"}}, ws, ag, b) == ([], ["../.pi/agent/auth.json"])
    assert classify_paths(call("ls ../.."), ws, ag, b) == (["../.."], [])
    assert classify_paths(call("cat /var/folders/x/T/other/answer.yaml"), ws, ag, b) == (["/var/folders/x/T/other/answer.yaml"], [])
    assert classify_paths(call("find .. -maxdepth 2 -type f 2>/dev/null"), ws, ag, b) == ([], [".."])
    assert classify_paths(call("echo x > ../.pi/agent/settings.json"), ws, ag, b) == (["../.pi/agent/settings.json"], [])
    assert classify_paths(call("rm -rf ../.pi/agent/sessions"), ws, ag, b) == (["../.pi/agent/sessions"], [])
    w = {"name": "write", "args": {"path": "../.pi/agent/settings.json", "content": ""}}
    assert classify_paths(w, ws, ag, b) == (["../.pi/agent/settings.json"], [])


def test_c2_inline_evaluation(tmp_path):
    """Evaluation 절 대신 요구사항·제약 항목 아래에 적은 것도 인정한다(2026-10-23). 어디에도 없으면 실패."""
    from skilleval.graders.process import c2_six_sections
    from skilleval.record import RunRecord
    g = ("# G\n## Objective\nx\n## Deliverable\nx\n## Requirements\n- R1 x\n{ev}\n"
         "## Constraints\n- C1 x\n## Out of scope\n- x\n")
    rec = lambda ev: RunRecord(dir=tmp_path, meta={}, dialogue=[], turns=[], fs_changes={}, goal_text=g.format(ev=ev))
    assert c2_six_sections(rec("  - Evaluation — Criteria: a. Method: b. Evidence: c."))["pass"]
    assert c2_six_sections(rec("  - **평가 기준**: a"))["pass"]
    out = c2_six_sections(rec("  - 검토함"))
    assert not out["pass"] and "Evaluation" in out["detail"]
