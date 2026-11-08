#!/usr/bin/env python3
"""workflow-worktree: 지금 하던 작업을 저장소 옆 worktree로 옮기고, 끝나면 로컬 merge로 합친다.

명령: status · create · finish (뒤에 goal 이름, --json이면 JSON 출력)
종료 코드: 0 성공 · 2 멈춤 · 1 script 오류
구조: 검사 → 계획 → 실행. 상태를 바꾸는 것은 apply 하나다.
"""
import argparse
import errno
import hashlib
import json
import os
import re
import shutil
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


# ---------------------------------------------------------------- 목록 파일

LIST_FILE = ".workflow-worktree"
MODES = ("link", "copy", "sync", "sync-empty", "move", "skip")


class Rule:
    def __init__(self, mode, pattern, line):
        self.mode = mode
        self.pattern = pattern
        self.line = line


class Rules:
    def __init__(self, rules, setup):
        self.rules = rules      # [Rule]
        self.setup = setup      # [(명령, 줄 번호)]


def load_rules(repo):
    """목록 파일을 읽는다. 없으면 빈 목록. 잘못된 줄이 있으면 줄 번호와 함께 list-invalid로 멈춘다."""
    path = os.path.join(repo.top, LIST_FILE)
    if not os.path.exists(path):
        return Rules([], [])
    with open(path) as f:
        lines = f.read().splitlines()
    rules, setup, errors = [], [], []
    seen = {}
    for no, raw in enumerate(lines, 1):
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        parts = text.split(None, 1)
        mode = parts[0]
        rest = parts[1].strip() if len(parts) > 1 else ""
        if mode == "setup":
            if rest:
                setup.append((rest, no))
            else:
                errors.append((no, "setup 명령이 비어 있다"))
            continue
        if mode not in MODES:
            errors.append((no, "모르는 방식 '%s'" % mode))
            continue
        pattern = normalize_pattern(rest)
        if pattern is None:
            errors.append((no, "경로 '%s'를 쓸 수 없다(저장소 맨 위 기준 상대 경로)" % rest))
        elif pattern in seen:
            errors.append((seen[pattern], "같은 경로 '%s'가 %d행에 또 있다" % (pattern, no)))
            errors.append((no, "같은 경로 '%s'가 %d행에 이미 있다" % (pattern, seen[pattern])))
        else:
            seen[pattern] = no
            rules.append(Rule(mode, pattern, no))
    if errors:
        errors.sort()
        raise Stopped([Stop("list-invalid",
                            "목록 파일에 잘못된 줄이 있다: " + "; ".join("%d행 %s" % e for e in errors),
                            [LIST_FILE], lines=sorted(set(no for no, _ in errors)))])
    return Rules(rules, setup)


def normalize_pattern(text):
    """`./a/b/` → `a/b`. 비었거나 절대 경로이거나 `.`·`..`·빈 단계가 있으면 None."""
    if not text or text.startswith("/"):
        return None
    while text.startswith("./"):
        text = text[2:]
    text = text.rstrip("/")
    segs = text.split("/")
    if not text or any(s in ("", ".", "..") for s in segs):
        return None
    return text


# ---------------------------------------------------------------- 경로 맞추기

def seg_matches(pat, seg):
    if "*" not in pat:
        return pat == seg
    regex = "".join(".*" if ch == "*" else re.escape(ch) for ch in pat)
    return re.fullmatch(regex, seg) is not None


