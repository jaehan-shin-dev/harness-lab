"""LLM 심판 (goal.md R2 보조): 사실별 판정 + 루브릭. 팔 이름은 넣지 않는다 (plan.md T11).
대화에는 후보 글도 넣는다(2026-10-22 사용자 결정). 시작 요청은 팔 구성이 드러나지 않게 task.yaml 원문을 쓴다."""
from ..llm_json import call_json
from ..workspace import cleanup_dirs, make_llm_dirs

SYSTEM = """너는 목표 정의 문서(goal.md)를 읽고 판정하는 심판이다. JSON 하나만 출력한다.

입력
- 사실 목록: 사용자가 알고 있던 사실. 문서가 각 사실을 담았는지 판정한다.
- 대화: 문서를 쓴 쪽(후보)과 사용자가 실제로 주고받은 말. 루브릭 4번(지어내지 않음) 판단에 쓴다.
  사용자가 "추천대로 해주세요" 같은 말로 받아들였다면, 바로 앞 후보 글의 추천이 무엇이었는지 여기서 확인한다.
- 루브릭: 기준마다 0/1/2.
- 문서: 판정할 goal.md.

판정 방법
- facts: 사실마다 captured(문서가 그 사실의 핵심을 담았으면 true, 표현은 달라도 된다), evidence(문서에서 근거가 된 짧은 인용, 없으면 빈 문자열).
  facts는 문서만 보고 판정한다. 대화에 나온 사실이라도 문서에 없으면 false다.
- rubric: 기준 번호마다 score(0, 1, 2)와 reason(한 줄). 루브릭은 문서의 품질을 매긴다.
  대화는 문서 내용이 어디서 왔는지 확인하는 데만 쓰고, 질문하는 방식 자체는 점수에 넣지 않는다.
  사실 목록은 facts 판정에만 쓴다. 사용자가 대화에서 말하지 않은 사실이 문서에 없는 것은 루브릭에서 감점하지 않는다.

출력 형식
{"facts": [{"id": "U1", "captured": true, "evidence": "..."}], "rubric": [{"id": 1, "score": 2, "reason": "..."}]}"""

MESSAGE = """## 사실 목록
{facts}

## 대화
{dialogue}

## 루브릭
{rubric}

## 문서 (goal.md)
{goal}

위 문서를 판정해 JSON만 출력하라."""


def build_message(answer, goal_text: str, dialogue: list, rubric: str) -> str:
    """dialogue: [(누가, 글)] 순서대로."""
    facts = "\n".join(f"- {f.id}: {f.content}" for f in answer.facts if f.scored)
    dlg = "\n\n".join(f"### {who}\n{text.strip()}" for who, text in dialogue) or "(없음)"
    return MESSAGE.format(facts=facts, dialogue=dlg, rubric=rubric.strip(), goal=goal_text or "(빈 문서)")


def validate(data: dict, answer) -> dict:
    ids = {f.id for f in answer.facts if f.scored}
    facts = {f["id"]: {"captured": bool(f.get("captured")), "evidence": str(f.get("evidence", ""))}
             for f in data.get("facts") or [] if f.get("id") in ids}
    missing = sorted(ids - set(facts))
    rubric = {}
    for it in data.get("rubric") or []:
        try:
            k, s = int(it.get("id")), int(it.get("score"))
        except (TypeError, ValueError):
            continue
        if 1 <= k <= 5 and s in (0, 1, 2):
            rubric[k] = {"score": s, "reason": str(it.get("reason", ""))}
    if missing or len(rubric) != 5:
        raise ValueError(f"심판 출력 불완전: 빠진 사실 {missing}, 루브릭 {sorted(rubric)}")
    return {"facts": facts, "rubric": {str(k): v for k, v in sorted(rubric.items())},
            "rubric_total": sum(v["score"] for v in rubric.values())}


def run_judge(cfg, answer, goal_text: str, dialogue: list, rubric: str, log) -> dict:
    msg = build_message(answer, goal_text, dialogue, rubric)
    dirs = make_llm_dirs(cfg)
    try:
        last = None
        for attempt in range(1 + cfg.retries["json_parse"]):
            try:
                data, call = call_json(cfg, system_prompt=SYSTEM, message=msg, thinking=cfg.thinking["judge"],
                                       timeout=cfg.timeouts["judge"], cwd=dirs["cwd"], agent_dir=dirs["agent"],
                                       prompt_dir=dirs["base"], log=log, label="judge", tries=1)
            except RuntimeError as ex:
                last = ex
                continue
            try:
                out = validate(data, answer)
                out["call"] = {**call, "attempt": attempt + 1}
                out["input_message"] = msg
                return out
            except ValueError as ex:
                last = ex
                log({"_runner": "judge_invalid", "error": str(ex), "data": data})
        raise RuntimeError(str(last))
    finally:
        cleanup_dirs(dirs)
