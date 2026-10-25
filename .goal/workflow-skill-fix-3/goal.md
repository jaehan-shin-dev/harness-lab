# Goal: workflow 스킬 개선 (단계 산출물, goal/plan 구분, 단계별 commit, 독립 Verify)

작성: 2026-10-25, Round 10 반영. Define 종료(frontier 비어 있음, 사용자가 공동 이해 도달을 확인함). 근거 자료: `analysis.md`, `goal-plan-boundary.html`
표기: [합의 Qn] 사용자 확인 / [미결정 Qn] 질문 중 / [가정] 확인 전 추정 / [사실] 파일에서 확인

## Objective

[합의 Q1] goal과 plan의 경계를 분명히 하고(grilling은 goal에서만), 단계마다 산출물과 commit을 남기고, Verify를 독립적으로 돌리고, plan에서 필요하면 subagent로 빠르게 구현할 수 있도록 workflow 스킬을 고친다.

배경 [합의]
- 사용자는 goal과 plan의 경계에 의문을 가져 왔다. 둘을 확실히 구분하려 한다.
- plan에서 필요하면 subagent도 써서 빠른 개발을 지원하는 방향으로 바꾸려 한다.
- workflow는 범용이다. tdd는 코드를 짤 때 쓰이기를 바란다(사용자, Round 3)

## Deliverable

[합의 Q2, Q22] 고치거나 만드는 파일
- 고침: `.agents/skills/`의 workflow-analysis, workflow-define, workflow-plan, workflow-execute, workflow-verify, 그리고 `AGENTS.md`
- 새로 만듦: `.agents/skills/tdd/`(Matt 원문 `SKILL.md`, `tests.md`, `mocking.md`)
- [합의 Q29] 새로 만듦: `.agents/skills/codebase-design/`(Matt 원문 `SKILL.md`, `DEEPENING.md`, `DESIGN-IT-TWICE.md`, 수정 없음)
- 그대로 둠: workflow-grill, workflow-review, workflow-handoff

[합의 Q25] 고치거나 만드는 파일마다 문장 지도(원문 문장 → 그대로 / 빼기 / 일부 바꿈 / 새 문장)를 이 Deliverable에 만든다. Define이 길어져도 괜찮다(사용자). 문장 지도는 Q29, Q30이 정해진 뒤 채운다.

파일별 바뀐 모습
- workflow-analysis: 결과를 `.goal/<goal>/analysis.md`에 쓴다. 형식은 지금 끝 조건의 네 부분(Concept, Context, Problem, 남은 불확실성)이다 [합의 Q5]
- workflow-define
  - analysis.md가 있으면 읽고, 그 "남은 불확실성"을 첫 질문 후보로 쓴다. 없으면 사용자 요청에서 시작한다 [합의 Q5]
  - 질문 앞에 배경과 용어를 먼저 쓴다는 규칙 한 줄 [합의 Q3]
  - [합의 Q24] 경계 문장(지금 `define:18`의 "tree는 Deliverable까지 내려간다. 만드는 순서와 방법만 Plan에서 정한다.")을 "tree는 Plan이 사용자에게 다시 묻지 않고 ticket을 만들 수 있을 때까지 내려간다."로 바꾼다
  - [합의 Q22, Q32] 코드를 만드는 목표면 codebase-design 스킬을 불러, 그 용어로 Evaluation의 Method에 테스트할 seam(공개 인터페이스)을 적는다는 구절
- workflow-plan: Matt `to-tickets`를 원문으로 한다 [합의 Q8, Q12]
  - grilling 없이 goal.md에서 ticket 목록을 만들어 보여 주고, 사용자는 쪼갠 크기, 막는 관계, 합치기·나누기만 확인한다. 사용자 결정이 필요한 빈칸이 나오면 멈추고 Define으로 돌려보낸다 [합의 Q8]
  - [합의 Q23] ticket은 `.goal/<goal>/tickets/NN-slug.md`로 ticket마다 파일을 둔다(Matt 원문대로). plan.md는 만들지 않는다. 전체 목록은 확인 단계에서 대화로 보여 준다
  - ticket 카드 칸 [합의 Q13]: `# NN: 제목`, What to build, Covers(goal.md의 R·C), Blocked by, Files, Owner, Parallel(yes/no), Status, Checks(체크박스마다 조건 + 확인 방법. Matt의 Acceptance criteria 자리)
  - [합의 Q27] Owner는 Plan이 ticket마다 정한다. subagent에게 맡기는 기준은 다른 ticket과 동시에 돌려 시간을 줄일 수 있을 때(Parallel: yes), 또는 읽거나 시도할 게 많아 main의 대화를 무겁게 만들 때다. 그 밖에 바로 고치는 게 빠른 ticket은 main이 직접 한다
  - [합의 Q30] Owner 값은 `main | subagent | HITL` 셋이다. HITL은 사용자가 직접 하거나 같이 하는 ticket이고, main이 사용자와 함께 진행한다. 사용자가 할 일은 What to build와 Checks에 적는다. 지금 plan의 AI / User / Collaborative 구분은 User와 Collaborative가 Execute에서 똑같이 처리되므로 HITL 하나로 묶었다(Matt `wayfinder:75`의 HITL/AFK)
