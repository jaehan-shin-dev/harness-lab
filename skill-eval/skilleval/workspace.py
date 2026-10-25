"""임시 작업 폴더, 실행별 pi 설정 폴더, 실행 전 가방 검사 (goal.md R5 ①②③, Q11)."""
import fnmatch
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import CACHE, PILAB, RESULTS
from .pi_process import clean_env

# 후보가 보는 이름·경로·러너가 넣는 글에 나오면 안 되는 단어 (goal.md Deliverable 단어 비노출)
FORBIDDEN = ["eval", "benchmark", "judge", "rubric", "grader", "answer", "평가", "채점", "답변표",
             "swe-bench", "clareval", "skill-eval"]
# 작업 폴더·설정 폴더 파일 내용에 0건이어야 하는 글자 (goal.md R5 ①)
TOOL_NAMES = ["skill-eval", "skilleval"]
# 과정 검사 7번 해시 비교에서 무시 (plan.md T7)
HASH_IGNORE = ["__pycache__", "*.pyc", ".pytest_cache"]
# .git 안에서는 이것만 본다 (커밋·브랜치 변경은 잡고, git status가 바꾸는 index는 무시)
GIT_TRACKED = ["HEAD", "config", "refs/*"]
FAKE_REFRESH = "not-used-in-this-copy"


class PrepError(Exception):
    pass


@dataclass
class RunPaths:
    base: Path            # 후보 쪽 임시 폴더(끝나면 삭제)
    workspace: Path       # 작업 폴더(프로젝트 모양 이름)
    agent_dir: Path       # 후보의 PI_CODING_AGENT_DIR
    mock_base: Path       # 모의 사용자·심판 쪽 임시 폴더(끝나면 삭제)
    mock_agent_dir: Path
    mock_cwd: Path
    added_files: list = field(default_factory=list)   # 러너가 넣은 파일(작업 폴더·설정 폴더 기준 경로)

    def to_dict(self):
        return {k: str(v) if isinstance(v, Path) else v for k, v in self.__dict__.items()}


def _hex() -> str:
    # 16진수만 쓰면 금지 단어가 우연히 만들어지지 않는다
    return secrets.token_hex(4)


# ---------- 인증 ----------

def auth_hours_left(source: Path, provider: str) -> float:
    d = json.loads(source.read_text())
    entry = d.get(provider) or {}
    exp = entry.get("expires")
    if not exp:
        raise PrepError(f"{source}에 {provider} 출입증이 없다")
    return (exp / 1000 - time.time()) / 3600


def check_auth(cfg) -> float:
    left = auth_hours_left(cfg.auth_source, cfg.provider)
    if left < cfg.auth["min_hours_left"]:
        raise PrepError(
            f"출입증 남은 시간 {left:.1f}시간 < {cfg.auth['min_hours_left']}시간. 메인에서 갱신한 뒤 다시 실행:\n"
            f"  pi auth print-bearer-token --provider {cfg.provider} --min-expiry {int(cfg.auth['min_hours_left'] * 60 + 60)}m > /dev/null")
    return left


def copy_auth(cfg, agent_dir: Path):
    """auth.json 복사 + refresh를 가짜 값으로 (복사본은 갱신을 시도하지 않는다, plan.md Q39)."""
    d = json.loads(cfg.auth_source.read_text())
    for v in d.values():
        if isinstance(v, dict) and "refresh" in v:
            v["refresh"] = FAKE_REFRESH
    p = agent_dir / "auth.json"
    p.write_text(json.dumps(d, indent=2))
    os.chmod(p, 0o600)


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------- 준비 ----------

