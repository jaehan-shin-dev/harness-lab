"""회차 하나 판정: 결정적 검사(과정, 회수율, 누출) + 심판(저장된 judge.json이 있으면 다시 부르지 않음)."""
import json
from pathlib import Path

from .events import read_jsonl
from .graders.judge import run_judge
from .graders.leak import run_leak
from .graders.process import run_process
from .graders.recall import run_recall
from .record import load_run
from .runner import JsonlLog
from .trace import summarize_candidate, summarize_mock


def judge_dialogue(r, task) -> list:
    """심판에게 보여 줄 대화. 첫 메시지는 팔마다 달라(/skill:, 대조 팔 안내문) task.yaml의 시작 요청으로 바꾼다."""
    out = [("사용자 (시작 요청)", task.start_request)]
    for d in r.dialogue:
        if d.get("kind") == "start":
            continue
        out.append((f"후보 {d['n']}턴" if d["role"] == "assistant" else "사용자", d["text"]))
    return out


def grade_run(cfg, suite, run_dir: Path, judge: str = "cached") -> dict:
    """judge: "cached"(있으면 재사용, 없으면 호출) / "skip" / "fresh"(다시 호출)."""
    run_dir = Path(run_dir)
    r = load_run(run_dir)
    task = suite.task(r.meta["task"])
    arm = suite.arms[r.meta["arm"]]
    scores = {
        "run": r.meta["run"], "task": task.id, "arm": r.meta["arm"], "rep": r.meta["rep"],
        "end_reason": r.meta.get("end_reason"), "rounds": r.meta.get("rounds"), "turns": r.meta.get("turns"),
        "goal_path": r.meta.get("goal_path"),
        "process": run_process(r),
        "recall": run_recall(task.answer, r.goal_text),
        "leak": run_leak(r, task.answer),
        "mock": mock_stats(r),
    }
    jp = run_dir / "judge.json"
    if judge == "skip":
        scores["judge"] = None
    elif judge == "cached" and jp.exists():
        scores["judge"] = json.loads(jp.read_text())
    else:
        rubric = (suite.dir / "rubric.md").read_text()
        try:
            j = run_judge(cfg, task.answer, r.goal_text or "", judge_dialogue(r, task), rubric,
                          JsonlLog(run_dir / "judge.jsonl"))
        except Exception as ex:
            j = {"error": str(ex)}
        jp.write_text(json.dumps(j, ensure_ascii=False, indent=2))
        scores["judge"] = j
    scores["trace"] = {"candidate": summarize_candidate(read_jsonl(run_dir / "candidate.jsonl"),
                                                        cfg.context_window, arm),
                       "mock_user": summarize_mock(read_jsonl(run_dir / "mock_user.jsonl"))}
    (run_dir / "scores.json").write_text(json.dumps(scores, ensure_ascii=False, indent=2))
    return scores


def mock_stats(r) -> dict:
    """참고 기록: 수락 결정 일치, 찾을 수 있는 사실을 사용자에게 물은 횟수 (plan.md Q36)."""
    rep = [d for d in r.dialogue if d["role"] == "user" and d.get("kind") != "start"]
    items = [it for d in rep for it in d.get("items") or []]
    return {
        "replies": len(rep),
        "kinds": {k: sum(d.get("kind") == k for d in rep) for k in ("answer", "confirm", "next_step", "progress")},
        "revealed": sorted({i for d in rep for i in d.get("revealed_fact_ids") or []}),
        "accepted": sorted({i for d in rep for i in d.get("accepted_ids") or []}),
        "findable_asked": sum(it["type"] == "findable" for it in items),
        "unknown_items": sum(it["type"] == "unknown" for it in items),
        "fixes": [f for d in rep for f in d.get("fixes") or []],
    }
