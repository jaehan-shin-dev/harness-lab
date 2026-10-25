# Goal: workflow-handoff 스킬 만들기

작성: 2026-10-24, Round 6 반영. Define 종료(frontier 비어 있음, 사용자가 공동 이해 도달을 확인함). 근거 자료: `analysis.md`
갱신: 2026-10-25, Plan Round 3의 Q13을 Evaluation(C2 Method, R2·R3·R5 근거)에 반영
표기: [합의] 사용자 확정 / [사실] 확인된 환경 / [가정] 내가 세운 가정이고 확인이 필요

## Objective

[합의 Q1] compact 품질이 아쉬우므로, 사용자가 compact되기 전에 이 스킬을 직접 불러 상태를 남기고, 새 세션에서 그 상태로 이어서 작업한다. 검증된 원문(pstack, Matt handoff)을 최대한 그대로 쓴다.

## Deliverable

[합의 Q9, Q10] 파일 하나: `.agents/skills/workflow-handoff/SKILL.md`. `agents/openai.yaml`과 CREDITS.md는 두지 않는다
[합의 Q9] SKILL.md 본문은 두 부분이다
  1. 저장 절차(D1): 사용자가 부르면 멈추고, 커밋하고, handoff 문서를 쓰고, 보고한다
  2. "How to resume" 블록(D2): handoff 문서 끝에 그대로 복사해 넣을 재개 규칙
[합의 Q5] handoff 문서: `.goal/<goal>/handoff.md` 한 개. 부를 때마다 덮어쓴다
[합의 Q17] 언어 지시는 두지 않는다. 본문은 대화 언어로 쓰이고, 재개 블록만 원문 영어로 복사된다
사용 흐름
  1. 이전 세션: 사용자가 부른다. Claude Code `/workflow-handoff`, pi `/skill:workflow-handoff`, Codex `$workflow-handoff`
  2. 에이전트가 진행 중인 원자 단계를 끝내거나 되돌린다(goal.md/plan.md 갱신 포함) → 이 세션에서 바꾼 파일만 `wip:` 커밋 → handoff.md 작성(그 커밋을 가리킴, 끝에 재개 블록) → 보고(마지막 줄은 새 세션에 붙여 넣을 문장)
  3. 새 세션: 사용자가 "`Read .goal/<goal>/handoff.md and continue.`"를 붙여 넣는다. 세 하네스 모두 같다
  4. 새 에이전트가 재개 블록대로 상태를 다시 세우고, suggested skills로 이어간다

D1 저장 쪽 문장 지도 [합의 Q15, Q20, Q23] (M = Matt handoff, P = pstack pause-safely, H = pstack hillclimb, N = 새 문장). 표의 순서가 SKILL.md 본문 순서다

| # | 처리 | 결과 |
|---|---|---|
| fm | name만 바꿈 | `name: workflow-handoff`. description, argument-hint, `disable-model-invocation: true`는 그대로 |
| M1 | 그대로 | "Write a handoff document summarising the current conversation so a fresh agent can continue the work." |
| M2 | 바꿈 | "Save it to `.goal/<goal>/handoff.md`, overwriting any previous one." |
| P1 | 그대로 | "**You own a clean stop. Leave a checkpoint a cold-start agent can resume from.**" |
| P2 | 뺌 | "This is explicit only…" (사용자만 부르므로) |
| P3 | 그대로 | 1단계 "Stop at a safe boundary. Finish the current atomic step or back out of it. Start nothing new, and cancel any nested subagents." |
| P4 | 그대로 | 2단계 "Take no irreversible action to pause. No PR and no push unless you already had one out." |
| P5 + H | 원문 + 구절 덧붙임 [합의 Q12, Q22, Q23] | 3단계 "Make the work durable. Commit uncommitted edits as one clear `wip:` commit on the current branch so nothing is lost, staging only the files you changed (`git add <files>`, never `-A`). If the tree is broken, say so in the commit body in one line." 현재 브랜치가 main이어도 그대로 |
| P6 | 일부 바꿈 [합의 Q26] | 4단계 "Write the handoff document off-context. Capture intent, what you were doing, the decisions made and why, progress and what's verified, current state, next steps, key files, and gotchas." ("resume note" → "handoff document", K3의 "the decisions made"에 "and why"를 붙여 넣음. goal.md/plan.md에 이미 적힌 결정은 M4대로 경로로 가리킴) |
| P7 | 뺌 | `/tmp/<slug>-resume.md` (M2가 대신함) |
| P8 | 뺌 | show-me-your-work trail (M4와 같은 말) |
| N1 | 뺌 [합의 Q19] | transcript 위치 기록 |
| M3 | 그대로 | "Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for." |
| M4 | 일부 바꿈 | "Do not duplicate content already captured in other artifacts (`goal.md`, `plan.md`, specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead." |
| M5 | 그대로 | "Redact any sensitive information, such as API keys, passwords, or personally identifiable information." |
| N2 | 새 문장 | "End the document with the "How to resume" section below, copied verbatim." |
| M6 | 그대로 | "If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly." |
| P9 | 그대로 [합의 Q12] | Reply: "where you are in the loop, what's on disk versus still in your head (paths, no diff dumps), the commits you made and whether the tree is clean, and the first action on resume. This is a pause, not a final report." |
| N3 | 새 문장 | Reply 끝에 새 세션에 붙여 넣을 한 줄 `Read .goal/<goal>/handoff.md and continue.`를 보여 준다 |

