# C5 문장별 대조표 (workflow-skill-fix-3)

작성: 2026-10-25, 독립 판정 subagent. 기준: `goal.md` Deliverable의 문장 지도(D-plan, D-execute, D-tdd, D-analysis, D-define, D-verify, D-agents)와 Evaluation C5.

## 판정 방식

- 판정자: 이전 맥락이 없는 판정용 subagent. 구현자의 완료 주장은 쓰지 않음.
- 읽은 것: `goal.md`, Deliverable의 산출물(workflow-plan, workflow-execute, tdd 3파일, codebase-design 3파일, workflow-analysis, workflow-define, workflow-verify SKILL.md, AGENTS.md), 원문(`docs/matt-skills/to-tickets/SKILL.md`, `implement-spec/SKILL.md`, `tdd/`, `codebase-design/`), `git log --stat bd29585..HEAD`, `git diff bd29585..HEAD -- <산출물>`, `git show bd29585:<한국어 스킬·AGENTS.md>`.
- 읽지 않은 것: `plan.md`, `handoff.md`, `analysis.md`, `tickets/`, plan.md의 diff, 다른 `.goal/` 폴더.
- 방법: `/tmp/c5verify/c5.py`(`python3 -I`)가 지도 행마다 기대 문장을 만든다. "그대로" 행은 원문(또는 `bd29585` 판) 줄을 줄 번호로 가져오고, 바꿈·일부 바꿈·새 문장 행은 goal.md의 결과 문장을 쓰되 그 문장이 goal.md에 글자 그대로 있는지 `assert`로 확인한다. 행마다 (a) 기대 줄이 산출물에 정확히 있는지(`grep -Fx`와 같음), (b) 같은 줄에 이어 쓴 문장은 부분 문자열로 있는지(`grep -F`와 같음), (c) 빼기 행의 문장·핵심어가 0건인지 센다. 그리고 지도 순서대로 기대 파일 전체를 재구성해 실제 파일과 `diff -u`한다. diff가 비면 모든 행이 순서까지 일치하고 지도에 없는 문장도 없다는 뜻이다.
- 보조 확인: 원문 "그대로" 줄마다 셸 `grep -Fxc`(plan 29줄, execute 5줄 모두 1), 빼기 핵심어 `grep -n -i -E "worktree|integration branch|code-review|issue tracker|setup-matt|expand–contract|draft PR|merger"` → 0건(exit 1).
- 해석 규칙(판정에 영향 없음): 빈 줄과 frontmatter `---`는 문장이 아니라 구조로 본다. D-execute N4·N5·E16의 앞 들여쓰기 3칸은 원문 28-30줄 하위 목록의 들여쓰기를 따른 것으로 본다. P32의 `<local-ticket-template>` 태그 두 줄은 원문 69·82줄(지도 범위 69-82 안)로 본다. D-define F3를 16줄 끝에 이어 쓸 때의 구분자(". ")는 지도에 없으므로 판정하지 않는다.

## 파일별 요약 (스크립트 출력)

| 지도 | 일치 | 불일치 | 재구성 diff | 지도에 없는 줄 |
|---|---|---|---|---|
| D-plan | 42 | 0 | diff 없음 | 0 |
| D-execute | 29 | 0 | diff 없음 | 0 |
| D-tdd | 8 | 0 | diff 없음 | 0 |
| D-analysis | 3 | 0 | diff 없음 | 0 |
| D-define | 7 | 1 | diff 2줄 | 1 |
| D-verify | 5 | 0 | diff 없음 | 0 |
| D-agents | 4 | 0 | diff 없음 | 0 |

