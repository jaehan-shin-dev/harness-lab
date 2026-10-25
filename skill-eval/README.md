# skill-eval

workflow 스킬을 고친 뒤 "행동이 실제로 바뀌었는지(과정)"와 "나온 goal.md가 좋은지(결과)"를 pi로 돌려서 보는 환경.
목표와 계획: `../.goal/skill-eval/goal.md`, `../.goal/skill-eval/plan.md`

## 준비

```bash
cd skill-eval
uv sync                         # Python 3.12 이상 + pyyaml, pytest
pi auth check --provider openai-codex --json --no-refresh   # 출입증 확인 (메인 ~/.pi/agent)
```

출입증 남은 시간이 `config.yaml`의 `auth.min_hours_left`보다 적으면 실행이 멈춘다. 메인에서 갱신한다:
`pi auth print-bearer-token --provider openai-codex --min-expiry 420m > /dev/null`

## 명령

```bash
# 전체 실행: 과제 3 × 팔 2 × 3회 = 18회, 끝나면 results/<오늘 날짜>/report.md
uv run skilleval run workflow-define
# 로그를 결과 폴더에 남기며 (T16에서 쓴 방식, 약 1시간·$4)
mkdir -p results/t16 && uv run skilleval run workflow-define --out t16 >> results/t16/run.log 2>&1

# 일부만 / 이름 붙인 결과 폴더 / 동시 실행
uv run skilleval run workflow-define --tasks workflow-skill-fix --arms skill --reps 1 --out m1
uv run skilleval run workflow-define --out 2026-10-22 --jobs 2   # 동시 실행은 옆 회차의 모의 사용자 기록이 잠깐 보일 수 있어 T16은 jobs 1

# 같은 --out으로 다시 부르면 scores.json이 있는 회차는 건너뛰고 남은 회차만 돈다(실패 회차는 다시 돈다)

# 저장된 결과만 다시 판정 (심판: cached=저장된 것 재사용, skip=안 부름, fresh=다시 호출)
uv run skilleval grade workflow-define --out m1 --judge cached

# goal.md 파일 하나의 회수율만
uv run skilleval grade workflow-define --task workflow-skill-fix --goal tests/fixtures/goals/workflow-skill-fix.correct.md

# 준비 단계만: 작업 폴더 파일 목록과 실행 전 가방 검사를 보여 주고 지운다
uv run skilleval run workflow-define --prepare-only --tasks workflow-skill-fix

# 라운드 상한 시험: 항상 "모르겠다"만 하는 가짜 사용자
uv run skilleval run workflow-define --tasks workflow-skill-fix --arms skill --reps 1 --mock always-unknown --out cap

# 환경 자체 검사 (pi 호출 없음)
uv run pytest -q
```

## 한 회차가 도는 방식

1. 준비: `$TMPDIR/<16진수>/`에 작업 폴더(프로젝트 모양 이름)와 pi 설정 폴더를 만든다.
   설정 폴더 = 인증 복사본(refresh는 가짜 값) + settings.json(홈 스킬 빼기) + 스킬 팔이면 `../.agents/skills` 전부와 `../AGENTS.md`.
   pi에는 필요한 환경 변수만 넘긴다(`pi_process.clean_env`: PATH에서 pi-lab·.venv를 빼고, 이 도구의 세션 변수는 안 넘김).
2. 가방 검사: 답변표 파일 없음, `skill-eval` 글자 0건, 경로·러너가 넣은 이름·시작 요청·pi에 넘기는 환경 변수에 금지 단어 0건, git 1커밋.
3. 대화: 후보 pi를 `--session-id`로 턴마다 다시 부른다. 턴이 끝날 때마다 goal.md를 찾아 `rounds/`에 복사한다.
   모의 사용자(pi, 도구 없음)는 질문마다 답변표의 어떤 사실로 대답할지만 고르고, 문장은 답변표에서 만든다.
4. 종료: (a) 마무리 확인을 받은 뒤 질문 없는 턴 → 종료 (b) 대답 5번 뒤에도 안 끝남 → 미종료
   (c) 두 턴 연속 질문도 없고 goal.md도 그대로 → 자연 종료
5. 회수와 정리: goal.md(작업 폴더 어디에 있든), 대화 기록을 `results/<날짜>/runs/<과제>__<팔>__r<n>/`에 남기고 임시 폴더를 지운다.
6. 판정: 과정 검사 8개, 회수율(키워드), 누출 검사, LLM 심판(사실별 + 루브릭 5개), 실행 기록 요약.
   누출 검사는 회차 폴더(작업 폴더 + 설정 폴더) 안 읽기는 허용하고 따로 적는다. 그 위·밖 경로, 회차 폴더에 쓰기,
   받아 올 수 있는 명령(curl, pip install, `uv run --with` 등, `--offline`은 제외), 아직 안 들은 사용자 사실은 오염 의심.

## 파일

```
config.yaml                 모델, thinking, 반복 횟수, 라운드 상한, 타임아웃 (설정은 여기 한 곳)
skilleval/
  __main__.py               run, grade
  runner.py                 과제×팔×회 반복, 대화 고리, 종료 규칙, 이어 돌리기
  workspace.py              임시 작업 폴더, 설정 폴더, 인증 복사, 가방 검사, 파일 해시
  mock_user.py              모의 사용자
  trace.py                  실행 기록 요약
  drivers/                  base(인터페이스), pi, fake(시험용), claude_code(자리만)
  graders/                  process(과정 8개), recall(회수율), judge(LLM 심판), leak(누출)
  report.py                 report.md, summary.csv
  grade.py                  회차 하나 판정(scores.json)
  record.py, events.py      회차 폴더 읽기, pi json 사건 풀기
  pi_process.py             pi 프로세스 띄우기(stdin 닫기, 타임아웃, 환경 변수 고르기)
  suite.py, config.py       suite·task·answer YAML, config.yaml 읽기
  llm_json.py               pi로 순수 텍스트 모델을 불러 JSON 하나 받기(모의 사용자·심판 공통)
suites/workflow-define/     suite.yaml(두 팔), rubric.md, tasks/<과제>/{task.yaml, answer.yaml}
tests/                      환경 자체 검사, fixtures/, live/(실제 pi를 부르는 수동 검사)
.cache/                     [git 제외] 받은 저장소
results/<날짜 또는 --out>/   report.md, summary.csv, runs/[git 제외] (m1, m2, t16)
```

## 회차 폴더

| 파일 | 내용 |
|---|---|
| `meta.json` | 모델, pi 버전, 경로, 종료 사유, 라운드 수, 걸린 시간 |
| `preflight.json` | 실행 전 가방 검사 결과 |
| `candidate.jsonl` | 후보 pi json 출력 전체 (턴마다 `_runner` 표지 줄로 나눔, 실행 명령 포함) |
| `mock_user.jsonl` | 모의 사용자 pi json 출력 전체 + 분류 결과 |
| `dialogue.json`, `transcript.md` | 대화 (기계용, 사람용) |
| `rounds/goal.round<n>.md` | 턴마다 goal.md |
| `goal.md`, `fs_changes.json` | 최종 goal.md, 실행 전후 파일 변경 |
| `judge.json`, `judge.jsonl` | 심판 결과와 원본 |
| `scores.json` | 판정 전체 (있으면 끝난 회차) |
