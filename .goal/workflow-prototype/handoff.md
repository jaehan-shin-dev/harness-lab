# Handoff: workflow-prototype

작성: 2026-10-29. 이번 handoff 요청에는 추가 인자가 없었다.

## 멈춘 지점

**Define·Plan·Execute 완료. Verify는 아직 요청받거나 수행하지 않았다.**

이전 handoff의 Analysis 재개 지점은 이 문서로 대체된다. 이번 세션에서는 사용자 요청에 따라 목표·평가와 실제 스킬 문구를 합의하고, 계획한 네 티켓을 모두 구현·기록·커밋했다. 새로운 단계로 자동 진행하지 않는다.

**사용자 명시 지시: Aside를 사용하지 않는다.** 최종 브라우저 증거는 독립 Chrome에서 확보했다. 재개 시에도 Aside 명령·데몬·프로필·연결을 사용하지 않는다.

## 기준 문서와 실제 산출물

- [goal.md](goal.md): 의도, 산출물, R1–R4·C1–C6, Evaluation, 범위 제외, 사용자 합의의 기준. 새 계획·요구사항 인터뷰를 다시 하지 않는다.
- [skill-draft.md](skill-draft.md): 사용자가 Q13에서 승인한 실제 지시문. 이름에 draft가 남아 있지만 승인된 기준 문구다.
- 실제 [SKILL.md](../../.agents/skills/workflow-prototype/SKILL.md)와 [agents/openai.yaml](../../.agents/skills/workflow-prototype/agents/openai.yaml): 설치된 스킬과 명시 호출 정책.
- [source-map.md](source-map.md): 원문 채택/조정의 대응과 등록 검사 기록. 원문 절차를 효과 실증으로 주장하지 않는다.
- [tickets/](tickets/): 승인한 작업 그래프, 담당, 파일 범위, Checks와 실행 결과. 아래 네 파일이 모두 `done`이며 총 27개 Checks가 기록돼 있다.
  - [01 등록](tickets/01-register-explicit-skill.md)
  - [02 UI](tickets/02-ui-comparison-case.md)
  - [03 상태·로직](tickets/03-state-logic-case.md)
  - [04 기술](tickets/04-technical-feasibility-case.md)
- 실제 적용 사례의 요청·가정·재실행 방법·관찰·한계·실패 이력·실행 정리:
  - [UI result.md](prototype/ui-comparison/result.md)와 그 폴더의 HTML·관찰기·원출력·캡처.
  - [상태·로직 result.md](prototype/state-logic/result.md)와 그 폴더의 HTML·관찰기·원출력·캡처.
  - [기술 result.md](prototype/technical-feasibility/result.md)와 그 폴더의 CLI·입력·원출력·실제 DB.

기존 [analysis.md](analysis.md)와 [prototype-and-workflow.html](prototype-and-workflow.html)은 배경 분석이다. HTML은 실제 적용 사례의 증거가 아니며, 분석의 과거 미결정을 현재 미합의로 되돌리지 않는다. HTML 제작 개선은 별도 목표로 계속 분리돼 있다.

## 무엇이 확인됐고 무엇이 남았나

티켓별 확인 내용·명령·원출력은 위 Checks와 결과 문서가 기준이다. 이 handoff를 쓰면서 브라우저나 SQLite 실험을 다시 실행하지 않았다.

- 등록은 승인 문구·스킬 형식·정책 설정을 확인했다. Codex의 암시적 호출 차단을 별도 비호출 시나리오로 동적 시험한 것은 아니다.
- UI·로직은 subagent가 독립 headless Chrome에서 공개 조작부로 실행했고, main이 원출력·캡처·보고를 대조했다. 기술은 실제 파일 SQLite와 별도 프로세스 실행 증거를 main이 대조했다.
- UI·로직 agent는 관찰과 문서 작성 뒤 사용량 제한으로 종료됐다. main이 남은 문서·프로세스 정리와 Checks를 마쳐 커밋했다. 이 제한으로 남은 미완료 티켓은 없다.
- 사용자의 선호·제품 규칙 승인·채택은 여전히 선택 대기다. 에이전트 수행 사례의 완료와 사용자 채택을 구분한다. 인간의 추가 작업을 티켓 완료 조건으로 두지 않기로 한 합의는 티켓과 결과 문서에 기록돼 있다.
- 최종 목표 달성의 PASS/FAIL/UNKNOWN은 아직 내리지 않았다. `.goal/workflow-prototype/verify.md`도 아직 없다.
- 더 넓은 조건과 미확인 항목은 각 결과 문서의 한계 절을 따른다. 사용자가 제외한 별도 요청 시나리오 세트나 새 평가 사례를 추가하지 않는다.