[합의 Q24] 원문 순서(3단계 커밋 → 4단계 문서 작성)를 지킨다. 그래서 handoff.md는 wip 커밋에 들어가지 않고 그 커밋을 가리킨다. 끝난 뒤 작업 트리에는 handoff.md만 남는다

D2 재개 블록 문장 지도 [합의 Q16, Q19] (K = pstack session-pickup)

| # | 처리 | 결과 |
|---|---|---|
| K0 | 바꿈 | "## How to resume" |
| K1 | 그대로 | "**You own the resume point. Read the prior trail, don't redo it.**" |
| K2a~K2d | 뺌 | 1단계 전체(이전 기록 찾기, transcript 읽는 방법, poteto-mode Subagents 절 참조). 재개 블록은 K1 다음 K3으로 이어진다. trail은 handoff.md, goal.md/plan.md, git 기록 |
| K3 | 그대로 | 2단계 "Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it." |
| K4 | 그대로 | 3단계 "Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative." |
| K5 | 바꿈 | "Route the remaining work to the suggested skills above. The pickup ends here. The routed skill owns the rest." (판정 4종 뺌) |
| K6 | 괄호만 뺌 | 5단계 "Verify the inherited claims against the original goal on the real artifact. A passing prior self-report is not the proof." |
| K7 | 그대로 | Reply: "where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome." |

단계 번호는 남은 단계에 맞춰 다시 매긴다(Plan에서 정해도 되는 형식 문제)

## Requirements

R1 호출
  [합의] 사용자가 직접 부른다. Claude Code·pi에서는 에이전트가 스스로 부르지 않는다
  [합의 Q10] Codex는 예외다. openai.yaml을 두지 않으므로 기본값(implicit 허용)이 적용되어 에이전트가 스스로 부를 수도 있다. 이것을 받아들인다
  [사실] Claude Code·pi는 SKILL.md의 `disable-model-invocation: true`를 지킨다(analysis.md)
  [사실] Codex 0.162.1은 이 키 대신 `agents/openai.yaml`의 `policy.allow_implicit_invocation`을 쓰고, 기본값은 true다. 사용자는 `$skill`로 부른다(실행 파일 안 skill-creator 설명)
R2 저장
  [합의 Q5] `.goal/<goal>/handoff.md` 한 개를 덮어쓴다. goal이 불분명하면 AGENTS.md 규칙대로 먼저 확인한다
  [합의 Q24] handoff.md 자체는 커밋하지 않는다(wip 커밋 뒤에 쓰이므로)
R3 사용 범위
  [합의 Q6] 어느 단계(Analysis~Verify), 어느 순간이든 사용자가 부르면 동작한다
  [합의 Q6] 멈추는 지점은 pstack pause 1단계 "Finish the current atomic step or back out of it"이 정한다. 예: Round 중이면 goal.md 갱신을 마치고 멈춘다
R4 (삭제) [합의 Q19] transcript는 쓰지 않는다. "Matt도 따로 보지 않는다"(사용자)
R5 작업물 보존
  [합의 Q12] pstack pause 3단계 원문대로 `wip:` 커밋을 한다. `.goal/` 파일도 커밋 대상이 될 수 있다(사용자)
  [합의 Q20, Q23] 이 세션에서 바꾼 파일만 이름으로 지정해 커밋한다. 문장은 pstack `hillclimb.md:15` 구절 "staging only the files you changed (`git add <files>`, never `-A`)"을 쓴다
  [합의 Q22] main이어도 원문대로 현재 브랜치에 커밋한다
  [합의 Q21] Plan의 사전 작업: harness-lab 폴더에 자체 git 저장소를 만든다(`git init`). 홈 폴더 저장소는 건드리지 않는다
  [사실] 지금 harness-lab에는 자기 저장소가 없다. git 저장소는 홈 폴더 전체(`/Users/sinjaehan/.git`)이고 커밋은 0개다. untracked 목록에 `.ssh/`, `.claude.json`, `.codex/`, `.pi/`(인증 파일 포함), `.zsh_history`가 있다

## Constraints

C1 원문 활용
  [합의 Q3] 영어 원문을 문장 단위로 가져온다. 허용하는 수정은 문장 빼기와 문장 안 일부 바꾸기. 새 문장은 꼭 필요한 곳에만 쓴다(현재 N2, N3 두 개)
  [합의 Q3] 바꾼 곳을 기록하는 CREDITS.md는 두지 않는다. [사실] 사용자가 `workflow-grill/CREDITS.md`를 지웠다
  [합의 Q4, Q23] 원문: Matt `docs/matt-skills/handoff/SKILL.md`, pstack `docs/pstack/skills/poteto-mode/playbooks/pause-safely.md`, `session-pickup.md`, 그리고 `hillclimb.md:15` 구절 하나. gstack과 addy는 쓰지 않는다. Matt `handoff/agents/openai.yaml`은 쓰지 않는다(Q10)
