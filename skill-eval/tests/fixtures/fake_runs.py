"""가짜 회차 만들기: FakeDriver + 정해진 모의 사용자 분류로 runner를 실제로 돌린다 (pi 호출 없음)."""
from skilleval.drivers.fake import FakeDriver
from skilleval.runner import run_one

GOOD_GOAL = """# Goal: x

## Objective
[합의] 1·2·3·4 적용
## Deliverable
스킬 7개
## Requirements
R1 [합의] 미니멀, 한눈에, 중복 없이
## Constraints
C1 [가정] 커밋은 요청 시
## Out of scope
분석 항목 5, 6, 7
## Evaluation
R1: grep
"""

Q_ROUND = "배경 설명입니다.\n\n❓ **Q1** - **범위**: 1~4만 할까요?\n\n➡️ 네, 1~4만.\n\n---\n\n❓ **Q2** - **조건**: 지켜야 할 조건이 있나요?\n\n➡️ 미니멀하게."
CONFIRM = "정리했습니다. 이대로 마무리할까요?"
DONE = "Define을 닫았습니다. 다음 단계는 요청하실 때 시작합니다."


def write(path, content):
    return {"name": "write", "args": {"path": path, "content": content}, "result": "ok"}


def goal_v(i, extra=""):
    return GOOD_GOAL + f"\n<!-- v{i} -->\n{extra}"


def good_script(goal_path=".goal/fix/goal.md"):
    """질문 라운드 → 질문 라운드 → 마무리 확인 → 질문 없음 = 종료(a)"""
    return [
        {"steps": [{"text": "", "tools": [{"name": "read", "args": {"path": "notes/x.md"}}]},
                   {"text": Q_ROUND, "tools": [write(goal_path, goal_v(1))]}, {"text": "goal.md에 적었습니다."}]},
        {"steps": [{"text": Q_ROUND.replace("Q1", "Q3").replace("Q2", "Q4"), "tools": [write(goal_path, goal_v(2))]}]},
        {"steps": [{"text": CONFIRM, "tools": [write(goal_path, goal_v(3))]}]},
        {"steps": [{"text": DONE}]},
    ]


def classify_by_text(dialogue, last):
    """시험용 모의 사용자 분류: 문장 모양만 본다."""
    if "마무리할까요" in last:
        return {"items": [], "confirm_requested": True, "next_step_asked": False}
    if "❓" in last or "?" in last:
        return {"items": [{"label": "Q1", "type": "fact", "fact_ids": ["U3"]},
                          {"label": "Q2", "type": "unknown", "fact_ids": []}],
                "confirm_requested": False, "next_step_asked": False}
    return {"items": [], "confirm_requested": False, "next_step_asked": False}


def make_run(cfg, suite, task, out_dir, script, arm="skill", rep=1, classify=classify_by_text, mock_policy="llm"):
    res = run_one(cfg, suite, task, arm, rep, out_dir, lambda: FakeDriver(script), mock_policy=mock_policy,
                  classify=classify)
    return out_dir / "runs" / res["run"], res
