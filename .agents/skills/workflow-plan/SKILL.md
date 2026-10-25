---
name: workflow-plan
description: goal.md를 바탕으로 전략, 작업 분해, 역할과 작업별 점검 기준(Checks)을 plan.md에 설계한다. Plan 단계에 사용한다.
---

# Plan

goal.md를 기반으로 plan.md를 작성한다.

- Strategy: 목표 달성을 위한 접근 방식
- Decomposition: 실행 가능한 작업과 의존관계
- Responsibility: AI / User / Collaborative 역할 구분
- Checks: 작업마다 Criteria(실행 과정에서 만족해야 할 조건), Method(점검 방법과 시점). 점검이 불필요한 작업은 그 이유

설계 결정은 `workflow-grill` 스킬을 로드해 Round로 묻고, Round마다 plan.md를 갱신한다.
작업이 정해지면 "어떻게 점검하나"가 그 자식 질문으로 frontier에 오른다.
설계 중 드러난 목표 수준의 결정은 사용자와 확인해 goal.md에 반영한다.
goal.md가 없거나 필요한 내용이 부족하면 사용자에게 확인한다.

실제 작업은 Execute에서, 최종 평가는 Verify에서 진행한다.
frontier가 비고, 작업마다 Checks 항목이나 "점검 불필요"와 그 이유가 적히면 끝.
