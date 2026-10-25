"""pi --mode json 기록(JSONL)을 읽는 공통 함수."""
import json
import re
from pathlib import Path

# 러너가 candidate.jsonl, mock_user.jsonl에 끼워 넣는 표지 줄
MARK = "_runner"


def parse_jsonl(data: bytes | str) -> list:
    """LF로만 자른다(유니코드 줄 구분자는 문자열 안에 있을 수 있음, docs/json.md)."""
    if isinstance(data, str):
        data = data.encode()
    out = []
    for raw in data.split(b"\n"):
        raw = raw.rstrip(b"\r")
        if not raw.strip():
            continue
        try:
            out.append(json.loads(raw.decode("utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            out.append({"type": "_unparsed", "raw": raw.decode("utf-8", "replace")})
    return out


def read_jsonl(path: Path) -> list:
    return parse_jsonl(Path(path).read_bytes()) if Path(path).exists() else []


def split_turns(records: list) -> list:
    """러너 표지(turn_start ~ turn_end)로 나눈다. [{start, end, events}]"""
    turns, cur = [], None
    for r in records:
        if r.get(MARK) == "turn_start":
            cur = {"start": r, "end": None, "events": []}
            turns.append(cur)
        elif r.get(MARK) == "turn_end":
            if cur is not None:
                cur["end"] = r
            cur = None
        elif cur is not None:
            cur["events"].append(r)
    return turns


def messages(events: list, role: str | None = None) -> list:
    out = []
    for e in events:
        if e.get("type") == "message_end":
            m = e.get("message") or {}
            if role is None or m.get("role") == role:
                out.append(m)
    return out


def content_text(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if b.get("type") == "text")


def assistant_text(events: list) -> str:
    """후보의 한 턴 = assistant 글 블록 전부(생각·도구 호출 제외, plan.md T4)."""
    parts = [content_text(m.get("content")) for m in messages(events, "assistant")]
    return "\n\n".join(p for p in parts if p.strip())


def tool_calls(events: list) -> list:
    """도구 실행: [{id, name, args, isError, durationMs, result_text}] (시작 순서)."""
    calls, by_id = [], {}
    for e in events:
        t = e.get("type")
        if t == "tool_execution_start":
            c = {"id": e.get("toolCallId"), "name": e.get("toolName"), "args": e.get("args") or {},
                 "isError": None, "durationMs": None, "result_text": ""}
            calls.append(c)
            by_id[c["id"]] = c
        elif t == "tool_execution_end":
            c = by_id.get(e.get("toolCallId"))
            if c is None:
                c = {"id": e.get("toolCallId"), "name": e.get("toolName"), "args": {}}
                calls.append(c)
            c["isError"] = bool(e.get("isError"))
            c["durationMs"] = e.get("durationMs")
            res = e.get("result") or {}
            c["result_text"] = content_text(res.get("content")) if isinstance(res, dict) else str(res)
    return calls


_Q_LINE = re.compile(r"[?？]\s*[*_`)\]\"'”’]*\s*$")


def has_question(text: str) -> bool:
    """질문이 있는 턴인가: ❓ 표식, 또는 코드 블록 밖에서 물음표로 끝나는 줄."""
    if "❓" in text:
        return True
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and _Q_LINE.search(line):
            return True
    return False


def system_sections(events: list) -> dict:
    """1턴 스트림의 system 메시지 sections (skills, project_context 등). 없으면 {}."""
    for e in events:
        if e.get("type") in ("message_start", "message_end"):
            m = e.get("message") or {}
            if m.get("role") == "system" and m.get("sections"):
                return m["sections"]
    return {}


def first_user_text(events: list) -> str:
    for m in messages(events, "user"):
        return content_text(m.get("content"))
    return ""
