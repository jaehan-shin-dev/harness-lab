# 03: Define의 Evaluation 항목 분리

**What to build:** 사람이 Evaluation 구성과 조건부 지시 두 가지를 구분해 읽도록 기존 문구를 유지한 채 하위 항목으로 나눈다.

**Covers:** R2·R3, C1~C6. R1은 사용자의 Plan 범위 조정으로 제외됐다.

**Blocked by:** None (can start immediately).

**Files:**

- `.agents/skills/workflow-define/SKILL.md`
- `.goal/skill-readability/tickets/03-define-evaluation.md`

**Owner:** main

**Parallel:** no

**Status:** ready

**Checks:**

- [ ] D1의 원문·수정안·이유와 개별 승인 기록이 있다: 아래 변경안·사용자 응답을 대조한다.
- [ ] 실제 수정은 승인된 D1 한 건과 같다: 기준 버전의 전체 파일에서 아래 원문을 수정안으로 한 번 치환한 결과와 최종 파일이 정확히 같은지 확인한다.
- [ ] 문구·조건·의무 수준을 보존했다: bullet·공백을 제외한 전후 문구가 같고 Evaluation 구성과 조건부 지시 두 가지가 구분되는지 확인한다.
- [ ] 다른 스킬·부속 문서와 frontmatter·링크를 보존했다: 기준 버전과 diff, 메타데이터·링크 대조로 확인한다.
- [ ] 다른 작업을 보존하고 대상 파일만 커밋한다: 작업 전후 git status와 staged 파일 목록을 확인한다.

## 변경안 D1

- 대상: `.agents/skills/workflow-define/SKILL.md` 원문 18줄.
- 이유: Evaluation 구성과 두 조건부 지시를 같은 항목 아래에서 시각적으로 나눈다.
- 승인: 사용자가 기존 ticket 03만 진행하도록 요청했다. 이 ticket의 수정안은 D1 한 건이며 이전 제시안과 동일하다.
- 사용자 응답: “ticket3 정도만 진행하고 나머지 수정은 괜찮은 것 같아. 오히려 강조하는 느낌이라. ticket3만 진행해줘.”
- 적용 상태: 미적용.

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

## Check 결과

실행 후 기록한다. 문서 편집이므로 코드 테스트는 추가하지 않으며, 이 기록은 Execute의 Checks다. 독립 Verify는 별도 요청 시 진행한다.
