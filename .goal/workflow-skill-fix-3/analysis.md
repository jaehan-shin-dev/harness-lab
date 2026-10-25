# Analysis: workflow 스킬 개선 (playbook·외부 스킬셋 비교, goal/plan 경계)

작성: 2026-10-25. 단계: Analysis (Define 전).
입력: `docs/ai-native-sdlc-playbook/playbook.md` 전체, `docs/`의 외부 스킬셋 6종(superpowers, claude-feature-dev, addy-osmani-skills, matt-skills, pstack, gstack), `.agents/skills/workflow-*` 8개, `AGENTS.md`, `.goal/workflow-handoff/`, `skill-eval/results/t16/report.md`, pi-lab 메모리.
읽은 방법: 외부 스킬셋은 서브에이전트 3개가 12개 차원(A~L)으로 원문 인용을 뽑았다. 순위와 경계 판단의 근거가 된 줄은 원문에서 다시 확인했다. goal/plan 경계는 Matt, superpowers, addy, pstack, gstack 원문을 직접 읽었다.
상세 설명(쉬운 말, 비교표): `goal-plan-boundary.html`

## 사용자가 정한 것

- [사용자] 폴더 이름은 `workflow-skill-fix-3`. 10/21 분석(pi-lab `.goal/workflow-skill-fix-2/`)은 가져오지 않는다.
- [사용자] 현재 개선 후보
  - 각 단계별 산출물 생성
  - git으로 단계별 commit
  - verify는 독립적으로
- [사용자] 다음으로 깊게 볼 것: goal과 plan의 경계. 가설은 두 가지다.
  - plan은 ticket마다 혼자 읽어도 구현할 수 있어야 하고, 구현은 subagent가 한다. 그래서 파일 독립성이 중요해진다.
  - Matt은 goal과 plan을 합친 spec으로 구현한다(추정).
- 단계별 commit은 아래 순위에서 6위였지만 사용자가 후보로 남겼다.

## Concept

- 순위 기준: ① 내 기록에 실제 실패 증거가 있는가 → ② 여러 자료가 같은 장치를 가졌는가(수렴) → ③ 한 자료에만 있는가. 같으면 수렴한 자료 수, 그다음 비용과 하네스 3개(Claude Code, pi, Codex) 적합성으로 가른다.
- 용어
  - spec: 무엇을, 왜 만들지와 이미 정한 설계 결정을 적은 문서
  - ticket(작업 카드): 실행 단위 하나를 적은 카드
  - vertical slice(수직 조각): 한 층만이 아니라 처음부터 끝까지 동작하는 좁은 조각
  - frontier: 앞선 작업이 다 끝나 지금 시작할 수 있는 작업들
  - worktree: 같은 저장소를 브랜치별로 따로 꺼낸 작업 폴더
- "혼자 읽어도 구현 가능한 ticket"에는 서로 반대인 두 형태가 있다.
  - Matt형: 카드는 얇게(무엇이 되나, 합격 기준, 막는 작업) 쓰고 파일 경로는 금지한다. 실행자는 spec을 가리키는 포인터와 코드 탐색으로 채우고, ticket마다 새 컨텍스트에서 시작한다.
  - superpowers형: 카드에 파일, 이름, 시그니처, 테스트까지 적는다. 실행자는 자기 작업만 본다.

## Context

- 스킬: analysis 19줄, define 23, grill 30, plan 21, execute 17, verify 19, review 29, handoff 40. 산출물은 goal.md와 plan.md다. 공통 규칙은 AGENTS.md 한 곳에 있다.
- T16(10/23)은 지금과 같은 스킬 버전을 쟀다. pi-lab `4a54524`와 harness-lab의 스킬 7개, AGENTS.md가 글자까지 같다.
- 반복된 실패 증거 [사실]
  - 분석이 다음 단계로 이어지지 않음, 3건
    - 10/20 분석이 사라졌다.
    - 10/21 분석은 파일로 남았지만 Define으로 이어지지 않았고 harness-lab으로 옮겨지지 않았다.
    - 2026-10-25 이 세션이 그 분석을 모른 채 다시 시작했다.
  - Define·Plan 왕복, 2건
    - 10/20에 관찰한 통증이 "Define과 Plan 왕복"이었다.
    - workflow-handoff Plan Q13이 goal.md Evaluation을 고쳤다(`goal.md:4`).
    - 10/21 Deliverable을 추가한 뒤의 첫 사례는 Define Round 6, Q1~Q27까지 갔고 goal.md는 125줄이 됐다.
  - Verify 미완, 3건 연속: workflow-skill-fix는 생략했고, skill-eval은 10/23부터 대기 중이고, workflow-handoff도 대기 중이다.
  - 질문 앞에 배경이 없어 답하지 못함, 2건(08-09, 08-15, pi-lab 메모리). harness-lab 메모리 폴더는 비어 있다.
  - T16 과정 검사 5("라운드마다 goal.md 갱신")는 skill 팔 9회 중 2회만 통과했다.
