"""T4(가짜 드라이버·pi 호출), T5(종료 규칙·모의 사용자 정리), T6(회수), T15(이어 돌리기)."""
import json
import time

from fixtures.fake_runs import CONFIRM, DONE, Q_ROUND, classify_by_text, good_script, goal_v, make_run, write

from skilleval.drivers.base import TurnResult
from skilleval.drivers.pi import PiDriver
from skilleval.mock_user import compose, normalize
from skilleval.pi_process import pid_alive, run_pi
from skilleval.runner import run_all
from skilleval.drivers.fake import FakeDriver


def test_closed_and_files(cfg, suite, task3, tmp_path):
    d, res = make_run(cfg, suite, task3, tmp_path, good_script())
    assert res["status"] == "done", res
    meta = json.loads((d / "meta.json").read_text())
    assert meta["end_reason"] == "closed" and meta["rounds"] == 3 and meta["turns"] == 4
    for f in ("goal.md", "candidate.jsonl", "mock_user.jsonl", "transcript.md", "dialogue.json",
              "rounds/goal.round1.md", "rounds/goal.round3.md", "preflight.json", "fs_changes.json"):
        assert (d / f).exists(), f
    assert meta["cleaned"] is True


def test_goal_outside_dotgoal_is_collected(cfg, suite, task3, tmp_path):
    d, _ = make_run(cfg, suite, task3, tmp_path, good_script("goal.md"), arm="control")
    meta = json.loads((d / "meta.json").read_text())
    assert meta["goal_path"] == "goal.md" and (d / "goal.md").exists()


def test_unfinished_at_round_cap(cfg, suite, task3, tmp_path):
    turn = {"steps": [{"text": Q_ROUND, "tools": []}]}
    calls = {"n": 0}

    def script(n, msg, paths):
        p = paths.workspace / ".goal/fix/goal.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(goal_v(n))
        return turn

    d, res = make_run(cfg, suite, task3, tmp_path, script, mock_policy="always_unknown")
    meta = json.loads((d / "meta.json").read_text())
    assert meta["end_reason"] == "unfinished" and meta["rounds"] == cfg.max_rounds == 5
    dia = json.loads((d / "dialogue.json").read_text())
    assert all(x["text"] == task3.answer.replies["unknown"] for x in dia if x["role"] == "user" and x["n"] > 0)


def test_natural_end(cfg, suite, task3, tmp_path):
    script = [{"steps": [{"text": "goal.md를 썼습니다.", "tools": [write("goal.md", "x")]}]},
              {"steps": [{"text": "진행 중입니다."}]},
              {"steps": [{"text": "계속 진행 중입니다."}]}]
    d, _ = make_run(cfg, suite, task3, tmp_path, script, arm="control")
    meta = json.loads((d / "meta.json").read_text())
    assert meta["end_reason"] == "natural" and meta["turns"] == 3
    dia = json.loads((d / "dialogue.json").read_text())
    assert dia[2]["text"] == task3.answer.replies["progress"]


def test_failed_turn_is_recorded(cfg, suite, task3, tmp_path):
    d, res = make_run(cfg, suite, task3, tmp_path, [{"steps": [], "error": "pi 종료 코드 1"}])
    assert res["status"] == "failed" and (d / "failed.json").exists() and not (d / "scores.json").exists()


def test_resume_skips_done(cfg, suite, task3, tmp_path):
    seen = []

    def factory():
        seen.append(1)
        return FakeDriver(good_script())

    from dataclasses import replace
    c = replace(cfg, reps=2)
    graded = lambda d: (d / "scores.json").write_text("{}")
    import skilleval.runner as R
    orig = R.MockUser

    class M(orig):
        def __init__(self, *a, **k):
            k["classify"] = classify_by_text
            super().__init__(*a, **k)
    R.MockUser = M
    try:
        run_all(c, suite, tmp_path, factory, tasks=["workflow-skill-fix"], arms=["skill"], reps=1, grade_fn=graded,
                log=lambda *_: None)
        assert len(seen) == 1
        run_all(c, suite, tmp_path, factory, tasks=["workflow-skill-fix"], arms=["skill"], reps=2, grade_fn=graded,
                log=lambda *_: None)
        assert len(seen) == 2          # r1은 건너뛰고 r2만
    finally:
        R.MockUser = orig


def test_pi_command_flags(cfg, suite):
    for arm, want, unwanted in (("skill", [], ["--no-skills", "--no-context-files"]),
                                ("control", ["--no-skills", "--no-context-files"], [])):
        d = PiDriver()
        from types import SimpleNamespace
        from pathlib import Path
        d.start(cfg, SimpleNamespace(agent_dir=Path("/a"), workspace=Path("/w")), suite.arms[arm])
        cmd = d.command("hi")
        for f in ["--no-extensions", "--no-mcp", "--no-approve", "--session-id", "--provider", *want]:
            assert f in cmd, (arm, f)
        for f in unwanted:
            assert f not in cmd
        assert cmd[-2:] == ["--", "hi"]


