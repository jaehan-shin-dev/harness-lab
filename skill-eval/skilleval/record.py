"""저장된 회차 폴더 하나를 판정용으로 읽는다."""
import json
from dataclasses import dataclass
from pathlib import Path

from .events import read_jsonl, split_turns


@dataclass
class RunRecord:
    dir: Path
    meta: dict
    dialogue: list
    turns: list          # [{n, events, start, end}]
    fs_changes: dict
    goal_text: str | None

    @property
    def assistant_turns(self):
        return [d for d in self.dialogue if d["role"] == "assistant"]

    def reply_after(self, n):
        """n번째 후보 턴 뒤 모의 사용자 대답(없으면 None)."""
        return next((d for d in self.dialogue if d["role"] == "user" and d.get("n") == n and d.get("kind") != "start"),
                    None)

    def reply_before(self, n):
        return self.reply_after(n - 1) if n > 1 else None

    def goal_snapshot(self, n) -> str | None:
        p = self.dir / "rounds" / f"goal.round{n}.md"
        return p.read_text() if p.exists() else None

    def events_of(self, n) -> list:
        for t in self.turns:
            if t["start"].get("turn") == n:
                return t["events"]
        return []

    @property
    def workspace(self) -> str:
        return (self.meta.get("paths") or {}).get("workspace", "")

    @property
    def agent_dir(self) -> str:
        return (self.meta.get("paths") or {}).get("agent_dir", "")

    @property
    def base(self) -> str:
        """회차 폴더: 작업 폴더와 설정 폴더(.pi/agent)만 들어 있는 곳."""
        return (self.meta.get("paths") or {}).get("base", "")


def load_run(run_dir: Path) -> RunRecord:
    run_dir = Path(run_dir)
    j = lambda name, default: json.loads((run_dir / name).read_text()) if (run_dir / name).exists() else default
    goal = run_dir / "goal.md"
    return RunRecord(dir=run_dir, meta=j("meta.json", {}), dialogue=j("dialogue.json", []),
                     turns=split_turns(read_jsonl(run_dir / "candidate.jsonl")),
                     fs_changes=j("fs_changes.json", {"added": [], "removed": [], "modified": []}),
                     goal_text=goal.read_text() if goal.exists() else None)
