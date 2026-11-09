"""workflow-worktree script 시험.

바깥 seam(status·create·finish 명령과 목록 파일)을 임시 폴더의 진짜 git 저장소에서 시험한다.
내부 seam은 3-way 판정(`three_way`) 하나다.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "worktree.py")

sys.path.insert(0, os.path.dirname(HERE))
import worktree  # noqa: E402  내부 seam three_way만 쓴다

# design.md "데이터 모양" 5의 stop code 목록. SKILL.md의 해결 표가 이 code로 찾는다
STOP_CODES = {
    "not-git-repo", "goal-invalid", "branch-exists", "folder-exists", "git-busy", "list-invalid",
    "worktree-dirty", "base-moved", "sync-conflict", "move-target-exists", "merge-conflict",
    "main-dirty-overlap", "remove-refused", "run-from-main", "receipt-missing",
    "receipt-invalid", "worktree-missing", "create-incomplete", "foreign-worktree", "remove-incomplete",
}


def git(cwd, *args):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError("git %s failed: %s" % (" ".join(args), out.stderr))
    return out.stdout


def git_may_fail(cwd, *args):
    """충돌로 멈추는 merge·rebase처럼 실패가 예상되는 git 명령."""
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          env=dict(os.environ, GIT_EDITOR="true")).returncode


def check_stop_shape(stop):
    """D9: 모든 Stop에 영어 code, 한국어 message, paths 목록이 있다."""
    assert stop.get("code") in STOP_CODES, "unknown stop code: %r" % stop
    assert re.search("[가-힣]", stop.get("message", "")), "message not Korean: %r" % stop
    assert isinstance(stop.get("paths"), list), "paths missing: %r" % stop


class Repo:
    """임시 부모 폴더 안에 `proj` 저장소 하나를 만든다. worktree는 그 옆에 생긴다."""

    def __init__(self, name="proj"):
        self.parent = os.path.realpath(tempfile.mkdtemp(prefix="wt-test-"))
        self.path = os.path.join(self.parent, name)
        os.makedirs(self.path)
        git(self.path, "-c", "init.defaultBranch=main", "init", "-q")
        git(self.path, "config", "user.name", "tester")
        git(self.path, "config", "user.email", "tester@example.com")
        git(self.path, "config", "commit.gpgsign", "false")
        self.write("a.txt", "a\n")
        git(self.path, "add", "a.txt")
        git(self.path, "commit", "-q", "-m", "init")

    def cleanup(self):
        shutil.rmtree(self.parent, ignore_errors=True)

    def write(self, rel, text, root=None):
        full = os.path.join(root or self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def list_file(self, text):
        """목록 파일 `.workflow-worktree`를 쓰고 커밋한다(D4: 추적 파일)."""
        self.write(".workflow-worktree", text)
        git(self.path, "add", ".workflow-worktree")
        git(self.path, "commit", "-q", "-m", "list")

    def head(self, cwd=None):
        return git(cwd or self.path, "rev-parse", "HEAD").strip()

    def wt_path(self, goal):
        return os.path.join(self.parent, os.path.basename(self.path) + "-" + goal)

    def run(self, *args, cwd=None):
        """script를 --json으로 부르고 (종료 코드, JSON)을 돌려준다."""
        out = subprocess.run(
            [sys.executable, SCRIPT, *args, "--json"],
            cwd=cwd or self.path, capture_output=True, text=True,
        )
        try:
            data = json.loads(out.stdout)
        except ValueError:
            raise AssertionError("not JSON (exit %d): %r %r" % (out.returncode, out.stdout, out.stderr))
        for stop in data.get("stops", []):
            check_stop_shape(stop)
        return out.returncode, data

    def receipt_file(self, goal="goal-x"):
        return os.path.join(self.path, ".git", "workflow-worktree", goal + ".json")

    def snapshot(self):
        """E6 전후 비교: 브랜치·worktree 목록·stash·폴더마다 git status, 부모 폴더 아래 파일 목록과 내용 지문, 영수증."""
        files = {}
        for dirpath, dirnames, names in os.walk(self.parent):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for name in dirnames + names:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, self.parent)
                if os.path.islink(full):
                    files[rel] = "link:" + os.readlink(full)
                elif os.path.isdir(full):
                    files[rel] = "dir"
                else:
                    with open(full, "rb") as f:
                        files[rel] = hashlib.sha256(f.read()).hexdigest()
        worktrees = git(self.path, "worktree", "list", "--porcelain")
        status = {}
        for line in worktrees.splitlines():
            if line.startswith("worktree ") and os.path.isdir(line[len("worktree "):]):
                root = line[len("worktree "):]
                status[root] = git(root, "status", "--porcelain", "--untracked-files=all")
        receipt = None
        if os.path.exists(self.receipt_file()):
            with open(self.receipt_file()) as f:
                receipt = f.read()
        return {"branches": git(self.path, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads"),
                "worktrees": worktrees, "stash": git(self.path, "stash", "list", "--format=%H"),
                "status": status, "files": files, "receipt": receipt}


class StopTestCase(unittest.TestCase):
    """멈춤마다 종료 코드 2와 code, 그리고 E6 전후 상태 같음을 확인한다."""

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.wt = self.repo.wt_path("goal-x")

    def assert_stops(self, code, *args, cwd=None, finishing=False):
        """명령이 code로 멈추고 아무것도 바꾸지 않았는지. finishing이면 영수증 상태가 finishing으로 바뀐 것만 허용한다."""
        before = self.repo.snapshot()
        exit_code, out = self.repo.run(*args, cwd=cwd)
        after = self.repo.snapshot()
        self.assertEqual(exit_code, 2, out)
        self.assertIn(code, [s["code"] for s in out["stops"]], out)
        if finishing:
            receipt = json.loads(after["receipt"])
            self.assertEqual(receipt["state"], "finishing")
            receipt["state"] = json.loads(before["receipt"])["state"]
            after["receipt"] = json.dumps(receipt)
            before["receipt"] = json.dumps(json.loads(before["receipt"]))
        self.assertEqual(after, before)
        return [s for s in out["stops"] if s["code"] == code][0]

    def commit_in_wt(self, rel="goal.txt", text="goal work\n"):
        self.repo.write(rel, text, root=self.wt)
        git(self.wt, "add", rel)
        git(self.wt, "commit", "-q", "-m", "goal work")

    def make_conflict(self):
        """worktree와 원래 폴더가 a.txt를 서로 다르게 고쳐 커밋한다."""
        self.repo.run("create", "goal-x")
        self.commit_in_wt("a.txt", "a\nfrom worktree\n")
        self.repo.write("a.txt", "a\nfrom main\n")
        git(self.repo.path, "commit", "-q", "-am", "main work")

    def receipt(self):
        with open(self.repo.receipt_file()) as f:
            return json.load(f)

    def read(self, rel, root=None):
        with open(os.path.join(root or self.repo.path, rel)) as f:
            return f.read()

    def leave_unexpected_file(self):
        """link 항목 docs의 링크를 worktree에서 실제 폴더로 바꿔 둔다. 목록 항목 아래라 미커밋 검사는 통과하고
        링크가 아니라 지워지지 않으므로 worktree 지우기 때 남는다."""
        os.unlink(os.path.join(self.wt, "docs"))
        self.repo.write("docs/own.md", "made in worktree instead of the link\n", root=self.wt)


class CreateTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_create_makes_sibling_worktree_on_goal_branch_from_head(self):
        head = self.repo.head()
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        wt = self.repo.wt_path("goal-x")
        self.assertEqual(out["worktree"], wt)
        self.assertEqual(out["branch"], "goal/goal-x")
        listing = git(self.repo.path, "worktree", "list", "--porcelain")
        self.assertIn("worktree " + wt, listing)
        self.assertEqual(git(wt, "branch", "--show-current").strip(), "goal/goal-x")
        self.assertEqual(self.repo.head(wt), head)

    def test_create_moves_uncommitted_changes_and_leaves_main_clean(self):
        self.repo.write("b.txt", "b\n")
        git(self.repo.path, "add", "b.txt")
        git(self.repo.path, "commit", "-q", "-m", "b")
        self.repo.write("a.txt", "a\nstaged\n")
        git(self.repo.path, "add", "a.txt")
        self.repo.write("b.txt", "b\nunstaged\n")
        self.repo.write("new.txt", "new\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        wt = self.repo.wt_path("goal-x")
        status = git(wt, "status", "--porcelain").splitlines()
        self.assertEqual(sorted(status), [" M b.txt", "?? new.txt", "M  a.txt"])
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), "")
        self.assertEqual(git(self.repo.path, "stash", "list"), "")
        self.assertEqual(sorted(out["moved_by_git"]), ["a.txt", "b.txt", "new.txt"])

    def test_create_writes_working_receipt_in_git_dir(self):
        head = self.repo.head()
        self.repo.write("new.txt", "new\n")
        self.repo.run("create", "goal-x")
        path = os.path.join(self.repo.path, ".git", "workflow-worktree", "goal-x.json")
        with open(path) as f:
            receipt = json.load(f)
        self.assertEqual(receipt["version"], 1)
        self.assertEqual(receipt["goal"], "goal-x")
        self.assertEqual(receipt["state"], "working")
        self.assertEqual(receipt["main"], self.repo.path)
        self.assertEqual(receipt["worktree"], self.repo.wt_path("goal-x"))
        self.assertEqual(receipt["branch"], "goal/goal-x")
        self.assertEqual(receipt["base"], {"branch": "main", "commit": head})
        self.assertEqual(receipt["moved_by_git"], ["new.txt"])
        self.assertEqual(receipt["items"], [])
        self.assertEqual(receipt["done"], ["stash", "worktree-add", "stash-pop"])


class FinishTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_finish_merges_with_merge_commit_and_cleans_up(self):
        self.repo.run("create", "goal-x")
        wt = self.repo.wt_path("goal-x")
        self.repo.write("goal.txt", "goal work\n", root=wt)
        git(wt, "add", "goal.txt")
        git(wt, "commit", "-q", "-m", "goal work")
        self.repo.write("other.txt", "other goal\n")
        git(self.repo.path, "add", "other.txt")
        git(self.repo.path, "commit", "-q", "-m", "other goal")

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        parents = git(self.repo.path, "rev-list", "--parents", "-n", "1", "HEAD").split()
        self.assertEqual(len(parents), 3)  # 자기 자신 + 부모 둘
        self.assertEqual(out["merge_commit"], parents[0])
        self.assertTrue(os.path.exists(os.path.join(self.repo.path, "goal.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.repo.path, "other.txt")))
        self.assertFalse(os.path.exists(wt))
        self.assertNotIn(wt, git(self.repo.path, "worktree", "list", "--porcelain"))
        self.assertEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        receipt = os.path.join(self.repo.path, ".git", "workflow-worktree", "goal-x.json")
        self.assertFalse(os.path.exists(receipt))


class OutputTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_default_output_is_korean_summary_not_json(self):
        out = subprocess.run([sys.executable, SCRIPT, "status", "goal-x"],
                             cwd=self.repo.path, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("다음 할 일: 만들기", out.stdout)
        with self.assertRaises(ValueError):
            json.loads(out.stdout)

    def test_outside_git_repo_stops_with_not_git_repo(self):
        plain = tempfile.mkdtemp(prefix="wt-plain-")
        self.addCleanup(shutil.rmtree, plain, True)
        code, out = self.repo.run("status", "goal-x", cwd=plain)
        self.assertEqual(code, 2, out)
        self.assertEqual(out["ok"], False)
        self.assertEqual(out["stops"][0]["code"], "not-git-repo")

    def test_default_output_shows_items_missing_and_discarded_copies(self):
        self.repo.list_file("copy notes\nmove .goal/{goal}\n")
        self.repo.write("notes/a.txt", "a\n")
        out = subprocess.run([sys.executable, SCRIPT, "create", "goal-x"],
                             cwd=self.repo.path, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("목록 항목: notes → copy", out.stdout)
        self.assertIn("만들 때 없던 항목: .goal/goal-x", out.stdout)

        self.repo.write("notes/a.txt", "changed\n", root=self.repo.wt_path("goal-x"))
        out = subprocess.run([sys.executable, SCRIPT, "finish", "goal-x"],
                             cwd=self.repo.path, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("바뀐 채로 버린 사본: notes/a.txt", out.stdout)

    def test_default_output_reports_failed_setup(self):
        self.repo.list_file("setup exit 3\n")
        out = subprocess.run([sys.executable, SCRIPT, "create", "goal-x"],
                             cwd=self.repo.path, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("준비 명령 실패(종료 코드 3): exit 3", out.stdout)

    def test_default_output_shows_git_message_of_refusal(self):
        self.repo.run("create", "goal-x")
        wt = self.repo.wt_path("goal-x")
        self.repo.write("a.txt", "a\nfrom worktree\n", root=wt)
        git(wt, "commit", "-q", "-am", "goal work")
        self.repo.write("a.txt", "a\nnot committed in main\n")
        out = subprocess.run([sys.executable, SCRIPT, "finish", "goal-x"],
                             cwd=self.repo.path, capture_output=True, text=True)
        self.assertEqual(out.returncode, 2, out.stderr)
        self.assertIn("멈춤 [main-dirty-overlap]", out.stdout)
        self.assertIn("  git: \ta.txt", out.stdout)  # git 메시지의 파일 줄(언어 설정과 관계없이 탭으로 들여 쓴다)

    def test_unexpected_git_failure_is_script_error(self):
        empty = os.path.join(self.repo.parent, "empty")
        os.makedirs(empty)
        git(empty, "init", "-q")  # 커밋이 하나도 없어 HEAD가 없다
        code, out = self.repo.run("create", "goal-x", cwd=empty)
        self.assertEqual(code, 1, out)
        self.assertEqual(out["ok"], False)
        self.assertIn("error", out)


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def receipt_file(self, goal="goal-x"):
        return os.path.join(self.repo.path, ".git", "workflow-worktree", goal + ".json")

    def set_state(self, state, goal="goal-x"):
        with open(self.receipt_file(goal)) as f:
            data = json.load(f)
        data["state"] = state
        with open(self.receipt_file(goal), "w") as f:
            json.dump(data, f)

    def test_status_without_receipt_says_create(self):
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "create")
        self.assertEqual(out["goal"], "goal-x")

    def test_status_inside_worktree_says_finish_and_lists_uncommitted(self):
        self.repo.run("create", "goal-x")
        wt = self.repo.wt_path("goal-x")
        self.repo.write("work.txt", "w\n", root=wt)
        code, out = self.repo.run("status", "goal-x", cwd=wt)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "finish")
        self.assertEqual(out["uncommitted"], ["work.txt"])

    def test_status_outside_working_worktree_says_reenter(self):
        self.repo.run("create", "goal-x")
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "reenter")
        self.assertEqual(out["worktree"], self.repo.wt_path("goal-x"))

    def test_status_while_finishing_says_continue_finish(self):
        self.repo.run("create", "goal-x")
        self.set_state("finishing")
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "continue-finish")

    def test_status_inside_worktree_while_finishing_lists_uncommitted(self):
        # worktree-dirty로 멈춘 뒤 worktree에 들어가 다시 부르면 ① 미커밋 검사에 쓸 목록이 나와야 한다
        self.repo.run("create", "goal-x")
        self.set_state("finishing")
        wt = self.repo.wt_path("goal-x")
        self.repo.write("work.txt", "w\n", root=wt)
        code, out = self.repo.run("status", "goal-x", cwd=wt)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "continue-finish")
        self.assertEqual(out["uncommitted"], ["work.txt"])

    def test_status_with_creating_receipt_stops_as_create_incomplete(self):
        self.repo.run("create", "goal-x")
        self.set_state("creating")
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["action"], "stop")
        self.assertEqual(out["stops"][0]["code"], "create-incomplete")
        self.assertEqual(out["stops"][0]["done"], ["worktree-add"])


class ListFileTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_unknown_mode_stops_with_list_invalid_and_line_number(self):
        self.repo.list_file("# 주석\n\nlink docs\nmirror notes\n")
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["action"], "stop")
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "list-invalid")
        self.assertEqual(stop["lines"], [4])
        self.assertIn("4", stop["message"])

    def test_same_pattern_twice_stops_create_and_changes_nothing(self):
        self.repo.list_file("link docs\ncopy docs/\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.write("new.txt", "new\n")
        head = self.repo.head()
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["ok"], False)
        self.assertEqual(out["stops"][0]["code"], "list-invalid")
        self.assertEqual(out["stops"][0]["lines"], [1, 2])
        self.assertFalse(os.path.exists(self.repo.wt_path("goal-x")))
        self.assertEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        self.assertEqual(git(self.repo.path, "stash", "list"), "")
        self.assertEqual(self.repo.head(), head)
        self.assertEqual(sorted(git(self.repo.path, "status", "--porcelain").splitlines()),
                         ["?? docs/", "?? new.txt"])
        self.assertFalse(os.path.exists(os.path.join(self.repo.path, ".git", "workflow-worktree")))

    def test_status_lists_only_unlisted_items_with_defaults(self):
        self.repo.write(".gitignore", "build/\n")
        git(self.repo.path, "add", ".gitignore")
        git(self.repo.path, "commit", "-q", "-m", "ignore")
        self.repo.list_file(
            "# 주석\n"
            "\n"
            "link docs\n"
            "copy alias\n"
            "sync tools\n"
            "sync-empty tools/out\n"
            "move .goal/{goal}\n"
            "link .goal/*\n"
            "skip **/__pycache__\n"
            "setup echo ready\n"
        )
        self.repo.write("docs/a.md", "a\n")
        self.repo.write(".goal/goal-x/goal.md", "g\n")
        self.repo.write(".goal/other/goal.md", "o\n")
        self.repo.write("lib/m.py", "m\n")
        self.repo.write("lib/__pycache__/m.pyc", "c\n")
        self.repo.write("stray.txt", "s\n")
        self.repo.write("build/out.bin", "b\n")
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "create")
        self.assertEqual(out["unlisted"], [
            {"path": "build", "git": "ignored", "mode": "skip", "from": "default", "line": None},
            {"path": "lib/m.py", "git": "untracked", "mode": "git", "from": "default", "line": None},
            {"path": "stray.txt", "git": "untracked", "mode": "git", "from": "default", "line": None},
        ])


class ModeTest(unittest.TestCase):
    """목록 방식마다 만들 때·끝낼 때 동작(Q19)."""

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.wt = self.repo.wt_path("goal-x")

    def read(self, rel, root=None):
        with open(os.path.join(root or self.repo.path, rel)) as f:
            return f.read()

    def commit_in_wt(self, rel, text):
        self.repo.write(rel, text, root=self.wt)
        git(self.wt, "add", rel)
        git(self.wt, "commit", "-q", "-m", "goal work")

    def test_link_points_to_main_by_absolute_path_and_is_removed_on_finish(self):
        self.repo.list_file("link docs\n")
        self.repo.write("docs/a.md", "a\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        link = os.path.join(self.wt, "docs")
        self.assertTrue(os.path.islink(link))
        self.assertEqual(os.readlink(link), os.path.join(self.repo.path, "docs"))
        self.assertEqual(out["items"], [{"path": "docs", "mode": "link"}])

        self.commit_in_wt("goal.txt", "goal work\n")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.lexists(self.wt))
        self.assertFalse(os.path.islink(os.path.join(self.repo.path, "docs")))
        self.assertEqual(self.read("docs/a.md"), "a\n")

    def test_copy_keeps_relative_links_and_reports_changed_files_on_finish(self):
        self.repo.write("shared/x.md", "x\n")
        git(self.repo.path, "add", "shared")
        git(self.repo.path, "commit", "-q", "-m", "shared")
        self.repo.list_file("copy alias\ncopy notes\n")
        os.symlink("shared", os.path.join(self.repo.path, "alias"))
        self.repo.write("notes/a.txt", "a\n")
        self.repo.write("notes/b.txt", "b\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        alias = os.path.join(self.wt, "alias")
        self.assertEqual(os.readlink(alias), "shared")
        self.assertEqual(os.path.realpath(alias), os.path.join(self.wt, "shared"))
        self.assertFalse(os.path.islink(os.path.join(self.wt, "notes")))
        self.assertEqual(self.read("notes/a.txt", root=self.wt), "a\n")

        self.repo.write("notes/a.txt", "a\nchanged in worktree\n", root=self.wt)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["copy_changed"], ["notes/a.txt"])
        self.assertFalse(os.path.lexists(self.wt))
        self.assertEqual(self.read("notes/a.txt"), "a\n")
        self.assertEqual(os.readlink(os.path.join(self.repo.path, "alias")), "shared")

    def test_new_path_under_copy_with_skip_rule_is_not_reported_as_copy_changed(self):
        self.repo.list_file("copy notes\nskip **/__pycache__\n")
        self.repo.write("notes/a.txt", "a\n")
        self.repo.run("create", "goal-x")
        self.repo.write("notes/a.txt", "a\nchanged in worktree\n", root=self.wt)
        self.repo.write("notes/__pycache__/a.pyc", "made after create\n", root=self.wt)
        self.commit_in_wt("goal.txt", "goal work\n")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["copy_changed"], ["notes/a.txt"])
        self.assertFalse(os.path.lexists(self.wt))

    def test_move_takes_item_out_of_main_and_brings_edits_back_on_finish(self):
        self.repo.list_file("move notes\n")
        self.repo.write("notes/a.txt", "a\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.lexists(os.path.join(self.repo.path, "notes")))
        self.assertEqual(self.read("notes/a.txt", root=self.wt), "a\n")

        self.repo.write("notes/a.txt", "a\nedited in worktree\n", root=self.wt)
        self.repo.write("notes/new.txt", "new\n", root=self.wt)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.lexists(self.wt))
        self.assertEqual(self.read("notes/a.txt"), "a\nedited in worktree\n")
        self.assertEqual(self.read("notes/new.txt"), "new\n")

    def test_move_back_onto_existing_name_stops_and_changes_nothing(self):
        self.repo.list_file("move notes\n")
        self.repo.write("notes/a.txt", "a\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt("goal.txt", "goal work\n")
        self.repo.write("notes/other.txt", "made in main meanwhile\n")
        head = self.repo.head()

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["ok"], False)
        self.assertEqual(out["stops"][0]["code"], "move-target-exists")
        self.assertEqual(out["stops"][0]["paths"], ["notes"])
        self.assertEqual(self.repo.head(), head)
        self.assertFalse(os.path.exists(os.path.join(self.repo.path, "goal.txt")))
        self.assertEqual(os.listdir(os.path.join(self.repo.path, "notes")), ["other.txt"])
        self.assertEqual(self.read("notes/a.txt", root=self.wt), "a\n")
        self.assertNotEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")

    def test_skip_is_not_taken_to_worktree(self):
        self.repo.list_file("skip cache\n")
        self.repo.write("cache/c.bin", "c\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.lexists(os.path.join(self.wt, "cache")))
        self.assertEqual(self.read("cache/c.bin"), "c\n")
        self.assertEqual(out["moved_by_git"], [])
        self.assertEqual(out["items"], [{"path": "cache", "mode": "skip"}])

    def test_skip_items_made_again_in_worktree_are_removed_with_it(self):
        # gitignore하지 않은 skip 항목: 만들 때 있던 것(cache), 없던 것(build), pattern으로만 아는 것(lib/__pycache__)
        self.repo.write("lib/m.py", "m\n")
        git(self.repo.path, "add", "lib")
        git(self.repo.path, "commit", "-q", "-m", "lib")
        self.repo.list_file("skip cache\nskip build\nskip **/__pycache__\n"
                            "setup mkdir -p build && echo built > build/out.bin\n")
        self.repo.write("cache/c.bin", "c\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read("build/out.bin", root=self.wt), "built\n")

        self.repo.write("cache/c.bin", "made again\n", root=self.wt)
        self.repo.write("lib/__pycache__/m.pyc", "pyc\n", root=self.wt)
        self.commit_in_wt("goal.txt", "goal work\n")
        code, out = self.repo.run("status", "goal-x", cwd=self.wt)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["uncommitted"], [])

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.lexists(self.wt))
        self.assertNotIn(self.wt, git(self.repo.path, "worktree", "list", "--porcelain"))
        self.assertEqual(self.read("cache/c.bin"), "c\n")
        self.assertFalse(os.path.lexists(os.path.join(self.repo.path, "build")))
        self.assertFalse(os.path.lexists(os.path.join(self.repo.path, "lib/__pycache__")))

    def test_setup_runs_inside_worktree_and_failure_does_not_stop_create(self):
        self.repo.list_file("setup pwd -P > where.txt\nsetup echo noise on stdout\nsetup exit 3\n")
        code, out = self.repo.run("create", "goal-x")  # stdout이 JSON 그대로여야 읽힌다
        self.assertEqual(code, 0, out)
        self.assertEqual(out["ok"], True)
        self.assertEqual(out["setup"], [
            {"cmd": "pwd -P > where.txt", "exit": 0},
            {"cmd": "echo noise on stdout", "exit": 0},
            {"cmd": "exit 3", "exit": 3},
        ])
        self.assertEqual(self.read("where.txt", root=self.wt), self.wt + "\n")
        self.assertFalse(os.path.exists(os.path.join(self.repo.path, "where.txt")))

    def test_unlisted_new_file_moves_by_git_and_listed_items_stay_out_of_stash(self):
        self.repo.list_file("link docs\nmove notes\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.write("notes/n.txt", "n\n")
        self.repo.write("new.txt", "new\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["moved_by_git"], ["new.txt"])
        self.assertEqual(git(self.wt, "status", "--porcelain", "--", "new.txt"), "?? new.txt\n")
        self.assertFalse(os.path.exists(os.path.join(self.repo.path, "new.txt")))
        self.assertEqual(git(self.repo.path, "stash", "list"), "")
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), "?? docs/\n")
        self.assertTrue(os.path.islink(os.path.join(self.wt, "docs")))
        self.assertFalse(os.path.islink(os.path.join(self.wt, "notes")))

    def ignore_cache(self, mode):
        """`.gitignore`가 무시하는 cache를 목록 파일에도 적는다(예: `skip skill-eval/.venv`)."""
        self.repo.write(".gitignore", "cache/\n")
        git(self.repo.path, "add", ".gitignore")
        git(self.repo.path, "commit", "-q", "-m", "ignore")
        self.repo.list_file("%s cache\n" % mode)
        self.repo.write("cache/x", "x\n")

    def test_ignored_skip_path_in_list_does_not_block_moving_tracked_edits(self):
        self.ignore_cache("skip")
        self.repo.write("a.txt", "a\nnot committed\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read("a.txt", root=self.wt), "a\nnot committed\n")
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), "")
        self.assertEqual(git(self.repo.path, "stash", "list"), "")
        self.assertEqual(self.read("cache/x"), "x\n")

    def test_ignored_link_path_in_list_does_not_block_moving_new_files(self):
        self.ignore_cache("link")
        self.repo.write("new.txt", "new\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["moved_by_git"], ["new.txt"])
        self.assertEqual(self.read("new.txt", root=self.wt), "new\n")
        self.assertFalse(os.path.exists(os.path.join(self.repo.path, "new.txt")))
        self.assertEqual(git(self.repo.path, "stash", "list"), "")
        self.assertEqual(os.readlink(os.path.join(self.wt, "cache")), os.path.join(self.repo.path, "cache"))

    def test_most_specific_line_wins_per_path(self):
        # 뒤에 적은 줄이 이기는 규칙이었다면 결과가 반대가 되도록 순서를 놓았다
        self.repo.list_file("move .goal/{goal}\nlink .goal/*\nskip **/__pycache__\ncopy notes\n")
        self.repo.write(".goal/goal-x/goal.md", "g\n")
        self.repo.write(".goal/other/goal.md", "o\n")
        self.repo.write("notes/a.txt", "a\n")
        self.repo.write("notes/__pycache__/a.pyc", "c\n")
        self.repo.write("notes/sub/__pycache__/b.pyc", "c\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["items"], [
            {"path": ".goal/goal-x", "mode": "move"},
            {"path": ".goal/other", "mode": "link"},
            {"path": "notes", "mode": "copy", "except": ["notes/__pycache__", "notes/sub/__pycache__"]},
            {"path": "notes/__pycache__", "mode": "skip"},
            {"path": "notes/sub/__pycache__", "mode": "skip"},
        ])
        self.assertFalse(os.path.lexists(os.path.join(self.repo.path, ".goal/goal-x")))
        self.assertEqual(self.read(".goal/goal-x/goal.md", root=self.wt), "g\n")
        self.assertEqual(os.readlink(os.path.join(self.wt, ".goal/other")),
                         os.path.join(self.repo.path, ".goal/other"))
        self.assertEqual(self.read("notes/a.txt", root=self.wt), "a\n")
        self.assertFalse(os.path.lexists(os.path.join(self.wt, "notes/__pycache__")))
        self.assertFalse(os.path.lexists(os.path.join(self.wt, "notes/sub/__pycache__")))
        self.assertEqual(git(self.repo.path, "stash", "list"), "")

    def test_move_item_missing_at_create_is_recorded_and_moved_back_if_made(self):
        self.repo.list_file("move .goal/{goal}\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["missing"], [".goal/goal-x"])
        receipt = os.path.join(self.repo.path, ".git", "workflow-worktree", "goal-x.json")
        with open(receipt) as f:
            items = json.load(f)["items"]
        self.assertEqual(items, [{"path": ".goal/goal-x", "mode": "move", "missing": True}])

        self.repo.write(".goal/goal-x/goal.md", "made in worktree\n", root=self.wt)
        self.commit_in_wt("goal.txt", "goal work\n")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read(".goal/goal-x/goal.md"), "made in worktree\n")
        self.assertFalse(os.path.lexists(self.wt))

    def test_worktree_status_does_not_count_list_items_as_uncommitted(self):
        self.repo.list_file("link docs\ncopy notes\nmove .goal/{goal}\nmove drafts\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.write("notes/n.txt", "n\n")
        self.repo.write(".goal/goal-x/goal.md", "g\n")
        self.repo.run("create", "goal-x")
        self.repo.write("drafts/d.txt", "made after create\n", root=self.wt)
        self.repo.write("work.txt", "w\n", root=self.wt)
        code, out = self.repo.run("status", "goal-x", cwd=self.wt)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "finish")
        self.assertEqual(out["uncommitted"], ["work.txt"])

    def test_list_items_never_enter_goal_branch_or_merge_commit(self):
        self.repo.list_file("link docs\ncopy notes\nmove drafts\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.write("notes/n.txt", "n\n")
        self.repo.write("drafts/d.txt", "d\n")
        base = self.repo.head()
        self.repo.run("create", "goal-x")
        self.repo.write("drafts/d.txt", "d\nedited\n", root=self.wt)
        self.commit_in_wt("goal.txt", "goal work\n")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        names = git(self.repo.path, "log", "-m", "--name-only", "--format=", base + "..HEAD").split()
        self.assertEqual(set(names), {"goal.txt"})
        self.assertEqual(sorted(git(self.repo.path, "status", "--porcelain").splitlines()),
                         ["?? docs/", "?? drafts/", "?? notes/"])


class SameRuleTwoReposTest(unittest.TestCase):
    """Q10: 같은 목록 줄 `move .goal/{goal}`이 추적하는 저장소에서는 git, 안 하는 저장소에서는 move가 된다."""

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.wt = self.repo.wt_path("goal-x")
        self.repo.list_file("move .goal/{goal}\n")

    def read(self, rel, root=None):
        with open(os.path.join(root or self.repo.path, rel)) as f:
            return f.read()

    def test_tracked_goal_folder_goes_through_branch_commit_and_merge(self):
        self.repo.write(".goal/goal-x/goal.md", "v1\n")
        git(self.repo.path, "add", ".goal")
        git(self.repo.path, "commit", "-q", "-m", "goal doc")
        self.repo.write(".goal/goal-x/goal.md", "v1\nv2 started in main\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["moved_by_git"], [".goal/goal-x/goal.md"])
        self.assertEqual(out["items"], [])

        git(self.wt, "commit", "-q", "-am", "goal doc v2")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read(".goal/goal-x/goal.md"), "v1\nv2 started in main\n")
        merged = git(self.repo.path, "log", "--name-only", "--format=", "HEAD^2", "-1")
        self.assertEqual(merged.split(), [".goal/goal-x/goal.md"])
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), "")

    def test_untracked_goal_folder_is_moved_and_never_committed(self):
        self.repo.write(".goal/goal-x/goal.md", "v1\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["moved_by_git"], [])
        self.assertEqual(out["items"], [{"path": ".goal/goal-x", "mode": "move"}])

        self.repo.write(".goal/goal-x/goal.md", "v1\nv2 in worktree\n", root=self.wt)
        self.repo.write("goal.txt", "goal work\n", root=self.wt)
        git(self.wt, "add", "goal.txt")
        git(self.wt, "commit", "-q", "-m", "goal work")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read(".goal/goal-x/goal.md"), "v1\nv2 in worktree\n")
        self.assertNotIn(".goal", git(self.repo.path, "log", "--all", "--name-only", "--format="))
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), "?? .goal/\n")


SHA_A = "87428fc522803d31065e7bce3cf03fe475096631e5e07bbd7a0fde60c4cf25c7"  # sha256("a\n")
SHA_X = "73cb3858a687a8494ca3323053016282f3dad39d42cf62ca4e79dda2aac7d9ac"  # sha256("x\n")


class SyncTest(unittest.TestCase):
    """sync·sync-empty: 만들 때 시작 지문을 적고, 끝낼 때 파일마다 3-way로 돌려준다(Q19·Q20·Q23)."""

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.wt = self.repo.wt_path("goal-x")

    def read(self, rel, root=None):
        with open(os.path.join(root or self.repo.path, rel)) as f:
            return f.read()

    def receipt(self):
        with open(os.path.join(self.repo.path, ".git", "workflow-worktree", "goal-x.json")) as f:
            return json.load(f)

    def test_receipt_records_start_fingerprints_for_sync_and_copy(self):
        self.repo.write("shared/x.md", "x\n")
        git(self.repo.path, "add", "shared")
        git(self.repo.path, "commit", "-q", "-m", "shared")
        self.repo.list_file("sync tools\ncopy alias\n")
        os.symlink("shared", os.path.join(self.repo.path, "alias"))
        self.repo.write("tools/a.txt", "a\n")
        self.repo.write("tools/sub/x.txt", "x\n")
        os.symlink("a.txt", os.path.join(self.repo.path, "tools/ln"))
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["items"], [{"path": "alias", "mode": "copy"}, {"path": "tools", "mode": "sync"}])
        self.assertEqual(self.receipt()["items"], [
            {"path": "alias", "mode": "copy", "base": {"alias": "link:shared"}},
            {"path": "tools", "mode": "sync", "base": {
                "tools/a.txt": SHA_A, "tools/ln": "link:a.txt", "tools/sub/x.txt": SHA_X}},
        ])
        # sync는 복사다: 원래 폴더에도 남는다
        self.assertEqual(self.read("tools/a.txt", root=self.wt), "a\n")
        self.assertEqual(os.readlink(os.path.join(self.wt, "tools/ln")), "a.txt")
        self.assertEqual(self.read("tools/a.txt"), "a\n")

    def commit_in_wt(self):
        self.repo.write("goal.txt", "goal work\n", root=self.wt)
        git(self.wt, "add", "goal.txt")
        git(self.wt, "commit", "-q", "-m", "goal work")

    def test_sync_brings_worktree_edits_back_and_keeps_main_edits(self):
        self.repo.list_file("sync tools\n")
        self.repo.write("tools/edit.txt", "e\n")
        self.repo.write("tools/del.txt", "d\n")
        self.repo.write("tools/main-edit.txt", "m\n")
        self.repo.write("tools/same.txt", "s\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)

        self.repo.write("tools/edit.txt", "e\nedited in worktree\n", root=self.wt)
        self.repo.write("tools/new/n.txt", "new in worktree\n", root=self.wt)
        os.remove(os.path.join(self.wt, "tools/del.txt"))
        self.repo.write("tools/main-edit.txt", "m\nedited in main\n")
        self.commit_in_wt()

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["synced"], ["tools/del.txt", "tools/edit.txt", "tools/new/n.txt"])
        self.assertEqual(self.read("tools/edit.txt"), "e\nedited in worktree\n")
        self.assertEqual(self.read("tools/new/n.txt"), "new in worktree\n")
        self.assertFalse(os.path.lexists(os.path.join(self.repo.path, "tools/del.txt")))
        self.assertEqual(self.read("tools/main-edit.txt"), "m\nedited in main\n")
        self.assertEqual(self.read("tools/same.txt"), "s\n")
        self.assertFalse(os.path.lexists(self.wt))
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), "?? tools/\n")

    def snapshot(self, *roots):
        """브랜치·worktree 목록·HEAD와 폴더마다 파일 내용."""
        files = {}
        for root in roots:
            for dirpath, _, names in os.walk(root):
                if ".git" in dirpath.split(os.sep):
                    continue
                for name in names:
                    full = os.path.join(dirpath, name)
                    with open(full, "rb") as f:
                        files[full] = f.read()
        return (self.repo.head(), git(self.repo.path, "branch", "--list"),
                git(self.repo.path, "worktree", "list", "--porcelain"), files)

    def test_sync_conflict_stops_before_merge_and_changes_nothing(self):
        self.repo.list_file("sync tools\n")
        self.repo.write("tools/a.txt", "a\n")
        self.repo.write("tools/b.txt", "b\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.repo.write("tools/a.txt", "a\nedited in worktree\n", root=self.wt)
        self.repo.write("tools/b.txt", "b\nonly worktree\n", root=self.wt)
        self.repo.write("tools/a.txt", "a\nedited in main\n")
        before = self.snapshot(self.repo.path, self.wt)

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["ok"], False)
        self.assertEqual(out["stops"][0]["code"], "sync-conflict")
        self.assertEqual(out["stops"][0]["paths"], ["tools/a.txt"])
        self.assertEqual(self.snapshot(self.repo.path, self.wt), before)
        self.assertFalse(os.path.exists(os.path.join(self.repo.path, "goal.txt")))

    def test_sync_empty_starts_empty_and_brings_back_only_new_results(self):
        self.repo.list_file("sync-empty results\n")
        self.repo.write("results/m1/summary.csv", "m1\n")
        self.repo.write("results/m2/report.md", "m2\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(os.listdir(os.path.join(self.wt, "results")), [])
        self.assertEqual(self.receipt()["items"], [{"path": "results", "mode": "sync-empty", "base": {}}])

        self.repo.write("results/t17/summary.csv", "t17\n", root=self.wt)
        self.repo.write("results/t17/runs/r.json", "{}\n", root=self.wt)
        self.commit_in_wt()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["synced"], ["results/t17/runs/r.json", "results/t17/summary.csv"])
        self.assertEqual(self.read("results/t17/summary.csv"), "t17\n")
        self.assertEqual(sorted(os.listdir(os.path.join(self.repo.path, "results"))), ["m1", "m2", "t17"])
        self.assertEqual(self.read("results/m1/summary.csv"), "m1\n")
        self.assertEqual(self.read("results/m2/report.md"), "m2\n")
        self.assertFalse(os.path.lexists(self.wt))

    def test_sync_empty_same_name_on_both_sides_is_sync_conflict(self):
        self.repo.list_file("sync-empty results\n")
        self.repo.write("results/m1/summary.csv", "m1\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.repo.write("results/r1/summary.csv", "from worktree\n", root=self.wt)
        self.repo.write("results/r1/summary.csv", "from main\n")
        before = self.snapshot(self.repo.path, self.wt)

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["stops"][0]["code"], "sync-conflict")
        self.assertEqual(out["stops"][0]["paths"], ["results/r1/summary.csv"])
        self.assertEqual(self.snapshot(self.repo.path, self.wt), before)

    def test_sync_item_missing_at_create_starts_from_empty_base(self):
        self.repo.list_file("sync tools\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["missing"], ["tools"])
        self.assertEqual(self.receipt()["items"], [{"path": "tools", "mode": "sync", "missing": True, "base": {}}])

        self.repo.write("tools/w.txt", "made in worktree\n", root=self.wt)
        self.repo.write("tools/m.txt", "made in main\n")
        self.commit_in_wt()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["synced"], ["tools/w.txt"])
        self.assertEqual(self.read("tools/w.txt"), "made in worktree\n")
        self.assertEqual(self.read("tools/m.txt"), "made in main\n")
        self.assertFalse(os.path.lexists(self.wt))

    def test_nested_skip_and_sync_empty_under_sync(self):
        # 줄 순서를 일부러 섞었다. 경로마다 가장 구체적인 줄이 이긴다
        self.repo.list_file(
            "skip **/__pycache__\n"
            "sync-empty skill-eval/results\n"
            "sync skill-eval\n"
            "skip skill-eval/.venv\n"
        )
        self.repo.write("skill-eval/.gitignore", ".venv/\n__pycache__/\n*.pyc\n")
        self.repo.write("skill-eval/config.yaml", "c\n")
        self.repo.write("skill-eval/skilleval/runner.py", "r\n")
        self.repo.write("skill-eval/skilleval/__pycache__/runner.pyc", "pyc in main\n")
        self.repo.write("skill-eval/.venv/bin/python", "venv in main\n")
        self.repo.write("skill-eval/results/m1/summary.csv", "m1\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["items"], [
            {"path": "skill-eval", "mode": "sync",
             "except": ["skill-eval/.venv", "skill-eval/results", "skill-eval/skilleval/__pycache__"]},
            {"path": "skill-eval/.venv", "mode": "skip"},
            {"path": "skill-eval/results", "mode": "sync-empty"},
            {"path": "skill-eval/skilleval/__pycache__", "mode": "skip"},
        ])
        self.assertEqual(self.read("skill-eval/skilleval/runner.py", root=self.wt), "r\n")
        self.assertFalse(os.path.lexists(os.path.join(self.wt, "skill-eval/.venv")))
        self.assertFalse(os.path.lexists(os.path.join(self.wt, "skill-eval/skilleval/__pycache__")))
        self.assertEqual(os.listdir(os.path.join(self.wt, "skill-eval/results")), [])

        # 양쪽에서 시험을 돌린 것처럼 캐시가 생기고 바뀐다. worktree는 결과 하나와 설정 하나를 고친다
        self.repo.write("skill-eval/skilleval/__pycache__/runner.pyc", "pyc changed in main\n")
        self.repo.write("skill-eval/tests/__pycache__/t.pyc", "new pyc in main\n")
        self.repo.write("skill-eval/tests/__pycache__/t.pyc", "new pyc in worktree\n", root=self.wt)
        self.repo.write("skill-eval/skilleval/__pycache__/runner.pyc", "pyc in worktree\n", root=self.wt)
        self.repo.write("skill-eval/.venv/bin/python", "venv in worktree\n", root=self.wt)
        self.repo.write("skill-eval/config.yaml", "c\nedited in worktree\n", root=self.wt)
        self.repo.write("skill-eval/results/t17/summary.csv", "t17\n", root=self.wt)
        self.commit_in_wt()

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["synced"], ["skill-eval/config.yaml", "skill-eval/results/t17/summary.csv"])
        self.assertEqual(self.read("skill-eval/config.yaml"), "c\nedited in worktree\n")
        self.assertEqual(self.read("skill-eval/results/t17/summary.csv"), "t17\n")
        self.assertEqual(self.read("skill-eval/results/m1/summary.csv"), "m1\n")
        self.assertEqual(self.read("skill-eval/skilleval/__pycache__/runner.pyc"), "pyc changed in main\n")
        self.assertEqual(self.read("skill-eval/tests/__pycache__/t.pyc"), "new pyc in main\n")
        self.assertEqual(self.read("skill-eval/.venv/bin/python"), "venv in main\n")
        self.assertFalse(os.path.lexists(self.wt))


class CreateStopTest(StopTestCase):
    """Q16: 만들기는 바꾸기 전에 모두 검사하고, 걸리면 종료 코드 2로 멈추며 아무것도 바꾸지 않는다."""

    def setUp(self):
        super().setUp()
        self.repo.write("new.txt", "uncommitted work\n")  # 멈추면 stash되지 않고 그대로여야 한다

    def test_create_outside_git_repo_stops_with_not_git_repo(self):
        plain = os.path.join(self.repo.parent, "plain")
        self.repo.write("note.txt", "n\n", root=plain)
        self.assert_stops("not-git-repo", "create", "goal-x", cwd=plain)

    def test_unusable_goal_name_stops_with_goal_invalid(self):
        for goal in ["", "..", "a/b", "a b"]:
            with self.subTest(goal=goal):
                self.assert_stops("goal-invalid", "create", goal)
        self.assert_stops("goal-invalid", "status", "..")

    def test_existing_goal_branch_stops_with_branch_exists(self):
        git(self.repo.path, "branch", "goal/goal-x")
        self.assert_stops("branch-exists", "create", "goal-x")

    def test_existing_sibling_folder_stops_with_folder_exists(self):
        self.repo.write("keep.txt", "someone else's folder\n", root=self.wt)
        stop = self.assert_stops("folder-exists", "create", "goal-x")
        self.assertEqual(stop["paths"], [self.wt])

    def start_conflicting(self, *command):
        """main과 side가 a.txt를 다르게 고친 뒤 command(merge·rebase)를 충돌로 멈춰 둔다."""
        git(self.repo.path, "switch", "-q", "-c", "side")
        self.repo.write("a.txt", "from side\n")
        git(self.repo.path, "commit", "-q", "-am", "side")
        git(self.repo.path, "switch", "-q", "main")
        self.repo.write("a.txt", "from main\n")
        git(self.repo.path, "commit", "-q", "-am", "main")
        self.assertNotEqual(git_may_fail(self.repo.path, *command), 0)

    def test_merge_in_progress_stops_with_git_busy(self):
        os.remove(os.path.join(self.repo.path, "new.txt"))  # merge 중에는 일반 작업이 없어도 멈춰야 한다
        self.start_conflicting("merge", "side")
        self.assert_stops("git-busy", "create", "goal-x")

    def test_rebase_in_progress_stops_with_git_busy(self):
        os.remove(os.path.join(self.repo.path, "new.txt"))  # rebase는 미커밋 작업이 있으면 시작하지 않는다
        self.start_conflicting("rebase", "side")
        self.assert_stops("git-busy", "create", "goal-x")

    def test_inside_worktree_this_skill_did_not_make_stops_with_foreign_worktree(self):
        other = os.path.join(self.repo.parent, "other")
        git(self.repo.path, "worktree", "add", "-q", "-b", "other", other, "HEAD")
        self.repo.write("work.txt", "work in other worktree\n", root=other)
        stop = self.assert_stops("foreign-worktree", "create", "goal-x", cwd=other)
        self.assertEqual(stop["paths"], [other])
        self.assert_stops("foreign-worktree", "status", "goal-x", cwd=other)


@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root는 읽기 권한을 무시한다")
class CreateFailsMidwayTest(StopTestCase):
    """D9: 만들기의 한 단계가 예상 밖으로 실패하면 영수증이 creating으로 남고 다음 부르기가 create-incomplete로 멈춘다.
    실패는 진짜 조건으로 만든다: copy 항목의 원본을 읽을 수 없게 해 items 단계가 실패한다."""

    def test_failed_items_step_leaves_creating_receipt_and_status_shows_done_steps(self):
        self.repo.list_file("copy secret.txt\n")
        secret = os.path.join(self.repo.path, "secret.txt")
        self.repo.write("secret.txt", "s\n")
        os.chmod(secret, 0)
        self.addCleanup(os.chmod, secret, 0o644)
        self.repo.write("new.txt", "uncommitted work\n")
        code, out = self.repo.run("create", "goal-x")
        self.assertEqual(code, 1, out)  # 예상 못 한 실패는 script 오류
        os.chmod(secret, 0o644)  # 원인을 고쳐도 반쯤 만든 상태는 그대로 보고되어야 한다
        self.assertEqual(self.receipt()["state"], "creating")
        done = ["stash", "worktree-add", "stash-pop"]
        self.assertEqual(self.receipt()["done"], done)

        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["action"], "stop")
        self.assertEqual(out["stops"][0]["code"], "create-incomplete")
        self.assertEqual(out["stops"][0]["done"], done)
        for command in ("create", "finish"):
            with self.subTest(command=command):
                stop = self.assert_stops("create-incomplete", command, "goal-x")
                self.assertEqual(stop["done"], done)


class FinishStopTest(StopTestCase):
    """Q17: 끝내기는 바꾸기 전에 모두 검사한다. 멈추면 영수증 상태가 finishing으로 바뀌는 것 말고는 그대로다."""

    def test_finish_without_receipt_stops_with_receipt_missing(self):
        self.repo.write("new.txt", "uncommitted work\n")
        stop = self.assert_stops("receipt-missing", "finish", "goal-x")
        self.assertEqual(stop["paths"], [self.repo.receipt_file()])

    def test_finish_inside_worktree_stops_with_run_from_main(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        stop = self.assert_stops("run-from-main", "finish", "goal-x", cwd=self.wt)  # 영수증도 그대로
        self.assertEqual(stop["paths"], [self.repo.path])

    def test_receipt_without_worktree_folder_stops_with_worktree_missing(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        shutil.rmtree(self.wt)
        stop = self.assert_stops("worktree-missing", "finish", "goal-x")  # 영수증도 그대로
        self.assertEqual(stop["paths"], [self.wt])
        self.assert_stops("worktree-missing", "status", "goal-x")

    def test_unreadable_receipt_stops_with_receipt_invalid(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        with open(self.repo.receipt_file()) as f:
            good = json.load(f)
        broken = ['{"version": 1, "goal": ', json.dumps(dict(good, version=99)),
                  json.dumps(dict(good, state="paused")), json.dumps({k: v for k, v in good.items() if k != "done"})]
        for text in broken:
            with self.subTest(receipt=text[:40]):
                with open(self.repo.receipt_file(), "w") as f:
                    f.write(text)
                stop = self.assert_stops("receipt-invalid", "finish", "goal-x")
                self.assertEqual(stop["paths"], [self.repo.receipt_file()])
                self.assert_stops("receipt-invalid", "status", "goal-x")

    def test_uncommitted_work_in_worktree_stops_with_worktree_dirty(self):
        self.repo.list_file("link docs\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.repo.write("a.txt", "a\nnot committed\n", root=self.wt)
        self.repo.write("work.txt", "not committed\n", root=self.wt)
        stop = self.assert_stops("worktree-dirty", "finish", "goal-x", finishing=True)
        self.assertEqual(stop["paths"], ["a.txt", "work.txt"])  # 목록 항목 docs는 미커밋 작업이 아니다

    def test_main_on_other_branch_stops_with_base_moved(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        git(self.repo.path, "switch", "-q", "-c", "elsewhere")
        stop = self.assert_stops("base-moved", "finish", "goal-x", finishing=True)
        self.assertIn("main", stop["message"])
        self.assertIn("elsewhere", stop["message"])

    def test_conflicting_merge_preview_stops_with_merge_conflict(self):
        self.make_conflict()
        stop = self.assert_stops("merge-conflict", "finish", "goal-x", finishing=True)
        self.assertEqual(stop["paths"], ["a.txt"])


class GitRefusesTest(StopTestCase):
    """Q17: 미리 검사로 못 잡고 git이 스스로 거부하는 경우. --force 없이 멈추고 git의 메시지를 담는다."""

    def test_main_uncommitted_change_overlapping_merge_stops_with_main_dirty_overlap(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt("a.txt", "a\nfrom worktree\n")
        self.repo.write("a.txt", "a\nanother session, not committed\n")
        head = self.repo.head()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "main-dirty-overlap")
        self.assertEqual(stop["paths"], ["a.txt"])
        self.assertIn("a.txt", stop["git"])
        self.assertEqual(self.read("a.txt"), "a\nanother session, not committed\n")
        self.assertEqual(self.repo.head(), head)
        self.assertNotIn("merge", self.receipt()["done"])
        self.assertEqual(git(self.repo.path, "status", "--porcelain"), " M a.txt\n")

    def test_sync_path_also_committed_on_goal_branch_stops_without_half_change(self):
        self.repo.list_file("sync tools\n")
        self.repo.write("tools/t.txt", "t\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt("tools/t.txt", "t\nedited and committed in worktree\n")  # 원래 폴더에는 untracked 사본이 있다
        head = self.repo.head()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "main-dirty-overlap")
        self.assertEqual(stop["paths"], ["tools/t.txt"])
        self.assertIn("tools/t.txt", stop["git"])
        self.assertEqual(self.read("tools/t.txt"), "t\n")
        self.assertEqual(self.read("tools/t.txt", root=self.wt), "t\nedited and committed in worktree\n")
        self.assertEqual(self.repo.head(), head)
        self.assertEqual(self.receipt()["done"], ["worktree-add", "items"])
        self.assertNotIn("synced", self.receipt())

    def test_unexpected_leftover_stops_with_remove_refused_and_keeps_worktree(self):
        self.repo.list_file("link docs\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.leave_unexpected_file()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "remove-refused")
        self.assertEqual(stop["paths"], ["docs/own.md"])
        self.assertIn("git", stop)
        self.assertEqual(self.read("docs/own.md", root=self.wt), "made in worktree instead of the link\n")
        self.assertIn("worktree " + self.wt, git(self.repo.path, "worktree", "list", "--porcelain"))
        self.assertNotEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        self.assertEqual(self.receipt()["done"][-2:], ["merge", "restore-items"])
        self.assertEqual(self.read("docs/a.md"), "a\n")


class ResumeTest(StopTestCase):
    """Q25·E7: 멈춘 원인을 고치고 다시 부르면 처음부터 다시 검사하고 끝난 단계는 건너뛰어 끝까지 간다."""

    def log(self):
        return git(self.repo.path, "log", "--format=%H %P", "main")

    def test_finish_again_after_remove_refused_does_not_merge_twice(self):
        self.repo.list_file("link docs\n")
        self.repo.write("docs/a.md", "a\n")
        base = self.repo.head()
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.leave_unexpected_file()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        merged = self.log()

        shutil.rmtree(os.path.join(self.wt, "docs"))  # 남은 파일을 치운다
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(out["action"], "continue-finish")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.log(), merged)  # merge를 다시 하지 않았다
        self.assertEqual(git(self.repo.path, "rev-list", "--merges", "--count", base + "..HEAD").strip(), "1")
        self.assertEqual(out["merge_commit"], self.repo.head())
        self.assertFalse(os.path.lexists(self.wt))
        self.assertEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        self.assertFalse(os.path.exists(self.repo.receipt_file()))
        self.assertEqual(self.read("docs/a.md"), "a\n")

    def test_finish_again_after_resolving_merge_conflict_in_worktree_goes_to_the_end(self):
        self.make_conflict()
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["stops"][0]["code"], "merge-conflict")
        main_before = self.repo.head()

        # Q25: worktree에서 원래 브랜치를 먼저 merge해 충돌을 풀고 커밋한다
        self.assertNotEqual(git_may_fail(self.wt, "merge", "main"), 0)
        self.repo.write("a.txt", "a\nfrom main\nfrom worktree\n", root=self.wt)
        git(self.wt, "add", "a.txt")
        git(self.wt, "commit", "-q", "--no-edit")
        branch_tip = self.repo.head(self.wt)
        self.assertEqual(self.log(), git(self.repo.path, "log", "--format=%H %P", main_before))

        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        parents = git(self.repo.path, "rev-list", "--parents", "-n", "1", "HEAD").split()
        self.assertEqual(parents, [out["merge_commit"], main_before, branch_tip])
        self.assertEqual(self.read("a.txt"), "a\nfrom main\nfrom worktree\n")
        self.assertFalse(os.path.lexists(self.wt))
        self.assertEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        self.assertFalse(os.path.exists(self.repo.receipt_file()))

    def test_finish_again_after_deleting_whole_worktree_once_items_are_restored_goes_to_the_end(self):
        self.repo.list_file("link docs\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.leave_unexpected_file()
        code, out = self.repo.run("finish", "goal-x")  # merge·restore-items 뒤 remove-refused
        self.assertEqual(out["stops"][0]["code"], "remove-refused")
        merged = self.log()

        shutil.rmtree(self.wt)  # 등록은 남고 폴더만 없다. 돌려줄 것은 이미 돌려줬다
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual((code, out["action"]), (0, "continue-finish"), out)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.log(), merged)
        self.assertNotIn(self.wt, git(self.repo.path, "worktree", "list", "--porcelain"))
        self.assertEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        self.assertFalse(os.path.exists(self.repo.receipt_file()))
        self.assertEqual(self.read("docs/a.md"), "a\n")

    def test_move_item_made_again_after_restore_is_remove_refused_not_move_target_exists(self):
        self.repo.list_file("link docs\nmove notes\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.write("notes/n.txt", "n\n")
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.leave_unexpected_file()
        code, out = self.repo.run("finish", "goal-x")  # move는 되돌린 뒤 멈춘다
        self.assertEqual(out["stops"][0]["code"], "remove-refused")
        self.assertEqual(self.read("notes/n.txt"), "n\n")

        shutil.rmtree(os.path.join(self.wt, "docs"))
        self.repo.write("notes/late.txt", "made after the stop\n", root=self.wt)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual([s["code"] for s in out["stops"]], ["remove-refused"])
        self.assertEqual(out["stops"][0]["paths"], ["notes/late.txt"])

    def test_sync_edits_made_after_restore_are_not_cleared_on_finish_again(self):
        self.repo.list_file("link docs\nsync tools\n")
        self.repo.write("docs/a.md", "a\n")
        self.repo.write("tools/edit.txt", "e\n")
        self.repo.write("tools/keep.txt", "k\n")
        self.repo.run("create", "goal-x")
        self.repo.write("tools/edit.txt", "e\nreturned from worktree\n", root=self.wt)
        self.commit_in_wt()
        self.leave_unexpected_file()
        code, out = self.repo.run("finish", "goal-x")  # restore-items까지 끝나고 멈춘다
        self.assertEqual(code, 2, out)
        self.assertEqual(out["stops"][0]["code"], "remove-refused")
        self.assertEqual(self.read("tools/edit.txt"), "e\nreturned from worktree\n")

        # 다시 부르기 전에 worktree의 sync 파일을 고치고 새로 만든다. 돌려준 것과 같은 사본은 지워도 된다
        shutil.rmtree(os.path.join(self.wt, "docs"))
        self.repo.write("tools/edit.txt", "e\nedited again after the stop\n", root=self.wt)
        self.repo.write("tools/new.txt", "made after the stop\n", root=self.wt)
        self.repo.write("tools/keep.txt", "k\n", root=self.wt)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "remove-refused")
        self.assertEqual(stop["paths"], ["tools/edit.txt", "tools/new.txt"])
        self.assertEqual(self.read("tools/edit.txt", root=self.wt), "e\nedited again after the stop\n")
        self.assertEqual(self.read("tools/new.txt", root=self.wt), "made after the stop\n")
        self.assertFalse(os.path.lexists(os.path.join(self.wt, "tools/keep.txt")))
        self.assertEqual(self.read("tools/edit.txt"), "e\nreturned from worktree\n")


@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root는 쓰기 권한을 무시한다")
class PartialRemoveTest(StopTestCase):
    """Q17·Q25: worktree를 지우다 도중에 실패하는 경우(NFS의 열린 파일, 권한).
    git은 폴더를 다 못 지워도 등록을 지운다. 그래서 남은 폴더는 저장소가 아니다.
    실패는 진짜 조건으로 만든다: 추적 파일이 든 폴더의 쓰기 권한을 뺀다."""

    def setUp(self):
        super().setUp()
        self.repo.write("src/deep/f1.txt", "1\n")
        self.repo.write("src/deep/f2.txt", "2\n")
        git(self.repo.path, "add", "src")
        git(self.repo.path, "commit", "-q", "-m", "src")

    def protect(self, rel):
        full = os.path.join(self.wt, rel)
        os.chmod(full, 0o555)
        self.addCleanup(lambda: os.path.isdir(full) and os.chmod(full, 0o755))
        return full

    def registered(self):
        return ("worktree " + self.wt) in git(self.repo.path, "worktree", "list", "--porcelain").splitlines()

    def test_failure_while_deleting_stops_with_remove_incomplete_and_lists_leftovers(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.protect("src/deep")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "remove-incomplete")
        self.assertFalse(self.registered())  # git이 등록은 지웠다
        self.assertIn("src/deep/f1.txt", stop["paths"])
        self.assertIn("src/deep/f2.txt", stop["paths"])
        for rel in stop["paths"]:
            self.assertTrue(os.path.lexists(os.path.join(self.wt, rel)), rel)
        self.assertTrue(stop["git"])
        self.assertEqual(self.receipt()["state"], "finishing")
        self.assertIn("merge", self.receipt()["done"])

    def test_finish_again_with_leftover_folder_stops_again_instead_of_script_error(self):
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        deep = self.protect("src/deep")
        self.repo.run("finish", "goal-x")
        os.chmod(deep, 0o755)  # 원인은 고쳤지만 남은 폴더는 아직 그대로다

        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["action"], "continue-finish")
        stop = self.assert_stops("remove-incomplete", "finish", "goal-x")
        self.assertIn("src/deep/f1.txt", stop["paths"])

    def test_finish_again_after_deleting_leftover_folder_goes_to_the_end(self):
        base = self.repo.head()
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        deep = self.protect("src/deep")
        self.repo.run("finish", "goal-x")
        merged = git(self.repo.path, "log", "--format=%H %P", "main")
        os.chmod(deep, 0o755)
        shutil.rmtree(self.wt)  # 사용자가 확인하고 남은 폴더를 지운다

        code, out = self.repo.run("status", "goal-x")
        self.assertEqual((code, out["action"]), (0, "continue-finish"), out)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(git(self.repo.path, "log", "--format=%H %P", "main"), merged)  # merge를 다시 하지 않았다
        self.assertEqual(git(self.repo.path, "rev-list", "--merges", "--count", base + "..HEAD").strip(), "1")
        self.assertEqual(git(self.repo.path, "branch", "--list", "goal/goal-x"), "")
        self.assertFalse(os.path.exists(self.repo.receipt_file()))

    def test_failure_while_clearing_skip_item_stops_and_finish_again_goes_to_the_end(self):
        self.repo.list_file("skip build\n")
        base = self.repo.head()
        self.repo.run("create", "goal-x")
        self.commit_in_wt()
        self.repo.write("build/sub/out.bin", "made by a build in worktree\n", root=self.wt)
        sub = self.protect("build/sub")
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 2, out)
        stop = out["stops"][0]
        self.assertEqual(stop["code"], "remove-incomplete")
        self.assertEqual(stop["paths"], ["build/sub/out.bin"])
        self.assertTrue(self.registered())  # git까지 가지 않았다. worktree는 그대로 저장소다

        os.chmod(sub, 0o755)
        code, out = self.repo.run("finish", "goal-x")
        self.assertEqual(code, 0, out)
        self.assertEqual(git(self.repo.path, "rev-list", "--merges", "--count", base + "..HEAD").strip(), "1")
        self.assertFalse(os.path.lexists(self.wt))
        self.assertFalse(os.path.exists(self.repo.receipt_file()))


class ThreeWayTest(unittest.TestCase):
    """Q20 표: (시작, 원래, worktree) 지문 → 판정. None은 그 쪽에 파일이 없다는 뜻이다."""

    TABLE = [
        # 있던 파일
        ("안 바뀜", "A", "A", "A", "same"),
        ("worktree만 바뀜", "A", "A", "B", "take-worktree"),
        ("원래만 바뀜", "A", "B", "A", "keep-main"),
        ("양쪽이 같게 바뀜", "A", "B", "B", "same"),
        ("양쪽이 다르게 바뀜", "A", "B", "C", "conflict"),
        # 새 파일
        ("worktree에만 새 파일", None, None, "B", "take-worktree"),
        ("원래에만 새 파일", None, "B", None, "keep-main"),
        ("양쪽에 같은 새 파일", None, "B", "B", "same"),
        ("양쪽에 다른 새 파일", None, "B", "C", "conflict"),
        # 지운 파일
        ("worktree만 지움", "A", "A", None, "take-worktree"),
        ("원래만 지움", "A", None, "A", "keep-main"),
        ("worktree는 지웠는데 원래가 바뀜", "A", "B", None, "conflict"),
        ("원래는 지웠는데 worktree가 바뀜", "A", None, "B", "conflict"),
        ("양쪽 다 지움", "A", None, None, "same"),
    ]

    def test_three_way_table(self):
        for name, base, main, wt, expected in self.TABLE:
            with self.subTest(name):
                self.assertEqual(worktree.three_way(base, main, wt), expected)


if __name__ == "__main__":
    unittest.main()