- 사용자의 이전 선호
  - "커밋은 요청 시만"(workflow-skill-fix 제약, 10/20). skill-eval에서는 "커밋 금지"를 지시했다(메모리).
  - "미니멀하게, 한눈에, 중복 없이"(10/20).

## Problem

### A. 개선 후보 순위

| 순위 | 항목 | 실패 증거 | 수렴 | 비용 | 고칠 곳 |
|---|---|---|---|---|---|
| 1 | Analysis 산출물을 Define 입력으로 | 3건 | 5/7 | 작음 | analysis, define |
| 2 | Define/Plan 경계를 "누가 정할 수 있나"로 | 2건 + 무게 | 기준은 수렴, 위치는 갈림 | 큼 | define, plan |
| 3 | Verify를 독립적으로, 끝까지 | 3건 (원인 미상) | 7/7 | 작음~중간 | verify, plan Checks |
| 4 | 메모리에만 있는 "질문 앞에 배경·용어" 규칙을 스킬로 | 2건 + 이 저장소에 메모리 없음 | 4/7 | 아주 작음 | define·plan 또는 AGENTS.md |
| 5 | 회고: 교훈과 지난 권고를 되돌리기 | 2건 | 4/7 | 중간 | verify 끝 또는 새 스킬 |
| 6 | 단계 끝 커밋 | 직접 실패 없음 | 갈림 | 작음 | AGENTS.md |
| 7 | 스킬 시험 범위 넓히기 | T16이 실제 문제를 잡음 | 4/7 | 큼 | skill-eval |
| 8 | Plan에 위험·대안 칸 | 없음 | 6/7 | 작음 | plan |
| 9 | 규칙 강제(문서 구조 lint) | 1건 (T16 검사 5) | 갈림 | 중간 | 스크립트 |

1. **Analysis 산출물을 Define 입력으로.** analysis 스킬에는 결과를 적을 위치가 없다. define은 "사용자가 제공한 목표·현재 상황·조건"에서 출발하고(`define:8`) analysis.md를 읽으라는 말이 없다.
   - 밖에서는: gstack은 다음 단계가 design doc을 "source of truth"로 읽고, 문서가 없으면 앞 단계로 되돌린다(`plan-eng-review:563, :570`). superpowers는 plan 머리에 spec 경로가 필수다(`writing-plans` Plan Document Header).
   - intent.md 질문(workflow-intent의 D1~D6)은 이 항목의 하위 질문이 된다.
2. **Define/Plan 경계.** 지금 경계는 높이로 나뉜다(Deliverable까지 / 순서·방법, `define:18`). grill은 모든 결정을 사용자에게 묻는다(`grill:28`).
   - 경계를 아래로 내리면 Define이 무거워지고, 위로 올리면 결정이 새거나 왕복이 생긴다(해석).
   - 밖에서는 "누가 정할 수 있나"로 가른다. superpowers spec은 사람에게 되묻지 않고 plan을 짤 수 있는 수준까지 쓰고(`brainstorming:147-148`), plan은 "the set of decisions the implementer cannot make alone"이다(`writing-plans:157`). gstack은 Mechanical / Taste / User Challenge로 나눈다(`autoplan:546-556`).
   - 설계 결정을 어느 문서에 둘지는 자료마다 갈린다(matt은 spec, addy는 plan.md). 아래 B에서 자세히 본다.
3. **Verify.** 판정을 실행한 세션이 스스로 내린다(`verify:14`).
   - 증거는 "Verify가 안 돌았다"이고, 독립성이 그 해결책인지는 해석이다. 원인 후보로 Evaluation과 Checks의 겹침이 있다(C1 `goal.md:118`과 T2 `plan.md:72`는 둘 다 원문 문장 대조).
   - subagent가 없는 하네스용 대체 경로가 레퍼런스에 적혀 있다. superpowers는 자기 검토가 약하다고 기록하고 알린다(`executing-plans:256-258`). addy는 리뷰어에게 결론 없이 산출물과 기준만 준다(`doubt-driven:106`).
