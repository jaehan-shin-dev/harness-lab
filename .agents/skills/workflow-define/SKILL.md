---
name: workflow-define
description: workflow-grill로 사용자를 인터뷰해 목표를 Objective, Deliverable, Requirements, Constraints, Out of scope로 구체화하고 항목별 평가 기준(Evaluation)까지 goal.md에 작성한다. Define 단계에 사용한다.
---

# Define

`workflow-grill` 스킬을 로드해, 사용자가 제공한 목표·현재 상황·조건에서 출발해 인터뷰하고,
결과를 goal.md에 나열식·계층적으로 기록한다.

- Objective: 궁극적으로 달성하려는 상태
- Deliverable: 완성됐을 때 산출물이 어떤 모습인지. 읽는 사람이 이상한 점을 알아볼 수 있는 해상도로
- Requirements: 목표 달성을 위해 만족해야 하는 조건
- Constraints: 목표 달성 과정에서 지켜야 하는 제약
- Out of scope: 이번 목표에서 하지 않기로 한 것
- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유

tree는 Deliverable까지 내려간다. 만드는 순서와 방법만 Plan에서 정한다. 위 여섯 항목의 미결정이 질문 대상이며,
Requirement나 Constraint가 정해지면 "어떻게 확인하나"가 그 자식 질문으로 frontier에 오른다.
Round마다 goal.md를 갱신하고, 합의·미결정·가정을 구분해 적는다.

실제 검증은 Verify에서 진행한다.
frontier가 비고, Requirements와 Constraints 항목마다 Evaluation 항목이나 "평가 불필요"와 그 이유가 적히면 끝.