- workflow-execute: Matt `implement-spec`을 원문으로 한다 [합의 Q11, Q12]
  - [합의 Q27, Q15 바로잡음] main은 orchestrator다. 다음 ticket 고르기, 맡기기, 상태 기록, commit을 한다. Owner가 main인 ticket은 main이 직접 하고 Checks와 commit도 main이 한다. Owner가 subagent인 ticket은 implementer subagent에게 맡긴다
  - implementer subagent에게는 goal.md, 해당 ticket 파일, 관련 파일을 가리키는 정보만 넘긴다(context pointers) [합의 Q15]
  - [합의 Q23] implementer는 자기 ticket의 Files만 고치고, 범위 밖에서 본 것은 보고만 한다
  - Parallel: yes이고 막는 ticket이 다 끝난 것끼리만 동시에 돌린다. 나머지는 하나씩 돌린다 [합의 Q15]
  - 사용자가 참여하는 ticket은 사용자에게 할 일을 요청하고 결과를 확인한다 [합의 Q15, 값은 Q30]
  - [합의 Q16] implementer subagent는 자기 ticket의 Checks를 돌리고 증거를 보고한다. commit은 하지 않는다. orchestrator가 증거를 확인하고 ticket 상태와 Checks 결과를 ticket 파일에 적은 뒤, 그 ticket의 Files와 ticket 파일만 commit한다. worktree는 쓰지 않는다
  - [합의 Q22] 코드를 바꾸는 ticket은 tdd를 불러 만든다(main이든 subagent든). 문서 ticket은 tdd를 부르지 않고 Checks만 돌린다
- tdd [합의 Q22]: Matt 원문 세 파일을 가져온다. SKILL.md에서 세 군데를 고친다.
  - seam을 사용자에게 확인받는 문장 → "goal.md Evaluation과 ticket Checks가 미리 합의한 seam이다"
  - [합의 Q29] codebase-design 문장은 그대로 둔다
  - "(code-review 스킬)" 괄호 빼기
  - `tests.md`, `mocking.md`는 그대로 둔다
- workflow-verify [합의 Q10, Q18]
  - 사용자가 main에서 `/workflow-verify`를 부르면 main이 판정용 subagent를 보낸다
  - subagent에게는 goal.md(Evaluation), Deliverable에 적힌 산출물 경로, Plan 끝 commit 이후의 git 기록만 준다. Execute의 완료 기록(ticket 상태)은 주지 않는다
  - 결과는 `.goal/<goal>/verify.md`에 쓰고 판정 방식을 적는다
- AGENTS.md [합의 Q19, Q23]: 단계별 commit 규칙(언제, 어떻게, 메시지 형식)을 여기에만 둔다. execute에는 "ticket commit은 orchestrator가 한다"는 누가만 적는다

Matt 원문을 가져오는 규칙 [합의 Q12, Q22]
- 영어 원문을 문장 단위로 가져온다. 허용하는 수정은 문장 빼기와 문장 안 일부 바꾸기다. 새 문장은 꼭 필요한 곳에만 쓴다
- plan과 execute 스킬은 영어가 된다
- 원문은 plan ← `docs/matt-skills/to-tickets/SKILL.md`, execute ← `docs/matt-skills/implement-spec/SKILL.md`, tdd ← `docs/matt-skills/tdd/`
- 뺄 것: 이슈 트래커와 라벨, setup 스킬 안내, code-review, integration branch·worktree·merger·draft PR, expand–contract 문단
- 새 문장이 필요한 곳: goal.md 가리키기, ticket Checks, Owner·Parallel 표시, 빈칸이면 Define으로, ticket마다 commit(orchestrator), 자기 Files만 고치기, 코드 ticket은 tdd, 끝 조건
- Execute 중에 goal에 없는 사용자 결정이 필요해지면 멈추고 알린다(Q8 규칙을 Execute에도 적용) [합의 Q35: D-execute의 N6]

### 문장 지도 D-plan: workflow-plan ← `docs/matt-skills/to-tickets/SKILL.md` [합의 Q34]

