# Analysis: workflow-handoff 설계

작성: 2026-10-24. 단계: Analysis (Define 전). 폴더명 `workflow-handoff`는 요청에 적힌 goal 이름을 그대로 쓴 것이고, 바꿀 수 있다.
요청: (1) Matt의 handoff 원문을 기본으로 쓰고, (2) 파일은 `.goal/<goal>/`에 저장하고, (3) 단계 중간에 context가 찰 것 같을 때 이 스킬을 써도 되는지 리뷰한다.
입력:
- `docs/matt-skills/handoff/`, `docs/matt-skills/ask-matt/{SKILL.md,PHASE-BOUNDARIES.md}`
- 업스트림 mattpocock/skills main: `skills/productivity/handoff/`, `docs/productivity/handoff.md`, `skills/in-progress/claude-handoff/`, handoff 커밋 이력
- `.agents/skills/workflow-*` 7개, `AGENTS.md`
- `../portfolio-manager/.agents/skills/handoff/SKILL.md`와 그 스킬로 쓴 `.handoff/2026-07-27-design-review-tier1-done.md`
- `../pi-lab/.goal/workflow-skill-fix-2/analysis.md`
- pi 1.3.0 문서(`skills.md`, `compaction.md`, `slash-commands.md`), Claude Code 2.1.310과 Codex 0.162.1 실행 파일의 문자열

## Concept (이해에 필요한 개념)

- **handoff 문서**: 지금 대화를 요약해서, 새 세션의 에이전트가 이어받을 수 있게 만든 markdown 파일 하나. Matt는 이 스킬이 주는 것이 압축이 아니라 **이동성(portability)**이라고 설명한다. 파일이 어딘가로 옮겨 가야 할 때 쓰는 도구라는 뜻이다(`docs/productivity/handoff.md`).
- **Matt `handoff` 원문** (`docs/matt-skills/handoff/SKILL.md`, 16줄). 문장마다 하는 일:

  | 위치 | 내용 |
  |---|---|
  | frontmatter | `name: handoff`, `description`, `argument-hint`, `disable-model-invocation: true` |
  | L8 | 대화를 요약해 OS 임시 폴더에 저장한다. "Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - **not the current workspace**." |
  | L10 | "suggested skills" 섹션을 넣는다 |
  | L12 | spec, plan, ADR, issue, commit, diff처럼 이미 있는 산출물은 복사하지 않고 경로로 참조한다 |
  | L14 | API 키, 비밀번호, 개인정보 같은 민감 정보를 가린다 |
  | L16 | 사용자가 넘긴 인자를 다음 세션의 용도로 보고 문서를 맞춘다 |
  | `agents/openai.yaml` | Codex용 표시 이름과 `allow_implicit_invocation: false` |

- **사용자만 부르는 스킬 (`disable-model-invocation: true`)**: 사람이 `/이름`을 직접 쳐야만 실행된다. 모델은 이 스킬을 스스로 부를 수 없고, 다른 스킬을 통해 부를 수도 없다.
  - Claude Code 2.1.310: 모델이 Skill 도구로 부르면 거절하고 이런 메시지를 낸다. "Do not replicate this skill's workflow by other means — it is reserved for explicit user invocation." (실행 파일 문자열에서 확인)
  - pi 1.3.0: 같은 키를 지원한다. 실행은 `/skill:name` (`docs/skills.md:53`).
  - Codex: Matt 구성에서는 `agents/openai.yaml`의 `allow_implicit_invocation: false`가 이 역할을 맡는다. Codex가 실제로 그렇게 동작하는지는 확인하지 않았다(F4).
- **1차 출처와 2차 출처 (primary / secondary source)**: 대화 원본이 1차 출처이고, 그것을 요약한 것이 2차 출처다. 그대로 이어가기(Continue)를 뺀 나머지 선택(`/compact`, `/handoff`, `/clear`)은 모두 1차 출처를 잃는다. 요약은 정보가 빠지는 대신 잡음이 줄고 컨텍스트 여유가 생긴다(`PHASE-BOUNDARIES.md:44-51`).
- **단계 경계와 다섯 가지 선택 (Matt)**: 단계와 단계 사이에서 아래 순서로 묻고, 처음 "예"가 나오는 것을 고른다(`PHASE-BOUNDARIES.md:17-40`).
  1. 이 세션에서 계속할 수 있나? → Continue
  2. 지금 컨텍스트가 다음 일과 무관한가? → `/clear`
  3. 무언가가 옮겨 가야 하나? → `/handoff`
  4. 사람 없이 돌릴 수 있는 일인가? → subagent
  5. 그 밖의 경우 → `/compact`

  이 결정은 단계 경계에서만 내린다. 단계 중간에는 계속하거나, 남은 일을 subagent로 나눈다. "Compacting mid-phase makes the agent lose the thread." (`PHASE-BOUNDARIES.md:5`)
