# Goal: workflow 스킬 수정 (2026-10-20 분석 항목 1·2·3·4)

작성: 2026-10-20, Round 3 반영. Define 종료(frontier 비어 있음, 사용자 확인). Plan에서 Evaluation 절 추가
표기: [합의] 사용자 확정 / [사실] 확인된 환경

## Objective

[합의] 2026-10-20 분석의 개선 포인트 1·2·3·4를 `.agents/skills/workflow-*`에 적용한다.
  1. 종료 조건이 없는 스킬에 체크 가능한 종료 조건 한 줄
  2. goal.md에 Out of scope 항목
  3. 반복 문단 두 개(`.goal/<goal>/` 규칙, "다른 단계는 사용자가 요청할 때만")를 한 곳으로
  4. -eval 스킬(define-eval, plan-eval)을 기존 과정 스킬과 합침. 스킬과 산출물 둘 다

끝 모양
  스킬 7개: analysis, define, plan, execute, verify, review, grill
  산출물 2개: goal.md(Out of scope, 평가 기준 섹션 포함), plan.md(점검 기준 섹션 포함)

## Requirements

R1 종료 조건
  [합의] 대상: analysis, execute, define의 평가 부분, plan의 점검 부분
  [합의] 형태: 스킬 끝에 "~이면 끝" 한 줄. 에이전트가 스스로 판별 가능
  [사실] workflow-grill(frontier 비면 끝), review(Accept/Revise/Explore), verify(PASS/FAIL/UNKNOWN)는 이미 있음
R2 Out of scope
  [합의] goal.md의 네 번째 항목. define 스킬의 질문 대상 목록(Objective/Requirements/Constraints)에 추가
R3 단일 출처
  [합의] 두 문단은 AGENTS.md로 옮긴다. "다른 단계는 사용자가 요청할 때만"은 Principles에, `.goal/<goal>/` 규칙은 작업 문서 규칙으로
  [합의] 옮긴 뒤 모든 스킬에서 해당 문단 삭제
  [합의] AGENTS.md에 붙는 문단은 기존 파일과 같이 영어로 쓴다
  [합의] AGENTS.md 말미의 오타("evidence.v O")는 이번 편집에서 함께 지운다
R4 합치기
  [합의] define-eval은 define-goal에, plan-eval은 plan-process에 합친다
  [합의] 합쳐진 스킬 이름은 workflow-define, workflow-plan. 폴더와 `.claude/skills/` 심링크를 함께 옮긴다
  [합의] define-eval·plan-eval 폴더와 심링크 삭제. 스킬 9개에서 7개로
  [합의] 산출물: goal-eval.md는 goal.md 안의 평가 기준 섹션으로, process-eval.md는 plan.md 안의 점검 기준 섹션으로. process.md는 plan.md로 이름 변경
  [합의] 산출물 파일명이 바뀌므로 읽는 쪽의 참조를 고친다
  [사실] 현재 goal-eval.md를 읽는 스킬: plan-process, verify. process-eval.md를 읽는 스킬: execute. process.md를 읽는 스킬: plan-eval, execute

## Constraints

C1 [합의, 10/20 메모] 미니멀 변경. 중복 없이 한눈에
  [합의] "길어지지 않게"의 기준: 합친 스킬은 두 원본의 합보다 짧다. 개별 줄 수 상한은 없음
  [사실] 현재 줄 수: define-goal 22 + define-eval 25 = 47, plan-process 26 + plan-eval 24 = 50
C2 [합의] workflow-grill 본문은 Matt 원문 그대로 유지(CREDITS.md 조건)
C3 [합의] 수정 파일 범위: `.agents/skills/` 안과 AGENTS.md. `.claude/skills/` 심링크는 폴더 변경에 따라 정리
C4 [사실] `.claude/skills/*`는 `.agents/skills/*` 심링크. 실제 파일은 한 벌
C5 [사실] 10/20 grill 분리는 커밋됨(9fa2b04). 작업 트리에 미커밋 변경 없음
C6 [합의] 커밋은 사용자가 요청할 때만 한다

## Out of scope

- 분석 항목 5(호출 방식), 6(no-op 가지치기), 7(행동 단어, execute frontier, retro, analysis 산출물)
- 10/19 Pi 비교 평가 환경(workflow-skill-eval). 보류 유지
- workflow-grill 본문 수정
- 해결 방법의 구체 문구(섹션 이름, 종료 조건 문장, AGENTS.md 문구). Plan에서 정함

## Evaluation

R1 종료 조건
  Criteria: analysis, define, plan, execute의 SKILL.md에 "~이면 끝" 문장이 각 1개
  Method: grep "적히면 끝" .agents/skills/*/SKILL.md (문장이 모두 "~적히면 끝"으로 끝남. Execute 중 측정 문자열 정정)
  Evidence: 4건, 파일마다 1건
R2 Out of scope
  Criteria: workflow-define SKILL.md의 goal.md 항목 목록과 질문 대상 목록에 Out of scope가 있음
  Method: 파일 읽기
  Evidence: 해당 줄 인용
R3 단일 출처
  Criteria: AGENTS.md에 두 문단이 있고, 스킬 7개 어디에도 `.goal/<goal>/` 규칙과 "다른 단계는 사용자가 요청할 때만"이 없음. 말미 오타 없음
  Method: grep ".goal/<goal>" 와 grep "다른 단계는" 을 AGENTS.md와 .agents/skills에 각각
  Evidence: AGENTS.md 각 1건, 스킬 0건
R4 합치기
  Criteria: .agents/skills에 폴더 7개(analysis, define, plan, execute, verify, review, grill)만 있음. .claude/skills 심링크 7개가 모두 해석됨. 스킬 어디에도 goal-eval.md, process-eval.md, process.md 참조 없음. define이 Evaluation을 쓰고 verify가 그것을 읽음. plan이 Checks를 쓰고 execute가 그것을 읽음
  Method: ls, readlink -f, grep
  Evidence: 명령 출력
C1 길이
  Criteria: workflow-define < 47줄, workflow-plan < 50줄
  Method: wc -l
  Evidence: 줄 수
C2 grill 불변
  Criteria: workflow-grill/SKILL.md와 CREDITS.md에 변경 없음
  Method: git diff --stat
  Evidence: 출력 0건
C3 수정 파일 범위: 평가 불필요. git status로 R3·R4 증거에서 함께 드러남
C4, C5: 사실이라 평가 불필요
C6 커밋: 평가 불필요. 요청 전까지 커밋하지 않는 것은 Execute 행동 규칙
추가 증거(선택, Verify에서 결정): 새 define 스킬을 작은 목표에 한 번 돌려 Define이 한 라운드에 끝나지 않는지 본다

## 결정 기록

- R1-Q1 산출물까지 합침, 읽는 쪽 참조 수정 포함 (추천 수락)
- R1-Q2 합친 스킬은 두 원본 합보다 짧게, 개별 상한 없음 (추천 수락)
- R1-Q3 단일 출처는 AGENTS.md (추천 수락)
- R1-Q4 폴더명 `.goal/workflow-skill-fix/` (추천 수락)
- R2-Q5 스킬 이름 workflow-define, workflow-plan (추천 수락). 가정 셋(영어, 오타, 커밋) 이의 없음
- R3-Q6 Plan 산출물은 plan.md (사용자 제안, 수락)
