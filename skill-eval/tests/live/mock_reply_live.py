"""T5: 대답 규칙을 짧은 가짜 후보 메시지 3개로 실제 호출해 본다. 사용: uv run python tests/live/mock_reply_live.py <기록 폴더>"""
import json, sys
from pathlib import Path
from skilleval.config import load_config
from skilleval.suite import load_suite
from skilleval.mock_user import MockUser
from skilleval.workspace import make_llm_dirs, cleanup_dirs
from types import SimpleNamespace

cfg = load_config()
task = load_suite("workflow-define").task("workflow-skill-fix")
out = Path(sys.argv[1])
dirs = make_llm_dirs(cfg)
paths = SimpleNamespace(mock_cwd=dirs["cwd"], mock_agent_dir=dirs["agent"], mock_base=dirs["base"])
log = lambda r: open(out / "mock_t5.jsonl", "a").write(json.dumps(r, ensure_ascii=False) + "\n")
start = {"role": "user", "n": 0, "kind": "start", "text": task.start_request}
cases = {
  "questions": "goal.md 초안을 썼습니다.\n\n❓ **Q1** - **지켜야 할 조건**: 스킬을 고칠 때 지켜야 할 조건이나 선호가 있나요? 예를 들어 길이나 문체.\n\n➡️ 지금 길이를 크게 늘리지 않기.\n\n---\n\n❓ **Q2** - **목표 폴더명**: `.goal/workflow-skill-fix/`로 할까요?\n\n➡️ 네.\n\n---\n\n❓ **Q3** - **현재 줄 수**: 지금 define-goal과 define-eval은 몇 줄인가요?\n\n➡️ 모르겠어요.\n\n---\n\n❓ **Q4** - **합친 이름**: 합친 스킬 이름을 workflow-define, workflow-plan으로 줄일까요?\n\n➡️ 네, 줄입니다.",
  "confirm": "Q1~Q4 답을 반영해 goal.md를 정리했습니다. frontier가 비었습니다. 이대로 Define을 마무리해도 될까요?",
  "progress": "goal.md의 Evaluation 절을 채우는 중입니다. 다음 턴에 결과를 보여 드리겠습니다.",
}
try:
    m = MockUser(cfg, task.answer, paths, log)
    for k, txt in cases.items():
        dia = [start, {"role": "assistant", "n": 1, "text": txt}]
        r = m.reply(dia, txt)
        print(f"== {k}: kind={r.kind} revealed={r.revealed_fact_ids} accepted={r.accepted_ids} findable={r.findable_ids} fixes={r.fixes} {r.call.get('duration_s')}s")
        print(r.text)
finally:
    cleanup_dirs(dirs)
    print("dirs removed:", not dirs["base"].exists())