- **smart zone**: 모델이 여전히 정확하게 추론하는 컨텍스트 구간. Matt는 최신 모델 기준 약 150k 토큰으로 본다(`ask-matt/SKILL.md:40`). 이 한계는 컨텍스트 창이 다 차기 **전에** 온다. 그래서 "다 찰 것 같다"고 느낄 때는 이미 이 구간을 지났을 수 있다.
- **자동 요약 (compaction)**: 사용자가 아무것도 하지 않아도 하네스가 오래된 대화를 요약해서 공간을 만든다.
  - pi: `contextTokens > contextWindow − reserveTokens(기본 16384)`이면 자동으로 요약한다. 도구 실행이 끝나고 다음 응답을 시작하기 전에 검사한다. `/compact [instructions]`로 직접 실행할 수도 있다(`compaction.md`).
  - Claude Code: `/compact` 명령이 있고("Free up context by summarizing the conversation so far"), 자동 요약도 한다. 자동 요약은 이 세션의 시스템 지시문에서 확인했다.
  - Codex: compaction 관련 문자열은 있지만 세부 동작은 확인하지 않았다.

  결국 "꽉 차는 순간"은 하네스가 알아서 처리한다. 문제는 그 요약이 단계 중간 아무 지점에서나 일어날 수 있다는 점이다.
- **이 워크플로의 단계별 산출물** (각 스킬 본문 기준):

  | 단계 | 스킬이 정한 파일 | 진행 중 상태가 남는 곳 |
  |---|---|---|
  | Analysis | 없음 (관행상 `analysis.md`를 썼다) | 대화 |
  | Define | `goal.md`. Round마다 갱신하고 합의, 미결정, 가정을 구분해 적는다 | 대부분 `goal.md` |
  | Plan | `plan.md`. Round마다 갱신한다 | 대부분 `plan.md` |
  | Execute | `plan.md`. 작업별 완료/미완/막힘은 단계 **끝**에 적는다 | 대화와 diff |
  | Verify | 없음 | 대화 |

  Round는 grill에서 질문 한 묶음을 묻고 답을 받는 한 번이다. Round가 끝날 때마다 문서가 갱신되므로, 이때 문서와 대화의 차이가 가장 작다.

## Context (배경과 현재 상황)

- **원문 기준점**: 로컬 `docs/matt-skills/handoff/SKILL.md`는 오늘(2026-10-24) 업스트림 main과 글자까지 같다. 최근 업스트림 변경은 두 번이다. 0f5e033(2026-10-06)은 temp 경로를 찾는 순서를 적었고, d28dfdc(2026-08-15)는 L10 문구를 "call the Skill tool"로 통일했다.
- **선례 1, `workflow-grill`**: Matt의 `grilling` SKILL.md를 글자 그대로 옮기고 `name`만 바꿨다. 나중에 Matt 원본을 설치해도 이름이 부딪치지 않게 하려는 것이고, 이 사실은 `CREDITS.md`에 적었다. `agents/openai.yaml`은 가져오지 않았다(grilling은 모델이 부르는 스킬이라 policy 줄이 원래 없다). `CREDITS.md`에 적힌 출처 경로 `assets/matt-skills/grilling/`은 지금 폴더 이름 `docs/`와 다르다.
- **선례 2, portfolio-manager의 `handoff`** (2026-07-27):
  - L8만 바꿨다. 저장 위치는 gitignore된 `.handoff/`, 파일명은 `<YYYY-MM-DD>-<slug>.md`이고, 끝에 절대 경로를 출력한다. 바꾼 이유도 문장에 적었다: "durable across sessions/reboots/job cleanup yet never enters the project record".
  - L10이 다른 것은 사용자가 고친 게 아니다. 업스트림 386d4ff(8월 이전 판)의 문구와 같다(확인함).
  - 이 스킬로 실제 쓴 문서가 하나 있다(5.8KB). grill 세션에서 Tier 1을 끝낸 시점, 즉 단계 경계에서 썼다. 구성은 현재 상태, 끝난 일(산출물 경로만 참조), 남은 일, 관찰한 사용자 선호, suggested skills, 다음 첫 행동이다.