### D-plan: `.agents/skills/workflow-plan/SKILL.md` ← `docs/matt-skills/to-tickets/SKILL.md`

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| P1 | 2 | 바꿈 | name: workflow-plan | L2 | 일치 |
| P2 | 3 | 바꿈 | description: Break goal.md into a set of tracer-bullet tickets, each declaring its blocking edges, written as one file per ticket. Use for the Plan phase. | L3 | 일치 |
| P3 | 4 | 그대로 | disable-model-invocation: true | L4 | 일치 |
| P4 | 7 | 바꿈 | # Plan | L7 | 일치 |
| P5 | 9 | 일부 바꿈 | Break `goal.md` into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it. | L9 | 일치 |
| P6 | 11 | 빼기 | (삭제: `issue tracker and triage label`, `setup-matt-pocock-skills` 이 없어야 함) | `issue tracker and triage label` 0건; `setup-matt-pocock-skills` 0건 | 일치 |
| P7 | 13 | 그대로 | ## Process | L11 | 일치 |
| P8 | 15 | 그대로 | ### 1. Gather context | L13 | 일치 |
| P9 | 17 첫 문장 | 일부 바꿈 | Work from `.goal/<goal>/goal.md`: read it in full. | L15 안에 있음 | 일치 |
| P10 | 17 둘째 문장 | 빼기 | (삭제: `If the user passes a reference`, `fetch it and read its full body` 이 없어야 함) | `If the user passes a reference` 0건; `fetch it and read its full body` 0건 | 일치 |
| N1 | (P9 뒤) | 새 문장 | Do not interview the user. If a ticket would need a decision goal.md does not record, stop and tell the user to return to Define and update goal.md. <br>※ P9와 같은 줄(L15)에 이어 씀 | L15 안에 있음 | 일치 |
| P11 | 19 | 그대로 | ### 2. Explore the codebase (optional) | L17 | 일치 |
| P12 | 21 첫 문장 | 그대로 | If you have not already explored the codebase, do so to understand the current state of th… <br>※ P13을 뺀 결과 줄 전체가 원문 첫 문장과 같아야 함 | L19 | 일치 |
| P13 | 21 둘째 문장 | 빼기 | (삭제: `domain glossary`, `ADRs` 이 없어야 함) | `domain glossary` 0건; `ADRs` 0건 | 일치 |
| P14 | 23 | 그대로 | Look for opportunities to prefactor the code to make the implementation easier. "Make the … | L21 | 일치 |
| P15 | 25 | 그대로 | ### 3. Draft vertical slices | L23 | 일치 |
| P16 | 27 | 그대로 | Break the work into **tracer bullet** tickets. | L25 | 일치 |
| P17 | 29-36 | 그대로 | <vertical-slice-rules> / - Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests):… / - A completed slice is demoable or verifiable on its own / - Each slice is sized to fit in a single fresh context window / - Any prefactoring should be done first / </vertical-slice-rules> | L27; L29; L30; L31; L32; L34 | 일치 |
| P18 | 38 | 그대로 | Give each ticket its **blocking edges**: the other tickets that must complete before it ca… | L36 | 일치 |
| N2 | (P18 뒤) | 새 문장 | Give each ticket an **Owner**: `main` when doing it directly is quicker, `subagent` when it can run alongside other tickets or needs enough reading to weigh down the main session, `HITL` when the user does it or does it with you. | L38 | 일치 |
| N3 | (새) | 새 문장 | Mark a ticket **Parallel: yes** only when it can finish on its own and touches no file another ticket touches. | L40 | 일치 |
| N4 | (새) | 새 문장 | Give each ticket **Checks**, each one a condition and how to check it. A ticket that changes code writes its Checks as tests at the seams goal.md's Evaluation names. | L42 | 일치 |
| N5 | (새) | 새 문장 | Every requirement in goal.md is covered by at least one ticket; list them under **Covers**. | L44 | 일치 |
| P19 | 40 | 빼기 | (삭제: `Wide refactors`, `expand–contract`, `blast radius` 이 없어야 함) | `Wide refactors` 0건; `expand–contract` 0건; `blast radius` 0건 | 일치 |
| P20 | 42 | 그대로 | ### 4. Quiz the user | L46 | 일치 |
| P21 | 44 | 그대로 | Present the proposed breakdown as a numbered list. For each ticket, show: | L48 | 일치 |
| P22 | 46-48 | 그대로 | - **Title**: short descriptive name / - **Blocked by**: which other tickets (if any) must complete first / - **What it delivers**: the end-to-end behaviour this ticket makes work | L50; L51; L52 | 일치 |
| N6 | (P22 뒤) | 새 문장 | - **Owner**: main, subagent, or HITL | L53 | 일치 |
| P23 | 50-54 | 그대로 | Ask the user: / - Does the granularity feel right? (too coarse / too fine) / - Are the blocking edges correct: does each ticket only depend on tickets that genuinely g… / - Should any tickets be merged or split further? | L55; L57; L58; L59 | 일치 |
| P24 | 56 | 그대로 | Iterate until the user approves the breakdown. | L61 | 일치 |
| P25 | 58 | 바꿈 | ### 5. Write the tickets | L63 | 일치 |
| P26 | 60 첫 문장 | 일부 바꿈 | Write the approved tickets. | L65 | 일치 |
| P27 | 60 둘째 문장 | 빼기 | (삭제: `depends on the tracker`, `shape of the blocking edges` 이 없어야 함) | `depends on the tracker` 0건; `shape of the blocking edges` 0건 | 일치 |
| P28 | 62 | 일부 바꿈 | Write one file per ticket under `.goal/<goal>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file. | L67 | 일치 |
| P29 | 63 | 빼기 | (삭제: `A real issue tracker`, `ready-for-agent`, `sub-issue` 이 없어야 함) | `A real issue tracker` 0건; `ready-for-agent` 0건; `sub-issue` 0건 | 일치 |
| P30 | 65 | 그대로 | Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain t… | L69 | 일치 |
| P31 | 67 | 빼기 | (삭제: `parent issue` 이 없어야 함) | `parent issue` 0건 | 일치 |
| P32 | 69-82 | 일부 바꿈 | <local-ticket-template> / # <NN>: <Ticket title> / **What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list. / **Covers:** the goal.md requirements this ticket serves. / **Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)". / **Files:** the files this ticket changes. / **Owner:** main \| subagent \| HITL / **Parallel:** yes \| no / **Status:** ready / **Checks:** / - [ ] <condition>: <how to check> / - [ ] <condition>: <how to check> / </local-ticket-template> <br>※ 기대 = 원문 69·82줄의 `<local-ticket-template>` 태그(원문 줄, 지도 범위 69-82 안) + goal.md 템플릿 블록 20줄 | L71; L73; L75; L77; L79; L81; L83; L85; L87; L89; L91,92; L91,92; L94 | 일치 |
| P33 | 84-103 | 빼기 | (삭제: `<issue-template>`, `## Parent`, `Acceptance criteri` 이 없어야 함) | `<issue-template>` 0건; `## Parent` 0건; `Acceptance criteri` 0건 | 일치 |
| P34 | 105 첫 문장 | 일부 바꿈 | Avoid code snippets: they go stale fast. | L96 안에 있음 | 일치 |
| P35 | 105 나머지 | 그대로 | Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits. <br>※ P34와 같은 줄(L96) | L96 안에 있음 | 일치 |
| N7 | (끝) | 새 문장 | Done when the user has approved the breakdown and every ticket file has Checks, or "No checks needed" with the reason. | L98 | 일치 |

