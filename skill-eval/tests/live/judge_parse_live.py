"""T11: 심판을 실제로 3번 불러 파싱과 팔 이름 노출을 본다. 사용: uv run python tests/live/judge_parse_live.py <회차 폴더> <기록 폴더>"""
import json, sys, re
from pathlib import Path
from skilleval.config import load_config
from skilleval.suite import load_suite
from skilleval.graders.judge import run_judge, build_message
from skilleval.record import load_run
from skilleval.grade import judge_dialogue

cfg = load_config()
suite = load_suite("workflow-define")
run_dir = Path(sys.argv[1]); out = Path(sys.argv[2])
r = load_run(run_dir)
task = suite.task(r.meta["task"])
rubric = (suite.dir / "rubric.md").read_text()
msg = build_message(task.answer, r.goal_text or "", judge_dialogue(r, task), rubric)
arm_words = [w for w in ["skill arm", "control", "스킬 팔", "대조 팔", r.meta["arm"] + "__", "__skill", "__control"] if w in msg]
print("심판 입력에 팔 이름:", arm_words or "0건", "| 입력 길이", len(msg))
log = lambda rec: open(out / "judge_t11.jsonl", "a").write(json.dumps(rec, ensure_ascii=False) + "\n")
for i in range(3):
    try:
        j = run_judge(cfg, task.answer, r.goal_text or "", judge_dialogue(r, task), rubric, log)
        print(f"호출 {i+1}: 파싱 성공 (시도 {j['call']['attempt']}), 사실 {sum(v['captured'] for v in j['facts'].values())}/{len(j['facts'])}, 루브릭 {j['rubric_total']}/10",
              {k: v['score'] for k, v in j['rubric'].items()})
    except Exception as ex:
        print(f"호출 {i+1}: 실패 {ex}")
