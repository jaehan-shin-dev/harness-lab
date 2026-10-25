"""pi 드라이버: --session-id로 다회전 (research/pi-smoke.md 권장 호출)."""
import uuid

from ..events import first_user_text, messages, parse_jsonl
from ..pi_process import run_pi
from .base import Driver, TurnResult


class PiDriver(Driver):
    name = "pi"

    def start(self, cfg, paths, arm: dict):
        self.cfg, self.paths, self.arm = cfg, paths, arm
        self.session_id = str(uuid.uuid4())

    def command(self, message: str) -> list:
        c = self.cfg
        cmd = ["pi", "--mode", "json", "--provider", c.provider, "--model", c.model,
               "--thinking", c.thinking["candidate"],
               "--session-dir", str(self.paths.agent_dir / "sessions"), "--session-id", self.session_id,
               # 두 팔 공통: 확장·MCP 끄기(plan.md Q42), 작업 폴더의 .pi/·.agents/ 무시(plan.md T3)
               "--no-extensions", "--no-mcp", "--no-approve", "--tools", ",".join(c.candidate_tools)]
        if not self.arm.get("skills"):
            cmd.append("--no-skills")
        if not self.arm.get("agents_md"):
            cmd.append("--no-context-files")
        return cmd + ["--", message]

    def turn(self, n: int, message: str) -> TurnResult:
        cmd = self.command(message)
        r = run_pi(cmd, self.paths.workspace, self.paths.agent_dir, self.cfg.timeouts["candidate_turn"])
        events = parse_jsonl(r["stdout"])
        tr = TurnResult(n=n, prompt=message, cmd=cmd, events=events, stderr=r["stderr"],
                        returncode=r["returncode"], duration_s=r["duration_s"], timed_out=r["timed_out"],
                        extra={"pid": r["pid"]})
        tr.error = self.check(n, tr)
        return tr

    def check(self, n: int, tr: TurnResult) -> str | None:
        if tr.timed_out:
            return f"시간 초과({self.cfg.timeouts['candidate_turn']}초)"
        if tr.returncode != 0:
            return f"pi 종료 코드 {tr.returncode}: {tr.stderr[-500:]}"
        if n > 1 and "No project session found" in tr.stderr:
            return "세션이 이어지지 않음(No project session found)"
        if n == 1 and self.arm.get("start_skill"):
            want = f'<skill name="{self.arm["start_skill"]}"'
            if not first_user_text(tr.events).startswith(want):
                return f"1턴 사용자 메시지가 {want}로 시작하지 않음(스킬이 안 풀림)"
        asst = messages(tr.events, "assistant")
        if not asst:
            return "assistant 메시지 없음"
        if asst[-1].get("stopReason") in ("error", "aborted"):
            return f"assistant 오류: {asst[-1].get('errorMessage')}"
        if not any(e.get("type") == "agent_settled" for e in tr.events):
            return "agent_settled 없음(출력이 끝까지 안 옴)"
        return None

    def describe(self) -> dict:
        return {"driver": self.name, "session_id": getattr(self, "session_id", None)}