행 판정: 일치 42 / 불일치 0

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
(차이 없음)
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 없음

### D-execute: `.agents/skills/workflow-execute/SKILL.md` ← `docs/matt-skills/implement-spec/SKILL.md`

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| E1 | 2 | 바꿈 | name: workflow-execute | L2 | 일치 |
| E2 | 3 | 바꿈 | description: Implement the tickets from the Plan phase, with the main session as orchestrator. Use for the Execute phase. | L3 | 일치 |
| E3 | 4 | 그대로 | disable-model-invocation: true | L4 | 일치 |
| E4 | 7 | 일부 바꿈 | You have been provided a goal: `.goal/<goal>/goal.md`. This goal should have tickets associated with it under `.goal/<goal>/tickets/`, describing how to implement the goal. | L7 | 일치 |
| E5 | 9 | 빼기 | (삭제: `issue tracker should have been provided`, `setup-matt-pocock-skills` 이 없어야 함) | `issue tracker should have been provided` 0건; `setup-matt-pocock-skills` 0건 | 일치 |
| E6 | 11 | 일부 바꿈 | The aim is the entire goal implemented on the current branch, with every ticket marked done in its file. | L9 | 일치 |
| E7 | 13 | 그대로 | The tickets are not a list of steps. They are a **task graph** with blocking relationships… | L11 | 일치 |
| E8 | 15 | 일부 바꿈 | Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to goal.md, the ticket file, research notes, and previous commits. Don't duplicate information already available via pointers. <br>※ 원문 15줄에서 "to the spec, tickets, research notes, and previous commits" → "to goal.md, the ticket file, research notes, and previous commits"만 바꾼 줄 | L13 | 일치 |
| E9 | 17 | 그대로 | **Implementer subagents** should be run in the background where possible for maximum concu… | L15 | 일치 |
| N1 | (E9 뒤) | 새 문장 | You are the **orchestrator**: you pick the next tickets, hand them out, record their status, and commit them. | L17 | 일치 |
| N2 | (새) | 새 문장 | Work each ticket by its **Owner**: do `main` tickets yourself, give `subagent` tickets to implementer subagents, and work `HITL` tickets with the user, asking for what they need to do and checking the result. When a `main` ticket changes code, call the Skill tool with `tdd` to build it. | L19 | 일치 |
| N3 | (새) | 새 문장 | Run tickets at the same time only when they are on the frontier and marked **Parallel: yes**; run the rest one at a time. | L21 | 일치 |
| E10 | 19 | 그대로 | ## Steps | L23 | 일치 |
| E11 | 21 | 일부 바꿈 | 1. Read goal.md and the tickets to understand the task graph. | L25 | 일치 |
| E12 | 23 | 그대로(번호 2) | 2. (optional) Use an **exploration subagent** to conduct any exploration required by the t… | L27 | 일치 |
| E13 | 25 | 빼기 | (삭제: `Create the integration branch`, `draft PR` 이 없어야 함) | `Create the integration branch` 0건; `draft PR` 0건 | 일치 |
| E14 | 27 | 일부 바꿈 | 3. Use **implementer subagents** to implement each `subagent` ticket. Each implementer subagent: | L29 | 일치 |
| E15 | 28 | 빼기 | (삭제: `confirms its worktree`, `worktree` 이 없어야 함) | `confirms its worktree` 0건; `worktree` 0건 | 일치 |
| E16 | 29 | 일부 바꿈 |    - calls the Skill tool with `tdd` to build the ticket when the ticket changes code; <br>※ 들여쓰기 3칸은 원문 28-30줄의 하위 목록 들여쓰기 | L30 | 일치 |
| N4 | (새 줄) | 새 문장 |    - changes only its ticket's Files, and reports anything it notices outside them instead of fixing it; <br>※ 들여쓰기 3칸(원문 하위 목록 형식) | L31 | 일치 |
| N5 | (새 줄) | 새 문장 |    - runs its ticket's Checks and reports the evidence, without committing. <br>※ 들여쓰기 3칸(원문 하위 목록 형식) | L32 | 일치 |
| E17 | 30 | 빼기 | (삭제: `merges the integration branch tip`, `integration branch` 이 없어야 함) | `merges the integration branch tip` 0건; `integration branch` 0건 | 일치 |
| E18 | 32 | 일부 바꿈 | 4. Once a ticket completes, check the evidence for its Checks, write its status and Check results into the ticket file, and commit only the ticket's Files and the ticket file. | L34 | 일치 |
| E19 | 34 | 일부 바꿈 | 5. If this changes the **frontier** of available tickets, start the newly available tickets. This allows for maximum concurrency. | L36 | 일치 |
| E20 | 36 | 빼기 | (삭제: `code-review`, `code review` 이 없어야 함) | `code-review` 0건; `code review` 0건 | 일치 |
| E21 | 38 | 바꿈 | 6. Report each ticket's status and Check results, and anything implementers reported outside their Files. | L38 | 일치 |
| E22 | 40 | 빼기 | (삭제: `Clean up all`, `merger subagent` 이 없어야 함) | `Clean up all` 0건; `merger subagent` 0건 | 일치 |
| N6 | (끝) | 새 문장 | If a ticket turns out wrong, fix the ticket files yourself when no user decision is involved; otherwise stop and tell the user to return to Define and update goal.md. | L40 | 일치 |
| N7 | (끝) | 새 문장 | Done when every ticket file shows done, incomplete, or blocked, with its Check results. | L42 | 일치 |