처리: 그대로 / 일부 바꿈 / 바꿈(통째로) / 빼기 / 새 문장. "그대로"는 원문 줄을 글자까지 옮긴다.

| # | 원문 줄 | 처리 | 결과 (일부 바꿈·새 문장은 결과 문장) |
|---|---|---|---|
| P1 | 2 `name: to-tickets` | 바꿈 | `name: workflow-plan` |
| P2 | 3 description | 바꿈 | `description: Break goal.md into a set of tracer-bullet tickets, each declaring its blocking edges, written as one file per ticket. Use for the Plan phase.` |
| P3 | 4 `disable-model-invocation: true` | 그대로 [합의 Q33] | 사용자만 부른다 |
| P4 | 7 `# To Tickets` | 바꿈 | `# Plan` |
| P5 | 9 | 일부 바꿈 | Break `goal.md` into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it. ("a plan, spec, or conversation" → "`goal.md`") |
| P6 | 11 이슈 트래커·setup 두 문장 | 빼기 | |
| P7 | 13 `## Process` | 그대로 | |
| P8 | 15 `### 1. Gather context` | 그대로 | |
| P9 | 17 첫 문장 | 일부 바꿈 | Work from `.goal/<goal>/goal.md`: read it in full. ("whatever is already in the conversation context" → 앞 구절) |
| P10 | 17 둘째 문장(참조를 받아 fetch) | 빼기 | |
| N1 | (새 문장, P9 뒤) | 새 문장 | Do not interview the user. If a ticket would need a decision goal.md does not record, stop and tell the user to return to Define and update goal.md. (Q8) |
| P11 | 19 `### 2. Explore the codebase (optional)` | 그대로 | |
| P12 | 21 첫 문장 | 그대로 | |
| P13 | 21 둘째 문장(glossary·ADR) | 빼기 | domain-modeling을 가져오지 않음(Q31) |
| P14 | 23 prefactor 두 문장 | 그대로 | |
| P15 | 25 `### 3. Draft vertical slices` | 그대로 | |
| P16 | 27 | 그대로 | |
| P17 | 29-36 vertical-slice-rules 블록(규칙 4개) | 그대로 | |
| P18 | 38 blocking edges 두 문장 | 그대로 | |
| N2 | (새 문장, P18 뒤) | 새 문장 | Give each ticket an **Owner**: `main` when doing it directly is quicker, `subagent` when it can run alongside other tickets or needs enough reading to weigh down the main session, `HITL` when the user does it or does it with you. (Q27, Q30) |
| N3 | (새 문장) | 새 문장 | Mark a ticket **Parallel: yes** only when it can finish on its own and touches no file another ticket touches. (Q11) |
| N4 | (새 문장) | 새 문장 | Give each ticket **Checks**, each one a condition and how to check it. A ticket that changes code writes its Checks as tests at the seams goal.md's Evaluation names. (C2, Q13, Q22) |
| N5 | (새 문장) | 새 문장 | Every requirement in goal.md is covered by at least one ticket; list them under **Covers**. (Q13) |
| P19 | 40 wide refactor(expand–contract) 문단 | 빼기 | Q12 |
| P20 | 42 `### 4. Quiz the user` | 그대로 | |
| P21 | 44 | 그대로 | |
| P22 | 46-48 Title, Blocked by, What it delivers 세 줄 | 그대로 | |
| N6 | (새 줄, P22 뒤) | 새 문장 | `- **Owner**: main, subagent, or HITL` |
| P23 | 50-54 Ask the user 블록(질문 3개) | 그대로 | |
| P24 | 56 | 그대로 | |
| P25 | 58 `### 5. Publish the tickets to the configured tracker` | 바꿈 | `### 5. Write the tickets` |
| P26 | 60 첫 문장 | 일부 바꿈 | Write the approved tickets. ("Publish" → "Write") |
| P27 | 60 둘째 문장(tracker마다 다름) | 빼기 | |
| P28 | 62 Local files 줄 | 일부 바꿈 | Write one file per ticket under `.goal/<goal>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file. ("- **Local files** →" 머리 빼기, 경로 바꿈) |
| P29 | 63 real issue tracker 줄 | 빼기 | |
| P30 | 65 frontier 두 문장 | 그대로 | |
| P31 | 67 parent issue 문장 | 빼기 | |
| P32 | 69-82 local-ticket-template | 일부 바꿈 | 아래 템플릿 |
| P33 | 84-103 issue-template | 빼기 | |
| P34 | 105 첫 문장 | 일부 바꿈 | Avoid code snippets: they go stale fast. ("In either form, avoid specific file paths or code snippets" → 앞 구절. Files 칸이 생겨서 파일 경로 금지는 뺌, Q13) |
| P35 | 105 나머지(prototype 예외) | 그대로 | |
| N7 | (새 문장, 끝) | 새 문장 | Done when the user has approved the breakdown and every ticket file has Checks, or "No checks needed" with the reason. (끝 조건) |

P32 템플릿 결과("What to build"와 "Blocked by"의 설명 문장은 원문 그대로, 나머지 칸은 새 문장)

```
# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Covers:** the goal.md requirements this ticket serves.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Files:** the files this ticket changes.

