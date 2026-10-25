"""과제×팔×회 반복: 준비 → 대화 → 회수 → 정리 (plan.md T6, T15)."""
import datetime as dt
import json
import shutil
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .events import MARK, has_question
from .mock_user import MockUser
from .workspace import (PrepError, check_auth, cleanup, diff_trees, file_sha, find_goal, hash_tree, pi_version,
                        prepare, preflight)

END_LABELS = {"closed": "종료", "natural": "자연 종료", "unfinished": "미종료", "failed": "실패"}


class RunFailed(Exception):
    def __init__(self, msg, retryable=True):
        super().__init__(msg)
        self.retryable = retryable


def run_name(task_id, arm, rep):
    return f"{task_id}__{arm}__r{rep}"


def first_message(suite, task, arm_name):
    return suite.arms[arm_name]["first_message"].format(request=task.start_request)


class JsonlLog:
    def __init__(self, path: Path):
        self.path, self.lock = path, threading.Lock()

    def __call__(self, rec):
        with self.lock, self.path.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def converse(cfg, suite, task, arm_name, paths, driver, mock, run_dir: Path, cand_log) -> dict:
    """대화 고리와 종료 규칙 (goal.md R1 a·b·c)."""
    arm = suite.arms[arm_name]
    rounds_dir = run_dir / "rounds"
    rounds_dir.mkdir(exist_ok=True)
    msg = first_message(suite, task, arm_name)
    dialogue = [{"role": "user", "n": 0, "kind": "start", "text": msg}]
    driver.start(cfg, paths, {**arm, "skill_names": arm.get("skill_names", [])})
    prev_sha, confirmed, streak, replies, n = None, False, 0, 0, 0
    end = None
    while True:
        n += 1
        cand_log({MARK: "turn_start", "turn": n, "prompt": msg})
        tr = driver.turn(n, msg)
        for e in tr.events:
            cand_log(e)
        cand_log({MARK: "turn_end", "turn": n, "cmd": tr.cmd, "returncode": tr.returncode,
                  "stderr": tr.stderr[-4000:], "duration_s": tr.duration_s, "timed_out": tr.timed_out,
                  "error": tr.error})
        if tr.error:
            raise RunFailed(f"{n}턴: {tr.error}")
        g = find_goal(paths.workspace)
        goal = None
        if g:
            shutil.copyfile(g, rounds_dir / f"goal.round{n}.md")
            goal = {"path": g.relative_to(paths.workspace).as_posix(), "sha": file_sha(g)}
        sha = goal["sha"] if goal else None
        changed = sha != prev_sha
        prev_sha = sha
        text = tr.text
        q = has_question(text)
        dialogue.append({"role": "assistant", "n": n, "text": text, "has_question": q, "goal": goal,
                         "goal_changed": changed, "duration_s": tr.duration_s})
        # (a) 마무리 확인을 받은 뒤 질문 없는 턴 → 종료
        if confirmed and not q:
            end = "closed"
            break
        # (c) 두 턴 연속 질문도 없고 goal.md도 그대로 → 자연 종료
        streak = streak + 1 if (not q and not changed) else 0
        if streak >= 2:
            end = "natural"
            break
        # (b) 대답 상한
        if replies >= cfg.max_rounds:
            end = "unfinished"
            break
        r = mock.reply(dialogue, text)
        replies += 1
        if r.items:
            streak = 0          # 물음표 없는 질문("알려 주세요.")도 모의 사용자가 질문으로 읽었으면 질문 턴
        if r.kind == "confirm":
            confirmed = True
        dialogue.append({"role": "user", "n": n, "text": r.text, **{k: v for k, v in r.to_dict().items()
                                                                     if k != "text"}})
        msg = r.text
    return {"end_reason": end, "turns": n, "rounds": replies, "dialogue": dialogue}


def transcript_md(meta: dict, dialogue: list) -> str:
    lines = [f"# {meta['run']}", "",
             f"- 종료: {END_LABELS.get(meta.get('end_reason'), meta.get('end_reason'))}, 턴 {meta.get('turns')}, "
             f"라운드 {meta.get('rounds')}", f"- goal.md: {meta.get('goal_path')}", ""]
    for d in dialogue:
        if d["role"] == "user":
            tag = {"start": "시작 요청"}.get(d.get("kind"), f"모의 사용자 ({d.get('kind')})")
            extra = ""
            if d.get("revealed_fact_ids"):
                extra += f" · 알려 준 사실 {', '.join(d['revealed_fact_ids'])}"
            if d.get("accepted_ids"):
                extra += f" · 수락 {', '.join(d['accepted_ids'])}"
            if d.get("findable_ids"):
                extra += f" · 찾을 수 있음 {', '.join(d['findable_ids'])}"
            lines += [f"## 사용자 — {tag}{extra}", "", d["text"], ""]
        else:
            g = d.get("goal")
            gl = f"goal.md {'갱신' if d.get('goal_changed') else '그대로'}" if g else "goal.md 없음"
            lines += [f"## 후보 {d['n']}턴 ({gl}, {d.get('duration_s')}초)", "", d["text"], ""]
    return "\n".join(lines)


def _set_aside(run_dir: Path, out_dir: Path, name: str):
    """끝나지 않았거나 실패한 회차 폴더는 지우지 않고 runs/_attempts/로 옮긴다(기록 보존)."""
    dst_root = out_dir / "runs" / "_attempts"
    dst_root.mkdir(parents=True, exist_ok=True)
    k = 1
    while (dst_root / f"{name}-a{k}").exists():
        k += 1
    shutil.move(str(run_dir), str(dst_root / f"{name}-a{k}"))


