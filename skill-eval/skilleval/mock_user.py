"""모의 사용자 (goal.md R1). 모델은 질문마다 어떤 사실로 대답할지만 고르고, 대답 문장은 답변표에서 만든다.
그래서 답변표 밖의 사실은 문장에 들어갈 수 없다."""
from dataclasses import dataclass, field

from .events import has_question
from .llm_json import call_json

ITEM_TYPES = ("fact", "accept", "findable", "unknown")
KIND_FOR_TYPE = {"fact": "user", "accept": "accept", "findable": "findable"}

SYSTEM = """너는 AI 에이전트와 대화하는 "사용자" 역할을 맡은 분류기다.
에이전트의 마지막 메시지를 읽고, 질문마다 사용자가 아는 사실 중 무엇으로 대답할지 고른다.
대답 문장은 프로그램이 만든다. 너는 JSON 하나만 출력한다.

## 사용자
{persona}

## 사용자가 아는 것 (이 목록 밖의 것은 모른다)
종류
- user: 사용자만 아는 사실. 에이전트가 관련된 것을 물으면 말한다.
- accept: 사용자가 받아들일 결정. 에이전트가 같은 방향을 추천하거나 제안하면 수락한다.
- findable: 에이전트가 파일·코드·명령으로 직접 확인할 수 있는 사실.

{facts}

## 출력 형식
{{"items": [{{"label": "Q1", "type": "fact", "fact_ids": ["U1"]}}], "confirm_requested": false, "next_step_asked": false}}

## 규칙
1. items: 마지막 메시지 안의 질문(결정 요청 포함)마다 하나. 번호가 있으면 label에 그 번호(예: Q1), 없으면 질문을 4~10글자로 줄인 제목. 질문이 아닌 설명이나 보고는 넣지 않는다. "이대로 마무리할까요" 같은 마무리 확인과 다음 단계로 넘어갈지 묻는 말은 items에 넣지 않는다(아래 3, 4번).
2. type은 위에서부터 먼저 맞는 것을 고른다.
   - fact: user 사실 중 이 질문에 직접 답이 되는 것이 있다. fact_ids에 그 id. 질문과 직접 관련 없는 사실은 넣지 않는다.
   - accept: 질문의 추천이나 제안이 accept 결정 중 하나와 같은 방향이다. fact_ids에 그 id.
   - findable: 질문이 묻는 것이 파일·코드·명령으로 확인할 수 있는 사실이다. 결정이나 선호는 여기에 해당하지 않는다. 맞는 findable id가 있으면 fact_ids에 넣고, 없으면 빈 목록.
   - unknown: 위 어디에도 해당하지 않는다. fact_ids는 빈 목록.
3. confirm_requested: 에이전트가 정리를 마무리(확정, 종료, 닫기, "이대로 가도 될까요")해도 되는지 확인을 구하면 true.
4. next_step_asked: 에이전트가 다음 단계(계획, 구현, 실행 시작 등)로 넘어갈지 물으면 true.
5. JSON 말고 다른 글은 쓰지 않는다."""

MESSAGE = """## 지금까지 대화
{history}

## 에이전트의 마지막 메시지
{last}

위 마지막 메시지를 규칙대로 분류해 JSON만 출력하라."""


@dataclass
class Reply:
    kind: str                     # answer / confirm / next_step / progress
    text: str
    items: list = field(default_factory=list)
    revealed_fact_ids: list = field(default_factory=list)
    accepted_ids: list = field(default_factory=list)
    findable_ids: list = field(default_factory=list)
    decision: dict = field(default_factory=dict)
    fixes: list = field(default_factory=list)
    call: dict = field(default_factory=dict)

    def to_dict(self):
        return dict(self.__dict__)


def facts_block(answer) -> str:
    lines = []
    for f in answer.facts:
        sec = " (하지 않기로 한 것)" if f.section == "out_of_scope" else ""
        lines.append(f"- {f.id} [{f.kind}]{sec} {f.content}")
        if f.trigger:
            lines.append(f"  이런 질문에: {f.trigger}")
    return "\n".join(lines)


def history_block(dialogue: list) -> str:
    out = []
    for d in dialogue:
        who = "사용자" if d["role"] == "user" else f"에이전트 {d['n']}번째"
        out.append(f"[{who}]\n{d['text']}")
    return "\n\n".join(out)