class Matcher:
    """goal 이름을 넣은 한 줄. `*`는 한 단계, `**`는 0개 이상의 단계."""

    def __init__(self, rule, goal):
        self.mode = rule.mode
        self.line = rule.line
        self.segs = rule.pattern.replace("{goal}", goal).split("/")
        self.literal = sum(1 for s in self.segs if "*" not in s)

    def _closure(self, states):
        out, stack = set(states), list(states)
        while stack:
            i = stack.pop()
            if i < len(self.segs) and self.segs[i] == "**" and i + 1 not in out:
                out.add(i + 1)
                stack.append(i + 1)
        return out

    def _walk(self, segs):
        """경로 단계를 하나씩 먹으며 (단계 수, 남은 상태)를 낸다."""
        states = self._closure({0})
        for d, seg in enumerate(segs, 1):
            nxt = set()
            for i in states:
                if i < len(self.segs):
                    if self.segs[i] == "**":
                        nxt.add(i)
                    elif seg_matches(self.segs[i], seg):
                        nxt.add(i + 1)
            states = self._closure(nxt)
            yield d, states
            if not states:
                return

    def depth(self, segs):
        """경로 자신이나 그 위 폴더 중 이 줄이 맞는 가장 깊은 곳의 단계 수. 안 맞으면 0."""
        best = 0
        for d, states in self._walk(segs):
            if len(self.segs) in states:
                best = d
        return best

    def below(self, segs):
        """이 경로 아래 어딘가에 맞을 수 있는가."""
        states = self._closure({0})
        for _, states in self._walk(segs):
            pass
        return any(i < len(self.segs) for i in states)

    @property
    def literal_path(self):
        return None if any("*" in s for s in self.segs) else "/".join(self.segs)


def most_specific(matchers, path):
    """가장 구체적인 줄: 더 깊은 곳에서 맞는 줄 → 글자 그대로인 단계가 많은 줄 → 뒤에 적은 줄."""
    segs = path.split("/")
    best, key = None, None
    for m in matchers:
        d = m.depth(segs)
        if d and (key is None or (d, m.literal, m.line) > key):
            best, key = m, (d, m.literal, m.line)
    return best


def is_under(path, parent):
    return path.startswith(parent + "/")


def covered(path, parents):
    return any(path == p or is_under(path, p) for p in parents)


# ---------------------------------------------------------------- 항목 모으기

DEFAULT_MODE = {"untracked": "git", "ignored": "skip"}
MISSING_MODES = ("move", "sync", "sync-empty")


class Item:
    def __init__(self, path, git, mode, matcher, children, missing=False):
        self.path = path
        self.git = git                  # untracked | ignored | None(없던 항목)
        self.mode = mode
        self.matcher = matcher          # None이면 Q22 기본값
        self.children = children        # 아래에서 방식이 바뀌는 항목
        self.missing = missing
        self.excepts = [c.path for c in children]

    @property
    def listed(self):
        return self.matcher is not None

    def to_json(self, path=None):
        return {"path": path or self.path, "git": self.git, "mode": self.mode,
                "from": "list" if self.listed else "default",
                "line": self.matcher.line if self.listed else None}


def untracked_entries(cwd, *pathspec):
    """git이 추적하지 않는 항목 {경로: untracked|ignored}. 통째로 추적하지 않는 폴더는 한 줄로 온다."""
    args = ["--untracked-files=normal", "--ignored"]
    if pathspec:
        args += ["--"] + list(pathspec)
    kinds = {"??": "untracked", "!!": "ignored"}
    return {path.rstrip("/"): kinds[xy] for xy, path in status_entries(cwd, *args) if xy in kinds}


def units(root, rel, excepts):
    """rel에서 excepts를 뺀 가장 큰 덩어리들. except가 아래에 있으면 폴더 안으로 내려간다."""
    full = os.path.join(root, rel)
    if not os.path.lexists(full) or covered(rel, excepts):
        return []
    if not any(is_under(e, rel) for e in excepts) or os.path.islink(full) or not os.path.isdir(full):
        return [rel]
    out = []
    for name in sorted(os.listdir(full)):
        out += units(root, rel + "/" + name, excepts)
    return out


