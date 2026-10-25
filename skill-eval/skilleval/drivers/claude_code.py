"""Claude Code 드라이버 자리 (goal.md Q21: 이번 목표에서는 구현하지 않음)."""
from .base import Driver


class ClaudeCodeDriver(Driver):
    name = "claude_code"

    def start(self, cfg, paths, arm: dict):
        raise NotImplementedError("Claude Code 드라이버는 다음 목표에서 구현한다")