- **선례 3, 지난 분석** (`../pi-lab/.goal/workflow-skill-fix-2/analysis.md`): 실패 증거 (c)가 "분석 결과가 파일로 남지 않아 다음 세션이 이어받지 못했다"이고, "Claude Code의 메모리는 pi에서 안 보인다"는 기록도 있다. 이번 목표가 다루는 문제와 같다.
- **Matt가 temp를 고른 이유와 그 약점** (`docs/productivity/handoff.md`):
  - 이유: "Temp is deliberate, because a handoff is a document in transit, not an artifact you maintain."
  - 약점도 직접 적었다. Codex는 세션 사이에 temp를 지우는 경우가 있고, 재부팅하면 `/private/tmp`가 빈다. 그래서 "copy the file somewhere durable yourself as soon as it's written"라고 권한다.
  - 한계: "It captures the what, not the why." 확인하지 않은 믿음이 사실처럼 적히면, 다음 에이전트는 다시 확인하지 않고 그것을 전제로 삼는다.
- **하네스**: 이 저장소는 `.agents/skills`가 실제 폴더이고 `.claude`는 그 심링크다. `CLAUDE.md`도 `AGENTS.md`의 심링크다. Claude Code, pi(skill-eval이 pi로 돈다), Codex가 모두 설치되어 있다. 세 도구 모두 내장 `/handoff` 명령은 없다. Claude Code와 Codex는 실행 파일 문자열로, pi는 `slash-commands.md`로 확인했고 pi에는 `/compact`만 있다. 따라서 이름이 내장 명령과 부딪치지는 않는다. Matt 원본을 나중에 설치하면 부딪친다(grill과 같은 이유).
- **git**: harness-lab은 커밋이 0개이고 `.gitignore`가 없다. pi-lab의 `.goal/`은 무시되지도 커밋되지도 않은 상태(untracked)다. goal 폴더에 둔 handoff 문서가 git에 들어갈지는 아직 정한 적이 없다.
- **`claude-handoff`** (업스트림 in-progress): temp에 문서를 쓴 다음 `claude --bg`로 백그라운드 에이전트를 바로 띄우는 변형이다. 관련은 있지만 이번 대상은 아니다.
- **관찰**: 이 Claude Code 세션에서는 모델 컨텍스트에 토큰 사용량 정보가 보이지 않았다. 모델이 "곧 찬다"를 스스로 알 수 있는지는 확인하지 않았다.

## Problem (핵심 문제)

해결 방법은 여기서 정하지 않는다(Define, Plan에서 정한다). 선택지는 범위를 보여 주려고 적은 것이다.

### 1. "원문 그대로"와 "goal에 저장"이 같은 한 문장에서 부딪친다

- L8은 저장 위치를 정하면서 "not the current workspace"라고 못 박는다. `.goal/<goal>/`은 current workspace 안에 있다. 그래서 grill처럼 `name`만 바꾸는 복사로는 요구 (2)를 채울 수 없다.
- 원문은 그대로 두고 AGENTS.md의 "Working documents" 규칙으로 덮는 방법은 근거가 약하다. 스킬 본문이 더 구체적이고 반대 방향(workspace에 두지 말 것)을 명시하므로, 모델이 어느 쪽을 따를지 아직 모른다(F1).
- 원문은 그대로 두고 다른 스킬로 감싸는 방법은 막혀 있다. 사용자만 부르는 스킬은 다른 스킬이 부를 수 없고, Claude Code는 다른 방법으로 흉내 내지도 말라고 한다.
- 남는 선택지의 범위: L8만 바꾸고 차이를 `CREDITS.md`에 적는 방법(portfolio-manager 방식), 원문 그대로 temp에 쓰고 사람이 goal 폴더로 옮기는 방법(Matt 문서가 권하는 방식) 등이 있다. 어느 쪽이든 그 전에 "원문을 얼마나 지키느냐"의 단위(글자, 문장, 의미)를 먼저 정해야 한다(D1).

### 2. 저장 위치를 바꾸면 문서의 성격이 바뀐다

