# Plan: workflow 스킬 개선

입력: goal.md(2026-10-25 Define 종료본, 커밋 `9b5eb6c`)
작성: 2026-10-25, Round 2 반영. Plan 종료(frontier 비어 있음, 작업마다 Checks가 적힘)
표기: [합의 Qn] / [미결정 Qn] / [가정] / [사실]

## Strategy

- [합의 Q1] 지금 plan 스킬대로 이 plan.md에 Strategy, Decomposition, Responsibility, Checks를 쓰고 질문 Round로 정한다. 새 방식(tickets/ 카드)은 흉내 내지 않는다
- [합의 Q2] 만드는 방법
  - Matt 원문 기반 파일(workflow-plan, workflow-execute, tdd `SKILL.md`)은 조립 스크립트로 만든다. 문장 지도의 "그대로" 문장은 원본에서 잘라 오고, 바꾸는 곳은 원래 구절이 정확히 한 번 있는지 확인(assert)한 뒤 바꾼다
  - 복사 파일 5개는 그대로 복사한다
  - 한국어 스킬(analysis, define, verify)과 AGENTS.md는 문장 지도대로 직접 고친다
  - 모두 이 세션(main)이 직접 한다. subagent는 쓰지 않는다
- [합의 Q3] Execute의 작업별 Checks는 만든 직후의 기계 점검이다(스크립트 확인 통과, frontmatter가 읽힘, `.claude/skills/`로 보임, 복사 파일 diff 없음, commit 범위). 원문 문장별 대조표(goal.md C5)는 Verify에서만 만든다
- [합의 Q4] 파일을 다 만든 뒤 사용자 검토 작업(HITL) 하나를 둔다. goal.md C4의 "한눈에 읽힌다" 확인을 여기서 받는다
- [합의 Q5] 작업 하나가 끝날 때마다 그 작업의 파일만 commit한다. 메시지는 `execute(workflow-skill-fix-3): NN 제목`. 사용자 검토에서 고친 것은 따로 commit한다
- [합의 Q6] 별도 시험 키트는 만들지 않는다. Execute 보고에 두 가지를 적는다. 다른 세션이 새 스킬을 보려면 할 일, 판정할 때 알려 줄 것(goal 폴더 경로, 세션 기록 위치)

[사실] 만들 것은 goal.md Deliverable의 문장 지도 7개(D-plan, D-execute, D-tdd, D-analysis, D-define, D-verify, D-agents)와, 그대로 복사할 파일 5개(tdd `tests.md`·`mocking.md`, codebase-design `SKILL.md`·`DEEPENING.md`·`DESIGN-IT-TWICE.md`)다. 파일끼리 겹치지 않는다.
[사실] `.claude`는 `.agents`의 심링크라서, `.agents/skills/`에 새 폴더를 만들면 `.claude/skills/`에서도 보인다.

## Decomposition

[합의 Q7]

| 작업 | 하는 일 | 파일 | 의존 |
|---|---|---|---|
| 01 tdd 가져오기 | `tests.md`, `mocking.md` 복사. `SKILL.md`는 D-tdd(T1 바꿈, T3 빼기, T4 괄호 빼기)대로 조립 | `.agents/skills/tdd/SKILL.md`, `tests.md`, `mocking.md` | 없음 |
| 02 codebase-design 가져오기 | 세 파일 복사, 수정 없음 | `.agents/skills/codebase-design/SKILL.md`, `DEEPENING.md`, `DESIGN-IT-TWICE.md` | 없음 |
| 03 workflow-plan 다시 쓰기 | D-plan대로 조립(지금 한국어 파일을 바꿔치움) | `.agents/skills/workflow-plan/SKILL.md` | 없음 |
| 04 workflow-execute 다시 쓰기 | D-execute대로 조립 | `.agents/skills/workflow-execute/SKILL.md` | 없음 |
| 05 한국어 스킬 고치기 | D-analysis(A1), D-define(F1~F4), D-verify(V1~V3) | `.agents/skills/workflow-analysis/SKILL.md`, `workflow-define/SKILL.md`, `workflow-verify/SKILL.md` | 없음 |
| 06 AGENTS.md 고치기 | D-agents(G1, G2 Commits 절) | `AGENTS.md` | 없음 |
| 07 사용자 검토 | 바뀐 파일 전부를 사용자가 읽고 승인하거나 고칠 곳을 말한다. 고친 것은 따로 commit | 고칠 곳이 나온 파일 | 01~06 |

순서는 01 → 06 → 07이다. 01~06은 서로 막지 않지만, 한 세션에서 차례로 한다(Q2).

## Responsibility

[합의 Q7]
- AI(main): 01~06, 07의 고치기
- Collaborative: 07. AI가 바뀐 파일과 요약을 보여 주고, 사용자가 읽고 판단한다
- Verify(이 Plan 밖): 사용자가 다른 세션에서 새 흐름으로 목표 하나를 돌리고, AI가 그 기록으로 판정한다

## Checks

[합의 Q8] 모든 작업에 공통으로 "commit 직후 `git show --stat HEAD`에 그 작업의 파일만 있음"을 점검한다.

