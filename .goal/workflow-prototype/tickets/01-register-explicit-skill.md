# 01: 사용자 직접 호출 전용 스킬 등록

**What to build:** 사용자가 `workflow-prototype`을 명시적으로 호출해 사용할 수 있도록 확정된 지시문과 호출 정책을 함께 등록한다. 질문·제작·관찰·사용자 판단·보고·보관 규칙을 승인 문구대로 제공하고, 원문에서 채택한 규칙과 로컬 조정 이유를 추적할 수 있게 한다.

**Covers:** O1, D1, D2, D3, R1, R2, R3, R4, C1, C2, C3, C4, C5, C6.

**Blocked by:** None (can start immediately).

**Files:**

- `.agents/skills/workflow-prototype/SKILL.md`
- `.agents/skills/workflow-prototype/agents/openai.yaml`
- `.goal/workflow-prototype/source-map.md`
- `.goal/workflow-prototype/tickets/01-register-explicit-skill.md` — 실행 시 상태와 Checks 기록만 갱신.

**Owner:** main

**Parallel:** no

**Status:** done

**Checks:**

- [x] 승인 문구가 등록됐다: `skill-draft.md`와 실제 `SKILL.md`를 문서 대조해 설명·본문이 보존됐는지 확인한다. 문구 일치만으로 동작이 입증됐다고 판정하지 않는다.
- [x] 명시 호출 전용 정책이 설정됐다: 새 `agents/openai.yaml`의 `policy.allow_implicit_invocation`이 불리언 `false`인지, 설정 위치가 공식 문서와 일치하는지 확인한다. 임의의 UI 메타데이터나 무관한 설정은 추가하지 않는다.
- [x] 스킬 형식이 유효하다: 사용 가능한 skill-creator 검증기로 이름·frontmatter·미완성 scaffold를 확인하고 실행 명령과 결과를 `source-map.md`에 기록한다. 이 검사가 확인한 범위와 실제 런타임 호출 확인을 구분한다.
- [x] 원문과 조정이 구분됐다: `source-map.md`에서 새 지시문/관련 요구사항, 원문 경로·위치, 채택한 내용, 조정 이유를 대조할 수 있다. 질문 우선·UI 3안·로직 상태/조작·작은 기술 실행·최소 측정·논의 복귀·결과 보존을 포함한다. 직접 호출·UI 1안 예외·사용자 판단·`.goal` 보관은 로컬 조정으로 표시한다.
- [x] 기존 흐름을 보존했다: 스킬 본문에 사용자 판단·단계 이동·탐색과 최종 검증의 구분·코드 재사용 기준이 있고, 이 티켓의 변경에 기존 단계 스킬·AGENTS.md·다른 목표의 변경이 없다.
- [x] 등록 결과가 추적된다: 시작 시 기존 작업 트리 변경을 확인하고, 이 티켓 파일만 스테이징해 Execute 티켓 완료 커밋을 남긴다. 검사 명령·결과와 커밋을 기록한다.

**Execution notes:**

- 기준은 `../goal.md`와 `../skill-draft.md`이다. 승인된 문구에 새 제품 요구사항이나 별도 요청 시나리오를 추가하지 않는다.
- 이 티켓 완료 후 02·03·04가 동시에 실행 가능하다. 세 티켓은 이 티켓의 산출물을 읽고 서로 다른 사례 폴더만 변경한다.
- 계획 승인: 사용자가 01은 main, 02–04는 subagent로 바꾼 분할안을 “확정하고 진행”으로 승인했다. 세 사례의 제작·실행·증거 수집은 에이전트가 수행하고 사용자 선호·채택 판단은 대기로 남길 수 있다.
- 다음 단계 진입은 기존 원칙을 따른다. 이 문서 작성은 Plan이며 실제 등록·사례 수행은 Execute의 작업이다.

**Check results:**

- 실제 문구는 승인본과 바이트 단위로 일치한다. 정책는 불리언 false로 파싱됐다.
- skill-creator quick_validate: `Skill is valid!` (exit 0).
- 출처·조정 대응과 실행 명령·출력·검사 범위는 [source-map.md](../source-map.md)에 있다.
- 본 티켓의 완료 커밋에는 Files의 네 파일만 포함한다. 기존 단계 스킬·AGENTS.md와 다른 목표의 변경은 포함하지 않는다.
- 스킬 형식·설정 검사를 실제 사례 동작이나 최종 목표 달성 판정으로 대신하지 않는다.
