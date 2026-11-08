"""workflow-worktree script 시험.

바깥 seam(status·create·finish 명령과 목록 파일)을 임시 폴더의 진짜 git 저장소에서 시험한다.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "worktree.py")


def git(cwd, *args):
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError("git %s failed: %s" % (" ".join(args), out.stderr))
    return out.stdout


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
        return out.returncode, data


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

    def test_status_with_creating_receipt_stops_as_create_incomplete(self):
        self.repo.run("create", "goal-x")
        self.set_state("creating")
        code, out = self.repo.run("status", "goal-x")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["action"], "stop")
        self.assertEqual(out["stops"][0]["code"], "create-incomplete")
        self.assertEqual(out["stops"][0]["done"], ["worktree-add"])


if __name__ == "__main__":
    unittest.main()