행 판정: 일치 29 / 불일치 0

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
(차이 없음)
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 없음

### D-tdd: `.agents/skills/tdd/SKILL.md` ← `docs/matt-skills/tdd/SKILL.md`

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| (나머지) | 1-21 | 그대로 | --- / name: tdd / description: Test-driven development. Use when the user wants to build features or fix bug… / --- / # Test-Driven Development / TDD is the red → green loop. This skill is the reference that makes that loop produce test… / When exploring the codebase, read `GLOSSARY.md` (if it exists) so test names and interface… / ## What a good test is / Tests verify behavior through public interfaces, not implementation details. Code can chan… / See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines. / ## Seams: where tests go / A **seam** is the public boundary you test at: the interface where you observe behavior wi… | L1,4; L2; L3; L1,4; L6; L8; L10; L12; L14; L16; L18; L20 | 일치 |
| T1 | 22 둘째 문장 | 바꿈 | The seams under test are agreed up front: the ones goal.md's Evaluation names, which the ticket's Checks test. | L22 안에 있음 | 일치 |
| T1-del | 22 둘째 문장 | (T1의 옛 문장) | (삭제: `Before writing any test, write down the seams under test and confirm them with the user.` 이 없어야 함) | `Before writing any test, write down the seams under test and confirm them with the user.` 0건 | 일치 |
| T2 | 22 나머지 세 문장 | 그대로 | **Test only at pre-agreed seams.** + No test is written at an unconfirmed seam. + You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case. | L22 안에 있음; L22 안에 있음; L22 안에 있음 | 일치 |
| T3 | 24 | 빼기 | (삭제: `What's the public interface, and which seams should we test?`, `Give each proposed seam a one-line note` 이 없어야 함) | `What's the public interface, and which seams should we test?` 0건; `Give each proposed seam a one-line note` 0건 | 일치 |
| (나머지) | 26 codebase-design 문장 | 그대로 | When the shape of that interface is itself in question (how deep the module is, where the … | L24 | 일치 |
| (나머지) | 27-37 | 그대로 | ## Anti-patterns / - **Implementation-coupled**: mocks internal collaborators, tests private methods, or veri… / - **Tautological**: the assertion recomputes the expected value the way the code does (`ex… / - **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests ver… / ## Rules of the loop / - **Red before green.** Write the failing test first, then only enough code to pass it. Do… / - **One slice at a time.** One seam, one test, one minimal implementation per cycle. | L26; L28; L29; L30; L32; L34; L35 | 일치 |
| T4 | 38 둘째 문장 | 일부 바꿈 | - **Refactoring is not part of the loop.** It belongs to the review stage, not the red → green implementation cycle. <br>※ 원문 38줄에서 " (see the `code-review` skill)"만 뺀 줄 | L36 | 일치 |

행 판정: 일치 8 / 불일치 0

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
(차이 없음)
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 없음

### D-analysis: `.agents/skills/workflow-analysis/SKILL.md` (before = `git show bd29585:`)

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| (나머지) | 1-18 | 그대로 | --- / name: workflow-analysis / description: 사용자가 문제를 이해하도록 개념, 맥락, 핵심 문제를 탐색한다. 목표 구체화 전에 이해가 필요한 Analysis 작업에 사용한다. / --- / # Analysis / 사용자가 제공한 목표와 배경을 바탕으로, / 사용자가 문제를 충분히 이해할 수 있도록 다음 요소를 탐색하고 설명한다. / - Concept: 이해에 필요한 개념과 원리 / - Context: 배경과 현재 상황 / - Problem: 해결하거나 탐색해야 할 핵심 문제 / 이미 제공된 정보는 활용하고, 부족한 정보만 질문한다. / 근거가 부족한 내용은 추측으로 단정하지 않고 불확실성을 명시한다. / 목표의 구체화는 Define에서 진행한다. | L1,4; L2; L3; L1,4; L6; L8; L9; L11; L12; L13; L15; L16; L18 | 일치 |
| A1 | 19 | 일부 바꿈 | Concept, Context, Problem이 각각 설명되고, 남은 불확실성이 목록으로 `.goal/<goal>/analysis.md`에 적히면 끝. | L19 | 일치 |
| A1-del | 19 옛 문장 | (바뀐 옛 줄) | (삭제: `남은 불확실성이 목록으로 적히면 끝.` 이 없어야 함) | `남은 불확실성이 목록으로 적히면 끝.` 0건 | 일치 |

행 판정: 일치 3 / 불일치 0

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
(차이 없음)
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 없음

### D-define: `.agents/skills/workflow-define/SKILL.md` (before = `git show bd29585:`)

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| (나머지) | 1-9 | 그대로 | --- / name: workflow-define / description: workflow-grill로 사용자를 인터뷰해 목표를 Objective, Deliverable, Requirements, Constrain… / --- / # Define / `workflow-grill` 스킬을 로드해, 사용자가 제공한 목표·현재 상황·조건에서 출발해 인터뷰하고, / 결과를 goal.md에 나열식·계층적으로 기록한다. | L1,4; L2; L3; L1,4; L6; L8; L9 | 일치 |
| F1 | (9 뒤) | 새 문장 | `.goal/<goal>/analysis.md`가 있으면 먼저 읽고, 그 남은 불확실성을 첫 질문 후보로 쓴다. | L10 | 일치 |
| F2 | (F1 뒤) | 새 문장 | 질문마다 그 질문에 필요한 배경과 용어를 먼저 설명한다. | L11 | 일치 |
| (나머지) | 10-15 | 그대로 | - Objective: 궁극적으로 달성하려는 상태 / - Deliverable: 완성됐을 때 산출물이 어떤 모습인지. 읽는 사람이 이상한 점을 알아볼 수 있는 해상도로 / - Requirements: 목표 달성을 위해 만족해야 하는 조건 / - Constraints: 목표 달성 과정에서 지켜야 하는 제약 / - Out of scope: 이번 목표에서 하지 않기로 한 것 | L13; L14; L15; L16; L17 | 일치 |
| F3 | 16 줄 끝 | 새 구절 | - Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유 + 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다. <br>※ 원문 16줄 끝은 마침표 없이 "그 이유"로 끝남. 이어 쓸 때의 구분자는 지도에 없어 재구성에서는 ". "로 둠(판정 대상 아님) | L18 안에 있음; 없음; 가장 가까운 줄: “- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유. 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다” | 불일치 |
| F4 | 18 앞 두 문장 | 바꿈 | tree는 Plan이 사용자에게 다시 묻지 않고 ticket을 만들 수 있을 때까지 내려간다. 위 여섯 항목의 미결정이 질문 대상이며, <br>※ 같은 줄의 "위 여섯 항목의 미결정이 질문 대상이며,"는 그대로 | L20 | 일치 |
| F4-del | 18 옛 문장 | (바뀐 옛 문장) | (삭제: `tree는 Deliverable까지 내려간다`, `만드는 순서와 방법만 Plan에서 정한다` 이 없어야 함) | `tree는 Deliverable까지 내려간다` 0건; `만드는 순서와 방법만 Plan에서 정한다` 0건 | 일치 |
| (나머지) | 19-23 | 그대로 | Requirement나 Constraint가 정해지면 "어떻게 확인하나"가 그 자식 질문으로 frontier에 오른다. / Round마다 goal.md를 갱신하고, 합의·미결정·가정을 구분해 적는다. / 실제 검증은 Verify에서 진행한다. / frontier가 비고, Requirements와 Constraints 항목마다 Evaluation 항목이나 "평가 불필요"와 그 이유가 적히면 끝. | L21; L22; L24; L25 | 일치 |

행 판정: 일치 7 / 불일치 1

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
--- expected(지도로 재구성)
+++ artifact
@@ -18 +18 @@
-- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유. 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다.
+- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유. 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 
- L18 “- Evaluation: Requirements와 Constraints 항목마다 Criteria(성공 조건), Method(확인 방법), Evidence(판단 증거). 평가가 불필요한 항목은 그 이유. 코드를 만드는 목표면 `codebase-design` 스킬을 로드해, Method에 테스트할 seam(공개 인터페이스)을 그 용어로 적는다”

### D-verify: `.agents/skills/workflow-verify/SKILL.md` (before = `git show bd29585:`)

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| (나머지) | 1-12 | 그대로 | --- / name: workflow-verify / description: goal.md의 Evaluation을 기준으로 객관적 증거를 확보하고 PASS, FAIL, UNKNOWN과 미충족 사항을 판단한다. 목표 … / --- / # Verify / goal.md의 Evaluation을 기반으로 다음 요소를 중심으로 검증한다. / - Evidence: 평가 기준을 판단할 객관적인 증거 확보 / - Assessment: 기준과 증거를 비교하여 PASS / FAIL / UNKNOWN 판단 / - Gap: 미충족 사항과 추가 확인이 필요한 사항 식별 | L1,4; L2; L3; L1,4; L6; L8; L10; L11; L12 | 일치 |
| V1 | (12 뒤) | 새 문장 | 판정은 판정용 subagent에게 맡긴다. subagent에게는 goal.md, goal.md Deliverable에 적힌 산출물 경로, Plan 끝 commit 이후의 git 기록만 넘기고, ticket 파일(Execute의 완료 기록)은 넘기지 않는다. | L14 | 일치 |
| V2 | (V1 뒤) | 새 문장 | 결과는 `.goal/<goal>/verify.md`에 쓰고, 판정 방식(누가, 무엇을 받아 판정했는지)을 함께 적는다. | L15 | 일치 |
| (나머지) | 14-19 | 그대로 | Agent의 완료 주장은 충분한 증거가 아니다. / 실제 실행 결과나 관찰 근거를 확보하고, 각 판단의 근거를 명확하게 제시한다. / 증거가 부족하거나 확인할 수 없는 항목은 UNKNOWN으로 표시한다. / goal.md에 Evaluation이 없거나 기준이 불명확하면 사용자에게 확인한다. / 미충족 사항은 적절한 단계에서 다시 다룰 수 있도록 정리한다. | L17; L18; L19; L20; L22 | 일치 |
| V3 | (끝) | 새 문장 | Evaluation 항목마다 PASS, FAIL, UNKNOWN과 그 근거가 verify.md에 적히면 끝. | L23 | 일치 |

행 판정: 일치 5 / 불일치 0

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
(차이 없음)
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 없음

### D-agents: `AGENTS.md` (before = `git show bd29585:`)

| # | 원문 줄 | 처리 | 기대 결과 | 실제 | 판정 |
|---|---|---|---|---|---|
| (나머지) | 1-19 | 그대로 | ## Workflow / Follow a dynamic workflow based on task requirements. / - Analysis: Understand the problem. / - Define: Specify goals and evaluation criteria. / - Plan: Design the execution process and its evaluation. / - Execute: Perform tasks, check progress, and adapt. / - Verify: Validate goal achievement with evidence. / ### Principles / - Execute only necessary phases. / - Skip phases when their objectives are already satisfied. / - Revisit earlier phases when necessary. / - Verify outcomes using objective evidence. / - Proceed to another phase only when the user asks. / ### Working documents / Keep working documents under `.goal/<goal>/` in the current working directory. | L1; L3; L5; L6; L7; L8; L9; L11; L12; L13; L14; L15; L16; L18; L19 | 일치 |
| G1 | (19 뒤) | 새 문장 | Each phase leaves its document there: `analysis.md`, `goal.md`, `tickets/`, `verify.md`. | L20 | 일치 |
| (나머지) | 20 | 그대로 | Reuse the goal folder name agreed with the user; if the target is unclear, confirm it firs… | L21 | 일치 |
| G2 | (끝, 새 절) | 새 문장 | ### Commits / Commit when a phase meets its end condition: Analysis, Define, Plan, each ticket in Execute, and Verify. Do not ask first. / Stage only the files that phase changed (`git add <files>`, never `-A`). Do not commit mid-Round in Define or Plan. / If the directory is not a git repository, skip committing and say so. / Message: `<phase>(<goal>): <summary>`, for example `define(workflow-skill-fix-3): goal.md` or `execute(workflow-skill-fix-3): 03 <ticket title>`. | L23; L24; L25; L26; L27 | 일치 |

행 판정: 일치 4 / 불일치 0

지도로 재구성한 기대 파일 vs 실제 파일 `diff -u` (n=0):

```
(차이 없음)
```

재구성 기대 파일에 없는(지도에 없는) 실제 줄: 없음


※ D-define의 "지도에 없는 실제 줄" L18은 F3 줄 자체다(위 F3 불일치로 집계). 별도의 지도 밖 문장은 아니다. 차이는 줄 끝 마침표 1자: goal.md 결과 문장은 `…그 용어로 적는다.`, 산출물 `workflow-define/SKILL.md:18`(변경 전 16줄)은 `…그 용어로 적는다`로 끝난다. 같은 파일의 F1(L10)·F2(L11)는 마침표가 있다.

### D-analysis, D-define, D-verify, D-agents: `git diff bd29585..HEAD` 덩어리와 지도 행 대응

- workflow-analysis: 덩어리 1개(@@ -16,4 +16,4 @@), 19줄 교체 = A1. 그 밖의 줄 변경 없음.
- workflow-define: 덩어리 1개(@@ -7,15 +7,17 @@), +2줄(9 뒤) = F1·F2, 16줄 교체 = F3, 18줄 교체 = F4. 그 밖의 줄 변경 없음.
- workflow-verify: 덩어리 1개(@@ -11,9 +11,13 @@), +3줄(12·13 뒤: V1, V2, 빈 줄) = V1·V2, 끝 +1줄 = V3. 그 밖의 줄 변경 없음.
- AGENTS.md: 덩어리 1개(@@ -17,4 +17,11 @@), 19 뒤 +1줄 = G1, 끝 +6줄(빈 줄 + `### Commits` 블록 5줄) = G2. 그 밖의 줄 변경 없음.

## 원문과 diff (D-tdd의 그대로 파일, codebase-design)

`diff docs/matt-skills/<f> .agents/skills/<f>` 와 `shasum -a 256`:

| 파일 | diff exit | sha256 (원문 = 산출물) |
|---|---|---|
| `tdd/tests.md` | 0 (차이 없음) | 859f9e592c188fda… = 859f9e592c188fda… |
| `tdd/mocking.md` | 0 (차이 없음) | 3ceb807fdf4a47d6… = 3ceb807fdf4a47d6… |
| `codebase-design/SKILL.md` | 0 (차이 없음) | 2c20617f87ec8af6… = 2c20617f87ec8af6… |
| `codebase-design/DEEPENING.md` | 0 (차이 없음) | f3dd099ce99289bd… = f3dd099ce99289bd… |
| `codebase-design/DESIGN-IT-TWICE.md` | 0 (차이 없음) | 52b52e75655a27ae… = 52b52e75655a27ae… |

`agents/openai.yaml`: 원문 `docs/matt-skills/tdd/agents/`, `docs/matt-skills/codebase-design/agents/`에는 있고, `.agents/skills/tdd/`, `.agents/skills/codebase-design/`에는 없다(`ls -a` 결과: tdd = mocking.md, SKILL.md, tests.md / codebase-design = DEEPENING.md, DESIGN-IT-TWICE.md, SKILL.md). 지도대로다.

`diff docs/matt-skills/tdd/SKILL.md .agents/skills/tdd/SKILL.md` 원문 출력(덩어리 3개 = T1, T3, T4. 그 밖의 줄은 같음):

```
22c22
< **Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.
---
> **Test only at pre-agreed seams.** The seams under test are agreed up front: the ones goal.md's Evaluation names, which the ticket's Checks test. No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.
24,25d23
< Ask: "What's the public interface, and which seams should we test?" Give each proposed seam a one-line note on what it catches and what it misses.
< 
38c36
< - **Refactoring is not part of the loop.** It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle.
---
> - **Refactoring is not part of the loop.** It belongs to the review stage, not the red → green implementation cycle.
```

## 요약

| 파일 | 일치 | 불일치 | 지도에 없는 문장 |
|---|---|---|---|
| workflow-plan (D-plan) | 42 | 0 | 없음 |
| workflow-execute (D-execute) | 29 | 0 | 없음 |
| tdd SKILL.md (D-tdd) | 8 | 0 | 없음 |
| tdd tests.md, mocking.md | diff 없음 | - | - |
| codebase-design 3파일 | diff 없음 | - | - |
| workflow-analysis (D-analysis) | 3 | 0 | 없음 |
| workflow-define (D-define) | 7 | 1 (F3 끝 마침표 없음) | 없음 |
| workflow-verify (D-verify) | 5 | 0 | 없음 |
| AGENTS.md (D-agents) | 4 | 0 | 없음 |

C5 정적 판정: FAIL. 불일치 1건, D-define F3 끝 마침표 1자(`workflow-define/SKILL.md:18`(변경 전 16줄)). 나머지는 모두 지도와 글자까지 같다.