def pi_version() -> str:
    try:
        return subprocess.run(["pi", "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                              timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def _git(args, cwd=None, **kw):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True,
                          stdin=subprocess.DEVNULL, **kw)


def _resolve_repo(src: dict) -> Path:
    repo = Path(src["repo"])
    if not repo.is_absolute():
        repo = (CACHE / repo) if src.get("clone_url") else (PILAB / repo)
    if not repo.exists():
        if not src.get("clone_url"):
            raise PrepError(f"저장소 없음: {repo}")
        repo.parent.mkdir(parents=True, exist_ok=True)
        _git(["clone", "--filter=blob:none", "--no-checkout", src["clone_url"], str(repo)])
    return repo


def build_workspace(task, dest: Path):
    """작업 폴더 = 저장소의 한 시점 파일(git archive) + 새 git 1커밋 (미래 기록 제거, goal.md R5 ③)."""
    src = task.workspace["source"]
    repo = _resolve_repo(src)
    dest.mkdir(parents=True)
    arch = subprocess.run(["git", "-C", str(repo), "archive", src["ref"]], capture_output=True,
                          stdin=subprocess.DEVNULL, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=arch, check=True)
    if task.workspace.get("git_init", True):
        env = {**os.environ, "GIT_AUTHOR_DATE": src.get("date", "2026-01-01T00:00:00"),
               "GIT_COMMITTER_DATE": src.get("date", "2026-01-01T00:00:00")}
        _git(["init", "-q", "-b", "main"], cwd=dest)
        _git(["add", "-A"], cwd=dest)
        _git(["-c", "user.name=dev", "-c", "user.email=dev@localhost", "commit", "-q", "-m", "Initial commit"],
             cwd=dest, env=env)


def resolve_input(task, item: dict) -> Path:
    """inputs 한 줄: from(과제 폴더 기준 고정 파일) 또는 from_run(이전 실행 결과물, goal.md Q28)."""
    if "from" in item:
        return task.dir / item["from"]
    fr = item["from_run"]
    name = f"{fr['task']}__{fr['arm']}__r{fr.get('rep', 1)}"
    dates = [fr["date"]] if fr.get("date", "latest") != "latest" else sorted(
        (p.name for p in RESULTS.iterdir() if p.is_dir()), reverse=True)
    for d in dates:
        p = RESULTS / d / "runs" / name / fr.get("file", "goal.md")
        if p.exists():
            return p
    raise PrepError(f"inputs from_run을 찾지 못함: {fr}")


def place_inputs(task, ws: Path) -> list:
    placed = []
    for item in task.inputs:
        src = resolve_input(task, item)
        dst = ws / item["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        placed.append(item["path"])
    return placed


def write_agent_dir(cfg, agent_dir: Path, arm: dict, home: Path) -> list:
    """실행별 pi 설정 폴더. 인증 + settings(홈 스킬 빼기) + 스킬 팔이면 스킬과 AGENTS.md (goal.md R5 ②)."""
    agent_dir.mkdir(parents=True)
    (agent_dir / "sessions").mkdir()
    copy_auth(cfg, agent_dir)
    settings = {"lastChangelogVersion": pi_version(), "quietStartup": True,
                "skills": [f"!{home}/.agents/skills/**"]}
    (agent_dir / "settings.json").write_text(json.dumps(settings, indent=2))
    added = ["auth.json", "settings.json"]
    if arm.get("skills"):
        src_root = PILAB / ".agents" / "skills"
        names = sorted(p.name for p in src_root.iterdir() if p.is_dir()) if arm["skills"] == "all" else arm["skills"]
        for n in names:
            shutil.copytree(src_root / n, agent_dir / "skills" / n)
            added += [f"skills/{n}/{f.relative_to(src_root / n)}" for f in (src_root / n).rglob("*") if f.is_file()]
    if arm.get("agents_md"):
        shutil.copyfile(PILAB / "AGENTS.md", agent_dir / "AGENTS.md")
        added.append("AGENTS.md")
    return added


def prepare(cfg, task, arm: dict) -> RunPaths:
    tmp = Path(tempfile.gettempdir()).resolve()
    base = tmp / _hex()
    mock_base = tmp / _hex()
    paths = RunPaths(base=base, workspace=base / task.workspace["name"], agent_dir=base / ".pi" / "agent",
                     mock_base=mock_base, mock_agent_dir=mock_base / ".pi" / "agent", mock_cwd=mock_base / "chat")
    try:
        build_workspace(task, paths.workspace)
        placed = place_inputs(task, paths.workspace)
        added = write_agent_dir(cfg, paths.agent_dir, arm, Path.home())
        write_agent_dir(cfg, paths.mock_agent_dir, {}, Path.home())
        paths.mock_cwd.mkdir(parents=True)
        paths.added_files = [f"workspace:{p}" for p in placed] + [f"agent:{p}" for p in added]
    except Exception:
        cleanup(paths)
        raise
    return paths


def cleanup(paths: RunPaths):
    for p in (paths.base, paths.mock_base):
        shutil.rmtree(p, ignore_errors=True)


# ---------- 실행 전 가방 검사 ----------

def _walk_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            yield Path(dirpath) / f


def _mask(text: str, spans: list) -> str:
    for s in spans:
        text = text.replace(s, " ")
    return text


def forbidden_hits(text: str) -> list:
    low = text.lower()
    return [w for w in FORBIDDEN if w in low]


def preflight(paths: RunPaths, task, runner_texts: dict, answer_files: list) -> dict:
    """R5 ①과 단어 비노출 검사. runner_texts: 후보에게 가는 글 {이름: 글}(과제 원래 내용은 original_spans로 제외)."""
    res = {"ok": True, "checks": []}

    def add(name, ok, detail):
        res["checks"].append({"name": name, "ok": ok, "detail": detail})
        res["ok"] = res["ok"] and ok

    answer_shas = {file_sha(p) for p in answer_files}
    found_answer, tool_hits = [], []
    for root in (paths.workspace, paths.agent_dir):
        for f in _walk_files(root):
            if f.name in {p.name for p in answer_files} or (f.stat().st_size < 5_000_000 and file_sha(f) in answer_shas):
                found_answer.append(str(f))
            try:
                low = f.read_bytes().decode("utf-8", "ignore").lower()
            except OSError:
                continue
            for w in TOOL_NAMES:
                if w in low:
                    tool_hits.append(f"{f}: {w}")
    add("답변표 파일 없음", not found_answer, found_answer or "0건")
    add("skill-eval 글자 0건", not tool_hits, tool_hits or "0건")

    path_hits = {str(p): forbidden_hits(str(p)) for p in (paths.workspace, paths.agent_dir)}
    path_hits = {k: v for k, v in path_hits.items() if v}
    add("경로에 금지 단어 0건", not path_hits, path_hits or "0건")

    name_hits = {n: forbidden_hits(n.split(":", 1)[1]) for n in paths.added_files}
    name_hits = {k: v for k, v in name_hits.items() if v}
    add("러너가 넣은 파일 이름에 금지 단어 0건", not name_hits, name_hits or f"{len(paths.added_files)}개 확인")

    text_hits = {}
    for k, t in runner_texts.items():
        h = forbidden_hits(_mask(t, task.original_spans))
        if h:
            text_hits[k] = h
    add("시작 요청(러너가 붙인 부분)에 금지 단어 0건", not text_hits,
        {"hits": text_hits or "0건", "제외한 과제 원래 내용": task.original_spans})

    env = clean_env(paths.agent_dir)
    env_hits = {k: forbidden_hits(v) for k, v in env.items() if k != "PI_CODING_AGENT_DIR"}
    env_hits = {k: v for k, v in env_hits.items() if v}
    env_hits.update({k: "pi-lab 경로" for k, v in env.items() if str(PILAB) in v})
    add("pi에 넘기는 환경 변수에 금지 단어·pi-lab 경로 0건", not env_hits, env_hits or f"{len(env)}개 확인")

    if (paths.workspace / ".git").exists():
        n = _git(["rev-list", "--count", "HEAD"], cwd=paths.workspace).stdout.strip()
        add("작업 폴더 git 기록 1커밋", n == "1", f"{n}커밋")
    return res


# ---------- 파일 해시 스냅샷 (과정 검사 7번) ----------

def _ignored(rel: str) -> bool:
    parts = rel.split("/")
    if parts[0] == ".git":
        sub = "/".join(parts[1:])
        return not any(fnmatch.fnmatch(sub, g) for g in GIT_TRACKED)
    return any(fnmatch.fnmatch(p, g) for p in parts for g in HASH_IGNORE)


def hash_tree(root: Path) -> dict:
    out = {}
    for f in _walk_files(root):
        rel = f.relative_to(root).as_posix()
        if _ignored(rel) or f.is_symlink():
            continue
        out[rel] = file_sha(f)
    return out


def diff_trees(before: dict, after: dict) -> dict:
    return {"added": sorted(set(after) - set(before)),
            "removed": sorted(set(before) - set(after)),
            "modified": sorted(k for k in set(before) & set(after) if before[k] != after[k])}


# ---------- goal.md 찾기 ----------

_GOAL_IN_DOTGOAL = re.compile(r"^\.goal/[^/]+/goal\.md$", re.I)


def find_goal(ws: Path) -> Path | None:
    """goal.md는 작업 폴더 어디에 있든 찾는다. .goal/<이름>/ 아래를 먼저, 여럿이면 가장 최근 것."""
    cands = [f for f in _walk_files(ws) if f.name.lower() == "goal.md" and ".git" not in f.relative_to(ws).parts]
    if not cands:
        return None
    pref = [f for f in cands if _GOAL_IN_DOTGOAL.match(f.relative_to(ws).as_posix())]
    pool = pref or cands
    return max(pool, key=lambda f: f.stat().st_mtime)


# ---------- 모델만 부르는 호출(심판 등)용 임시 폴더 ----------

def make_llm_dirs(cfg) -> dict:
    base = Path(tempfile.gettempdir()).resolve() / _hex()
    agent = base / ".pi" / "agent"
    write_agent_dir(cfg, agent, {}, Path.home())
    (base / "chat").mkdir()
    return {"base": base, "agent": agent, "cwd": base / "chat"}


def cleanup_dirs(dirs: dict):
    shutil.rmtree(dirs["base"], ignore_errors=True)
