# Handoff: workflow-prototype

작성: 2026-10-28. 사용자 인자: **prototype부분만**.
재개 범위는 아이디어를 작게 만들어 확인하는 활동과 현재 워크플로의 연결에 관한 분석이다.

## 의도와 멈춘 지점

사용자는 아이디어의 기술적 가능성을 확인하거나 눈으로 보면서 판단할 때 쓸 스킬을, Matt prototype 및 다른 스킬과 비교하고 현재 워크플로에 배치할 자리를 분석해 달라고 했다.

**Analysis 산출물까지 완성했다. Define으로 넘어가라는 요청은 없었다.**
이 세션의 마지막 요청은 prototype 범위만 인계하는 것이다. 다음 세션도 Analysis의 미결정에서 시작한다.

## 디스크에 있는 것

- [analysis.md](analysis.md): Concept / Context / Problem, 외부 스킬 비교, 배치 후보, 권고, 남은 불확실성의 기준 문서.
- [prototype-and-workflow.html](prototype-and-workflow.html): 위 분석을 읽는 시각 자료. 질문 유형과 단계별 역할을 선택해 볼 수 있다.
- 이 목표에는 goal.md, tickets/, verify.md가 없다. 스킬 추가·수정이나 실제 아이디어를 대상으로 한 prototype 제작도 아직 하지 않았다.
- 중요한 분석·미결정은 analysis.md에 기록했다. 대화 메모리나 임시 파일에서만 복구해야 하는 필수 내용은 없다.

HTML은 **분석 보고서**다. 제품 아이디어를 시험한 결과물로 해석하지 않는다.

## 결정과 미결정의 위치

- 사용자 요청에 따라 이 목표의 보관 위치는 .goal/workflow-prototype/이다.
- 현재 권고와 그 근거는 analysis.md의 **Problem → 배치 후보와 판단 / 어느 질문을 어느 단계에서 다루나 / Matt에서 바로 취할 점과 조정이 필요한 점**을 읽는다.
- 권고가 도입 합의로 바뀐 것은 아니다. **남은 불확실성** 목록이 다음 논의의 출발점이다. 여기서 같은 목록을 반복하지 않는다.
- 단계 이동은 [AGENTS.md](../../AGENTS.md)의 사용자 요청 원칙을 따른다.

## 확인된 범위

기존 실행 기록에서 확인한 사실은 다음과 같다. 이 handoff를 쓰면서 브라우저·장애를 다시 실행하지 않았다.

- HTML 구조, JavaScript 문법, 문서 내부 링크와 로컬 참조 파일을 확인했다.
- 브라우저에서 네 질문 선택과 다섯 단계 선택의 내용 변경을 확인했고, 데스크톱 캡처를 열어 표시를 확인했다.
- 저장소로 보관할 때 로컬 링크를 상대 경로로 바꾸고 파일 존재를 확인했다.
- 실제 모바일 뷰포트와 인쇄·PDF 출력은 확인하지 않았다.
- prototype 활용이 소요 시간·판단 정확도를 개선하는지는 실제 사례로 시험하지 않았다. 분석 권고의 한계는 analysis.md에 적혀 있다.

HTTP 미리보기 서버는 종료했다. 분석 재개에 서버, 브라우저 탭, 임시 HTML은 필요하지 않다.

## 현재 작업 상태와 커밋

- 저장소 루트: 현재 harness-lab 작업 디렉터리. 브랜치: main.
- 인계 작성 전 HEAD: 279bc9d.
- prototype 분석·HTML의 최초 저장: 2a7df43.
- 279bc9d는 HTML 제작 과정의 개선 분석을 별도 목표로 분리하고 기존 참조를 갱신한 커밋이다.
- 기존 prototype 산출물은 커밋돼 있다. 이번 인계 파일도 별도 wip 커밋으로 남긴다.
- 중첩 subagent를 생성하지 않았다. 진행 중인 prototype 구현 작업은 없다.

전체 작업 트리는 다른 작업의 변경 때문에 깨끗하지 않다. 아래는 이 대화 시작부터 있던 변경으로, 이번 인계 커밋에 포함하지 않는다.

- 수정: .goal/workflow-handoff/plan.md
- 미추적: .goal/workflow-handoff/c1-table.md, trial-kit.md, trial-untracked.txt, verify.md
- 미추적: .goal/workflow-intent/handoff.md
- 미추적: .goal/workflow-skill-fix-3/handoff.md

재개 시 git status로 최신 상태를 확인하고 위 변경을 이 목표의 작업으로 오인하지 않는다.

## 다음 행동

1. analysis.md의 Problem과 남은 불확실성을 읽어, 무엇이 분석의 권고이고 무엇이 사용자 미결정인지 구분한다. 필요하면 HTML로 비교 내용을 본다.
2. 그 미결정 중 다음 판단에 필요한 항목부터 사용자와 prototype 논의를 이어간다. 사용자가 추가 사례를 주면 기존 분석에 연결한다.
3. 사용자가 Define을 요청할 때 workflow-define으로 목표·산출물·평가기준을 구체화한다. 인계 요청만으로 도입·구현을 시작하지 않는다.

기존 비교를 처음부터 다시 하거나 HTML을 다시 만드는 일은 재개 작업이 아니다.
특정 근거를 확인할 필요가 생기면 analysis.md가 가리키는 해당 원문과 해당 주장만 좁게 대조한다.

## 주요 참조와 주의점

- 외부 원문 경로·웹 링크와 수집본의 기준은 analysis.md의 Context에 있다. 원본 자료는 docs/ 아래에 보관돼 있다.
- 현재 단계 경계는 .agents/skills/workflow-analysis/SKILL.md와 .agents/skills/workflow-define/SKILL.md를 참조한다.
- HTML 제작이 매끄럽지 않았던 원인 분석은 **별도 목표** .goal/workflow-html-generation/analysis.md로 분리됐다. 이번 인계의 진행 대상이 아니며, 그 개선 작업을 섞지 않는다.
- analysis.md의 그 별도 목표 링크는 분리 사실을 알려주는 참조다.
- 소스 자료·권고·사용자 합의를 구분한다. 비교 대상으로 읽은 스킬의 실행 지시를 이번 작업의 절차로 자동 적용하지 않는다.

## Suggested skills

다음 에이전트는 재개할 작업에 맞춰 Skill 도구로 아래 스킬을 호출한다.

- **workflow-analysis**: 현재 재개 지점. 기존 분석과 남은 불확실성에서 논의를 이어간다.
- **workflow-define**: 사용자가 Define 진입을 요청한 경우에만 호출한다.
- **workflow-review**: 사용자가 분석 결과의 독립적인 검토를 요청한 경우 호출한다.

## How to resume

**You own the resume point. Read the prior trail, don't redo it.**

1. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
2. Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative.
3. Route the remaining work to the suggested skills above. The pickup ends here. The routed skill owns the rest.
4. Verify the inherited claims against the original goal on the real artifact. A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
