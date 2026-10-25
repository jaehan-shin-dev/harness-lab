# Plan: workflow-handoff 스킬 만들기

입력: goal.md (2026-10-24 Define 종료본)
작성: 2026-10-24 Round 1 반영, 2026-10-25 Round 2, 3 반영. Plan 종료(frontier 비어 있음, 작업마다 Checks 또는 "점검 불필요"와 이유가 적힘)
표기: [합의] / [미결정 Qn] / [가정] / [사실]

## Strategy

[합의 Q1] AI 전략: 이 세션에서 직접 작성한다(Interaction). 만들 파일이 SKILL.md 하나라 subagent는 쓰지 않는다
접근 순서: 저장소 준비 → SKILL.md 작성(문장 지도 D1, D2를 그대로 옮김) → 정적 점검 → 사용자 검토 → 커밋 → 평가 준비물 → (Verify) Claude Code 실제 실행과 판정
[합의 Q5] Execute는 T0~T5(준비와 작성)까지다. Verify에서 goal.md Evaluation의 Method대로 실행하고 판정하며, C1 문장별 대조표도 만든다
[합의 Q7] 평가 세션은 사용자가 실행한다(스킬 호출, 중단, 새 세션 열기, 문장 붙여 넣기). AI는 준비물을 만들고, 끝난 뒤 git, handoff.md, transcript를 읽어 판정한다
[합의 Q11, 사용자가 Round 2에서 바꿈] 이번 Verify에서는 Claude Code만 시험한다. pi, Codex는 사용자가 나중에 직접 시험하고 feedback을 준다
[합의 Q13] goal.md에 반영함: C2 Method를 "Claude Code는 Verify에서 판정, pi·Codex는 사용자 시험 결과를 받을 때까지 UNKNOWN(사용자 시험 대기)"으로 바꿈. R2, R3, R5 판정 근거는 Claude Code 실행 결과만 씀

## Decomposition

T0 harness-lab 자체 저장소 (goal R5 사전 작업) [합의 Q2]
  - `git init` (harness-lab 폴더). 홈 폴더 저장소(`/Users/sinjaehan/.git`)는 건드리지 않는다
  - 첫 커밋: 지금 harness-lab에 있는 파일 전부. AI가 실행한다(Q2 답이 승인). `skill-eval/.gitignore`가 `.venv/`, `results/*/runs/`, 캐시를 뺀다
  - [합의 Q10] `.goal/workflow-intent/`는 첫 커밋에서 뺀다. 그 폴더는 intent 세션의 wip 커밋 몫으로 남긴다. `.gitignore`에는 넣지 않고 stage만 하지 않는다(나중에 intent 세션이 커밋할 수 있어야 하므로)
  - [사실] 크기: docs 17M(PDF 포함), skill-eval 82M(이 중 .venv 11M, results 66M 대부분이 runs/), .goal 44K, .agents 28K