def inventory(repo, rules, goal):
    """추적하지 않는 항목을 모아 방식을 붙인다. 목록이 우선이고, 없으면 Q22 기본값(untracked→git, ignored→skip).

    항목은 방식이 바뀌는 곳마다 하나다. 그 아래에서 다시 방식이 바뀌면 그 경로는 위 항목의 except가 된다.
    """
    root = repo.top
    matchers = [Matcher(r, goal) for r in rules.rules]
    entries = untracked_entries(root)

    def has_ancestor(path):
        segs = path.split("/")
        return any("/".join(segs[:i]) in entries for i in range(1, len(segs)))

    def walk(rel, kind, parent_mode):
        m = most_specific(matchers, rel)
        mode = m.mode if m else DEFAULT_MODE[kind]
        full = os.path.join(root, rel)
        subs = []
        if os.path.isdir(full) and not os.path.islink(full):
            segs = rel.split("/")
            descend = any(x.mode != mode and x.below(segs) for x in matchers)
            if m is None and not descend:
                descend = any(is_under(e, rel) and k != kind for e, k in entries.items())
            if descend:
                for name in sorted(os.listdir(full)):
                    child = rel + "/" + name
                    subs += walk(child, entries.get(child, kind), mode)
        if parent_mode is not None and mode == parent_mode:
            return subs
        return [Item(rel, kind, mode, m, subs)]

    tree = []
    for path in sorted(entries):
        if not has_ancestor(path):
            tree += walk(path, entries[path], None)
    items = []

    def flatten(nodes):
        for node in nodes:
            items.append(node)
            flatten(node.children)
    flatten(tree)

    for m in matchers:
        rel = m.literal_path
        if (m.mode in MISSING_MODES and rel and not os.path.lexists(os.path.join(root, rel))
                and most_specific(matchers, rel) is m):
            item = Item(rel, None, m.mode, m, [], missing=True)
            owners = [i for i in items if is_under(rel, i.path)]
            if owners:
                max(owners, key=lambda i: len(i.path)).excepts.append(rel)
            items.append(item)
    return items


def unlisted(repo, items):
    """목록에 없는 항목. 아래에 목록 항목이 있으면 그것을 뺀 덩어리로 보여 준다."""
    out = []
    for item in items:
        if not item.listed:
            out += [item.to_json(u) for u in units(repo.top, item.path, item.excepts)]
    return sorted(out, key=lambda i: i["path"])


# ---------------------------------------------------------------- 파일 다루기

def copy_entry(src, dst):
    """링크는 링크 그대로(상대 링크면 worktree 자기 파일을 가리킨다), 폴더는 안의 링크도 그대로 복사한다."""
    if os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    elif os.path.isdir(src):
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def move_entry(src, dst):
    """같은 디스크면 os.rename, 다른 디스크면 복사한 뒤 지운다."""
    try:
        os.rename(src, dst)
    except OSError as exc:
        if exc.errno != errno.EXDEV:
            raise
        copy_entry(src, dst)
        remove_entry(src)


def move_back_units(wt, item):
    """worktree에 있는 move 항목 중 git이 추적하지 않는 부분. 브랜치에 커밋한 부분은 merge가 맡는다."""
    path = item["path"]
    if not os.path.lexists(os.path.join(wt, path)):
        return []
    entries = untracked_entries(wt, path)
    out = []
    for entry in sorted(entries):
        if any(is_under(entry, other) for other in entries):
            continue
        top = path if is_under(path, entry) else entry  # git이 위 폴더로 묶어 보여 주면 항목 경로로 줄인다
        out += [u for u in units(wt, top, item.get("except", [])) if u not in out]
    return out


def remove_entry(path):
    if os.path.islink(path) or not os.path.isdir(path):
        os.unlink(path)
    else:
        shutil.rmtree(path)


