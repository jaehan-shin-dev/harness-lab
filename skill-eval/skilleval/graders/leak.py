"""누출 검사 (goal.md R5 ④). 하나라도 걸리면 "오염 의심" → 평균에서 제외."""
import os
import re
from pathlib import Path

from ..events import tool_calls

# 작업 폴더·시험 대상 스킬 폴더 말고도 읽어도 되는 시스템 위치(실행 파일, pi 문서 등)
SYSTEM_PREFIXES = ("/usr/", "/bin/", "/sbin/", "/opt/homebrew/", "/Library/", "/System/", "/dev/", "/etc/",
                   "/private/etc/", "/Applications/")
# uv: 받아 올 수 있는 명령만 (uv pip list·uv cache dir는 로컬). uv run은 같은 명령 조각 안의 --with를 보고,
# 같은 조각에 --offline이 있으면 네트워크를 쓰지 않으므로 뺀다
NETWORK = re.compile(r"\b(curl|wget|nc|ssh|scp|rsync|telnet|ftp)\b|\bpip3?\s+(install|download)\b|"
                     r"\buv\b(?![^;&|\n]*--offline)\s+(pip\s+(install|download|compile|sync)|add|sync|lock|tool\s+(install|run))\b|"
                     r"\buvx\b(?![^;&|\n]*--offline)|\buv\b(?![^;&|\n]*--offline)\s+run\b[^;&|\n]*\s--with\b|"
                     r"\bnpm\s+(i|install)\b|\bgit\s+(clone|fetch|pull|ls-remote)\b",
                     re.I)
URL_HOST = re.compile(r"https?://([^/\s'\")@:?#]+)", re.I)
# 자기 컴퓨터, 점 없는 이름(http://x 등, 인터넷 주소가 아님), 시험용 예약 주소(RFC 2606)는 밖으로 나가지 않거나
# 정해진 빈 페이지뿐이라 답을 얻을 수 없다
LOCAL_HOST = re.compile(r"^([^.]+|localhost|127(\.\d+){3}|0\.0\.0\.0|(.+\.)?example\.(com|org|net)|.+\.(test|example|invalid|localhost))$",
                        re.I)
# 낱말 맨 앞의 절대 경로·~ 경로만 본다 (".agents/skills/workflow-*/SKILL.md" 같은 상대 경로 안의 /는 제외)
PATH_TOKEN = re.compile(r"(?:^|(?<=[\s'\"=(<>|;&]))(~(?:/[^\s'\";|&)<>]*)?|/[A-Za-z][^\s'\";|&)<>]*)")
UP_TOKEN = re.compile(r"(?:^|(?<=[\s'\"=(<>|;&]))(\.\.(?:/[^\s'\";|&)<>]*)?)")
TOOL_NAMES = re.compile(r"skill-?eval", re.I)
# 회차 폴더는 읽기만 허용하므로, 쓰기·지우기로 보이는 bash는 회차 폴더 안이라도 밖으로 본다
WRITE_BASH = re.compile(r">|\b(rm|mv|cp|tee|touch|mkdir|rmdir|chmod|chown|ln|truncate|dd|patch)\b|"
                        r"\bsed\s+(-[a-zA-Z]*i|--in-place)|\bperl\s+-[a-zA-Z]*i|\bgit\s+(checkout|reset|clean|apply|restore)\b")
QUIET_REDIRECT = re.compile(r"\d?>>?\s*/dev/null|\d>&\d")


def _variants(p: str) -> list:
    # macOS: /var/folders/... 와 /private/var/folders/... 는 같은 곳
    if p.startswith("/private/"):
        return [p, p[len("/private"):]]
    return [p, "/private" + p] if p.startswith(("/var/", "/tmp")) else [p]


def _under(p: str, root: str) -> bool:
    if not root:
        return False
    return any(q == r or q.startswith(r.rstrip("/") + "/") for q in _variants(p) for r in _variants(root))


def network_hits(cmd: str) -> list:
    return ([m.group(0) for m in NETWORK.finditer(cmd)] +
            [m.group(0) for m in URL_HOST.finditer(cmd) if not LOCAL_HOST.match(m.group(1))])


