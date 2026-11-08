#!/usr/bin/env python3
"""workflow-worktree: 지금 하던 작업을 저장소 옆 worktree로 옮기고, 끝나면 로컬 merge로 합친다.

명령: status · create · finish (뒤에 goal 이름, --json이면 JSON 출력)
종료 코드: 0 성공 · 2 멈춤 · 1 script 오류
구조: 검사 → 계획 → 실행. 상태를 바꾸는 것은 apply 하나다.
"""
import argparse
import json
import os
import subprocess
import sys

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_STOP = 2


class GitError(Exception):
    pass


def run_git(cwd, *args):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise GitError("git %s: %s" % (" ".join(args), out.stderr.strip()))
    return out.stdout


# ---------------------------------------------------------------- 사실 읽기

class Repo:
    def __init__(self, cwd, top, main, common, branch, head):
        self.cwd = cwd
        self.top = top          # 지금 있는 작업 폴더의 맨 위
        self.main = main        # 원래 폴더(첫 번째 worktree)
        self.common = common    # 원래 폴더와 worktree가 함께 쓰는 .git
        self.branch = branch    # 지금 폴더의 브랜치
        self.head = head

    @property
    def in_worktree(self):
        return self.top != self.main


def read_repo(cwd):
    probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd,
                           capture_output=True, text=True)
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        raise Stopped([Stop("not-git-repo", "git 저장소 안이 아니다.", [cwd])])
    top = os.path.realpath(run_git(cwd, "rev-parse", "--show-toplevel").strip())
    listing = run_git(cwd, "worktree", "list", "--porcelain")
    main = os.path.realpath(listing.splitlines()[0][len("worktree "):])
    common = run_git(cwd, "rev-parse", "--git-common-dir").strip()
    common = os.path.realpath(os.path.join(cwd, common))
    branch = run_git(cwd, "branch", "--show-current").strip()
    head = run_git(cwd, "rev-parse", "HEAD").strip()
    return Repo(cwd, top, main, common, branch, head)


# ---------------------------------------------------------------- 영수증

RECEIPT_VERSION = 1


class Receipt:
    def __init__(self, path, data):
        self.path = path
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def delete(self):
        if os.path.exists(self.path):
            os.remove(self.path)


def receipt_path(repo, goal):
    return os.path.join(repo.common, "workflow-worktree", goal + ".json")


def load_receipt(repo, goal):
    path = receipt_path(repo, goal)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return Receipt(path, json.load(f))


def new_receipt(repo, goal, wt, br, moved):
    return Receipt(receipt_path(repo, goal), {
        "version": RECEIPT_VERSION,
        "goal": goal,
        "state": "creating",
        "main": repo.main,
        "worktree": wt,
        "branch": br,
        "base": {"branch": repo.branch, "commit": repo.head},
        "moved_by_git": moved,
        "items": [],
        "done": [],
    })


def uncommitted_paths(cwd):
    """git status 기준 미커밋 경로(추적 파일 수정 + 무시되지 않은 새 파일)."""
    raw = run_git(cwd, "status", "--porcelain", "-z", "--untracked-files=all")
    parts = raw.split("\0")
    paths = []
    i = 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if not entry:
            continue
        xy, path = entry[:2], entry[3:]
        paths.append(path)
        if "R" in xy or "C" in xy:
            i += 1  # 이름 바꾸기는 옛 경로가 한 칸 더 온다
    return paths


def worktree_path(repo, goal):
    return os.path.join(os.path.dirname(repo.main), os.path.basename(repo.main) + "-" + goal)


def branch_name(goal):
    return "goal/" + goal


# ---------------------------------------------------------------- 멈춤

class Stop:
    def __init__(self, code, message, paths=None, **extra):
        self.code = code
        self.message = message
        self.paths = paths or []
        self.extra = extra

    def to_json(self):
        data = {"code": self.code, "message": self.message, "paths": self.paths}
        data.update(self.extra)
        return data


class Stopped(Exception):
    """검사에서 멈출 이유가 나왔다. 아무것도 바꾸지 않은 상태다."""

    def __init__(self, stops):
        super().__init__(", ".join(s.code for s in stops))
        self.stops = stops


# ---------------------------------------------------------------- 다음 할 일

def decide(repo, receipt):
    """Q26 표: 영수증 상태와 지금 위치로 다음 할 일을 고른다. (action, stop 또는 None)"""
    if receipt is None:
        return "create", None
    state = receipt["state"]
    if state == "creating":
        return "stop", Stop("create-incomplete", "만들기가 도중에 멈췄다. 끝난 단계를 보고 정리 방법을 정해야 한다.",
                            done=list(receipt["done"]))
    if state == "finishing":
        return "continue-finish", None
    if repo.top == receipt["worktree"]:
        return "finish", None
    return "reenter", None


# ---------------------------------------------------------------- 계획

class Step:
    def __init__(self, sid, fn):
        self.id = sid
        self.fn = fn


def find_stash(cwd, sha):
    listing = run_git(cwd, "stash", "list", "--format=%H")
    for i, line in enumerate(listing.splitlines()):
        if line.strip() == sha:
            return "stash@{%d}" % i
    raise GitError("stash %s를 찾지 못했다" % sha)