def test_pi_turn_checks(cfg, suite):
    from types import SimpleNamespace
    from pathlib import Path
    d = PiDriver()
    d.start(cfg, SimpleNamespace(agent_dir=Path("/a"), workspace=Path("/w")), suite.arms["skill"])
    ok_events = [{"type": "message_end", "message": {"role": "user", "content": [{"type": "text",
                  "text": '<skill name="workflow-define" location="x">'}]}},
                 {"type": "message_end", "message": {"role": "assistant", "content": [], "stopReason": "stop"}},
                 {"type": "agent_settled"}]
    assert d.check(1, TurnResult(1, "", [], ok_events)) is None
    bad = [dict(ok_events[0], message={"role": "user", "content": "/skill:workflow-define x"})] + ok_events[1:]
    assert "스킬" in d.check(1, TurnResult(1, "", [], bad))
    tr = TurnResult(2, "", [], ok_events, stderr="Warning: No project session found with id")
    assert "세션" in d.check(2, tr)


def test_run_pi_closes_stdin_and_kills_on_timeout(tmp_path):
    t0 = time.monotonic()
    r = run_pi(["cat"], tmp_path, tmp_path, timeout=10)      # stdin이 열려 있으면 cat은 끝나지 않는다
    assert r["returncode"] == 0 and time.monotonic() - t0 < 5
    r = run_pi(["sh", "-c", "sleep 30 & sleep 30"], tmp_path, tmp_path, timeout=1)
    assert r["timed_out"]
    time.sleep(0.2)
    assert not pid_alive(r["pid"])


def test_mock_normalize_drops_bad_ids(task3):
    a = task3.answer
    dec, fixes = normalize({"items": [{"label": "Q1", "type": "fact", "fact_ids": ["U3", "A1", "ZZ"]},
                                      {"label": "Q2", "type": "accept", "fact_ids": ["U3"]},
                                      {"label": "Q3", "type": "weird"}]}, a, "질문?")
    assert dec["items"][0]["fact_ids"] == ["U3"]
    assert dec["items"][1]["type"] == "unknown" and dec["items"][2]["type"] == "unknown"
    r = compose(dec, a)
    assert r.kind == "answer" and r.revealed_fact_ids == ["U3"]
    assert a.by_id("U3").say in r.text and a.replies["unknown"] in r.text
    assert set(r.revealed_fact_ids) <= set(a.ids())


def test_mock_reply_kinds(task3):
    a = task3.answer
    base = {"items": [], "confirm_requested": False, "next_step_asked": False}
    assert compose({**base, "confirm_requested": True}, a).text == a.replies["confirm"]
    assert compose(base, a).kind == "progress"
    r = compose({**base, "next_step_asked": True}, a)
    assert r.kind == "next_step" and r.text == a.replies["next_step"]
    dec, _ = normalize(base, a, "이렇게 할까요?")         # 질문이 있는데 비어 있으면 모름 대답
    assert compose(dec, a).text == a.replies["unknown"]


def test_mock_no_duplicate_fact_in_one_reply(task3):
    a = task3.answer
    dec = {"items": [{"label": "Q2", "type": "fact", "fact_ids": ["U2"]},
                     {"label": "Q3", "type": "fact", "fact_ids": ["U1", "U2"]}],
           "confirm_requested": False, "next_step_asked": False}
    r = compose(dec, a)
    assert r.text.count(a.by_id("U2").say) == 1 and a.by_id("U1").say in r.text


def test_imperative_questions_do_not_end_naturally(cfg, suite, task3, tmp_path):
    """물음표 없는 질문을 두 턴 연속 해도, 모의 사용자가 질문으로 읽었으면 자연 종료가 아니다."""
    ask = "어떤 오류가 나는지 알려 주세요."
    script = [{"steps": [{"text": "goal.md를 썼습니다. " + ask, "tools": [write("goal.md", "x")]}]},
              {"steps": [{"text": ask}]}, {"steps": [{"text": ask}]},
              {"steps": [{"text": "정리했습니다. 이대로 마무리할까요?"}]}, {"steps": [{"text": "끝냈습니다."}]}]

    def classify(dia, last):
        if "마무리할까요" in last:
            return {"items": [], "confirm_requested": True, "next_step_asked": False}
        if "알려 주세요" in last:
            return {"items": [{"label": "오류", "type": "unknown", "fact_ids": []}]}
        return {"items": []}

    d, _ = make_run(cfg, suite, task3, tmp_path, script, arm="control", classify=classify)
    meta = json.loads((d / "meta.json").read_text())
    assert meta["end_reason"] == "closed" and meta["turns"] == 5
