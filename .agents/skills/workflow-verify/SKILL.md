---
name: workflow-verify
description: goal.md의 Evaluation을 기준으로 객관적 증거를 확보하고 PASS, FAIL, UNKNOWN과 미충족 사항을 판단한다. 목표 달성 여부를 검증하는 Verify 작업에 사용한다.
---

# Verify

goal.md의 Evaluation을 기반으로 다음 요소를 중심으로 검증한다.

- Evidence: 평가 기준을 판단할 객관적인 증거 확보
- Assessment: 기준과 증거를 비교하여 PASS / FAIL / UNKNOWN 판단
- Gap: 미충족 사항과 추가 확인이 필요한 사항 식별

판정은 판정용 subagent에게 맡긴다. subagent에게는 goal.md, goal.md Deliverable에 적힌 산출물 경로, Plan 끝 commit 이후의 git 기록만 넘기고, ticket 파일(Execute의 완료 기록)은 넘기지 않는다.
결과는 `.goal/<goal>/verify.md`에 쓰고, 판정 방식(누가, 무엇을 받아 판정했는지)을 함께 적는다.

Agent의 완료 주장은 충분한 증거가 아니다.
실제 실행 결과나 관찰 근거를 확보하고, 각 판단의 근거를 명확하게 제시한다.
증거가 부족하거나 확인할 수 없는 항목은 UNKNOWN으로 표시한다.
goal.md에 Evaluation이 없거나 기준이 불명확하면 사용자에게 확인한다.

미충족 사항은 적절한 단계에서 다시 다룰 수 있도록 정리한다.
Evaluation 항목마다 PASS, FAIL, UNKNOWN과 그 근거가 verify.md에 적히면 끝.