- temp에 두면 "옮겨 가는 중인 문서"다. 관리하지 않고 저절로 사라진다. goal 폴더에 두면 "남아 있는 작업 문서"가 되고, 그러면 새 질문이 생긴다(D3):
  - 여러 번 쓰면 덮어쓰나, 날짜별로 쌓나?
  - 이미 이어받은 handoff는 어떻게 처리하나? 나중 세션이 오래된 handoff를 현재 상태로 믿을 수 있다. Matt가 경고한 "확인하지 않은 믿음"이 더 오래 남는다.
  - git에 들어가나? 들어간다면 L14의 민감 정보 가리기가 더 중요해진다. portfolio-manager는 이 문제를 gitignore로 풀었다.
  - goal 이름은 어떻게 고르나? AGENTS.md는 "합의한 이름을 다시 쓰고, 불분명하면 먼저 확인"이라고 한다.
- 장점도 Matt 원문에서 바로 나온다.
  - L12의 "이미 있는 산출물은 경로로 참조"가 goal.md, plan.md와 그대로 맞는다. handoff 본문에는 "goal.md와 plan.md에 아직 안 적힌 것"만 담으면 되어서 문서가 작아진다.
  - goal 폴더 안에 있으면, 다음 세션은 경로를 따로 전해 받지 않아도 어디를 볼지 안다. Matt 문서가 가장 많이 보고된 문제로 꼽은 "Where did my handoff file go?"가 사라진다.

### 3. "단계 중간에 context가 찰 것 같을 때 써도 되나": Matt 원문 기준 답은 "대부분 아니다"

- **Matt의 기준**: handoff를 쓰는 경우는 네 가지뿐이다. 하네스를 바꿀 때, 디렉터리를 옮길 때, 동료에게 넘길 때, 단계 중간에 곁가지 일을 분기할 때. 같은 하네스, 같은 폴더에서 같은 일을 이어가면 `/compact`를 쓴다. 단계 중간이면 계속하거나 subagent로 나눈다. 결정은 경계에서 한다(`PHASE-BOUNDARIES.md:5`, `:27-34`, `:38`; `docs/productivity/handoff.md` "Staying on the same task is a compact, not a handoff.").
- **질문을 다시 세우면**: 가만히 두면 하네스가 단계 중간 아무 지점에서나 자동으로 요약한다. 그 전에 내가 고른 지점에서 의도적으로 넘길 것인가? Matt의 답은 "smart zone에 닿기 전에 가장 가까운 경계에서 `/compact`"다(`ask-matt/SKILL.md:40`).
- **이 사용자 상황이 Matt의 네 경우에 걸리는 지점**:
  - (사실) 하네스 교체: 사용자는 Claude Code, pi, Codex를 실제로 오간다. compact 요약은 해당 하네스 세션 안에만 있어서 다른 하네스로 가져갈 수 없다. 이 경우는 handoff가 맞다.
  - (해석, Matt 원문이 아님) 이 워크플로는 단계 경계가 명시적이고, 사용자만 다음 단계로 넘길 수 있다("Proceed to another phase only when the user asks"). Define과 Plan은 Round마다 문서를 갱신하므로, Round 경계가 단계 안의 작은 경계 역할을 할 수 있다. Matt가 말하는 phase는 "그 일은 끝났다"고 느끼는 덩어리라서, Round 경계를 그 phase로 봐도 되는지는 판단이 필요하다.
  - (해석) 단계마다 handoff의 무게가 다르다. Analysis, Execute, Verify 중간에는 대화에만 있는 내용이 많아 handoff가 두꺼워진다. Define, Plan의 Round 경계에서는 내용이 거의 다 문서에 있어 얇아진다.
- **누가 "찰 것 같다"를 판단하나**: 원문 frontmatter를 유지하면 사용자만 실행할 수 있다. 에이전트가 먼저 제안하게 하려면 그 규칙을 스킬 밖(AGENTS.md나 각 workflow 스킬)에 둬야 하고, 그 전에 에이전트가 자기 컨텍스트 사용량을 아는지부터 불확실하다(F2).
- **너무 늦게 하는 handoff의 위험**: 찰 무렵에는 추론 품질이 이미 떨어져 있을 수 있다(smart zone). 문서를 쓰는 일 자체도 토큰을 쓴다. 쓰는 도중에 자동 요약이 끼어들 수도 있다(pi는 도구 실행이 끝날 때마다 검사한다).

## 추가 조사: compact 대신 handoff 문서로 이어가기 (2026-10-24)

