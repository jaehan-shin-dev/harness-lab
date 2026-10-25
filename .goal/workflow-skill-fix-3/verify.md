# Verify: workflow 스킬 개선 (1차, 정적 판정)

작성: 2026-10-25. 기준: `goal.md` Evaluation(R1~R5, C1~C5).
상태: 1차 판정이다. 실행 기록(사용자가 다른 세션에서 새 workflow로 목표 하나를 돌린 기록)은 아직 받지 못했다. 받으면 실행 쪽 판정을 채워 이 파일을 갱신한다.

## 판정 방식

- 판정자: 판정용 subagent(Claude Code Agent 도구, general-purpose). 이전 맥락이 없는 새 컨텍스트에서 판정했다. main 세션은 결과를 받아 이 파일로 옮겼고, F3 불일치 한 건만 직접 다시 확인했다.
- 넘긴 것
  - `goal.md`
  - Deliverable의 산출물 경로(스킬 파일 12개와 `AGENTS.md`)와 goal.md가 가리키는 Matt 원문
  - Plan 끝 커밋 `bd29585` 이후의 git 기록(`git log --stat`, 산출물 경로로 좁힌 `git diff`, 변경 전 판 `git show bd29585:<경로>`)
- 넘기지 않은 것: `plan.md`(Execute 완료 기록), `handoff.md`, `analysis.md`, 다른 `.goal/` 폴더. 판정자는 `git log --stat`에 plan.md 파일 이름이 나오는 것만 보았다.
- 사용자에게서 받아 넘긴 사실
  - 실행 기록은 아직 없다
  - C4의 사용자 검토는 새 goal에서 한다(Execute 07에서 사용자가 말함)
- 문장 대조표: `c5-table.md`(판정자가 씀)

## 판정

| 항목 | 정적 | 실행 / 사용자 검토 | 종합 |
|---|---|---|---|
| R1 산출물 | 해당 없음 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| R2 goal/plan 구분 | PASS. `workflow-define/SKILL.md:20`에 F4 경계 문장, `workflow-plan/SKILL.md:15`에 N1("Do not interview the user. … return to Define …"), `workflow-execute/SKILL.md:40`에 N6이 있다. `grep -in grill workflow-plan/SKILL.md` 결과는 0건 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| R3 commit | 해당 없음 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| R4 독립 Verify | 해당 없음 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| R5 subagent | 해당 없음 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| C1 goal의 Evaluation | PASS. `workflow-define/SKILL.md:18` Evaluation 항목과 `:25` 끝 조건("항목마다 Evaluation 항목이나 '평가 불필요'와 그 이유")이 그대로 있다 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| C2 ticket check | 해당 없음 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| C3 하네스 | 해당 없음 | UNKNOWN: 사용자 실행 기록 대기 | UNKNOWN |
| C4 미니멀·중복 없음 | PASS. commit 규칙(언제, 어떻게, Round 중간 금지, git 저장소가 아닐 때, 메시지 형식)은 `AGENTS.md:24-27`에만 있다. execute에는 누가만 있다(`:17`, `:32`, `:34`). 아래 Gap 4의 handoff 문장은 범위 밖 스킬이다 | UNKNOWN: 사용자 검토는 새 goal에서 | UNKNOWN |
| C5 Matt 원문 | FAIL. 불일치 1건: D-define F3 끝의 마침표. 나머지 행은 모두 글자까지 일치한다 | 해당 없음 | FAIL |

## C5 요약 (상세: `c5-table.md`)

| 파일 | 일치 | 불일치 | 지도에 없는 문장 |
|---|---|---|---|
| workflow-plan (D-plan) | 42 | 0 | 없음 |
| workflow-execute (D-execute) | 29 | 0 | 없음 |
| tdd SKILL.md (D-tdd) | 8 | 0 | 없음 |
| workflow-analysis (D-analysis) | 3 | 0 | 없음 |
| workflow-define (D-define) | 7 | 1 | 없음 |
| workflow-verify (D-verify) | 5 | 0 | 없음 |
| AGENTS.md (D-agents) | 4 | 0 | 없음 |

- tdd `tests.md`, `mocking.md`와 codebase-design 세 파일은 원문과 diff가 없다(sha256 같음). `agents/openai.yaml`은 두 폴더 모두 없다(지도대로).
- 지도 순서대로 기대 파일 전체를 다시 만들어 비교했다. 7개 중 6개는 diff가 비어 있고, define은 F3 한 줄에서만 차이가 난다.
- 불일치 F3
  - goal.md 결과 문장은 "…seam(공개 인터페이스)을 그 용어로 적는다."이다
  - `workflow-define/SKILL.md:18`은 "…그 용어로 적는다"로 끝나 마침표가 없다. main이 직접 다시 확인했다
  - 같은 파일의 다른 Evaluation 목록 줄은 마침표 없이 끝나는 형식이라, 지도의 마침표를 문장 부호로 볼지 형식 차이로 볼지가 갈릴 수 있다. 판정은 C5 기준("새 문장은 goal.md의 결과 문장과 같음")을 글자대로 적용했다

## Gap (미충족과 추가 확인)

1. **C5 FAIL: F3 마침표 1자.** 다룰 단계는 Execute다. `workflow-define/SKILL.md:18` 끝에 마침표를 붙이고 따로 커밋한 뒤 C5 대조만 다시 돌리면 된다. 마침표를 붙일지, 지도 쪽을 고칠지는 사용자가 정한다.
2. **실행 기록 대기:** R1, R2(실행), R3, R4, R5, C1(실행), C2, C3. 다룰 단계는 Verify 재판정이다. 사용자가 다른 세션에서 새 workflow로 목표 하나를 끝까지 돌린 뒤 알려 줄 것은 세 가지다.
   - 그 goal 폴더
   - 세션 기록 위치
   - 쓴 하네스
3. **C4의 사용자 검토:** 사용자가 새 goal에서 하기로 했다. 그 goal에서 볼 만한 곳은 plan.md Execute 기록 07에 적어 두었다.
4. **범위 밖과 C4의 긴장(참고):** 스테이징 규칙 문장이 두 곳에 있다. `workflow-handoff/SKILL.md:14`("staging only the files you changed (`git add <files>`, never `-A`)")와 `AGENTS.md:25`("Stage only the files that phase changed (`git add <files>`, never `-A`)")다. handoff 쪽은 중단 때 쓰는 wip 커밋 규칙이고, 이번 goal의 Out of scope(handoff 수정 안 함)라 손대지 않았다. 합칠지는 새 goal에서 정할 수 있다.
