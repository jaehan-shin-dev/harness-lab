# 확정된 변경안

- 목표: `goal.md`. 기준 버전: `744310a`.
- Plan 결론: 기존 ticket 03·D1 한 건만 진행한다. 식별자를 유지해 사용자 요청과 연결한다.
- 사용자 결정: “ticket3 정도만 진행하고 나머지 수정은 괜찮은 것 같아. 오히려 강조하는 느낌이라. ticket3만 진행해줘.”
- D1 개별 승인: 위 요청으로 승인됐다. 원문·수정안은 이전 제안과 같다.
- 제외: P1·P2·CD1·CD2·T1·E1. 사용자는 다른 반복 설명을 강조로 받아들여 원문 유지를 요청했다. 해당 ticket 파일은 만들지 않는다.
- 적용 상태와 Checks는 `tickets/03-define-evaluation.md`에서 기록한다.

## D1 — ticket 03

- 대상: `.agents/skills/workflow-define/SKILL.md` 원문 18줄.
- 이유: Evaluation 구성과 두 조건부 지시를 같은 항목 아래에서 시각적으로 나눈다.
- 보존 근거: 단어·문장 순서를 그대로 유지하며 줄바꿈과 하위 bullet만 추가한다. 평가 불필요 이유와 코드 목표의 스킬 호출·seam 기재 조건을 보존한다.

원문:

```text
- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유. 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다
```

수정안:

```text
- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거).
  - 평가가 불필요한 항목은 그 이유.
  - 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다
```