def run_one(cfg, suite, task, arm_name, rep, out_dir: Path, driver_factory, mock_policy="llm",
            classify=None, keep_paths=False, grade_fn=None) -> dict:
    name = run_name(task.id, arm_name, rep)
    run_dir = out_dir / "runs" / name
    if (run_dir / "scores.json").exists():
        return {"run": name, "status": "skipped"}
    arm = suite.arms[arm_name]
    attempts = 1 + cfg.retries["pi_call"]
    last = None
    for attempt in range(1, attempts + 1):
        if run_dir.exists():
            _set_aside(run_dir, out_dir, name)
        run_dir.mkdir(parents=True)
        cand_log = JsonlLog(run_dir / "candidate.jsonl")
        mock_log = JsonlLog(run_dir / "mock_user.jsonl")
        meta = {"run": name, "task": task.id, "arm": arm_name, "rep": rep, "attempt": attempt,
                "suite": suite.name, "provider": cfg.provider, "model": cfg.model, "thinking": cfg.thinking,
                "pi_version": pi_version(), "started": dt.datetime.now().isoformat(timespec="seconds"),
                "mock_policy": mock_policy}
        paths = None
        t0 = time.monotonic()
        try:
            meta["auth_hours_left"] = round(check_auth(cfg), 1)
            paths = prepare(cfg, task, arm)
            meta["paths"] = paths.to_dict()
            meta["workspace_agents_md"] = (paths.workspace / "AGENTS.md").exists()
            pre = preflight(paths, task, {"first_message": first_message(suite, task, arm_name)},
                            [t.answer.path for t in suite.tasks])
            (run_dir / "preflight.json").write_text(json.dumps(pre, ensure_ascii=False, indent=2))
            if not pre["ok"]:
                raise RunFailed("가방 검사 실패: " + ", ".join(c["name"] for c in pre["checks"] if not c["ok"]),
                                retryable=False)
            before = hash_tree(paths.workspace)
            driver = driver_factory()
            mock = MockUser(cfg, task.answer, paths, mock_log, policy=mock_policy, classify=classify)
            conv = converse(cfg, suite, task, arm_name, paths, driver, mock, run_dir, cand_log)
            after = hash_tree(paths.workspace)
            fs = diff_trees(before, after)
            (run_dir / "fs_changes.json").write_text(json.dumps(fs, ensure_ascii=False, indent=2))
            g = find_goal(paths.workspace)
            if g:
                shutil.copyfile(g, run_dir / "goal.md")
            meta.update(end_reason=conv["end_reason"], turns=conv["turns"], rounds=conv["rounds"],
                        goal_path=g.relative_to(paths.workspace).as_posix() if g else None,
                        driver=driver.describe())
            (run_dir / "dialogue.json").write_text(json.dumps(conv["dialogue"], ensure_ascii=False, indent=2))
            last = None
        except RunFailed as ex:
            last = ex
        except PrepError as ex:
            last = RunFailed(str(ex), retryable=False)
        except Exception as ex:          # 예상 못 한 오류도 회차 실패로 적고 다음 회차로
            last = RunFailed(f"{type(ex).__name__}: {ex}\n{traceback.format_exc()[-1500:]}")
        finally:
            meta["duration_s"] = round(time.monotonic() - t0, 1)
            if paths and not keep_paths:
                cleanup(paths)
                meta["cleaned"] = not paths.base.exists() and not paths.mock_base.exists()
            (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        if last is None:
            break
        meta["error"] = str(last)
        (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        if not last.retryable:
            break
    if last is not None:
        meta["end_reason"] = "failed"
        (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        (run_dir / "failed.json").write_text(json.dumps({"error": str(last), "attempts": meta["attempt"]},
                                                        ensure_ascii=False, indent=2))
        return {"run": name, "status": "failed", "error": str(last)}
    (run_dir / "transcript.md").write_text(transcript_md(meta, json.loads((run_dir / "dialogue.json").read_text())))
    if grade_fn:
        grade_fn(run_dir)
    return {"run": name, "status": "done", "end_reason": meta["end_reason"]}


def plan_runs(suite, tasks=None, arms=None, reps=None, cfg=None):
    reps = reps or cfg.reps
    out = []
    for t in suite.tasks:
        if tasks and t.id not in tasks:
            continue
        for a in suite.arms:
            if arms and a not in arms:
                continue
            for r in range(1, reps + 1):
                out.append((t, a, r))
    return out


def run_all(cfg, suite, out_dir: Path, driver_factory, tasks=None, arms=None, reps=None, jobs=None,
            mock_policy="llm", grade_fn=None, log=print):
    todo = plan_runs(suite, tasks, arms, reps, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    def one(item):
        t, a, r = item
        res = run_one(cfg, suite, t, a, r, out_dir, driver_factory, mock_policy=mock_policy, grade_fn=grade_fn)
        log(f"[{len(results) + 1}/{len(todo)}] {res['run']}: {res['status']} {res.get('end_reason', '')}"
            f"{' ' + res['error'][:200] if res.get('error') else ''}")
        results.append(res)
        return res

    with ThreadPoolExecutor(max_workers=jobs or cfg.jobs) as ex:
        list(ex.map(one, todo))
    return results