**Owner:** main | subagent | HITL

**Parallel:** yes | no

**Status:** ready

**Checks:**

- [ ] <condition>: <how to check>
- [ ] <condition>: <how to check>
```

### 문장 지도 D-execute: workflow-execute ← `docs/matt-skills/implement-spec/SKILL.md` [합의 Q35]

원문에는 `#` 제목이 없다. 원문대로 두고 제목은 넣지 않는다. 단계 번호는 남은 단계에 맞춰 다시 매긴다.

| # | 원문 줄 | 처리 | 결과 (일부 바꿈·새 문장은 결과 문장) |
|---|---|---|---|
| E1 | 2 `name: implement-spec` | 바꿈 | `name: workflow-execute` |
| E2 | 3 description | 바꿈 | `description: Implement the tickets from the Plan phase, with the main session as orchestrator. Use for the Execute phase.` |
| E3 | 4 `disable-model-invocation: true` | 그대로 [합의 Q33] | 사용자만 부른다 |
| E4 | 7 두 문장 | 일부 바꿈 | You have been provided a goal: `.goal/<goal>/goal.md`. This goal should have tickets associated with it under `.goal/<goal>/tickets/`, describing how to implement the goal. ("a spec" → 앞 구절, "This spec" → "This goal", "with it" 뒤에 경로, "the spec" → "the goal") |
| E5 | 9 이슈 트래커·setup 문장 | 빼기 | |
| E6 | 11 | 일부 바꿈 | The aim is the entire goal implemented on the current branch, with every ticket marked done in its file. ("The goal is" → "The aim is", "spec" → "goal", "a single **integration branch**" → "the current branch", "resolved the way the issue tracker closes work" → "marked done in its file") |
| E7 | 13 task graph·frontier 세 문장 | 그대로 | |
| E8 | 15 context pointers 세 문장 | 일부 바꿈 | "to the spec, tickets, research notes, and previous commits" → "to goal.md, the ticket file, research notes, and previous commits". 나머지 그대로 |
| E9 | 17 background 문장 | 그대로 | |
| N1 | (새 문장, E9 뒤) | 새 문장 | You are the **orchestrator**: you pick the next tickets, hand them out, record their status, and commit them. (Q11, Q27) |
| N2 | (새 문장) | 새 문장 | Work each ticket by its **Owner**: do `main` tickets yourself, give `subagent` tickets to implementer subagents, and work `HITL` tickets with the user, asking for what they need to do and checking the result. When a `main` ticket changes code, call the Skill tool with `tdd` to build it. (Q22, Q27, Q30) |
| N3 | (새 문장) | 새 문장 | Run tickets at the same time only when they are on the frontier and marked **Parallel: yes**; run the rest one at a time. (Q11, Q15) |
| E10 | 19 `## Steps` | 그대로 | |
| E11 | 21 step 1 | 일부 바꿈 | 1. Read goal.md and the tickets to understand the task graph. ("the spec and tickets" → "goal.md and the tickets") |
| E12 | 23 step 2 (exploration subagent, 선택) | 그대로 | 번호만 2 |
| E13 | 25 step 3 (integration branch, draft PR) | 빼기 | Q12 |
| E14 | 27 step 4 머리 | 일부 바꿈 | 3. Use **implementer subagents** to implement each `subagent` ticket. Each implementer subagent: ("each ticket, each in its own worktree on its own branch" → "each `subagent` ticket") |
| E15 | 28 worktree 확인 줄 | 빼기 | Q16(worktree 안 씀) |
| E16 | 29 tdd 줄 | 일부 바꿈 | - calls the Skill tool with `tdd` to build the ticket when the ticket changes code; ("when the ticket changes code" 덧붙임, Q22) |
| N4 | (새 줄) | 새 문장 | - changes only its ticket's Files, and reports anything it notices outside them instead of fixing it; (Q23) |
| N5 | (새 줄) | 새 문장 | - runs its ticket's Checks and reports the evidence, without committing. (Q16) |
| E17 | 30 integration branch merge 줄 | 빼기 | |
| E18 | 32 step 5 | 일부 바꿈 | 4. Once a ticket completes, check the evidence for its Checks, write its status and Check results into the ticket file, and commit only the ticket's Files and the ticket file. ("an **implementer subagent**" → "a ticket", "merge its work to the integration branch with a **merger subagent**" → 뒷부분, Q16) |
| E19 | 34 step 6 두 문장 | 일부 바꿈 | 5. If this changes the **frontier** of available tickets, start the newly available tickets. This allows for maximum concurrency. ("kick off more **implementer subagents** to work on the new tickets" → "start the newly available tickets") |
| E20 | 36 step 7 (code-review) | 빼기 | Q12 |
| E21 | 38 step 8 | 바꿈 | 6. Report each ticket's status and Check results, and anything implementers reported outside their Files. |
| E22 | 40 step 9 (worktree 정리) | 빼기 | |
| N6 | (새 문장, 끝) | 새 문장 | If a ticket turns out wrong, fix the ticket files yourself when no user decision is involved; otherwise stop and tell the user to return to Define and update goal.md. (Q8을 Execute에 적용, 지금 execute의 "필요하면 계획을 수정하되, 중요한 변경은 사용자와 합의한다"를 대신함) |
| N7 | (새 문장, 끝) | 새 문장 | Done when every ticket file shows done, incomplete, or blocked, with its Check results. (지금 execute의 끝 조건) |

