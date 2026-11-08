"""workflow-worktree script 시험.

바깥 seam(status·create·finish 명령과 목록 파일)을 임시 폴더의 진짜 git 저장소에서 시험한다.
내부 seam은 3-way 판정(`three_way`) 하나다.
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

sys.path.insert(0, os.path.dirname(HERE))
import worktree  # noqa: E402  내부 seam three_way만 쓴다


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
