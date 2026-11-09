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


def try_git(cwd, *args):
    """실패해도 예외를 내지 않는다. (종료 코드, stdout, stderr)"""
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return out.returncode, out.stdout, out.stderr


def run_git(cwd, *args):
    code, stdout, stderr = try_git(cwd, *args)
    if code != 0:
        raise GitError("git %s: %s" % (" ".join(args), stderr.strip()))
    return stdout


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


def prune_empty_dirs(root, rel, stop):
    """rel의 위 폴더가 비었으면 stop(그 자신은 남김)까지 올라가며 지운다."""
    parent = os.path.dirname(rel)
    while parent and is_under(parent, stop):
        full = os.path.join(root, parent)
        if not os.path.isdir(full) or os.path.islink(full) or os.listdir(full):
            return
        os.rmdir(full)
        parent = os.path.dirname(parent)


SYNC_MODES = ("sync", "sync-empty")


def item_fingerprints(root, item, matchers):
    """copy·sync 항목의 파일마다 지문. 아래에서 방식이 바뀌는 곳은 뺀다.

    except(만들 때 있던 자리)만으로는 만든 뒤 새로 생긴 `**/__pycache__` 같은 자리를 못 빼므로,
    경로마다 영수증에 적은 목록 줄로 다시 고른다.
    """
    path, mode, excepts = item["path"], item["mode"], item.get("except", [])
    out = {}

    def visit(rel):
        full = os.path.join(root, rel)
        if rel != path:
            m = most_specific(matchers, rel)
            if covered(rel, excepts) or (m is not None and m.mode != mode):
                return
        if os.path.isdir(full) and not os.path.islink(full):
            for name in sorted(os.listdir(full)):
                visit(rel + "/" + name)
        else:
            out.update(fingerprints(root, rel))

    if os.path.lexists(os.path.join(root, path)):
        visit(path)
    return out


def sync_decisions(main, wt, item, matchers):
    """sync 항목의 파일마다 three_way. (돌려줄 [(경로, worktree 지문)], 충돌 [경로], 판정한 worktree 지문)"""
    base = item.get("base", {})  # 만들 때 없던 항목은 시작 지문이 빈 것이다
    ours, theirs = item_fingerprints(main, item, matchers), item_fingerprints(wt, item, matchers)
    take, conflicts = [], []
    for path in sorted(set(base) | set(ours) | set(theirs)):
        verdict = three_way(base.get(path), ours.get(path), theirs.get(path))
        if verdict == "take-worktree":
            take.append((path, theirs.get(path)))
        elif verdict == "conflict":
            conflicts.append(path)
    return take, conflicts, theirs


def apply_sync(main, wt, item_path, take):
    """worktree 쪽을 따를 파일을 원래 폴더에 반영한다. 지운 것을 먼저 지워야 폴더↔파일 바뀜도 맞는다."""
    for path, fp in take:
        if fp is None:
            full = os.path.join(main, path)
            if os.path.lexists(full):
                remove_entry(full)
            prune_empty_dirs(main, path, item_path)
    for path, fp in take:
        if fp is not None:
            dst = os.path.join(main, path)
            if os.path.islink(dst) or os.path.isfile(dst):
                os.unlink(dst)
            elif os.path.isdir(dst):
                os.rmdir(dst)  # 비어 있지 않으면 실패한다(지우지 않는다)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            copy_entry(os.path.join(wt, path), dst)


def skipped_by_rule(matchers, rel):
    """목록 줄로 보면 skip인 경로. 만들 때 없던 skip 자리(setup이 만든 폴더, 새 `__pycache__`)도 여기에 걸린다."""
    m = most_specific(matchers, rel)
    return m is not None and m.mode == "skip"