4. **"배경 먼저" 규칙.** pi-lab 메모리에만 있다. 그래서 harness-lab에서는 Claude Code에도 보이지 않고, pi와 Codex에는 원래 없다. gstack은 질문마다 ELI10을 붙이고, superpowers는 200~300단어로 되짚는다.
5. **회고.** `verify:19` "미충족 사항 정리"에는 출구가 없다. matt `retro`(코드가 아니라 작업 환경을 고친다), pstack reflect(다음 에이전트의 행동이 바뀌는 수정만 받는다), gstack `retro:761`(지난 권고를 addressed/partial/open으로 채점)이 참고가 된다.
6. **단계 끝 커밋.** 레퍼런스가 수렴하지 않는다. 단계마다 커밋하는 건 playbook뿐이다. superpowers는 spec과 작업마다 커밋하고, gstack은 ship 단계만, pstack은 중단 때 wip만 커밋한다. addy는 자기 안에서 갈린다. 사용자의 이전 선호와도 부딪친다. 대신 **작업(ticket)마다 커밋**은 수렴한다: matt `implement:17`, superpowers task Step 5, gstack `qa:676`. 커밋으로 무엇을 얻으려는지가 형태를 정한다.
7. **스킬 시험 범위.** suite는 workflow-define 하나다. superpowers는 "NO SKILL WITHOUT A FAILING TEST FIRST"를 수정에도 적용한다(`writing-skills:379,382`). 1~6을 고친 효과를 확인할 도구가 된다.
8. **위험·대안.** pstack plan 템플릿에 "Alternatives rejected"와 "Risks" 부록이 고정으로 있다(`multi-phase-plan:142,148`). gstack은 최소안과 이상안을 포함해 안을 2개 이상 낸다(`office-hours:931-933`).
9. **규칙 강제.** hook은 Claude Code 전용이다. 하네스와 무관한 형태는 pstack `check-plan.mjs` 같은 문서 구조 lint다.

낮은 순위: description을 트리거 형식으로 바꾸기, Open questions 칸(1에 흡수 가능), 작업 크기 상한, 단계를 건너뛸지 판단하는 기준(superpowers 크기 표 `brainstorming:134-140`), Execute 멈춤 조건과 Ruling 기록.

### B. goal과 plan의 경계 (상세: `goal-plan-boundary.html`)

- **Matt 가설은 반만 맞다.**
  - 맞는 부분: Matt의 spec은 goal.md에 해당하는 내용(문제, 해결, 범위 밖)에 설계 결정(Implementation Decisions, Testing Decisions)까지 합친 것이다(`to-spec:23-73`).
  - 다른 부분: 그다음 `to-tickets`로 다시 쪼갠다. 그래서 문서는 spec과 tickets 2장이고, 내 구조와 장 수가 같다.
  - ticket은 What to build / Blocked by / Acceptance criteria만 담고, 파일 경로와 코드는 금지한다(`to-tickets:71-81, :105`, `to-spec:55`).
  - 혼자 읽어도 되는 이유는 세 가지다. 수직 조각이라서(`to-tickets:31-33`), spec과 ticket을 가리키는 포인터로 소통해서(`implement-spec:15`), ticket마다 `/clear`로 새 컨텍스트에서 시작해서(`ask-matt:26`)다.
  - 파일 충돌은 파일을 나눠서 피하지 않는다. ticket마다 worktree를 쓰고 merger subagent가 합친다(`implement-spec:27-32`).
- **"파일까지 적힌, 혼자 읽고 구현하는 작업"은 superpowers다**(`writing-plans:10`, "A task's implementer sees only their own task" `:105`). 그런데 superpowers는 구현 subagent의 병렬 실행을 금지한다(`subagent-driven-development:282`). 파일 경로에 대해 Matt와 정반대 입장이다.
- **인터뷰 횟수가 다르다.** Matt은 grilling을 한 번 하고, 1~3단계(grill, spec, tickets)를 한 컨텍스트에서 한다(`ask-matt:38`). to-spec은 질문하지 않는다(`:7`). to-tickets는 쪼개는 크기, 막는 작업, 합치기·나누기만 확인한다(`:50-54`). 내 workflow는 Define과 Plan에서 각각 grill한다(`plan:15`).
- **workflow-handoff 사례로 보면** 내 구조는 이미 Matt형에 가깝다. goal.md Deliverable이 "어떻게"(문장 지도, `goal.md:11-65`)를 담았고, plan T1은 그것을 가리켰다.
  - Matt 대비 빠진 것: 작업별 합격 기준(T5에서 Evaluation 행과 손으로 대응시켰다), 사용자 관점의 "무엇이 되나"
  - superpowers 대비 빠진 것: 파일과 인터페이스 칸
