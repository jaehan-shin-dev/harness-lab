"""드라이버 인터페이스 (goal.md Q10: 드라이버 교체형). 한 턴 = 후보 에이전트 프로세스 한 번."""
from dataclasses import dataclass, field

from ..events import assistant_text


@dataclass
class TurnResult:
    n: int
    prompt: str
    cmd: list
    events: list
    stderr: str = ""
    returncode: int = 0
    duration_s: float = 0.0
    timed_out: bool = False
    error: str | None = None
    extra: dict = field(default_factory=dict)

    @property
    def text(self) -> str:
        return assistant_text(self.events)


class Driver:
    """start()로 회차를 열고 turn()을 라운드마다 부른다. 원본 기록은 러너가 저장한다."""
    name = "base"

    def start(self, cfg, paths, arm: dict):
        raise NotImplementedError

    def turn(self, n: int, message: str) -> TurnResult:
        raise NotImplementedError

    def describe(self) -> dict:
        """보고서 머리말용(드라이버 이름, 버전 등)."""
        return {"driver": self.name}