### 문장 지도 D-tdd: tdd ← `docs/matt-skills/tdd/` [합의 Q36]

`tests.md`, `mocking.md`는 글자까지 그대로 옮긴다. `agents/openai.yaml`은 가져오지 않는다(workflow-handoff 때와 같음). codebase-design도 `SKILL.md`, `DEEPENING.md`, `DESIGN-IT-TWICE.md`만 그대로 옮기고 `agents/openai.yaml`은 가져오지 않는다. 아래에 없는 `SKILL.md` 줄은 모두 그대로다(10줄 GLOSSARY·ADR 문장, 26줄 codebase-design 문장 포함).

| # | 원문 줄 | 처리 | 결과 |
|---|---|---|---|
| T1 | 22 둘째 문장 "Before writing any test, write down the seams under test and confirm them with the user." | 바꿈 | The seams under test are agreed up front: the ones goal.md's Evaluation names, which the ticket's Checks test. (Q22) |
| T2 | 22 나머지 세 문장 | 그대로 | "**Test only at pre-agreed seams.**", "No test is written at an unconfirmed seam.", "You can't test everything, …" |
| T3 | 24 "Ask: …" 두 문장(사용자에게 seam 묻기) | 빼기 | Execute에서는 사용자에게 묻지 않고, seam은 Define에서 정한다(Q22, Q32) |
| T4 | 38 둘째 문장 | 일부 바꿈 | It belongs to the review stage, not the red → green implementation cycle. ("(see the `code-review` skill)" 빼기) |

### 문장 지도 D-analysis: workflow-analysis (한국어, 지금 파일 기준) [합의 Q37]

| # | 지금 줄 | 처리 | 결과 |
|---|---|---|---|
| A1 | 19 "Concept, Context, Problem이 각각 설명되고, 남은 불확실성이 목록으로 적히면 끝." | 일부 바꿈 | Concept, Context, Problem이 각각 설명되고, 남은 불확실성이 목록으로 `.goal/<goal>/analysis.md`에 적히면 끝. (Q5) |

나머지 줄은 그대로다.

### 문장 지도 D-define: workflow-define (한국어, 지금 파일 기준) [합의 Q38]

| # | 지금 줄 | 처리 | 결과 |
|---|---|---|---|
| F1 | (새 문장, 9 뒤) | 새 문장 | `.goal/<goal>/analysis.md`가 있으면 먼저 읽고, 그 남은 불확실성을 첫 질문 후보로 쓴다. (Q5) |
| F2 | (새 문장, F1 뒤) | 새 문장 | 질문마다 그 질문에 필요한 배경과 용어를 먼저 설명한다. (Q3) |
| F3 | 16 Evaluation 줄 끝 | 새 구절 | (줄 끝에 이어서) 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다. (Q22, Q32) |
| F4 | 18 앞 두 문장 "tree는 Deliverable까지 내려간다. 만드는 순서와 방법만 Plan에서 정한다." | 바꿈 | tree는 Plan이 사용자에게 다시 묻지 않고 ticket을 만들 수 있을 때까지 내려간다. (Q24) 같은 줄의 "위 여섯 항목의 미결정이 질문 대상이며,"는 그대로 |

나머지 줄은 그대로다.

### 문장 지도 D-verify: workflow-verify (한국어, 지금 파일 기준) [합의 Q39]