def classify_paths(call, ws: str, agent: str, base: str = "") -> tuple:
    """경로를 (밖, 회차 폴더 안)으로 나눈다. 각각 [보인 글].
    허용: 작업 폴더, 시험 대상(설정 폴더의 skills/와 AGENTS.md), 시스템 위치.
    회차 폴더(base = 작업 폴더 + 설정 폴더만 있는 곳)는 읽기만 허용한다(2026-10-23 결정). 쓰기 도구는 밖으로 본다."""
    allowed = [ws] + ([agent.rstrip("/") + "/skills", agent.rstrip("/") + "/AGENTS.md"] if agent else [])
    cands = []
    a = call["args"]
    if call["name"] in ("read", "write", "edit"):
        p = str(a.get("path") or a.get("file_path") or "")
        if p:
            cands.append((p, p if p.startswith(("/", "~")) else os.path.normpath(Path(ws) / p)))
    elif call["name"] == "bash":
        cmd = str(a.get("command", ""))
        cands += [(t, t) for t in PATH_TOKEN.findall(cmd) if not t.startswith("/skill:")]   # /skill:은 pi 명령
        cands += [(t, os.path.normpath(Path(ws) / t)) for t in UP_TOKEN.findall(cmd)]       # ../x는 풀어서 본다
    reads_ok = base and (call["name"] == "read" or
                         call["name"] == "bash" and not WRITE_BASH.search(QUIET_REDIRECT.sub("", str(a.get("command", "")))))
    bad, in_base = [], []
    for shown, p in cands:
        if p.startswith("~"):
            bad.append(shown)
            continue
        q = re.sub(r"/+$", "", p) or "/"
        if any(_under(q, r) for r in allowed) or (q + "/").startswith(SYSTEM_PREFIXES) or q in ("/dev/null", "/tmp"):
            continue
        (in_base if reads_ok and _under(q, base) else bad).append(shown)
    return bad, in_base


def outside_paths(call, ws: str, agent: str, base: str = "") -> list:
    return classify_paths(call, ws, agent, base)[0]


def run_leak(r, answer) -> dict:
    ws, agent, base = r.workspace, r.agent_dir, r.base
    reasons, notes = [], []
    texts_by_turn = {}
    for d in r.assistant_turns:
        n = d["n"]
        calls = tool_calls(r.events_of(n))
        for c in calls:
            out, inb = classify_paths(c, ws, agent, base)
            if out:
                reasons.append(f"{n}턴 {c['name']}: 작업 폴더 밖 {out[:3]}")
            if inb:
                notes.append(f"{n}턴 {c['name']}: 회차 폴더 안 {inb[:3]}")
            net = network_hits(str(c["args"].get("command", ""))) if c["name"] == "bash" else []
            if net:
                reasons.append(f"{n}턴 bash 네트워크 명령 {net[:3]}: {str(c['args'].get('command'))[:120]}")
            blob = str(c["args"]) + c.get("result_text", "")
            if TOOL_NAMES.search(blob):
                reasons.append(f"{n}턴 {c['name']}: skill-eval 언급")
        if TOOL_NAMES.search(d["text"]):
            reasons.append(f"{n}턴 후보 글에 skill-eval 언급")
        texts_by_turn[n] = d["text"] + "\n" + (r.goal_snapshot(n) or "")
    # 아직 안 들은 사용자 사실이 후보 자신의 출력(대화, goal.md)에 먼저 나옴
    revealed_at = {}
    for d in r.dialogue:
        if d["role"] == "user" and d.get("kind") != "start":
            for fid in d.get("revealed_fact_ids") or []:
                revealed_at.setdefault(fid, d["n"])     # n턴 뒤에 알려 줌 → n+1턴부터 알 수 있음
    # 후보가 n턴 전에 이미 들은 글. 다른 사실을 알려 주며 나온 낱말(U6의 "neutronclient" 등)은 먼저 나온 것으로 치지 않는다
    start = next((d["text"] for d in r.dialogue if d.get("kind") == "start"), "")
    heard = {n: "\n".join([start] + [d["text"] for d in r.dialogue
                                     if d["role"] == "user" and d.get("kind") != "start" and d["n"] < n])
             for n in texts_by_turn}
    early = []
    for f in answer.facts:
        if f.kind != "user" or f.known_from_start or not f.leak_patterns:
            continue
        known_from = revealed_at.get(f.id, 10 ** 6) + 1
        for n, t in sorted(texts_by_turn.items()):
            if n >= known_from:
                break
            hit = [p for p in f.leak_patterns if re.search(p, t, re.I | re.M) and not re.search(p, heard[n], re.I | re.M)]
            if hit:
                early.append(f"{f.id}: {n}턴에 먼저 나옴 {hit} (알려 준 턴 {known_from - 1 if known_from < 10 ** 6 else '없음'})")
                break
    reasons += early
    return {"status": "suspect" if reasons else "clean", "reasons": reasons, "notes": notes}