def clear_items(wt, items, matchers):
    """worktree에 남은 목록 항목을 지운다. git이 추적하지 않는 것만 건드린다.

    skip 항목과 skip 규칙에 맞는 경로는 통째로 지운다. sync 사본은 끝내기가 판정할 때 본 내용(`seen`)과
    지문이 같은 파일만 지운다. 판정 뒤에 고치거나 새로 만든 파일은 돌아가지 않은 작업이라 남기고,
    그러면 git이 worktree 지우기를 거부한다(remove-refused).
    지울 수 있는 것은 모두 지우고, 지우지 못한 경로(열린 파일·권한)를 worktree 기준으로 돌려준다.
    """
    skips = [i["path"] for i in items if i["mode"] == "skip"]
    syncs = [i["path"] for i in items if i["mode"] in SYNC_MODES]
    seen = {}
    for item in items:
        if item["mode"] in SYNC_MODES:
            seen.update(item.get("seen", {}))
    skip_rules = [m for m in matchers if m.mode == "skip"]
    entries = untracked_entries(wt)
    failed = []

    def drop(rel):
        full = os.path.join(wt, rel)
        if os.path.isdir(full) and not os.path.islink(full):
            shutil.rmtree(full, ignore_errors=True)  # 나머지는 지우고 남은 것을 아래에서 센다
        else:
            try:
                os.unlink(full)
            except OSError:
                pass
        if os.path.lexists(full):
            left = leftovers(full) if os.path.isdir(full) and not os.path.islink(full) else []
            failed.extend([rel + "/" + p for p in left] or [rel])

    def visit(rel):
        full = os.path.join(wt, rel)
        if covered(rel, skips) or skipped_by_rule(matchers, rel):
            drop(rel)
        elif os.path.isdir(full) and not os.path.islink(full):
            if (covered(rel, syncs) or any(is_under(t, rel) for t in skips + syncs)
                    or any(m.below(rel.split("/")) for m in skip_rules)):
                for name in sorted(os.listdir(full)):
                    visit(rel + "/" + name)
        elif rel in seen and fingerprints(wt, rel).get(rel) == seen[rel]:
            drop(rel)

    for entry in sorted(entries):
        if not any(is_under(entry, other) for other in entries) and os.path.lexists(os.path.join(wt, entry)):
            visit(entry)
    return failed


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


def three_way(base, main, worktree):
    """Q20 표. 파일 하나의 시작·원래·worktree 지문(없으면 None) → keep-main · take-worktree · same · conflict.

    한쪽만 바뀌면 그쪽을 따르고, 양쪽이 같게 바뀌면 같고, 다르게 바뀌면 충돌이다. 새 파일·지운 파일도 같은 규칙이다.
    """
    if main == worktree:
        return "same"
    if main == base:
        return "take-worktree"
    if worktree == base:
        return "keep-main"
    return "conflict"


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


RECEIPT_STATES = ("creating", "working", "finishing")
RECEIPT_KEYS = (("goal", str), ("state", str), ("main", str), ("worktree", str), ("branch", str),
                ("base", dict), ("moved_by_git", list), ("items", list), ("done", list))


def receipt_problem(data, goal):
    """영수증을 믿고 쓸 수 없는 이유. 쓸 수 있으면 None."""
    if not isinstance(data, dict):
        return "JSON 객체가 아니다"
    if data.get("version") != RECEIPT_VERSION:
        return "모르는 version %r" % (data.get("version"),)
    for key, kind in RECEIPT_KEYS:
        if not isinstance(data.get(key), kind):
            return "'%s' 칸이 없거나 모양이 다르다" % key
    if data["state"] not in RECEIPT_STATES:
        return "모르는 상태 '%s'" % data["state"]
    if data["goal"] != goal:
        return "다른 goal('%s')의 영수증이다" % data["goal"]
    if not isinstance(data["base"].get("branch"), str):
        return "'base.branch' 칸이 없다"
    return None