def normalize(decision: dict, answer, last_text: str) -> tuple[dict, list]:
    """모델 출력을 답변표 id로만 정리한다. 맞지 않는 id는 버리고 기록한다."""
    fixes, items = [], []
    for it in decision.get("items") or []:
        t = it.get("type")
        if t not in ITEM_TYPES:
            fixes.append(f"알 수 없는 type {t!r} → unknown")
            t = "unknown"
        ids = [i for i in it.get("fact_ids") or [] if isinstance(i, str)]
        if t in KIND_FOR_TYPE:
            ok = [i for i in ids if i in answer.ids(KIND_FOR_TYPE[t])]
            if len(ok) != len(ids):
                fixes.append(f"{it.get('label')}: {t}에 맞지 않는 id {sorted(set(ids) - set(ok))} 버림")
            ids = ok
            if t in ("fact", "accept") and not ids:
                fixes.append(f"{it.get('label')}: {t}인데 id 없음 → unknown")
                t = "unknown"
        else:
            ids = []
        items.append({"label": str(it.get("label") or "").strip(), "type": t, "fact_ids": ids})
    out = {"items": items, "confirm_requested": bool(decision.get("confirm_requested")),
           "next_step_asked": bool(decision.get("next_step_asked"))}
    if not items and not out["confirm_requested"] and not out["next_step_asked"] and has_question(last_text):
        fixes.append("질문이 있는데 items가 비어 있음 → unknown 하나")
        out["items"] = [{"label": "", "type": "unknown", "fact_ids": []}]
    return out, fixes


def compose(decision: dict, answer) -> Reply:
    rp = answer.replies
    lines, revealed, accepted, findable = [], [], [], []
    for i, it in enumerate(decision["items"], 1):
        t, ids = it["type"], it["fact_ids"]
        if t == "fact":
            new = [x for x in ids if x not in revealed]       # 같은 대답 안에서 같은 사실을 두 번 말하지 않는다
            body = " ".join(answer.by_id(x).say or answer.by_id(x).content for x in new) or rp.get("same", "위에 말한 것과 같아요.")
            revealed += new
        elif t == "accept":
            body = rp["accept"]
            accepted += ids
        elif t == "findable":
            body = rp["findable"]
            findable += ids
        else:
            body = rp["unknown"]
        label = it["label"] or f"{i})"
        lines.append(f"{label}: {body}" if len(decision["items"]) > 1 or it["label"] else body)
    if decision["confirm_requested"]:
        lines.append(rp["confirm"])
    if decision["next_step_asked"]:
        lines.append(rp["next_step"])
    if decision["confirm_requested"]:
        kind = "confirm"
    elif decision["items"]:
        kind = "answer"
    elif decision["next_step_asked"]:
        kind = "next_step"
    else:
        kind = "progress"
        lines = [rp["progress"]]
    dedup = lambda xs: list(dict.fromkeys(xs))
    return Reply(kind=kind, text="\n".join(lines), items=decision["items"], revealed_fact_ids=dedup(revealed),
                 accepted_ids=dedup(accepted), findable_ids=dedup(findable), decision=decision)


class MockUser:
    """policy: "llm"(답변표 + 모델 분류) 또는 "always_unknown"(라운드 상한 시험용, goal.md R1 Evaluation)."""

    def __init__(self, cfg, answer, paths, log, policy: str = "llm", classify=None):
        self.cfg, self.answer, self.paths, self.log, self.policy = cfg, answer, paths, log, policy
        self.classify = classify      # 시험용: (dialogue, last_text) -> decision dict

    def reply(self, dialogue: list, last_text: str) -> Reply:
        if self.policy == "always_unknown":
            decision = {"items": [{"label": "", "type": "unknown", "fact_ids": []}],
                        "confirm_requested": False, "next_step_asked": False}
            r = compose(decision, self.answer)
            self.log({"_runner": "mock_reply", "policy": self.policy, "reply": r.to_dict()})
            return r
        if self.classify:
            raw, call = self.classify(dialogue, last_text), {}
        else:
            raw, call = call_json(
                self.cfg, system_prompt=SYSTEM.format(persona=self.answer.persona.strip(),
                                                      facts=facts_block(self.answer)),
                message=MESSAGE.format(history=history_block(dialogue), last=last_text),
                thinking=self.cfg.thinking["mock_user"], timeout=self.cfg.timeouts["mock_user"],
                cwd=self.paths.mock_cwd, agent_dir=self.paths.mock_agent_dir, prompt_dir=self.paths.mock_base,
                log=self.log, label="mock_user", tries=1 + self.cfg.retries["json_parse"])
        decision, fixes = normalize(raw, self.answer, last_text)
        r = compose(decision, self.answer)
        r.fixes, r.call = fixes, call
        self.log({"_runner": "mock_reply", "policy": self.policy, "raw": raw, "reply": r.to_dict()})
        return r