| # | 지금 줄 | 처리 | 결과 |
|---|---|---|---|
| V1 | (새 문장, 12 뒤) | 새 문장 | 판정은 판정용 subagent에게 맡긴다. subagent에게는 goal.md, goal.md Deliverable에 적힌 산출물 경로, Plan 끝 commit 이후의 git 기록만 넘기고, ticket 파일(Execute의 완료 기록)은 넘기지 않는다. (Q10, Q18) |
| V2 | (새 문장, V1 뒤) | 새 문장 | 결과는 `.goal/<goal>/verify.md`에 쓰고, 판정 방식(누가, 무엇을 받아 판정했는지)을 함께 적는다. (Q18) |
| V3 | (새 문장, 끝) | 새 문장 | Evaluation 항목마다 PASS, FAIL, UNKNOWN과 그 근거가 verify.md에 적히면 끝. (지금 verify에는 끝 조건이 없다. R3의 "Verify 끝 commit" 시점을 정하려면 필요하다) |

나머지 줄은 그대로다.

### 문장 지도 D-agents: AGENTS.md (영어, 지금 파일 기준) [합의 Q40]

| # | 지금 줄 | 처리 | 결과 |
|---|---|---|---|
| G1 | (새 문장, 19 뒤) | 새 문장 | Each phase leaves its document there: `analysis.md`, `goal.md`, `tickets/`, `verify.md`. (R1) |
| G2 | (새 절, 끝) | 새 문장 | 아래 블록 (Q9, Q19, Q23) |

```
### Commits
Commit when a phase meets its end condition: Analysis, Define, Plan, each ticket in Execute, and Verify. Do not ask first.
Stage only the files that phase changed (`git add <files>`, never `-A`). Do not commit mid-Round in Define or Plan.
If the directory is not a git repository, skip committing and say so.
Message: `<phase>(<goal>): <summary>`, for example `define(workflow-skill-fix-3): goal.md` or `execute(workflow-skill-fix-3): 03 <ticket title>`.
```

나머지 줄은 그대로다.

## Requirements

R1 단계 산출물
  [합의] Analysis가 analysis.md를 만들고, Define은 그것을 바탕으로 진행한다
  [합의 Q5] 위치는 `.goal/<goal>/analysis.md`, 형식은 Concept, Context, Problem, 남은 불확실성. Define은 "남은 불확실성"을 첫 질문 후보로 쓴다. Analysis를 건너뛰면 Define은 사용자 요청에서 시작한다
  [합의 Q6] 사용자의 시작 요청 원문은 따로 남기지 않는다. 목표는 Analysis를 거치며 구체화되기 때문이다(사용자)
R2 goal/plan 구분
  [합의] grilling은 Define(goal)에서만 한다
  [합의 Q7] 기준은 "누가 정할 수 있나"다. 사용자가 정해야 하는 결정(무엇, 왜, 산출물 모습, 요구사항, 제약, 범위, 평가 방법)은 전부 goal에 둔다. 에이전트가 goal만 보고 혼자 정할 수 있는 실행 결정(ticket 쪼개기, 순서, 건드릴 파일, 실행 방식)만 plan에 둔다
  [합의 Q8] Plan은 goal.md만 보고 ticket 목록을 만들어 보여 준다. 사용자는 쪼갠 크기, 순서(막는 관계), 합치기·나누기만 확인한다. 사용자가 정해야 할 빈칸이 나오면 Plan은 묻지 않고 멈춘 뒤 "Define으로 돌아가 goal.md를 고쳐야 한다"고 알린다
  [합의 Q24] Define의 멈춤 기준은 "Plan이 사용자에게 다시 묻지 않고 ticket을 만들 수 있을 때"다
R3 단계별 commit
  [합의] analysis, define, plan, execute(ticket마다) 등 단계마다 commit한다
  [합의 Q9] 시점은 다섯 곳이다.
    - Analysis 끝(analysis.md)
    - Define 끝(goal.md)
    - Plan 끝(ticket 파일)
    - Execute 중 ticket 하나가 끝날 때마다
    - Verify 끝(verify.md)
  [합의 Q9] 방식
    - 단계의 끝 조건이 충족되면 묻지 않고 커밋한다. 이전 선호 "커밋은 요청 시만"을 이 다섯 시점에서는 대체한다
    - 그 단계에서 바꾼 파일만 이름으로 지정한다(`git add <파일>`, `-A` 금지)
    - Define·Plan의 Round 중간에는 커밋하지 않는다
    - git 저장소가 아니면 건너뛰고 그 사실을 알린다
  [합의 Q23] 메시지 형식은 AGENTS.md의 commit 규칙에 고정으로 둔다