사용자가 목적을 밝혔다(D2): **같은 하네스에서 compact 대신 handoff 문서를 만들고, 그 문서로 이어서 작업한다. compact 요약의 품질이 아쉽기 때문이다.**

### Matt의 입장

- 막는 장치는 없다. 의도한 용도가 아닐 뿐이다. 근거 문장: "Staying on the same task is a compact, not a handoff." 그리고 "`/handoff` does not summarise better. Its advantage is that the result is a file" (`docs/productivity/handoff.md`).
- Matt는 handoff가 compact보다 요약을 잘한다고 보지 않는다. 둘 다 같은 모델이 같은 대화를 요약한다. 원문은 16줄이고, "무엇을 담을지"에 대한 지시는 "summarising the current conversation", suggested skills, 중복 금지, 민감 정보 가리기뿐이다.
- 그래서 compact 품질이 문제라면, Matt 원문을 그대로 쓴 handoff도 비슷한 품질에 머물 가능성이 있다. (해석이며 검증하지 않음)
- 단계 중간 경고("Compacting mid-phase makes the agent lose the thread")는 handoff에도 똑같이 해당한다. 둘 다 2차 출처이기 때문이다.

### handoff가 compact보다 실제로 나을 수 있는 지점

- 사람이 읽고 고칠 수 있다. Matt도 "Read the document before you hand it over, and downgrade anything you only assumed"라고 권한다. compact 요약은 검토할 틈 없이 바로 이어진다.
- 파일로 남는다. 다음에 compact가 또 일어나도 다시 읽을 수 있다(superpowers의 ledger와 같은 원리).
- 담을 내용의 틀을 정할 수 있다. 품질 차이는 대부분 이 틀에서 나온다. 아래 다른 스킬들이 이 부분을 채운다.

타이밍(언제 할지)과 지시문(무엇을 남길지)은 수동 `/compact [instructions]`로도 고를 수 있으므로 handoff만의 장점이 아니다.

### 다른 스킬셋의 참고 자료 (원문 확인)

| 출처 | 형태 | 이 목적에 쓸 만한 점 |
|---|---|---|
| pstack `skills/poteto-mode/playbooks/pause-safely.md` + `session-pickup.md` (10줄, 11줄) | 멈춤과 재개 한 쌍. 발동 조건에 "imminent context compaction"이 명시됨(`poteto-mode/SKILL.md:146`) | 멈춤: 안전한 경계에서 멈추고 진행 중인 원자 단계는 끝내거나 되돌린다. 되돌릴 수 없는 행동은 하지 않는다. resume note에 의도, 하던 일, 진행과 검증된 것, 현재 상태, 다음 단계, 핵심 파일, 함정을 적는다. 이미 있는 기록은 가리키기만 한다. 재개: 이전 기록은 권위 있는 입력이므로 다시 하지 않는다. 단, 물려받은 주장은 실제 산출물에서 확인한다. 이번 목적과 가장 가깝고 Matt처럼 짧다 |
| gstack `context-save` + `context-restore` (648줄, 623줄) | 저장과 복원 한 쌍. 저장 위치는 저장소 밖 `~/.gstack/projects/<slug>/checkpoints/` | 형식: Working on / Decisions Made / Remaining Work / Notes. Remaining Work 항목마다 출처 표시(`(path run)` 실행해 봄, `(path read)` 읽기만 함, `(path assumed)` 추정 등)를 붙이고, restore는 추정 항목을 "Verify first"로 분리한다. "Do not record an unchecked file claim as fact." 파일은 타임스탬프로 쌓고 덮어쓰지 않는다. 최신 파일이 모호하면 사용자에게 묻는다. 둘 다 코드 수정 금지(HARD GATE). 대신 `bin/` 스크립트에 의존하므로 그대로는 실행되지 않는다 |
| superpowers `subagent-driven-development:131-152`, `executing-plans:112-123` | 요약에 기대지 않고, 진행하면서 ledger 파일을 계속 갱신한다 | "Conversation memory does not survive compaction." "After compaction, trust the ledger and `git log` over your own recollection." 기록은 작업과 같은 호출에서 한다. 이 워크플로에서는 Round마다 갱신하는 goal.md, plan.md가 이미 ledger 역할을 한다. 다만 Execute 중간 상태는 비어 있다 |
| addy `context-engineering:123-137, 198-202` | 재시작해도 되는 경계를 정하는 규칙 | "A fresh session is safe at a completed task boundary, not at an arbitrary token count." 남길 것 5가지: 합의한 범위와 결정, 작업 상태와 다음 작업, 바뀐 파일과 작업 트리 상태, 정확한 검증 명령과 결과, 미해결 질문·위험·필요한 승인. 새 세션 규칙: "Do not infer approval from a previous conversation unless the durable artifact records it." 정리는 "75%에서 시작, 100% 아님" |