def load_receipt(repo, goal):
    path = receipt_path(repo, goal)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
    except ValueError as exc:
        problem = "JSON으로 읽히지 않는다(%s)" % exc
    else:
        problem = receipt_problem(data, goal)
    if problem:
        raise Stopped([Stop("receipt-invalid", "영수증을 쓸 수 없다: %s. 내용을 확인하고 고치거나 정리 방법을 정한다." % problem,
                            [path])])
    return Receipt(path, data)


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
        "rules": ctx["rules"],   # 끝내기가 만든 뒤 새로 생긴 자리(`**/__pycache__` 등)도 같은 규칙으로 고르게
        "items": ctx["items"],   # 같은 목록이라 apply가 적은 지문도 영수증에 들어간다
        "done": [],
    })


def rule_json(rule):
    return {"mode": rule.mode, "pattern": rule.pattern, "line": rule.line}


def receipt_matchers(receipt):
    return [Matcher(Rule(r["mode"], r["pattern"], r["line"]), receipt["goal"])
            for r in receipt.data.get("rules", [])]


def receipt_item(item):
    data = {"path": item.path, "mode": item.mode}
    if item.excepts:
        data["except"] = list(item.excepts)
    if item.missing:
        data["missing"] = True
    return data


def registered(repo, path):
    """path가 아직 git에 worktree로 등록돼 있는지. 원래 폴더에서 묻는다."""
    listing = run_git(repo.main, "worktree", "list", "--porcelain")
    return any(os.path.realpath(line[len("worktree "):]) == os.path.realpath(path)
               for line in listing.splitlines() if line.startswith("worktree "))


def leftovers(root):
    """폴더에 남은 파일과 빈 폴더를 git 없이 훑는다. 등록이 지워진 worktree에서 git을 부르면
    위 폴더의 다른 저장소를 볼 수 있다."""
    out = []
    for top, dirs, files in os.walk(root):
        rel = os.path.relpath(top, root)
        names = files + [d for d in dirs if os.path.islink(os.path.join(top, d))
                         or not os.listdir(os.path.join(top, d))]
        out += [n if rel == "." else rel + "/" + n for n in names]
    return sorted(out)


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


def worktree_uncommitted(receipt):
    """worktree의 미커밋 작업. 목록 항목(링크·사본·옮긴 폴더, 만들 때 없던 항목 포함)과
    목록 줄로 보면 skip인 새 파일은 커밋할 대상이 아니라 뺀다."""
    items = [i["path"] for i in receipt["items"]]
    matchers = receipt_matchers(receipt)
    return [path for xy, path in status_entries(receipt["worktree"], "--untracked-files=all")
            if not (xy == "??" and (covered(path, items) or skipped_by_rule(matchers, path)))]


def check_goal(goal):
    """goal 이름이 브랜치 `goal/<goal>`, 폴더 `<저장소>-<goal>`, 영수증 `<goal>.json` 이름으로 쓰일 수 있는지.
    `/`는 git이 받아도 폴더·영수증 위치를 바꾸므로 따로 막는다."""
    ref = subprocess.run(["git", "check-ref-format", "refs/heads/" + branch_name(goal)],
                         capture_output=True, text=True)
    if not goal or "/" in goal or ref.returncode != 0:
        raise Stopped([Stop("goal-invalid",
                            "goal 이름 '%s'은 브랜치·폴더 이름으로 쓸 수 없다. 빈칸·`/`·`..`·특수 문자가 없는 이름을 쓴다." % goal)])


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
    if repo.in_worktree and (receipt is None or receipt["worktree"] != repo.top):
        return "stop", Stop("foreign-worktree",
                            "이 goal을 위해 이 skill이 만든 worktree가 아닌 worktree 안에서 불렀다. 원래 폴더(%s)에서 부른다."
                            % repo.main, [repo.top])
    if receipt is None:
        return "create", None
    state = receipt["state"]
    if state == "creating":
        return "stop", Stop("create-incomplete", "만들기가 도중에 멈췄다. 끝난 단계를 보고 정리 방법을 정해야 한다.",
                            done=list(receipt["done"]))
    # worktree 지우기 단계에 들어섰으면(merge와 항목 되돌리기가 끝남) worktree에 남은 일이 없어 없어도 된다
    done = receipt["done"]
    removing = (state == "finishing" and "merge" in done
                and ("restore-items" in done or not receipt["items"]))
    if not removing and not os.path.isdir(receipt["worktree"]):
        return "stop", Stop("worktree-missing", "영수증은 있는데 worktree 폴더가 없다. 폴더를 지웠거나 옮겼는지 확인한다.",
                            [receipt["worktree"]])
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