| 작업 | Criteria (실행 중 만족할 조건) | Method (방법, 시점) |
|---|---|---|
| 01 | ① 조립 스크립트의 assert가 모두 통과(바꾸거나 빼는 원문 구절이 각각 정확히 한 번) ② `tests.md`, `mocking.md`가 원본과 diff 없음 ③ `SKILL.md` frontmatter가 읽히고 `name: tdd` ④ `.claude/skills/tdd/SKILL.md`가 같은 파일 | 스크립트 출력, `diff`, frontmatter 파싱, 경로 확인. 01 직후 |
| 02 | ① 세 파일이 원본과 diff 없음 ② `.claude/skills/codebase-design/`로 보임 | `diff`, 경로 확인. 02 직후 |
| 03 | ① 조립 스크립트의 assert가 모두 통과 ② frontmatter가 읽히고 `name: workflow-plan`, `disable-model-invocation: true` ③ `.claude/skills/workflow-plan/SKILL.md`가 같은 파일 | 스크립트 출력, frontmatter 파싱. 03 직후 |
| 04 | ① 조립 스크립트의 assert가 모두 통과 ② frontmatter가 읽히고 `name: workflow-execute`, `disable-model-invocation: true` | 스크립트 출력, frontmatter 파싱. 04 직후 |
| 05 | ① `git diff`가 세 파일뿐이고, 고친 곳의 수가 문장 지도 행 수와 같음(analysis 1, define 4, verify 3) ② 세 파일의 frontmatter가 그대로 읽힘 | `git diff`, frontmatter 파싱. 05 직후 |
| 06 | ① `git diff`가 추가만 있고(기존 줄 그대로) 추가가 G1, G2 두 곳 ② commit 규칙 문구(`git add`, `-A`)가 `.agents/skills/` 아래 다른 파일에 없음(C4). [사실] workflow-handoff에는 중단 때 쓰는 wip commit 문장("`git add <files>`, never `-A`")이 이미 있다. 이건 범위 밖 스킬의 다른 규칙이라 점검에서 뺀다 | `git diff`, `grep`. 06 직후 |
| 07 | 사용자의 승인, 또는 고칠 목록과 그 처리가 이 plan.md에 적힘. 고친 것은 별도 commit | 사용자 답. 06 뒤 |

## Execute 기록 (2026-10-25)

| 작업 | 상태 | Checks 결과 |
|---|---|---|
| 01 tdd 가져오기 | 완료. 커밋 `b46f2d5` | ① PASS: 조립 스크립트 assert 3/3(T1, T3, T4의 원문 구절이 각각 정확히 한 번) ② PASS: `tests.md`, `mocking.md`가 원본과 diff 없음 ③ PASS: frontmatter가 YAML로 읽힘, `name: tdd` ④ PASS: `.claude/skills/tdd/`로 읽힘. 커밋 파일 3개뿐 |
| 02 codebase-design 가져오기 | 완료. 커밋 `eb95ff2` | ① PASS: 세 파일이 원본과 diff 없음(`.claude/skills/` 경로로 비교) ② PASS. 커밋 파일 3개뿐 |
| 03 workflow-plan 다시 쓰기 | 완료. 커밋 `0e77dd8` | ① PASS: assert 21/21 ② PASS: frontmatter `name: workflow-plan`, `disable-model-invocation: true` ③ PASS: `.claude/skills/`로 읽힘. 커밋 파일 1개뿐 |
| 04 workflow-execute 다시 쓰기 | 완료. 커밋 `be63d38` | ① PASS: assert 19/19 ② PASS: frontmatter `name: workflow-execute`, `disable-model-invocation: true`. 커밋 파일 1개뿐 |
| 05 한국어 스킬 고치기 | 완료. 커밋 `89047a7` | ① PASS: 고친 곳이 analysis 1, define 4(F1·F2는 한 덩어리 두 줄, F3, F4), verify 3(V1·V2 두 줄, V3)으로 지도와 같음. `git diff --stat`에 보인 `.goal/workflow-handoff/plan.md`는 이 세션 전부터 있던 다른 세션의 변경이라 제외 ② PASS: 세 파일 frontmatter가 읽힘. 커밋 파일 3개뿐 |
| 06 AGENTS.md 고치기 | 완료. 커밋 `01a13c8` | ① PASS: 추가 7줄, 삭제 0줄, G1과 G2 두 곳 ② PASS: `git add`, ``never `-A` ``, "Do not commit mid-Round" 문구가 workflow-handoff를 빼면 `.agents/skills/` 아래에 없음. 커밋 파일 1개뿐 |
| 07 사용자 검토 | 미완. 사용자가 "한눈에 읽히는지는 새로운 goal로 다시 검토해서 진행하겠다"고 함 | 승인도 고칠 목록도 없음. goal.md C4의 "사용자 검토" 부분은 이번 Verify에서 UNKNOWN(새 goal 대기)이 된다. 검토 때 볼 만한 곳으로 네 가지를 짚어 두었다. ① workflow-plan 65~67줄에 "Write"가 연달아 나옴 ② 템플릿 태그가 `<local-ticket-template>` 그대로 ③ workflow-execute에 `#` 제목이 없음 ④ 영어 스킬과 한국어 스킬이 섞임 |