### pstack pause-safely / session-pickup 상세

- **위치와 구조**: pstack(Cursor 플러그인, MIT)의 `poteto-mode` 스킬에 들어 있는 playbook 23개 중 2개다. 따로 부를 수 있는 스킬이 아니다. `poteto-mode`(user-invoked)가 작업을 playbook에 맞춰 고르고, 그 playbook의 단계를 todolist에 글자 그대로 옮겨 수행한다(`poteto-mode/SKILL.md:110-112`). pause는 "The complement to Session pickup"이다(`:146`).
- **pause의 핵심**:
  - 발동은 명시적으로만 한다("keep going"이라고 하면 멈추지 않는다).
  - 원자 단계 단위로 멈추고, 되돌릴 수 없는 행동은 하지 않는다.
  - wip 커밋으로 작업을 디스크에 남긴다.
  - resume note에 7항목을 적는다.
  - 이미 있는 기록(trail)은 가리키기만 한다.
  - 마지막 보고에서 "디스크에 있는 것과 아직 머릿속에만 있는 것"을 구분한다.
- **pickup의 핵심**:
  - 1차 출처는 resume note가 아니라 **이전 transcript(원본 대화)**다. 길면 subagent로 읽고, 줄인 타임라인만 메인 세션에 가져온다.
  - 이전 기록을 권위 있는 입력으로 보고, 다시 도출하지 않는다.
  - 한 것과 남은 것을 비교해 재개 지점에 이름을 붙인다.
  - 남은 일을 맞는 playbook으로 넘긴다.
  - 물려받은 주장은 실제 산출물에서 확인한다.
- **transcript 위치**: Claude Code는 `~/.claude/projects/<project>/<session>.jsonl`(파일이 있는 것 확인), pi는 `~/.pi/agent/sessions/`(`sessions.md:50`)다. pi는 compaction 뒤에도 이전 기록을 세션 파일에 남긴다(`compaction.md` 그림). Claude Code도 compact 뒤에 원본이 jsonl에 남는지는 확인하지 않았다. 로컬에 compact를 거친 세션이 없었다(F8).
- **그대로 가져오기 어려운 점**:
  - Cursor 전제: `agent-transcripts/`, cloud agent, Cursor restart.
  - poteto-mode의 공통 규칙에 기대어 있다.
  - "imminent context compaction"을 에이전트가 어떻게 아는지 원문에 없다(F2와 같은 질문).
  - wip 커밋은 "사용자가 요청할 때만 커밋"하는 방침과 부딪칠 수 있다.
  - 저장 위치가 `/tmp`다.

### 하네스 차원의 장치 (스킬이 아님)

- pi: extension의 `session_before_compact` 이벤트로 자동 compaction이나 `/compact`를 취소하거나, 요약을 직접 만든 것으로 바꿀 수 있다(`compaction.md:297-299`). compact 품질 자체를 바꾸는 길이다.
- Claude Code 2.1.310 (실행 파일 문자열 기준이며, 버전이 바뀌면 달라질 수 있다):
  - `PreCompact`와 `PostCompact` hook이 있다. `PreCompact`는 compaction을 막을 수 있다("compaction blocked by PreCompact hook; continuing uncompacted"). 또 "Exit code 0 - stdout appended as custom compact instructions"이므로, hook이 출력한 내용이 요약 지시문으로 붙는다.
  - compact 프롬프트는 이미 구조가 있다. 2000단어 이내에 9개 절을 쓴다: 1 Primary Request and Intent, 2 Key Technical Concepts, 3 Files and Code Sections, 4 Errors and fixes, 5 Problem Solving, 6 All user messages(전부 나열), 7 Pending Tasks, 8 Current Work, 9 Optional Next Step(가장 최근 대화를 원문 인용으로). 그리고 "There may be additional summarization instructions provided in the included context"라고 하며, 예시로 `## Compact Instructions` 절을 든다. 따라서 CLAUDE.md에 그런 절을 두면 요약 지시로 쓰일 것으로 보인다(추론, 실험 안 함).
  - 비교: Matt handoff 원문보다 Claude Code compact의 틀이 더 자세하다. compact에 없는 것은 이 워크플로의 상태(지금 단계, grill frontier, goal.md와 plan.md 경로 참조), 확인한 것과 추정한 것의 구분, 이어받기 전 사람의 검토, 그리고 파일로 남는 것이다. compact 틀은 코드 개발 중심이고(파일, 코드 조각, 오류 수정), 산출물을 경로로 참조하는 대신 내용을 옮겨 적는다.