def create_stops(repo, goal):
    """Q16 검사. 걸린 것을 모두 모아 돌려준다."""
    wt = worktree_path(repo, goal)
    br = branch_name(goal)
    stops = []
    if try_git(repo.main, "rev-parse", "--verify", "--quiet", "refs/heads/" + br)[0] == 0:
        stops.append(Stop("branch-exists", "브랜치 '%s'가 이미 있다. 다른 goal 이름을 쓰거나 그 브랜치를 정리한다." % br))
    if os.path.lexists(wt):
        stops.append(Stop("folder-exists", "worktree를 만들 폴더가 이미 있다. 다른 goal 이름을 쓰거나 그 폴더를 정리한다.", [wt]))
    busy = git_busy(repo.top)
    if busy:
        stops.append(Stop("git-busy", "이 폴더에서 %s 작업이 진행 중이다. 먼저 끝내거나 취소한다." % "·".join(busy), [repo.top]))
    return stops


BUSY_MARKERS = (("MERGE_HEAD", "merge"), ("rebase-merge", "rebase"), ("rebase-apply", "rebase"),
                ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert"))


def git_busy(cwd):
    """진행 중인 merge·rebase·cherry-pick·revert. stash·merge가 그 위에서 실패하거나 섞인다."""
    found = []
    for marker, name in BUSY_MARKERS:
        path = os.path.join(cwd, run_git(cwd, "rev-parse", "--git-path", marker).strip())
        if os.path.exists(path) and name not in found:
            found.append(name)
    return found


def plan_create(repo, rules, items, goal):
    stops = create_stops(repo, goal)
    if stops:
        raise Stopped(stops)
    wt = worktree_path(repo, goal)
    br = branch_name(goal)
    listed = [i for i in items if i.listed]
    present = [i.path for i in listed if not i.missing]
    matchers = [Matcher(r, goal) for r in rules.rules]
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
            if item["mode"] in SYNC_MODES:
                item["base"] = {}  # 만들 때 없던 sync와 sync-empty는 빈 것에서 시작한다
            if item["mode"] == "sync-empty":
                os.makedirs(os.path.join(wt, item["path"]), exist_ok=True)
                continue
            if item.get("missing") or item["mode"] == "skip":
                continue
            for unit in units(repo.main, item["path"], item.get("except", [])):
                src, dst = os.path.join(repo.main, unit), os.path.join(wt, unit)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if item["mode"] == "link":
                    os.symlink(src, dst)
                elif item["mode"] in ("copy", "sync"):
                    copy_entry(src, dst)
                elif item["mode"] == "move":
                    move_entry(src, dst)
            if item["mode"] in ("copy", "sync"):
                item["base"] = item_fingerprints(wt, item, matchers)

    def setup(ctx):
        # 실패해도 멈추지 않고 종료 코드를 보고한다. 명령 출력은 stderr로 보내 stdout(JSON)을 깨지 않는다
        for cmd, _ in rules.setup:
            sys.stderr.flush()
            done = subprocess.run(cmd, shell=True, cwd=wt, stdin=subprocess.DEVNULL,
                                  stdout=sys.stderr.fileno(), stderr=sys.stderr.fileno())
            ctx["setup"].append({"cmd": cmd, "exit": done.returncode})

    steps = []
    if moved:
        steps.append(Step("stash", stash))
    steps.append(Step("worktree-add", worktree_add))
    if moved:
        steps.append(Step("stash-pop", stash_pop))
    if listed:
        steps.append(Step("items", place_items))
    if rules.setup:
        steps.append(Step("setup", setup))
    ctx = {"worktree": wt, "branch": br, "moved_by_git": moved, "setup": [],
           "rules": [rule_json(r) for r in rules.rules],
           "items": [receipt_item(i) for i in sorted(listed, key=lambda i: i.path)]}
    return steps, ctx


def merge_preview(cwd, branch):
    """작업 폴더를 건드리지 않고 HEAD에 branch를 합쳐 본다. 충돌 나는 파일 목록(없으면 빈 목록).
    원래 폴더의 미커밋 변경과 겹치는 것은 못 잡는다. 그건 merge가 스스로 거부한다(main-dirty-overlap)."""
    code, out, err = try_git(cwd, "merge-tree", "--write-tree", "--name-only", "--no-messages", "-z", "HEAD", branch)
    if code == 0:
        return []
    if code == 1:
        return sorted(set(p for p in out.split("\0")[1:] if p))  # 첫 칸은 합친 tree id
    raise GitError("git merge-tree: %s" % err.strip())


def git_listed_paths(text):
    """git 오류 메시지에서 탭으로 들여 쓴 파일 목록(언어 설정과 관계없이 같은 모양)."""
    return [line.strip() for line in text.splitlines() if line.startswith("\t") and line.strip()]


def plan_finish(repo, receipt):
    wt = receipt["worktree"]
    br = receipt["branch"]
    main = receipt["main"]
    done = receipt["done"]
    stops = []
    # merge 뒤(다시 부르기)에는 worktree의 새 작업이 합쳐지지 않으므로 worktree 지우기가 거부하게 둔다
    dirty = worktree_uncommitted(receipt) if "merge" not in done else []
    if dirty:
        stops.append(Stop("worktree-dirty", "worktree에 커밋 안 한 작업이 있다. worktree에서 커밋하거나 치운 뒤 다시 끝내기를 부른다.",
                          dirty))
    base = receipt["base"]["branch"]
    if repo.branch != base:
        stops.append(Stop("base-moved", "원래 폴더가 만들 때의 브랜치 '%s'가 아니라 '%s'에 있다. '%s'로 돌아간 뒤 다시 끝내기를 부른다."
                          % (base, repo.branch or "(브랜치 없음)", base)))
    elif "merge" not in done:  # 다른 브랜치를 기준으로 한 미리보기는 뜻이 없다
        conflicted = merge_preview(repo.main, br)
        if conflicted:
            stops.append(Stop("merge-conflict",
                              "합치면 충돌이 난다. worktree에서 '%s'를 먼저 merge해 충돌을 풀고 커밋한 뒤 다시 끝내기를 부른다." % base,
                              conflicted))

    move_back = {}
    taken = []
    for item in receipt["items"]:
        if item["mode"] == "move" and "restore-items" not in done:  # 이미 되돌렸으면 다시 옮기지 않는다
            move_back[item["path"]] = move_back_units(wt, item)
            taken += [u for u in move_back[item["path"]] if os.path.lexists(os.path.join(main, u))]
    # sync 판정은 바꾸기 전에 모두 한다. 이미 반영했으면(restore-items 끝남) worktree 사본이 없으니 다시 하지 않는다
    matchers = receipt_matchers(receipt)
    sync_take, sync_seen, conflicts = {}, {}, []
    if "restore-items" not in done:
        for item in receipt["items"]:
            if item["mode"] in SYNC_MODES:
                sync_take[item["path"]], found, sync_seen[item["path"]] = sync_decisions(main, wt, item, matchers)
                conflicts += found
    if taken:
        stops.append(Stop("move-target-exists",
                          "move 항목을 되돌릴 자리에 같은 이름이 이미 있다. 원래 폴더 쪽을 치운 뒤 다시 끝내기를 부른다.",
                          taken))
    if conflicts:
        stops.append(Stop("sync-conflict",
                          "sync 항목에서 원래 폴더와 worktree가 서로 다르게 바꾼 파일이 있다. 한쪽으로 맞춘 뒤 다시 끝내기를 부른다.",
                          conflicts))
    if stops:
        raise Stopped(stops)

    def merge(ctx):
        code, out, err = try_git(repo.main, "merge", "-q", "--no-ff", "--no-edit", br)
        if code != 0:
            text = (err + out).strip()
            paths = git_listed_paths(text)
            # 시작도 하지 않고 거부했다(HEAD 그대로, merge 진행 중 아님): 원래 폴더의 미커밋 변경과 겹침
            if paths and not git_busy(repo.main) and run_git(repo.main, "rev-parse", "HEAD").strip() == repo.head:
                raise Stopped([Stop("main-dirty-overlap",
                                    "원래 폴더의 커밋 안 한 변경이 합칠 내용과 겹쳐 git이 merge를 거부했다. 원래 폴더는 그대로다. "
                                    "그 변경을 어떻게 할지 정한 뒤 다시 끝내기를 부른다.", paths, git=text)])
            raise GitError("git merge: %s" % text)
        receipt["merge_commit"] = run_git(repo.main, "rev-parse", "HEAD").strip()

    def restore_items(ctx):
        # 다시 불러도 같은 결과가 되게 이미 끝난 것은 건너뛴다. copy_changed는 영수증에 남긴다
        changed = receipt.data.setdefault("copy_changed", [])
        synced = receipt.data.setdefault("synced", [])
        for item in receipt["items"]:
            mode = item["mode"]
            if mode == "link":
                for unit in units(wt, item["path"], item.get("except", [])):
                    full = os.path.join(wt, unit)
                    if os.path.islink(full) and os.readlink(full) == os.path.join(main, unit):
                        os.unlink(full)
            elif mode == "copy":
                now, base = item_fingerprints(wt, item, matchers), item.get("base", {})  # 새 skip 자리는 빠진다
                changed += sorted(p for p in set(now) | set(base)
                                  if now.get(p) != base.get(p) and p not in changed)
                for unit in units(wt, item["path"], item.get("except", [])):
                    remove_entry(os.path.join(wt, unit))
            elif mode == "move":
                for unit in move_back[item["path"]]:
                    dst = os.path.join(main, unit)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    move_entry(os.path.join(wt, unit), dst)
            elif mode in SYNC_MODES:
                take = sync_take[item["path"]]
                apply_sync(main, wt, item["path"], take)
                synced += sorted(p for p, _ in take if p not in synced)
                item["seen"] = sync_seen[item["path"]]  # worktree 지우기가 이 내용 그대로인 사본만 지운다

    def worktree_remove(ctx):
        text = ""
        if registered(repo, wt):
            # 돌려줄 것은 restore-items에서 돌려줬다. 폴더가 없으면 치울 것도 없고 git이 등록만 지운다
            failed = clear_items(wt, receipt["items"], matchers) if os.path.isdir(wt) else []
            if failed:  # git까지 가지 않았다. worktree는 그대로 저장소라 다시 부르면 다시 치운다
                raise Stopped([Stop("remove-incomplete",
                                    "worktree의 목록 항목을 치우다 일부를 지우지 못했다. git 등록은 남아 있고 합치기는 끝났다. "
                                    "`.nfs`로 시작하는 파일은 어떤 프로세스가 아직 열고 있는 파일이다. "
                                    "그 프로세스를 끄거나 권한을 고친 뒤 다시 끝내기를 부른다.", failed)])
            code, out, err = try_git(repo.main, "worktree", "remove", wt)
            text = (err + out).strip()
            if code != 0 and registered(repo, wt):  # 지우기 전에 거부했다. 강제로 지우지 않고 멈춘다(C3)
                left = [p for _, p in status_entries(wt, "--untracked-files=all")]
                raise Stopped([Stop("remove-refused",
                                    "worktree에 예상 못 한 파일이 남아 git이 worktree 지우기를 거부했다. 합치기는 끝났다. "
                                    "남은 파일을 옮기거나 치운 뒤 다시 끝내기를 부른다.", left, git=text)])
        if os.path.lexists(wt):
            # git은 폴더를 지우다 실패해도 등록을 지운다. 남은 폴더는 저장소가 아니라 git을 부르지 않는다
            raise Stopped([Stop("remove-incomplete",
                                "worktree 폴더를 지우다 도중에 실패했다. git 등록은 지워졌고 합치기는 끝났다. "
                                "`.nfs`로 시작하는 파일은 어떤 프로세스가 아직 열고 있는 파일이다. "
                                "그 프로세스를 끄거나 권한을 고친 뒤, 남은 폴더를 지우고 다시 끝내기를 부른다.",
                                leftovers(wt), git=text)])

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
    check_goal(goal)
    _, stop = decide(repo, load_receipt(repo, goal))  # 영수증이 있으면 아래 branch·folder 검사가 걸린다
    if stop is not None:
        raise Stopped([stop])
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
                     "setup": ctx["setup"]}