R4 독립 Verify
  [합의] Verify는 독립적으로 실행한다
  [합의 Q10, Q18] 판정은 subagent가 한다. 판정하는 쪽은 goal.md의 Evaluation, 실제 산출물, Plan 끝 commit 이후의 git 기록만 본다. Execute의 완료 기록은 주지 않는다. 결과는 verify.md에 쓰고 판정 방식을 적는다
R5 subagent
  [합의] plan에서 필요하면 subagent를 써서 빠르게 구현한다(배경에서)
  [합의 Q11, Q27] Plan이 ticket마다 Owner와 Parallel을 정한다. 바로 고치는 게 빠른 ticket은 main이 직접 하고, 동시 실행으로 시간을 줄이거나 main의 대화를 무겁게 할 ticket만 subagent에게 맡긴다. 동시 실행은 Parallel: yes(혼자 끝낼 수 있고 다른 ticket과 파일이 겹치지 않음)끼리만 한다. Matt `implement-spec` 원문을 참고한다. main은 orchestrator다(사용자)

## Constraints

C1 [합의] goal에서 verify 방법(Evaluation)을 정하는 것은 유지한다
C2 [합의] ticket별 check(Checks)는 유지한다. Matt 원문을 가져와도 check는 진행한다(사용자, Q8)
C3 [합의 Q4, Q20] Claude Code, pi, Codex 세 하네스 모두에서 동작한다. 세 하네스 모두 subagent를 쓸 수 있다고 본다. 사용자: "무조건 subagent가 있는 pi로 사용할 것"
  [사실] pi subagent 확장은 지금 `~/DEV/pi-lab/.pi/extensions/subagent`(프로젝트 전용)에 있고, harness-lab에는 `.pi/`가 없다. 환경을 맞추는 건 사용자 몫이다(Out of scope)
C4 [합의 Q4] 미니멀하게, 한눈에, 중복 없이(10/20 선호)
C5 [합의 Q8, Q11, Q12, Q22] plan, execute, tdd는 Matt 원문을 문장 단위로 최대한 가져온다(Deliverable의 규칙)
([합의 Q28] 이전 C5 "workflow-grill 본문은 Matt 원문 그대로"는 Out of scope의 "workflow-grill 수정 안 함"과 같은 말이라 지우고 그쪽으로 합쳤다)

## Out of scope

[합의 Q3]
- 회고(analysis.md 5위), 스킬 시험 확대(7위), plan의 위험·대안 칸(8위), 문서 구조 검사 스크립트(9위), description 형식 바꾸기
- 별도 intent.md 파일
[합의 Q6] 사용자 시작 요청 원문 보존
[합의 Q2, Q4, Q28] workflow-grill(본문은 Matt 원문 그대로), workflow-review, workflow-handoff 수정
[합의 Q20]
- subagent가 없는 하네스를 위한 대체 문장
- pi-lab의 `.pi/` subagent 확장을 harness-lab으로 옮기는 일

[합의 Q31] tdd와 codebase-design을 뺀 Matt 개발 스킬은 이번에 가져오지 않는다. 다음 목표 후보로 남긴다.

| 스킬 | 내 흐름에서 쓰일 자리 | 가져올 때 손볼 곳 |
|---|---|---|
| improve-codebase-architecture | Analysis(코드베이스 훑기, HTML 보고서) → Define(고른 후보) | 자체 grilling 단계를 "고른 후보로 Analysis·Define 시작"으로 바꾸기. Matt "grilling" 이름 → workflow-grill. domain-modeling과 `HTML-REPORT.md`가 함께 와야 함 |
| domain-modeling | Define(용어집 `GLOSSARY.md`, 결정 기록 ADR) | 저장소에 GLOSSARY와 `docs/adr/` 층이 생김 |
| diagnosing-bugs | Analysis(원인 찾기), Execute(버그 ticket의 회귀 테스트) | 거의 그대로. `scripts/hitl-loop.template.sh`가 함께 와야 함 |
| prototype | Analysis·Define(결정 전에 버릴 코드로 확인) | 프로토타입 브랜치와 이슈 포인터 문장 |
| research | Analysis(1차 자료 조사를 백그라운드 에이전트에게) | 거의 그대로 |
| wizard | Execute의 HITL ticket(사람만 할 수 있는 설정 절차) | `template.sh`가 함께 와야 함 |
| code-review의 Standards 축 | Verify(코드 목표) | 이슈 트래커 문장. Spec 축은 우리 Verify와 겹침 |
| pr | PR을 낼 때 | 없음 |

해당 없음: triage, setup-matt-pocock-skills(이슈 트래커), to-spec(goal.md가 대신함), implement(execute가 대신함)

