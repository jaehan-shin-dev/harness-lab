"""명령 두 개: run(실행 + 판정), grade(저장된 결과만 다시 판정)."""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from .config import RESULTS, load_config
from .suite import load_suite


def _csv(s):
    return [x for x in s.split(",") if x] if s else None


def _out_dir(name):
    return RESULTS / (name or dt.date.today().isoformat())


def cmd_run(args, cfg):
    from .drivers.pi import PiDriver
    from .grade import grade_run
    from .report import build_report
    from .runner import run_all

    suite = load_suite(args.suite)
    if args.prepare_only:
        return prepare_only(cfg, suite, args)
    out = _out_dir(args.out)
    judge = "skip" if args.no_judge else "cached"
    res = run_all(cfg, suite, out, PiDriver, tasks=_csv(args.tasks), arms=_csv(args.arms), reps=args.reps,
                  jobs=args.jobs, mock_policy=args.mock.replace("-", "_"),
                  grade_fn=lambda d: grade_run(cfg, suite, d, judge=judge))
    rep = build_report(out, suite)
    print(f"report: {rep}")
    return 0 if all(r["status"] != "failed" for r in res) else 1


def prepare_only(cfg, suite, args):
    """준비 단계만 실행: 작업 폴더 파일 목록과 가방 검사를 보여 주고 지운다 (goal.md Deliverable inputs 칸)."""
    from .runner import first_message
    from .workspace import cleanup, prepare, preflight
    for t in suite.tasks:
        if args.tasks and t.id not in _csv(args.tasks):
            continue
        for a in suite.arms:
            if args.arms and a not in _csv(args.arms):
                continue
            paths = prepare(cfg, t, suite.arms[a])
            try:
                pre = preflight(paths, t, {"first_message": first_message(suite, t, a)},
                                [x.answer.path for x in suite.tasks])
                files = sorted(p.relative_to(paths.workspace).as_posix() for p in paths.workspace.rglob("*")
                               if p.is_file() and ".git" not in p.relative_to(paths.workspace).parts)
                print(json.dumps({"task": t.id, "arm": a, "workspace": str(paths.workspace),
                                  "agent_dir": str(paths.agent_dir), "added_files": paths.added_files,
                                  "workspace_files": files, "preflight": pre}, ensure_ascii=False, indent=2))
            finally:
                cleanup(paths)
    return 0


def cmd_grade(args, cfg):
    from .grade import grade_run
    from .graders.recall import run_recall
    from .report import build_report

    suite = load_suite(args.suite)
    if args.goal:
        task = suite.task(args.task)
        p = Path(args.goal)
        print(json.dumps(run_recall(task.answer, p.read_text() if p.exists() else ""), ensure_ascii=False, indent=2))
        return 0
    out = _out_dir(args.out)
    for d in sorted((out / "runs").iterdir()):
        if d.is_dir() and not d.name.startswith("_") and (d / "dialogue.json").exists():
            s = grade_run(cfg, suite, d, judge=args.judge)
            print(f"{d.name}: 과정 {s['process']['passed']}/8, 회수율 {s['recall']['recalled']}/{s['recall']['total']}, "
                  f"누출 {s['leak']['status']}")
    print(f"report: {build_report(out, suite)}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="skilleval", description="workflow 스킬을 pi로 돌려 과정과 결과를 잰다")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="과제×팔×회 실행 후 판정")
    r.add_argument("suite", help="suites/ 아래 묶음 이름 (예: workflow-define)")
    r.add_argument("--tasks", help="쉼표로 구분한 과제 id (기본: 전부)")
    r.add_argument("--arms", help="쉼표로 구분한 팔 (기본: 전부)")
    r.add_argument("--reps", type=int, help="팔마다 반복 횟수 (기본: config.yaml)")
    r.add_argument("--jobs", type=int, help="동시 실행 회차 수 (기본: config.yaml)")
    r.add_argument("--out", help="results/ 아래 폴더 이름 (기본: 오늘 날짜). 같은 이름이면 남은 회차만 돈다")
    r.add_argument("--mock", default="llm", choices=["llm", "always-unknown"], help="모의 사용자 방식")
    r.add_argument("--no-judge", action="store_true", help="LLM 심판을 부르지 않는다")
    r.add_argument("--prepare-only", action="store_true", help="준비 단계만 돌리고 작업 폴더를 보여 준다")

    g = sub.add_parser("grade", help="저장된 결과만 다시 판정")
    g.add_argument("suite")
    g.add_argument("--out", help="results/ 아래 폴더 이름 (기본: 오늘 날짜)")
    g.add_argument("--judge", default="cached", choices=["cached", "skip", "fresh"],
                   help="심판: 저장된 것 재사용 / 부르지 않음 / 다시 호출")
    g.add_argument("--goal", help="goal.md 파일 하나만 회수율 판정 (--task 필요)")
    g.add_argument("--task", help="--goal과 함께 쓰는 과제 id")

    args = p.parse_args(argv)
    cfg = load_config()
    return {"run": cmd_run, "grade": cmd_grade}[args.cmd](args, cfg)


if __name__ == "__main__":
    sys.exit(main())