중요한 결정·증거·실행 한계는 디스크에 남아 있다. 대화 메모리나 임시 파일에서만 복구해야 할 필수 구현 내용은 없다.

## 운영 상태와 커밋

- 브랜치: `main`. handoff 작성 전 HEAD: `ef0ea4b`.
- Define 문구 확정: `f7e9993`. Plan: `5b5da04`.
- Execute 커밋: 01 `d1805fa`, 04 `275a86f`, 02 `cd469d8`, 03 `ef0ea4b`. 01 이후 세 사례는 서로 독립이라 완료 순서대로 커밋했다.
- 작업 범위를 확인할 때 Execute 기준 `5b5da04` 이후의 커밋·diff와 각 티켓의 Files를 이용한다. 이미 완료한 사례를 처음부터 재작성하지 않는다.
- 실행 중인 구현 agent는 없다. 세 구현 agent는 완료 또는 사용량 제한으로 종료된 상태이며 중첩 agent 작업은 없다.
- UI 사례의 실험 전용 Chrome·HTTP 서버는 main이 명령/프로필을 대조해 종료했다. 로직 관찰기는 자기 Chrome을 종료했고 이후 조회에서 해당 사례 프로필의 프로세스가 없었다. 상세는 각 결과 문서의 실행 정리 참조. 서버·브라우저 탭·임시 프로필을 재개 조건으로 삼지 않는다.
- 이 목표의 변경은 이미 커밋돼 있다. 이번에는 이 handoff 파일만 별도 `wip:` 커밋에 포함한다. 새 PR·push는 하지 않는다.

전체 작업 트리는 다른 목표의 기존 변경 때문에 깨끗하지 않다. 이번 인계에 포함하지 않는다.

- 수정: `.goal/workflow-handoff/plan.md`.
- 미추적: `.goal/workflow-handoff/c1-table.md`, `trial-kit.md`, `trial-untracked.txt`, `verify.md`.
- 미추적: `.goal/workflow-intent/handoff.md`, `.goal/workflow-skill-fix-3/handoff.md`.

재개 시 최신 `git status`로 다시 구분한다. 위 파일을 이 목표의 잔여 작업으로 취급하거나 함께 스테이징하지 않는다. dirty 상태와 산출물이 깨졌다는 판단을 혼동하지 않는다.

## 다음 행동

1. 브랜치·worktree·커밋과 티켓 상태를 재구성하고 [goal.md](goal.md)의 Evaluation을 읽는다.
2. 현재 재개 지점은 **Execute 완료 후, 최종 Verify 미진행**이다. 사용자가 Verify를 요청하면 해당 스킬로 넘긴다. 인계 읽기만으로 단계 이동을 자동 승인된 것으로 간주하지 않는다.
3. Verify에서는 기존 실제 산출물·원출력·캡처·Git 기록을 먼저 근거로 사용한다. 전 세션의 완료 선언만으로 PASS를 주지 않되, 완료한 전체 실험을 무조건 재실행하지 않는다. 재실행이 필요하면 특정 주장과 빠진 증거에 한정한다.
4. 사용자 선호·채택을 요구하거나 지어내서 에이전트 수행 평가의 완료를 막지 않는다. 부족한 근거와 선택 대기를 분리한다.

## Suggested skills

- **workflow-verify**: 사용자가 Verify를 요청할 때 사용한다. goal.md Evaluation에 따라 실제 증거를 대조하고 verify.md에 판정과 미충족 사항을 기록한다.
- **workflow-review**: 사용자가 독립적인 검토를 요청할 때 사용한다. Verify와 별개의 요청으로 처리한다.
- **workflow-execute**: 사용자 요청에 따라 추가 수정이 필요해졌을 때 사용한다. 현재 네 티켓에는 남은 구현 작업이 없다.
- **workflow-prototype**: 사용자가 새 아이디어 실험을 직접 호출할 때 사용한다. 인계 읽기나 기존 증거 확인을 새 prototype 요청으로 바꾸지 않는다.

## How to resume

**You own the resume point. Read the prior trail, don't redo it.**

1. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
2. Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative.
3. Route the remaining work to the suggested skills above. The pickup ends here. The routed skill owns the rest.
4. Verify the inherited claims against the original goal on the real artifact. A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