def plan_create(repo, goal):
    wt = worktree_path(repo, goal)
    br = branch_name(goal)
    moved = uncommitted_paths(repo.main)

    def stash(ctx):
        run_git(repo.main, "stash", "push", "-q", "-u", "-m", "workflow-worktree:" + goal)
        ctx["stash"] = run_git(repo.main, "rev-parse", "stash@{0}").strip()

    def worktree_add(ctx):
        run_git(repo.main, "worktree", "add", "-q", "-b", br, wt, "HEAD")

    def stash_pop(ctx):
        run_git(wt, "stash", "pop", "-q", "--index", find_stash(wt, ctx["stash"]))

    steps = []
    if moved:
        steps.append(Step("stash", stash))
    steps.append(Step("worktree-add", worktree_add))
    if moved:
        steps.append(Step("stash-pop", stash_pop))
    ctx = {"worktree": wt, "branch": br, "moved_by_git": moved}
    return steps, ctx


def plan_finish(repo, receipt):
    wt = receipt["worktree"]
    br = receipt["branch"]

    def merge(ctx):
        run_git(repo.main, "merge", "-q", "--no-ff", "--no-edit", br)
        receipt["merge_commit"] = run_git(repo.main, "rev-parse", "HEAD").strip()

    def worktree_remove(ctx):
        run_git(repo.main, "worktree", "remove", wt)

    def branch_delete(ctx):
        run_git(repo.main, "branch", "-q", "-d", br)

    steps = [Step("merge", merge), Step("worktree-remove", worktree_remove),
             Step("branch-delete", branch_delete)]
    return steps, {}


# ---------------------------------------------------------------- 실행

def apply(steps, ctx, receipt):
    """계획을 한 단계씩 실행하고, 끝난 단계를 영수증 done에 적는다. 이미 끝난 단계는 건너뛴다."""
    for step in steps:
        if step.id in receipt["done"]:
            continue
        step.fn(ctx)
        receipt["done"].append(step.id)
        receipt.save()


# ---------------------------------------------------------------- 명령

def cmd_create(cwd, goal):
    repo = read_repo(cwd)
    steps, ctx = plan_create(repo, goal)
    receipt = new_receipt(repo, goal, ctx["worktree"], ctx["branch"], ctx["moved_by_git"])
    receipt.save()
    apply(steps, ctx, receipt)
    receipt["state"] = "working"
    receipt.save()
    return EXIT_OK, {"ok": True, "worktree": ctx["worktree"], "branch": ctx["branch"],
                     "moved_by_git": ctx["moved_by_git"]}


def cmd_finish(cwd, goal):
    repo = read_repo(cwd)
    receipt = load_receipt(repo, goal)
    receipt["state"] = "finishing"
    receipt.save()
    steps, ctx = plan_finish(repo, receipt)
    apply(steps, ctx, receipt)
    receipt.delete()
    return EXIT_OK, {"ok": True, "merge_commit": receipt.data.get("merge_commit"),
                     "synced": [], "copy_changed": [], "removed": [receipt["worktree"]]}


def cmd_status(cwd, goal):
    repo = read_repo(cwd)
    receipt = load_receipt(repo, goal)
    action, stop = decide(repo, receipt)
    out = {"action": action, "goal": goal, "worktree": None,
           "unlisted": [], "uncommitted": [], "stops": []}
    if receipt is not None:
        out["worktree"] = receipt["worktree"]
    if action == "finish":
        out["uncommitted"] = uncommitted_paths(repo.top)
    if stop is not None:
        out["stops"] = [stop.to_json()]
        return EXIT_STOP, out
    return EXIT_OK, out


COMMANDS = {"status": cmd_status, "create": cmd_create, "finish": cmd_finish}


ACTION_NAMES = {
    "create": "만들기",
    "finish": "끝내기 시작",
    "reenter": "worktree로 다시 들어가기",
    "continue-finish": "끝내기 이어 하기",
    "stop": "멈춤",
}


def summarize(command, out):
    """사람이 읽는 한국어 요약."""
    lines = []
    if "error" in out:
        lines.append("script 오류: " + out["error"])
    if command == "status" and "action" in out:
        lines.append("다음 할 일: %s (%s)" % (ACTION_NAMES[out["action"]], out["goal"]))
        if out.get("worktree"):
            lines.append("worktree: " + out["worktree"])
        for path in out.get("uncommitted", []):
            lines.append("커밋 안 한 작업: " + path)
        for item in out.get("unlisted", []):
            lines.append("목록에 없는 항목: %s → %s" % (item["path"], item["mode"]))
    if command == "create" and out.get("ok"):
        lines.append("worktree를 만들었다: %s (브랜치 %s)" % (out["worktree"], out["branch"]))
        for path in out.get("moved_by_git", []):
            lines.append("옮긴 미커밋 변경: " + path)
    if command == "finish" and out.get("ok"):
        lines.append("합쳤다: " + str(out.get("merge_commit")))
    for stop in out.get("stops", []):
        lines.append("멈춤 [%s] %s" % (stop["code"], stop["message"]))
        for path in stop.get("paths", []):
            lines.append("  - " + path)
    return "\n".join(lines)


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        # 종료 코드 2는 "멈춤"이라서, 잘못된 인자는 script 오류(1)로 낸다
        self.print_usage(sys.stderr)
        sys.stderr.write("%s: error: %s\n" % (self.prog, message))
        sys.exit(EXIT_ERROR)


def main(argv=None):
    parser = ArgParser(prog="worktree.py")
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("goal")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        code, out = COMMANDS[args.command](os.getcwd(), args.goal)
    except Stopped as stopped:
        code = EXIT_STOP
        out = {"ok": False, "stops": [s.to_json() for s in stopped.stops]}
        if args.command == "status":
            out.update({"action": "stop", "goal": args.goal})
    except Exception as exc:  # 예상 못 한 실패는 script 오류
        code, out = EXIT_ERROR, {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc)}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(summarize(args.command, out))
    return code


if __name__ == "__main__":
    sys.exit(main())