C2 대상 하네스
  [합의 Q7] Claude Code, pi, Codex. 한 하네스에서 저장하고 다른 하네스에서 재개하는 경우는 막지 않지만 평가하지 않는다
  [사실] Codex 0.162.1은 `.agents/skills`를 저장소 스킬 위치로 다룬다(실행 파일 문자열). 실제로 불러 보는 것은 C2 평가 때 확인한다

## Out of scope

[합의 Q8]
- 에이전트가 먼저 handoff를 제안하거나 자동으로 실행하는 것
- compact 자체 튜닝(`## Compact Instructions`, PreCompact hook, pi extension)
- 다른 `workflow-*` 스킬이나 AGENTS.md 수정
- 새 세션을 자동으로 띄우는 것(`claude --bg` 방식). 새 세션은 사용자가 연다
[합의 Q19] 이전 transcript를 읽거나 기록하는 것
[합의 Q14] compact와 직접 비교하는 평가

## Evaluation

[합의 Q13, Q14, Q18 삭제, Q25, Q27, Round 4의 R1 변경, Plan Q13]
[합의 Plan Q13] R2, R3, R5의 판정 근거는 Claude Code 실행 결과만 쓴다. R3의 "pi·Codex는 각자의 중단 키" 구절은 두되 이번에 확인하지 않는다

| 항목 | Criteria | Method | Evidence |
|---|---|---|---|
| R1 호출 | 평가 불필요. 이유: 에이전트가 이 스킬을 스스로 부르지 않는지는 평가할 필요가 없다(사용자). 키는 Matt 원문 그대로이고, Claude Code·pi가 이 키를 지킨다는 것은 [사실] | | |
| R2 저장 | 실행 뒤 `.goal/<goal>/handoff.md`가 생기고, 두 번째 실행에서 덮어써지며, `/tmp`에는 아무것도 쓰지 않음 | 실제 실행 2회 | 파일 목록과 내용 변화 |
| R3 사용 범위 [합의 Q27] | 에이전트가 여러 파일을 고치거나 goal.md를 갱신하는 도중에 사용자가 끊고(Claude Code Esc, pi·Codex는 각자의 중단 키) 바로 부르면, 커밋과 문서 작성 전에 반쯤 된 단계를 끝내거나 되돌리고 그 결과를 handoff.md에 적음 | 중단 시나리오로 실제 실행 1회 | `git show --stat HEAD`, handoff.md, 실행 기록 |
| R5 작업물 보존 | 실행 뒤 현재 브랜치에 `wip:`로 시작하는 커밋 1개. 그 커밋의 파일이 이 세션에서 바꾼 파일과 같음(handoff.md 제외). 세션 전부터 있던 무관한 미커밋 파일은 들어가지 않음. handoff.md가 그 커밋을 가리킴. "깨진 상태면 커밋 본문에 한 줄"은 평가하지 않음(깨진 상태를 일부러 만들기 번거롭고, 원문 그대로인 문장) | harness-lab 자체 저장소(R5 사전 작업)에서 C2를 실행할 때 함께 확인. 시작 전에 무관한 미커밋 파일 하나를 만들어 둠 | `git show --stat HEAD`, `git status`, handoff.md |
| C1 원문 | SKILL.md 문장이 D1, D2 문장 지도와 일치함 | Verify에서 원문과 문장별 대조 | 대조표(`.goal/workflow-handoff/` 안) |
| C2 하네스 | 하네스마다 handoff → 새 세션 → 재개가 끝까지 됨. 새 세션이 상황을 다시 묻지 않고 이미 한 일을 다시 하지 않음. 지금 단계, 미결정 질문, 내린 결정과 이유, 다음 행동 4가지를 사용자에게 묻지 않고 답함 | [합의 Plan Q13] Claude Code는 Verify에서 실행하고 판정(plan.md Q11의 2단계). pi, Codex는 사용자가 나중에 직접 시험하고 결과를 알려 줌. 그전까지 Verify 보고서에 두 하네스는 UNKNOWN(사용자 시험 대기)으로 적고, 결과를 받으면 그 내용으로 판정을 고친다 | handoff.md, 새 세션 transcript. pi, Codex는 사용자 feedback |

## 사실 메모 (R4 삭제로 지금은 참고용)

- compact 전에 handoff하고 새 세션을 열면, 이전 세션 transcript는 요약되지 않은 원본 그대로다
- transcript 위치: Claude Code `CLAUDE_CODE_SESSION_ID` → `~/.claude/projects/<cwd를 바꾼 이름>/<id>.jsonl`, pi `PI_SESSION_FILE`, Codex `CODEX_THREAD_ID` → `~/.codex/sessions/YYYY/MM/DD/rollout-<시각>-<id>.jsonl`. 모두 MB 단위 JSONL
- subagent: Claude Code는 Agent 도구, Codex는 `spawn_agent`. pi는 extension으로만 쓸 수 있고, harness-lab에서는 쓸 수 없다