### 시사점 (해석)

- 원하는 흐름은 "저장 → 새 세션 → 재개"의 한 쌍이다. Matt에는 저장 쪽만 있고, 재개는 "이 파일 읽어"로 끝난다. pstack과 gstack은 두 쪽을 다 둔다.
- compact보다 나은 품질을 원할수록 Matt 원문 16줄에 없는 것이 필요해진다: 담을 항목의 틀, 출처 표시, 재개할 때의 확인 규칙. 이는 D1("원문 그대로")과 긴장 관계다.

## 남은 불확실성

내가 확인할 사실:
- F1. AGENTS.md 규칙과 원문 L8이 부딪칠 때 모델이 어느 쪽을 따르나? pi(skill-eval)로 실험할 수 있고, Claude Code에서는 직접 한 번 돌려 본다.
- F2. Claude Code, pi, Codex에서 모델이 자기 컨텍스트 사용량을 볼 수 있나? 이 세션에서는 보이지 않았고, 공식 문서는 아직 확인하지 않았다.
- F3. Claude Code의 자동 요약은 언제 발동하나? `/compact`에 지시문을 주면 단계 중간에 잃는 정보가 얼마나 줄어드나? (공식 문서)
- F4. Codex의 compaction 방식과 스킬 위치. `.agents/skills`를 읽는지, `agents/openai.yaml`이 있어야 user-invoked가 지켜지는지.
- F5. Matt가 temp를 고른 추가 이유가 업스트림 issue #272 등에 남아 있나? 지금 근거는 docs 문장뿐이다.
- F6. ~~Claude Code `PreCompact` hook이 요약 내용에 영향을 줄 수 있나?~~ → 실행 파일에서 확인: stdout이 요약 지시문으로 붙는다. 남은 것: CLAUDE.md의 `## Compact Instructions` 절이 실제로 반영되는지(실험), `PostCompact`나 `SessionStart`(compact 직후)로 goal.md를 다시 읽힐 수 있는지(공식 문서).
- F7. 같은 대화로 만든 compact 요약과 handoff 문서의 품질 차이가 실제로 있나? (같은 세션을 갈라 비교해 볼 수 있음)
- F8. Claude Code가 compact 뒤에도 원본 대화를 jsonl에 남기나? 남긴다면 pickup이 transcript를 1차 출처로 쓸 수 있다.

사용자가 정할 것:
- D1. "원문 그대로"의 단위. L8 한 문장만 예외로 두는 글자 단위인가, 의미 단위인가? frontmatter(`disable-model-invocation`)와 `agents/openai.yaml`까지 유지하나?
- D2. ~~이 스킬의 주된 용도~~ → 답함(2026-10-24): 같은 하네스에서 compact 대신 이어가기. 이유는 compact 품질이 아쉬워서. 남은 질문: 하네스를 바꾸는 경우도 포함하나? 저장 쪽만 만들지, 재개 쪽(pickup)까지 만들지?
- D6. 품질을 위해 Matt 원문에 무엇을 더할지, 혹은 더하지 않을지. 담을 항목의 틀(pstack, addy), 출처 표시(gstack), 재개 시 확인 규칙(pstack, gstack) 중 무엇을 고르나? 이것은 D1과 함께 정해야 한다.
- D3. goal 폴더에 둔 handoff 문서의 수명. 덮어쓸지 쌓을지, 이어받은 뒤 어떻게 처리할지, git에 넣을지. portfolio-manager의 `.handoff/` 방식을 그대로 쓰지 않는 이유(또는 쓸지).
- D4. 단계 중간 사용의 허용 범위. 허용하지 않음(Matt 원칙), Round 경계에서만, 언제든 중 무엇인가? 누가 시작하나(사용자만, 또는 에이전트가 제안)?
- D5. 이름을 `workflow-handoff`로 할지, grill처럼 `CREDITS.md`를 둘지.
