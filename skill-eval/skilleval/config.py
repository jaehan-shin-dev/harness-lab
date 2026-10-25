"""config.yaml과 경로를 한 곳에서 읽는다."""
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent      # skill-eval/
PILAB = ROOT.parent                                 # pi-lab/ (시험 대상 스킬이 있는 저장소)
CACHE = ROOT / ".cache"
RESULTS = ROOT / "results"
SUITES = ROOT / "suites"


@dataclass
class Config:
    provider: str
    model: str
    context_window: int
    thinking: dict
    reps: int
    max_rounds: int
    jobs: int
    timeouts: dict
    retries: dict
    auth: dict
    candidate_tools: list = field(default_factory=list)

    @property
    def auth_source(self) -> Path:
        return Path(self.auth["source"]).expanduser()


def load_config(path: Path | None = None) -> Config:
    data = yaml.safe_load((path or ROOT / "config.yaml").read_text())
    return Config(**data)