def cmd_finish(cwd, goal):
    repo = read_repo(cwd)
    check_goal(goal)
    receipt = load_receipt(repo, goal)
    _, stop = decide(repo, receipt)
    if stop is not None:
        raise Stopped([stop])
    if receipt is None:
        raise Stopped([Stop("receipt-missing", "이 goal의 영수증이 없다. 이 skill로 만든 worktree가 아니거나 이미 끝냈다.",
                            [receipt_path(repo, goal)])])
    if repo.in_worktree:  # worktree 세션은 원래 폴더·.git에 쓰지 못할 수 있다(C3). 영수증도 건드리지 않는다
        raise Stopped([Stop("run-from-main", "끝내기는 원래 폴더에서 부른다. 세션을 원래 폴더로 옮긴 뒤 다시 부른다.",
                            [receipt["main"]])])
    receipt["state"] = "finishing"
    receipt.save()
    steps, ctx = plan_finish(repo, receipt)
    apply(steps, ctx, receipt)
    receipt.delete()
    return EXIT_OK, {"ok": True, "merge_commit": receipt.data.get("merge_commit"),
                     "synced": receipt.data.get("synced", []),
                     "copy_changed": receipt.data.get("copy_changed", []),
                     "removed": [receipt["worktree"]]}


def cmd_status(cwd, goal):
    repo = read_repo(cwd)
    check_goal(goal)
    rules = load_rules(repo)
    receipt = load_receipt(repo, goal)
    action, stop = decide(repo, receipt)
    out = {"action": action, "goal": goal, "worktree": None,
           "unlisted": [], "uncommitted": [], "stops": []}
    if receipt is not None:
        out["worktree"] = receipt["worktree"]
    if action == "create":
        out["unlisted"] = unlisted(repo, inventory(repo, rules, goal))
    # worktree 안에서 부른 끝내기(처음이든 이어 하기든)는 ① 미커밋 검사에 이 목록을 쓴다
    if action == "finish" or (action == "continue-finish" and repo.top == receipt["worktree"]):
        out["uncommitted"] = worktree_uncommitted(receipt)
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
        for run in out.get("setup", []):
            if run["exit"] == 0:
                lines.append("준비 명령: " + run["cmd"])
            else:
                lines.append("준비 명령 실패(종료 코드 %d): %s" % (run["exit"], run["cmd"]))
    if command == "finish" and out.get("ok"):
        lines.append("합쳤다: " + str(out.get("merge_commit")))
        for path in out.get("synced", []):
            lines.append("원래 폴더로 돌려준 파일: " + path)
        for path in out.get("copy_changed", []):
            lines.append("바뀐 채로 버린 사본: " + path)
    for stop in out.get("stops", []):
        lines.append("멈춤 [%s] %s" % (stop["code"], stop["message"]))
        for path in stop.get("paths", []):
            lines.append("  - " + path)
        if stop.get("done") is not None:
            lines.append("  끝난 단계: " + (", ".join(stop["done"]) or "(없음)"))
        for line in stop.get("git", "").splitlines():
            lines.append("  git: " + line)
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
