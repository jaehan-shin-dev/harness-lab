"""시험용 가짜 드라이버: 모델 호출 없이 정해진 응답을 pi json 모양으로 낸다 (plan.md T4)."""
import json
import uuid
from pathlib import Path

from .base import Driver, TurnResult

_USAGE = {"input": 100, "output": 20, "cacheRead": 0, "cacheWrite": 0, "reasoning": 5, "totalTokens": 120,
          "cost": {"input": 0.001, "output": 0.002, "cacheRead": 0, "cacheWrite": 0, "total": 0.003}}


def make_events(n: int, prompt: str, steps: list, arm: dict | None = None, workspace: Path | None = None,
                agent_dir: str = "/agent") -> list:
    """steps: assistant 메시지 목록. 각 {"text": str, "tools": [{"name", "args", "result", "isError"}]}"""
    arm = arm or {}
    ev = [{"type": "session", "version": 3, "id": str(uuid.uuid4()), "cwd": str(workspace or "/w")},
          {"type": "agent_start"}]
    if n == 1:
        sections = {"preamble": "You are pi."}
        if arm.get("skills"):
            sections["skills"] = "\n".join(f"<skill><name>{s}</name></skill>" for s in arm.get("skill_names", []))
        if arm.get("agents_md"):
            sections["project_context"] = f'<project_instructions path="{agent_dir}/AGENTS.md">'
        sysmsg = {"role": "system", "content": "", "sections": sections, "timestamp": 0}
        ev += [{"type": "message_start", "message": sysmsg}, {"type": "message_end", "message": sysmsg}]
    utext = prompt
    if n == 1 and arm.get("start_skill") and prompt.startswith("/skill:"):
        name = arm["start_skill"]
        utext = f'<skill name="{name}" location="{agent_dir}/skills/{name}/SKILL.md">\n...\n</skill>\n\n' + \
            prompt.split(" ", 1)[-1]
    umsg = {"role": "user", "content": [{"type": "text", "text": utext}], "timestamp": 0}
    ev += [{"type": "turn_start"}, {"type": "message_start", "message": umsg}, {"type": "message_end", "message": umsg}]
    for i, st in enumerate(steps):
        tools = st.get("tools") or []
        content = [{"type": "thinking", "thinking": "..."}]
        if st.get("text"):
            content.append({"type": "text", "text": st["text"]})
        ids = []
        for t in tools:
            tid = f"call_{uuid.uuid4().hex[:8]}"
            ids.append(tid)
            content.append({"type": "toolCall", "id": tid, "name": t["name"], "arguments": t.get("args", {})})
        amsg = {"role": "assistant", "content": content, "usage": _USAGE, "provider": "fake", "model": "fake",
                "stopReason": "toolUse" if tools else "stop", "timestamp": 0}
        ev += [{"type": "message_start", "message": {"role": "assistant", "content": []}},
               {"type": "message_end", "message": amsg}]
        for tid, t in zip(ids, tools):
            res = {"content": [{"type": "text", "text": t.get("result", "ok")}], "details": {}}
            ev += [{"type": "tool_execution_start", "toolCallId": tid, "toolName": t["name"], "args": t.get("args", {})},
                   {"type": "tool_execution_end", "toolCallId": tid, "toolName": t["name"], "result": res,
                    "isError": bool(t.get("isError")), "durationMs": 3}]
            tr = {"role": "toolResult", "toolCallId": tid, "toolName": t["name"], "content": res["content"],
                  "isError": bool(t.get("isError")), "timestamp": 0}
            ev += [{"type": "message_end", "message": tr}]
        ev.append({"type": "turn_end"})
    ev += [{"type": "agent_end", "messages": [], "willRetry": False}, {"type": "agent_settled", "aborted": False}]
    return ev


class FakeDriver(Driver):
    """script(n, message, paths) -> {"steps": [...]} 또는 턴별 목록. write 도구는 실제로 파일을 쓴다."""
    name = "fake"

    def __init__(self, script):
        self.script = script

    def start(self, cfg, paths, arm: dict):
        self.paths, self.arm = paths, arm

    def turn(self, n: int, message: str) -> TurnResult:
        spec = self.script(n, message, self.paths) if callable(self.script) else self.script[n - 1]
        for st in spec.get("steps", []):
            for t in st.get("tools") or []:
                if t["name"] == "write":
                    p = self.paths.workspace / t["args"]["path"]
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(t["args"]["content"])
        events = make_events(n, message, spec.get("steps", []), self.arm, self.paths.workspace,
                             str(self.paths.agent_dir))
        cmd = ["fake", "--no-skills"] if not self.arm.get("skills") else ["fake"]
        if not self.arm.get("agents_md"):
            cmd.append("--no-context-files")
        return TurnResult(n=n, prompt=message, cmd=cmd + ["--", message], events=events,
                          error=spec.get("error"))
