"""suites/<스킬>/ 묶음: suite.yaml, tasks/<과제>/task.yaml, answer.yaml."""
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import SUITES

FACT_KINDS = ("user", "accept", "findable")


@dataclass
class Fact:
    id: str
    kind: str                 # user(물어야 나옴) / accept(수락 결정) / findable(찾을 수 있는 사실)
    content: str              # 사실 내용(심판·모의 사용자용 설명)
    say: str = ""             # 모의 사용자가 말할 문장
    trigger: str = ""         # 어떤 질문을 받으면 말하나
    keywords: list = field(default_factory=list)       # 회수율 패턴(정규식, 하나라도 맞으면 회수)
    leak_patterns: list = field(default_factory=list)  # 누출 검사 패턴(유도할 수 없는 핵심만)
    recall: bool = True       # user 사실 중 회수율 계산에 넣는가
    known_from_start: bool = False   # 시작 요청이나 inputs로 이미 알려진 사실
    section: str = ""         # out_of_scope 등
    source: str = ""          # 근거(대화 기록 줄 번호, 이슈 원문 등)

    @property
    def scored(self) -> bool:
        return self.kind == "user" and self.recall


@dataclass
class Answer:
    persona: str
    facts: list
    replies: dict             # unknown, confirm, progress, findable, accept, next_step
    path: Path

    def by_id(self, fid):
        return next((f for f in self.facts if f.id == fid), None)

    def ids(self, kind=None):
        return [f.id for f in self.facts if kind is None or f.kind == kind]


@dataclass
class Task:
    id: str
    dir: Path
    data: dict
    answer: Answer

    @property
    def workspace(self) -> dict:
        return self.data["workspace"]

    @property
    def inputs(self) -> list:
        return self.data.get("inputs") or []

    @property
    def start_request(self) -> str:
        return self.data["start_request"].strip()

    @property
    def original_spans(self) -> list:
        """시작 요청 중 과제 원래 내용(금지 단어 검사에서 뺀다, goal.md Q11)."""
        return self.data.get("original_spans") or []


@dataclass
class Suite:
    name: str
    dir: Path
    data: dict
    tasks: list

    @property
    def arms(self) -> dict:
        return self.data["arms"]

    def task(self, tid) -> Task:
        return next(t for t in self.tasks if t.id == tid)


def load_answer(path: Path) -> Answer:
    d = yaml.safe_load(path.read_text())
    facts = []
    for kind_key, kind in (("facts", None), ("out_of_scope", None)):
        for f in d.get(kind_key) or []:
            f = dict(f)
            if kind_key == "out_of_scope":
                f.setdefault("section", "out_of_scope")
            fact = Fact(**f)
            if fact.kind not in FACT_KINDS:
                raise ValueError(f"{path}: {fact.id} kind={fact.kind}")
            facts.append(fact)
    ids = [f.id for f in facts]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: 사실 id 중복")
    return Answer(persona=d["persona"], facts=facts, replies=d["replies"], path=path)


def load_suite(name: str, root: Path | None = None) -> Suite:
    sdir = (root or SUITES) / name
    data = yaml.safe_load((sdir / "suite.yaml").read_text())
    tasks = []
    for tid in data["tasks"]:
        tdir = sdir / "tasks" / tid
        tdata = yaml.safe_load((tdir / "task.yaml").read_text())
        tasks.append(Task(id=tid, dir=tdir, data=tdata, answer=load_answer(tdir / "answer.yaml")))
    return Suite(name=name, dir=sdir, data=data, tasks=tasks)
