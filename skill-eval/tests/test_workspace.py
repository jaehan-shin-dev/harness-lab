"""T3: 가방 검사, 인증 복사, 정리 / T2: inputs 원문 / Deliverable inputs 칸(from_run)."""
import json
import subprocess
from pathlib import Path

import pytest

from skilleval import workspace as W
from skilleval.runner import first_message

ORIGINAL = Path.home() / ".claude/projects/-Users-sinjaehan-DEV-pi-lab/a02499fe-6abf-4db3-bd1d-bbb1167eb7ec.jsonl"


def _pre(paths, task, suite, arm="skill", text=None):
    return W.preflight(paths, task, {"first_message": text or first_message(suite, task, arm)},
                       [t.answer.path for t in suite.tasks])


def test_clean_workspace_passes_and_cleanup(cfg, suite, task3):
    paths = W.prepare(cfg, task3, suite.arms["skill"])
    try:
        pre = _pre(paths, task3, suite)
        assert pre["ok"], pre
        names = [c["name"] for c in pre["checks"]]
        assert "작업 폴더 git 기록 1커밋" in names
        auth = json.loads((paths.agent_dir / "auth.json").read_text())
        assert auth["openai-codex"]["refresh"] == W.FAKE_REFRESH
        assert oct((paths.agent_dir / "auth.json").stat().st_mode)[-3:] == "600"
        assert (paths.agent_dir / "skills" / "workflow-define" / "SKILL.md").exists()
        assert len(list((paths.agent_dir / "skills").iterdir())) == 7
        assert (paths.agent_dir / "AGENTS.md").exists()
        st = json.loads((paths.agent_dir / "settings.json").read_text())
        assert st["skills"] == [f"!{Path.home()}/.agents/skills/**"]
        assert (paths.workspace / "notes/2026-10-20-workflow-skill-comparison.md").exists()
        assert not (paths.workspace / ".goal").exists()      # 9fa2b04에는 정답 폴더가 없다
    finally:
        W.cleanup(paths)
    assert not paths.base.exists() and not paths.mock_base.exists()


def test_control_arm_has_no_skills(cfg, suite, task3):
    paths = W.prepare(cfg, task3, suite.arms["control"])
    try:
        assert not (paths.agent_dir / "skills").exists()
        assert not (paths.agent_dir / "AGENTS.md").exists()
        assert _pre(paths, task3, suite, "control")["ok"]
    finally:
        W.cleanup(paths)


@pytest.mark.parametrize("plant", ["answer", "toolname", "word", "commit"])
def test_planted_problems_fail(cfg, suite, task3, plant):
    paths = W.prepare(cfg, task3, suite.arms["skill"])
    try:
        text = None
        if plant == "answer":
            (paths.workspace / "answer.yaml").write_text(task3.answer.path.read_text())
        elif plant == "toolname":
            (paths.workspace / "notes" / "todo.md").write_text("run skill-eval later")
        elif plant == "word":
            text = first_message(suite, task3, "skill") + " 이건 평가용이에요"
        elif plant == "commit":
            (paths.workspace / "x.txt").write_text("x")
            subprocess.run(["git", "add", "-A"], cwd=paths.workspace, check=True)
            subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-qm", "later"],
                           cwd=paths.workspace, check=True)
        pre = _pre(paths, task3, suite, text=text)
        assert not pre["ok"]
    finally:
        W.cleanup(paths)


def test_original_span_is_exempt(cfg, suite, task3):
    """시작 요청의 '-eval'은 과제 원래 내용이라 통과, 러너가 붙인 부분의 금지 단어는 실패."""
    msg = first_message(suite, task3, "skill")
    assert "-eval" in msg
    assert not W.forbidden_hits(W._mask(msg, task3.original_spans))
    assert W.forbidden_hits(msg)


def test_auth_too_short_stops(cfg, tmp_path):
    from dataclasses import replace
    p = tmp_path / "a.json"
    p.write_text(json.dumps({"openai-codex": {"expires": 1, "refresh": "r"}}))
    with pytest.raises(W.PrepError, match="갱신"):
        W.check_auth(replace(cfg, auth={**cfg.auth, "source": str(p)}))


def test_inputs_file_equals_original(task3):
    """T2: inputs의 분석 파일이 원래 대화의 139행 답변과 같다."""
    if not ORIGINAL.exists():
        pytest.skip("원래 대화 기록 없음")
    d = json.loads(ORIGINAL.read_text().split("\n")[138])
    orig = "\n\n".join(b["text"] for b in d["message"]["content"] if b.get("type") == "text")
    mine = (task3.dir / task3.inputs[0]["from"]).read_text()
    assert mine.strip() == orig.strip()


def test_inputs_from_previous_run(cfg, suite, task3, tmp_path, monkeypatch):
    """Deliverable inputs 칸: 이전 실행의 goal.md를 inputs로 지정하면 작업 폴더 지정 위치에 들어간다."""
    res = tmp_path / "results"
    run = res / "2026-10-21" / "runs" / "workflow-skill-fix__skill__r1"
    run.mkdir(parents=True)
    (run / "goal.md").write_text("# prior goal\n")
    monkeypatch.setattr(W, "RESULTS", res)
    from dataclasses import replace
    t = replace(task3, data={**task3.data, "inputs": task3.inputs + [
        {"path": ".goal/fix/goal.md", "from_run": {"task": "workflow-skill-fix", "arm": "skill", "rep": 1}}]})
    paths = W.prepare(cfg, t, suite.arms["skill"])
    try:
        assert (paths.workspace / ".goal/fix/goal.md").read_text() == "# prior goal\n"
    finally:
        W.cleanup(paths)


def test_pi_env_hides_tool_and_session(monkeypatch, tmp_path):
    """M2: uv run 아래에서 PATH·PWD·VIRTUAL_ENV가 skill-eval 경로를, 세션 변수가 토큰을 후보에게 넘겼다."""
    from skilleval.config import PILAB, ROOT
    from skilleval.pi_process import clean_env
    monkeypatch.setenv("PATH", f"{ROOT}/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin")
    for k, v in {"VIRTUAL_ENV": f"{ROOT}/.venv", "PWD": str(ROOT), "OLDPWD": str(ROOT),
                 "CLAUDE_CODE_MESSAGING_TOKEN": "secret", "TMUX": "x"}.items():
        monkeypatch.setenv(k, v)
    env = clean_env(tmp_path / "agent")
    assert not any(str(PILAB) in v for v in env.values())
    assert not {"VIRTUAL_ENV", "PWD", "OLDPWD", "CLAUDE_CODE_MESSAGING_TOKEN", "TMUX"} & set(env)
    assert env["PATH"] == "/opt/homebrew/bin:/usr/bin:/bin" and env["PI_OFFLINE"] == "1" and "HOME" in env