def fingerprints(root, rel):
    """파일마다 지문: 내용의 sha256, 링크는 `link:<가리키는 곳>`. 폴더는 안으로 내려간다."""
    full = os.path.join(root, rel)
    if os.path.islink(full):
        return {rel: "link:" + os.readlink(full)}
    if os.path.isdir(full):
        out = {}
        for name in sorted(os.listdir(full)):
            out.update(fingerprints(root, rel + "/" + name))
        return out
    digest = hashlib.sha256()
    with open(full, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            digest.update(chunk)
    return {rel: digest.hexdigest()}


def item_fingerprints(root, item):
    out = {}
    for unit in units(root, item["path"], item.get("except", [])):
        out.update(fingerprints(root, unit))
    return out


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


def new_receipt(repo, goal, ctx):
    return Receipt(receipt_path(repo, goal), {
        "version": RECEIPT_VERSION,
        "goal": goal,
        "state": "creating",
        "main": repo.main,
        "worktree": ctx["worktree"],
        "branch": ctx["branch"],
        "base": {"branch": repo.branch, "commit": repo.head},
        "moved_by_git": ctx["moved_by_git"],
        "items": ctx["items"],   # 같은 목록이라 apply가 적은 지문도 영수증에 들어간다
        "done": [],
    })


def receipt_item(item):
    data = {"path": item.path, "mode": item.mode}
    if item.excepts:
        data["except"] = list(item.excepts)
    if item.missing:
        data["missing"] = True
    return data


def status_entries(cwd, *args):
    """`git status --porcelain -z`의 (XY, 경로) 목록."""
    raw = run_git(cwd, "status", "--porcelain", "-z", *args)
    parts = raw.split("\0")
    entries = []
    i = 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if not entry:
            continue
        xy, path = entry[:2], entry[3:]
        entries.append((xy, path))
        if "R" in xy or "C" in xy:
            i += 1  # 이름 바꾸기는 옛 경로가 한 칸 더 온다
    return entries


def worktree_uncommitted(repo, receipt):
    """worktree의 미커밋 작업. 목록 항목(링크·사본·옮긴 폴더, 만들 때 없던 항목 포함)은 커밋할 대상이 아니라 뺀다."""
    items = [i["path"] for i in receipt["items"]]
    return [path for xy, path in status_entries(repo.top, "--untracked-files=all")
            if not (xy == "??" and covered(path, items))]


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


def plan_create(repo, rules, items, goal):
    wt = worktree_path(repo, goal)
    br = branch_name(goal)
    listed = [i for i in items if i.listed]
    later = sorted(i.path for i in listed if i.mode in ("sync", "sync-empty"))
    if later:
        raise NotImplementedError("sync·sync-empty 방식은 아직 처리하지 못한다: " + ", ".join(later))
    present = [i.path for i in listed if not i.missing]
    # 목록 항목은 git 방식으로 옮기지 않는다(stash에서 뺀다)
    moved = [p for xy, p in status_entries(repo.main, "--untracked-files=all")
             if not (xy == "??" and covered(p, present))]

    def stash(ctx):
        args = ["stash", "push", "-q", "-u", "-m", "workflow-worktree:" + goal]
        if present:
            args += ["--", "."] + [":(exclude,literal)" + p for p in present]
        run_git(repo.main, *args)
        ctx["stash"] = run_git(repo.main, "rev-parse", "stash@{0}").strip()

    def worktree_add(ctx):
        run_git(repo.main, "worktree", "add", "-q", "-b", br, wt, "HEAD")

    def stash_pop(ctx):
        run_git(wt, "stash", "pop", "-q", "--index", find_stash(wt, ctx["stash"]))

    def place_items(ctx):
        for item in ctx["items"]:
            if item.get("missing") or item["mode"] == "skip":
                continue
            for unit in units(repo.main, item["path"], item.get("except", [])):
                src, dst = os.path.join(repo.main, unit), os.path.join(wt, unit)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if item["mode"] == "link":
                    os.symlink(src, dst)
                elif item["mode"] == "copy":
                    copy_entry(src, dst)
                elif item["mode"] == "move":
                    move_entry(src, dst)
            if item["mode"] == "copy":
                item["base"] = item_fingerprints(wt, item)

    steps = []
    if moved:
        steps.append(Step("stash", stash))
    steps.append(Step("worktree-add", worktree_add))
    if moved:
        steps.append(Step("stash-pop", stash_pop))
    if listed:
        steps.append(Step("items", place_items))
    ctx = {"worktree": wt, "branch": br, "moved_by_git": moved,
           "items": [receipt_item(i) for i in sorted(listed, key=lambda i: i.path)]}
    return steps, ctx


def plan_finish(repo, receipt):
    wt = receipt["worktree"]
    br = receipt["branch"]
    main = receipt["main"]

    move_back = {}
    taken = []
    for item in receipt["items"]:
        if item["mode"] == "move":
            move_back[item["path"]] = move_back_units(wt, item)
            taken += [u for u in move_back[item["path"]] if os.path.lexists(os.path.join(main, u))]
    if taken:
        raise Stopped([Stop("move-target-exists",
                            "move 항목을 되돌릴 자리에 같은 이름이 이미 있다. 원래 폴더 쪽을 치운 뒤 다시 끝내기를 부른다.",
                            taken)])

    def merge(ctx):
        run_git(repo.main, "merge", "-q", "--no-ff", "--no-edit", br)
        receipt["merge_commit"] = run_git(repo.main, "rev-parse", "HEAD").strip()

    def restore_items(ctx):
        # 다시 불러도 같은 결과가 되게 이미 끝난 것은 건너뛴다. copy_changed는 영수증에 남긴다
        changed = receipt.data.setdefault("copy_changed", [])
        for item in receipt["items"]:
            mode = item["mode"]
            if mode == "link":
                for unit in units(wt, item["path"], item.get("except", [])):
                    full = os.path.join(wt, unit)
                    if os.path.islink(full) and os.readlink(full) == os.path.join(main, unit):
                        os.unlink(full)
            elif mode == "copy":
                now, base = item_fingerprints(wt, item), item.get("base", {})
                changed += sorted(p for p in set(now) | set(base)
                                  if now.get(p) != base.get(p) and p not in changed)
                for unit in units(wt, item["path"], item.get("except", [])):
                    remove_entry(os.path.join(wt, unit))
            elif mode == "move":
                for unit in move_back[item["path"]]:
                    dst = os.path.join(main, unit)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    move_entry(os.path.join(wt, unit), dst)

    def worktree_remove(ctx):
        run_git(repo.main, "worktree", "remove", wt)

    def branch_delete(ctx):
        run_git(repo.main, "branch", "-q", "-d", br)

    steps = [Step("merge", merge)]
    if receipt["items"]:
        steps.append(Step("restore-items", restore_items))  # 만들기의 "items"와 겹치지 않게
    steps += [Step("worktree-remove", worktree_remove), Step("branch-delete", branch_delete)]
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
    rules = load_rules(repo)
    items = inventory(repo, rules, goal)
    steps, ctx = plan_create(repo, rules, items, goal)
    receipt = new_receipt(repo, goal, ctx)
    receipt.save()
    apply(steps, ctx, receipt)
    receipt["state"] = "working"
    receipt.save()
    shown = [{k: v for k, v in i.items() if k != "base"} for i in ctx["items"]]
    return EXIT_OK, {"ok": True, "worktree": ctx["worktree"], "branch": ctx["branch"],
                     "moved_by_git": ctx["moved_by_git"], "items": shown,
                     "missing": [i["path"] for i in ctx["items"] if i.get("missing")],
                     "setup": []}


def cmd_finish(cwd, goal):
    repo = read_repo(cwd)
    receipt = load_receipt(repo, goal)
    receipt["state"] = "finishing"
    receipt.save()
    steps, ctx = plan_finish(repo, receipt)
    apply(steps, ctx, receipt)
    receipt.delete()
    return EXIT_OK, {"ok": True, "merge_commit": receipt.data.get("merge_commit"),
                     "synced": [], "copy_changed": receipt.data.get("copy_changed", []),
                     "removed": [receipt["worktree"]]}


def cmd_status(cwd, goal):
    repo = read_repo(cwd)
    rules = load_rules(repo)
    receipt = load_receipt(repo, goal)
    action, stop = decide(repo, receipt)
    out = {"action": action, "goal": goal, "worktree": None,
           "unlisted": [], "uncommitted": [], "stops": []}
    if receipt is not None:
        out["worktree"] = receipt["worktree"]
    if action == "create":
        out["unlisted"] = unlisted(repo, inventory(repo, rules, goal))
    if action == "finish":
        out["uncommitted"] = worktree_uncommitted(repo, receipt)
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
        for item in out.get("items", []):
            if not item.get("missing"):
                lines.append("목록 항목: %s → %s" % (item["path"], item["mode"]))
        for path in out.get("missing", []):
            lines.append("만들 때 없던 항목: " + path)
    if command == "finish" and out.get("ok"):
        lines.append("합쳤다: " + str(out.get("merge_commit")))
        for path in out.get("copy_changed", []):
            lines.append("바뀐 채로 버린 사본: " + path)
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