T1 SKILL.md 작성 — 의존: 없음(T0과 병행 가능)
  - `.agents/skills/workflow-handoff/SKILL.md`. 원문 문장은 `docs/` 원본에서 복사해 붙인다(손으로 다시 치지 않는다)
  - [합의 Q3] 형식
    - frontmatter 4개 키
    - 맨 위 제목 없음(Matt처럼)
    - 저장 쪽 단계는 번호 목록 1~4
    - Reply는 `**Reply:**` 문단
    - 재개 블록은 ```` ```markdown ```` 코드 블록으로 감싼다. 쓰는 에이전트가 재개 지시를 자기에게 하는 말로 읽지 않게 하려는 것이다. 블록 안 단계 번호는 남은 4단계에 맞춰 1~4로 다시 매긴다
T2 정적 점검 — 의존: T1
T3 사용자 검토 [합의 Q4] — 의존: T2. SKILL.md 초안과 T2 결과를 사용자가 보고 승인한 뒤 T4로 간다
T4 스킬 커밋 — 의존: T0, T3. SKILL.md를 harness-lab 저장소에 커밋한다
T5 평가 준비물(trial kit) — 의존: T4. `.goal/workflow-handoff/trial-kit.md`
  - Claude Code 2단계의 진행 순서, 사용자가 붙여 넣을 문장, 판정 체크리스트(goal.md Evaluation 행과 1:1)
  - 무관한 미커밋 파일로 쓸 빈 파일 하나를 만든다
  - [합의 Q14] 끝에 pi, Codex 수동 시험 메모를 넣는다. 판정하지 않는 메모라 T5 Checks에는 넣지 않는다
    - 호출: pi `/skill:workflow-handoff`, Codex `$workflow-handoff`
    - 이미 떠 있는 세션이 새 스킬을 못 볼 때: pi `/reload`, Codex 다시 시작
    - 새 세션에 붙여 넣을 문장: `Read .goal/<goal>/handoff.md and continue.`
    - 새 세션에 물어볼 4가지: 지금 단계, 미결정 질문, 내린 결정과 이유, 다음 행동
    - git 확인: `git show --stat HEAD`, `git status`
    - 결과는 이 항목 순서대로 받아 C2 판정에 옮긴다

평가 장소와 배분
  - [합의 Q9] harness-lab 안에서 실제 intent 세션으로 평가한다. Q6의 별도 clone(`../harness-lab-trial`)은 취소한다. 그 세션의 wip 커밋은 harness-lab 기록에 남는 정상 커밋으로 본다
  - [사실] 그 세션: Claude Code `4b616822-f180-46af-ae67-d17c7400c0ac`. `/workflow-analysis`로 intent.md를 분석하는 중이다. goal 폴더는 `.goal/workflow-intent/`이고, 지금 파일은 `intent-vs-goal.html` 하나다(10-24 19:18 수정)
  - 무관한 미커밋 파일: 이 세션이 계속 고치는 `.goal/workflow-handoff/` 파일들과 T5의 빈 파일. intent 세션의 wip 커밋에 들어가면 안 된다
  - [합의 Q11] Claude Code 배분

    | 순서 | 세션 | 하는 일 | 확인하는 항목 |
    |---|---|---|---|
    | 1 | 지금 intent 세션 | 작업 도중에 끊고 `/workflow-handoff` | R3 중단, R5 wip 커밋, R2 1회차 |
    | 2 | Claude Code 새 세션 | 붙여 넣기로 재개 → 4가지 질문 → 작업을 조금 더 진행 → 다시 `/workflow-handoff` | C2, R5, R2 2회차(덮어쓰기) |

  - 4가지 질문의 정답은 1단계 세션의 transcript에서 확인한다

## Responsibility

[합의 Q7]
AI: T0~T2, T4, T5 작성, Verify 판정
User: Q 답, T3 검토 승인, 평가 세션 실행. pi, Codex 수동 시험과 feedback

## Checks

[합의 Q12]

| 작업 | Criteria (실행 중 만족할 조건) | Method (방법, 시점) |
|---|---|---|
| T0 저장소 | ① `git rev-parse --show-toplevel`이 harness-lab ② 첫 커밋에 `.venv`, `results/*/runs/`, `.goal/workflow-intent/`가 없음 ③ 인증·키 파일(`auth.json`, `.env`, `id_*`)이 없음 | 커밋 직후 `git ls-files` 검사 |
| T1 작성 | 점검 불필요. T2가 T1의 결과를 점검한다 | |
| T2 정적 점검 | ① D1, D2에서 "그대로"인 문장은 `docs/` 원본과 글자까지 같음 ② "바꿈/일부 바꿈" 문장은 goal.md 결과 문장과 같음 ③ 새 문장은 N2, N3 둘뿐 ④ frontmatter 4개 키가 Matt 원문과 같음(name 제외) ⑤ `.claude/skills/workflow-handoff`로도 읽힘(심링크) | 스크립트로 원본 문장마다 `grep -F`, 남은 줄 목록 출력. T1 직후 |
| T3 검토 | 사용자 승인이 plan.md에 적힘 | 사용자 답 |
| T4 커밋 | 커밋 파일이 `.agents/skills/workflow-handoff/SKILL.md` 하나 | `git show --stat HEAD`, 커밋 직후 |
| T5 준비물 | ① Q11의 2단계마다 붙여 넣을 문장과 확인 항목이 있음 ② 판정 체크리스트가 goal.md Evaluation 행(R2, R3, R5, C2)과 1:1 ③ 이미 떠 있는 intent 세션이 새 스킬을 못 볼 때 할 일이 적힘 | 작성 뒤 AI가 goal.md와 대조, 평가 시작 전에 사용자가 읽음 |