## Evaluation

[합의 Q21, Q26] 평가는 두 가지로 한다.
- 실행: 사용자가 다른 세션에서 새 workflow로 목표 하나를 끝까지 돌리고, 그 goal 폴더와 세션을 알려 준다. Verify에서 그 기록(goal 폴더, git log, 세션 기록)으로 판정한다
- 정적: 이번에 고친 스킬 파일 자체를 검사한다

| 항목 | Criteria | Method | Evidence |
|---|---|---|---|
| R1 산출물 [합의 Q26] | 실행 폴더에 analysis.md가 있고 네 부분이 있음. Define의 첫 Round가 그 "남은 불확실성"을 씀 | 실행 | analysis.md, 세션의 Define Round 1 |
| R2 goal/plan 구분 [합의 Q42] | 정적: define에 F4 경계 문장, plan에 N1(인터뷰하지 않음, 빈칸이면 Define으로), execute에 N6이 있고, plan에는 workflow-grill을 부르는 문장이 없음. 실행: Plan 구간에 질문 Round가 없고, 사용자 확인은 ticket 목록 확인(쪼갠 크기, 막는 관계, 합치기·나누기) 한 번뿐임. Define 끝 commit과 Plan 끝 commit 사이에 goal.md가 바뀌지 않음(빈칸이 있었다면 Plan이 멈추고 Define으로 돌려보낸 기록이 있음). Execute 중 사용자 결정이 필요했다면 멈추고 Define으로 돌려보냄 | 정적 + 실행 | define·plan·execute SKILL.md, 세션의 Plan·Execute 구간, `git log --stat` |
| R3 commit [합의 Q26] | git log에 Analysis 끝, Define 끝, Plan 끝, ticket마다, Verify 끝 커밋이 있음. 각 커밋에는 그 단계의 파일만 있음. Round 중간 커밋은 없음 | 실행 | `git log --stat` |
| R4 독립 Verify [합의 Q26] | 판정을 subagent가 함. 넘긴 입력이 goal.md, 산출물, git 기록뿐임(ticket 상태 없음). verify.md에 판정 방식이 적힘 | 실행 | 세션 기록(subagent에게 보낸 내용), verify.md |
| R5 subagent [합의 Q41] | 실행 목표의 모든 ticket에 Owner와 Parallel이 있음. `subagent` ticket은 implementer subagent가, `main` ticket은 main이, `HITL` ticket은 사용자와 함께 진행함. 동시 실행은 Parallel: yes끼리만 함. implementer는 자기 Files만 고치고 commit하지 않으며, ticket commit은 orchestrator가 함. 실행 목표에 `subagent` ticket이나 동시 실행이 없었다면 그 부분은 UNKNOWN | 실행 | ticket 파일, 세션 기록(subagent 호출), `git log --stat` |
| C1 goal의 Evaluation [합의 Q26] | define이 여전히 Evaluation을 요구함. 실행 목표의 goal.md에 R·C마다 Evaluation이 있음 | 정적 + 실행 | define SKILL.md, 실행 goal.md |
| C2 ticket check [합의 Q26] | 실행 목표의 모든 ticket에 Checks가 있음. Execute가 ticket마다 Checks 결과를 남김 | 실행 | ticket 파일, 세션 기록 |
| C3 하네스 [합의 Q26] | 사용자가 실행에 쓴 하네스에서 R1~R5가 PASS면 충족. 다른 하네스는 평가하지 않음 | 실행 | 위 증거 |
| C4 미니멀·중복 없음 [합의 Q26] | 같은 규칙(commit 규칙 등)이 두 파일 이상에 없음. 사용자가 고친 스킬을 읽고 "한눈에 읽힌다"고 확인함 | 정적 + 사용자 검토 | grep 결과, 사용자 답 |
| C5 Matt 원문 [합의 Q43] | workflow-plan, workflow-execute, tdd의 SKILL.md가 D-plan, D-execute, D-tdd와 일치함. "그대로" 행은 원문과 글자까지 같고, 일부 바꿈·바꿈·새 문장은 goal.md의 결과 문장과 같고, 지도에 없는 문장은 없음. tdd의 `tests.md`·`mocking.md`와 codebase-design 세 파일은 원문과 diff가 없음. 같은 대조로 analysis, define, verify, AGENTS.md도 각 문장 지도(D-analysis, D-define, D-verify, D-agents)와 일치함 | 정적: 원문 문장마다 `grep -F`, `diff`. Verify에서 문장별 대조표를 만든다 | 대조표(`.goal/workflow-skill-fix-3/` 안), diff 결과 |
