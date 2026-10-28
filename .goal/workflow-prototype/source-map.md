# workflow-prototype 원문 채택·조정 대응

- Execute 기준 커밋: `5b5da04`.
- 승인 문구: [skill-draft.md](skill-draft.md). 실제 [SKILL.md](../../.agents/skills/workflow-prototype/SKILL.md)는 이 파일과 바이트 단위로 동일하다.
- 정책 파일: [agents/openai.yaml](../../.agents/skills/workflow-prototype/agents/openai.yaml). 선택적 UI 메타데이터 없이 명시 호출 정책만 추가했다.
- 아래 원문은 재사용한 절차의 근거다. 방법의 효과가 실증됐다는 증거로 해석하지 않는다.

## 지시문과 원문의 대응

| 새 지시문 | 관련 항목 | 원문 근거 | 채택·조정 |
|---|---|---|---|
| 질문에 답할 가장 작은 산출물, 이미 주어진 맥락 활용 | O1, R1, R3 | [Matt 질문 우선](../../docs/matt-skills/prototype/SKILL.md:8), [pstack 질문 좁히기](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md:7) | 질문이 형태를 정하는 원칙을 채택. 질문이 분명하면 재질문하지 않는 로컬 진행 원칙을 명시. |
| UI 비교 우선 3안, 한 아이디어는 1안 허용 | R1, R3, C4 | [Matt UI 기본 3안](../../docs/matt-skills/prototype/UI.md:38), [사용자 비교·선택](../../docs/matt-skills/prototype/UI.md:94) | 기본 3안을 채택. 단일 아이디어 1안은 사용자 합의에 따른 로컬 예외. 원문의 모든 UI 구현 방식이나 최대 개수를 일괄 의무화하지 않음. |
| 관련 상태·시나리오를 드러내고 직접 조작 | R1, R3, R4 | [Matt 로직 데모](../../docs/matt-skills/prototype/LOGIC.md:37) | 상태 표시와 조작 가능한 시나리오를 채택. 단일 HTML 등 구체 형식은 고정하지 않음. |
| 질문에 의존하는 실제 기술 조건 실행, 실제/대체 부분 구분 | R1, R3, R4 | [pstack 최소 스크립트](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md:9), [실제 출력·시간 관찰](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md:11) | 동작·시간 질문을 실제 실행하는 방식을 채택. API·권한 등을 질문에 따라 확인하는 기술 실험으로 넓힘. 원문이 모든 API·권한 시험을 일괄 요구한다고 주장하지 않음. |
| 제품 goal·ticket·제품 테스트 절차를 선행 요구하지 않고 작은 측정 허용 | R3, C6 | [Superpowers spike](../../docs/superpowers/brainstorming/SKILL.md:104), [Matt 테스트 생략](../../docs/matt-skills/prototype/SKILL.md:24) | Superpowers의 없거나 최소인 테스트에 맞춤. Matt/pstack의 일괄 테스트 생략을 보편 금지 규칙으로 이식하지 않음. 고정 시간·총 반복 횟수도 요구하지 않음. |
| 사용자 직접 호출, 범위 확대·추가 실험·종료·채택은 사용자 판단 | R2, C4 | [Superpowers 판단 주체](../../docs/superpowers/brainstorming/SKILL.md:57), [ask-matt 독립 도구](../../docs/matt-skills/ask-matt/SKILL.md:87), [사용자 합의와 에이전트 선택 구분](../../docs/superpowers/brainstorming/SKILL.md:64) | 직접 호출 전용과 모든 유형의 종료·채택 판단은 로컬 합의. 허용된 제작·실행·관찰은 반복 승인 없이 수행. 원문 전체의 공통 규칙으로 설명하지 않음. |
| 관찰·발견·한계·남은 선택 보고, 미확인/선택 대기 표시 | R4, C4 | [Matt 사용자 피드백](../../docs/matt-skills/prototype/LOGIC.md:52), [pstack 결과 보고](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md:14) | 직접 관찰·답 보존과 근거 보고를 채택. 사용자 선호와 관찰 사실을 구분하고 미확인 상태를 명시. |
| 원래 논의로 복귀, 자동 단계 이동·제품 반영 없음 | R2, C2, C6 | [Superpowers 탐색 후 대화 복귀](../../docs/superpowers/brainstorming/SKILL.md:104), [Matt 완료 후 코드 반영](../../docs/matt-skills/prototype/SKILL.md:26), [pstack 구현 인계](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md:12) | 배움을 대화로 돌려주는 원칙을 채택. Matt/pstack의 실제 코드 반영·Feature 인계를 자동 수행하는 대신 사용자의 별도 요청을 따름. |
| 탐색 관찰과 최종 목표 검증 구분, 재사용 시 정식 품질 기준 | C2, C6 | [goal.md](goal.md), [Matt 로직 보존·재사용](../../docs/matt-skills/prototype/LOGIC.md:56), [UI 정식 구현](../../docs/matt-skills/prototype/UI.md:112) | 로컬 다섯 단계의 최종 판정과 구분. 모두 삭제하거나 모두 재사용하는 단일 규칙을 두지 않음. 기존 단계 스킬 문구는 수정하지 않음. |
| .goal 보관, 필요한 경우만 격리·이동, 부모 단계 커밋 규칙 | C3, C5 | [Matt 결과 보존](../../docs/matt-skills/prototype/SKILL.md:26), [pstack scratch](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md:9), [Matt 현재 세션 우선](../../docs/matt-skills/ask-matt/PHASE-BOUNDARIES.md:21), [AGENTS.md](../../AGENTS.md) | 답·산출물 보존을 채택하고 경로·커밋은 로컬 규칙에 맞춤. 별도 브랜치·새 세션·handoff를 항상 요구하지 않음. |
| policy.allow_implicit_invocation: false | D2, C4 | [공식 Codex Build skills](https://learn.chatgpt.com/docs/build-skills#optional-metadata) | 공식 설정으로 암시적 호출을 비활성화. 호출 후 판단 주체는 본문에서 별도로 명시. |

## 01 실행과 검사 기록

- `.agents` 디렉터리 쓰기는 기본 샌드박스에서 `Operation not permitted`로 차단됐다. 같은 등록 작업의 에스컬레이션이 승인된 뒤 등록했다.
- 승인 문구를 그대로 복사하고 정책 두 줄을 기록했다. 불필요한 scaffold·보조 문서·선택적 UI 필드는 생성하지 않았다.
- 문구 대조: 실제 `SKILL.md`와 `skill-draft.md`의 바이트가 동일함을 확인.
- SHA-256: `243e9ff0992c8875ac05b7d96d393ae04317c87e1a43c4a33812af7df9c1be2c`.
- 형식 검사 명령: `python3 /Users/sinjaehan/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/workflow-prototype`.
- 실제 출력: `Skill is valid!`, 종료 코드 0. 검사 환경 Python 3.9.6 / PyYAML 6.0.3.
- 정책 파싱: `yaml.safe_load` 결과가 `{'policy': {'allow_implicit_invocation': False}}`와 정확히 일치함을 확인.
- 추가 파일은 `SKILL.md`, `agents/openai.yaml`뿐이다. 기존 단계 스킬과 AGENTS.md를 변경하지 않았다.
- 검사 범위: 문서·스킬 형식·정책 설정 대조다. 현재 앱의 암시적 호출 차단을 실제 비호출 시나리오로 시험한 것은 아니다. 02–04에서 명시적인 평가 적용과 관찰 증거를 확보한다.
- 01은 문서·설정 등록 티켓이며 제품 코드나 실행 스크립트를 추가하지 않았다.

## 기존 작업 트리와 커밋 경계

- 시작부터 있던 다른 목표의 변경은 그대로 둔다: `.goal/workflow-handoff/plan.md`, 해당 목표의 `c1-table.md`, `trial-kit.md`, `trial-untracked.txt`, `verify.md`, `.goal/workflow-intent/handoff.md`, `.goal/workflow-skill-fix-3/handoff.md`.
- 01 커밋 대상은 새 스킬 두 파일, 이 대응 기록, 01 티켓 파일뿐이다.
- 01 완료 커밋은 `git log --all --grep='execute(workflow-prototype): 01'`로 조회한다. 커밋 ID를 파일 안에 미리 쓰지 않는다.
- 이 문서는 Execute 증거이며 최종 Verify 판정을 내리지 않는다.