- **내 방식의 장점**
  - 합격 기준(Evaluation)이 실행 전에 따로 고정된다. Matt spec에도 Testing Decisions(좋은 테스트의 기준, 시험할 모듈, 선례, `to-spec:59-65`)는 있지만, 요구사항마다 Criteria/Method/Evidence를 적는 표는 없다. 이 기준은 독립 Verify(후보 3)에 넘길 "기준"으로 바로 쓸 수 있다.
  - 결정 기록([합의 Qn])이 남는다.
  - Responsibility(AI/User) 칸이 사람이 해야 하는 작업에 맞는다.
  - subagent 없이도 하네스 3개에서 돈다.
- **내 방식의 단점**
  - 작업 카드가 혼자 서지 못한다. 합격 기준이 없고, Checks는 과정 점검이다.
  - 인터뷰를 두 번 한다.
  - 경계 기준이 높이라서 양쪽 증상이 다 나왔다.
  - 작업 크기와 파일 겹침에 대한 규칙이 없다.
- **판단 (조건부, 해석)**
  - 문서 장 수(2장)를 바꿀 근거는 약하다. Matt, superpowers, gstack도 2장이다. spec 하나로 합치면 Evaluation 분리라는 장점을 잃는다.
  - 바꾸는 쪽이 유리해 보이는 곳은 plan의 **작업 형식**과 **Plan의 인터뷰 방식**이다.
  - subagent 구현은 일이 독립 조각 여러 개(대략 파일 3개 이상)로 나뉠 때 이득이다. pstack은 파일 1~2개면 plan 자체를 건너뛴다(`multi-phase-plan:5`). 최근 목표는 파일 1~2개였다.
  - pi는 harness-lab에서 subagent를 쓸 수 없다(`.goal/workflow-handoff/goal.md:125`). Matt의 "/clear 후 ticket 하나씩"은 subagent 없이도 된다.

## 이미 되어 있는 것

- 단계마다 있는 종료 조건 한 줄
- Out of scope
- 항목별 Evaluation과 작업별 Checks
- PASS/FAIL/UNKNOWN 판정
- [합의]/[미결정]/[가정]/[사실] 표기
- AGENTS.md 한 곳에 모은 공통 규칙
- 스킬 길이
- handoff

## 남은 불확실성

확인할 사실
- F1. 작업 형식을 ticket형으로 바꾸면 Define·Plan 왕복이 실제로 줄어드는가. 사례가 없고, skill-eval에 plan suite도 없다.
- F2. 지난 목표 중 작업이 독립 파일 3개 이상으로 나뉜 경우가 몇 번인가. subagent 구현의 이득 크기를 정한다.
- F3. pi와 Codex에서 새 컨텍스트로 넘어가는 방법(`/clear`에 해당하는 것)과 subagent 대체 방법. Codex에는 `spawn_agent`가 있다.
- F4. Verify가 끝까지 가지 않은 원인.
- F5. Define의 무게가 다른 목표에서도 같은가(사례 1건과 T16뿐).
- F6. 권고형 규칙이 안 지켜진 사례가 T16 검사 5 말고도 있는가.

사용자가 정할 것 (Define의 질문거리)
- D1. analysis.md에 무엇을 담고 Define이 어떻게 읽을지. goal 폴더끼리 어떻게 이어질지
- D2. "혼자 읽기"를 Matt형(얇은 카드 + 포인터)과 superpowers형(파일·이름까지) 중 어느 쪽으로 할지
- D3. Plan이 인터뷰할지, goal.md에서 합성하고 쪼개기만 확인할지
- D4. goal.md Deliverable에 "어떻게"를 얼마나 둘지. 경계 기준을 높이로 할지, 누가 정할 수 있나로 할지
- D5. 작업 카드의 칸(무엇이 되나 / 합격 기준과 goal.md R·C 연결 / 막는 작업 / 파일 / 담당)
- D6. subagent 구현을 언제 쓸지(크기 기준)와 pi에서의 대체 방법. 파일 겹침 규칙
- D7. 커밋 단위: 단계 끝인지 작업 끝인지. 커밋으로 얻으려는 것
- D8. Verify 판정 맥락: 같은 세션, 새 세션, 다른 하네스 중 무엇으로 할지. Evaluation과 Checks의 역할 분리
- D9. "배경 먼저" 규칙을 둘 곳
- D10. 회고, 스킬 시험, 위험·대안, 규칙 강제 중 이번 범위에 넣을 것
