# Verify: workflow-prototype

판정일: 2026-10-29 (KST). 대상 스냅샷: `6198de7` 및 검증 시작 시 같은 내용의 작업 트리.

**최종 목표 판정: UNKNOWN.** R1–R4, C1–C2, C4–C6는 PASS다. C3의 현재 보관 경로와 허용 구간의 변경 범위는 확인했지만, Define 종료 커밋과 Round 경계를 확인할 과거 이력은 허용 입력 밖이다. 확인된 FAIL은 없다. 이는 구현 결함 판정과 구분한다. 10개 Evaluation 각각의 판정·근거·Gap을 작성했으므로 이번 Verify의 문서 종료 조건은 충족한다.

## 판정 방식과 입력 경계

- 독립 판정자: `/root/verify_judgement` subagent. 부모는 아래 경로와 Git 범위, 원본 보존 제한만 전달했다. 판정자는 해당 자료를 직접 조회했고, 부모의 완료 요약을 판정 근거로 받지 않았다. 부모는 문서의 완결성과 증거 연결 점검 및 Verify 커밋을 담당한다.
- 목표 기준: [goal.md](goal.md)를 직접 읽고 R1–R4, C1–C6의 합의된 Criteria / Method / Evidence를 사용했다. 요구 범위나 합격 기준을 추가하지 않았다.
- 산출물 입력: [실제 스킬](../../.agents/skills/workflow-prototype/SKILL.md), [정책](../../.agents/skills/workflow-prototype/agents/openai.yaml), [확정 문구](skill-draft.md), [원문 대응 기록](source-map.md), `prototype/ui-comparison/`, `prototype/state-logic/`, `prototype/technical-feasibility/`의 실제 파일·결과 문서·원출력·캡처·DB다.
- Git 입력: Plan 완료 기준점 `5b5da04` 이후부터 `6198de7`까지의 log·변경 목록·허용 산출물 diff와 스냅샷이다. 기준점의 `goal.md`·`skill-draft.md` 스냅샷도 현재 파일과 대조했다. `5b5da04` 이전의 커밋 이력은 조회하지 않았다.
- 제외: 티켓 파일의 내용과 Execute 완료 기록, `handoff.md` 내용, `analysis.md`, 별도 Plan 문서, 부모 대화와 완료 요약. 티켓·handoff 경로는 Git 변경 목록에 나타나는 이름만 확인했다. 결과 문서가 티켓을 링크하거나 인용해도 대상 티켓은 열지 않았다.
- 방법 지침으로 `workflow-verify`를 읽었고, 공식 설정 대조에는 OpenAI Docs 지침을 사용했다. 이 지침들은 목표 달성 증거를 대신하지 않는다. 목표와 대응 기록이 인용한 원문은 채택 내용의 비교에 필요한 부분만 직접 읽었다.
- Aside의 명령·프로필·도구는 사용하지 않았다. 보존된 캡처와 공개 Interface 관찰 원출력으로 판정할 수 있어 새 브라우저 실행이나 전체 실험 재수행은 하지 않았다. 새로운 요청 시나리오 세트나 제품 구현도 만들지 않았다.
- 과거 에이전트의 `PASS` 또는 완료 문장 자체로 PASS를 주지 않았다. 출력의 구체 상태·오류·입력, 실제 캡처, DB의 실제 행과 스키마, 실행 코드의 공개 조작 경계를 서로 대조했다. 아래 실행 관찰은 **보존된 실행 증거의 독립 검토**이며 검증자가 그 과거 실행을 실시간으로 목격했다는 뜻이 아니다.

## 확보한 객관적 증거

### E1. 스킬 본문·설정·승인 문구

실제 스킬과 확정 문구는 각각 3,046 bytes이며 바이트가 동일했다. 두 파일의 SHA-256은 `243e9ff0992c8875ac05b7d96d393ae04317c87e1a43c4a33812af7df9c1be2c`다. 정책을 `yaml.safe_load`로 직접 읽은 결과는 `{'policy': {'allow_implicit_invocation': False}}`였다.

[공식 Build skills의 Optional metadata](https://learn.chatgpt.com/docs/build-skills#optional-metadata)를 2026-10-29 직접 검색하고 열어 확인했다. 공식 문서는 `agents/openai.yaml`의 해당 값을 false로 설정하면 Codex의 암시적 호출을 막고 명시 호출은 유지한다고 설명한다. 로컬 정책은 그 형식과 일치한다. 이는 설정·공식 의미의 대조이며, 현재 앱에서 비호출 입력을 실행해 차단을 관찰한 런타임 시험은 아니다.

### E2. UI 공개 화면과 상호작용 증거

[질문·요청 인용·실행 안내·결과](prototype/ui-comparison/result.md), [HTML](prototype/ui-comparison/index.html), [관찰기](prototype/ui-comparison/browser-check.mjs), [최종 상태 원자료](prototype/ui-comparison/evidence/green-observations.json)를 직접 읽었다. 질문은 같은 다섯 작업을 목록·카드·상태 보드로 볼 때 검토 작업과 메타데이터가 어떻게 보이는지다. 요청 기록은 에이전트가 작은 사례를 선택하고 스킬을 명시 적용한 위임 평가이며, 실제 사용자의 제품 아이디어나 사용자 조작으로 서술되지 않았다.

검증자가 `view_image`로 최종 PNG 9장을 모두 직접 열었다.

| 보기 | 전체 화면 | 검토 필터 | 상세 화면 | 직접 관찰한 내용 |
|---|---|---|---|---|
| A 목록 | [전체](prototype/ui-comparison/evidence/a-list-all.png) | [검토](prototype/ui-comparison/evidence/a-list-review.png) | [상세](prototype/ui-comparison/evidence/a-list-detail.png) | 전체 다섯 행, 필터 후 두 행, 상태·마감·담당자 열, 같은 첫 검토 작업의 상세 대화상자가 보인다. |
| B 카드 | [전체](prototype/ui-comparison/evidence/b-cards-all.png) | [검토](prototype/ui-comparison/evidence/b-cards-review.png) | [상세](prototype/ui-comparison/evidence/b-cards-detail.png) | 전체 3열·2행, 필터 후 두 카드가 같은 행에 보이며 같은 상세가 열린다. |
| C 상태 보드 | [전체](prototype/ui-comparison/evidence/c-board-all.png) | [검토](prototype/ui-comparison/evidence/c-board-review.png) | [상세](prototype/ui-comparison/evidence/c-board-detail.png) | 전체 예정 1·진행 중 2·검토 2, 필터 후 앞 두 열은 빈 상태이고 검토 열에 두 작업이 남는다. |

각 PNG의 동명 접근성 트리 9개도 JSON으로 읽어 버튼·대화상자의 이름을 대조했다. 최종 원자료에는 각 안의 전체·검토·상세 열림·닫힘, 총 12개 상태가 있다. 각 안에서 `5개 작업 표시` → `2개 작업 표시`, 검토 작업 두 제목, 상세 제목 `랜딩 페이지 문구 검토`, `dialogVisible` false → true → false가 기록돼 있다. 닫힌 뒤에도 두 작업과 필터가 남으며 `browserErrors`는 빈 배열이다. 마지막 항목은 실행한 조작 동안의 수집 결과로만 해석했다.

관찰기는 표시 이름을 가진 공개 버튼의 좌표를 얻고 Chrome `Input.dispatchMouseEvent`로 입력하며, 표시 DOM을 읽고 캡처·접근성 트리를 저장한다. 데모 내부 `render()`나 데이터 변수를 직접 실행하지 않는다. 원자료에는 Chrome `156.0.8078.49`, 1280×900이 남아 있다.

[필터 실패 원자료](prototype/ui-comparison/evidence/red-observations.json)와 [첫 변경 후 실패 원자료](prototype/ui-comparison/evidence/first-green-failure/green-observations.json)는 검토 필터가 선택돼도 다섯 작업이 남았음을 보여 준다. 최종 기록과 구분돼 보존되어 있다. 실패 원인의 세부 추정이나 과거 수정 전 코드 전체를 독립 재현했다고 판단하지 않았다.

이 증거는 배치 차이와 수행한 조작을 뒷받침한다. 어느 안이 빠른지·좋은지, 사용자 선호·채택은 입증하지 않으며 결과 문서도 선택 대기로 남긴다.

### E3. 상태/로직 공개 조작 증거

[질문·규칙·결과·실행 안내](prototype/state-logic/result.md), [단일 HTML](prototype/state-logic/index.html), [관찰기](prototype/state-logic/observe.mjs), [최종 원출력](prototype/state-logic/evidence/06-green-full.txt)과 앞선 실패 원출력을 직접 읽었다. 공개 Interface는 참가자 라디오와 Reserve / Cancel / Reset 버튼, 표시 명단·인원·안내·이력이다. 관찰기는 독립 Chrome의 실제 마우스 입력을 사용하고 표시 DOM을 읽으며 내부 상태 함수를 직접 호출하지 않는다.

원출력의 12개 상태를 전부 읽어 결과 표와 대조했다. 핵심 변화는 다음과 같다.

| 공개 조작 구간 | 실제 원출력의 확정 명단 | 대기열 |
|---|---|---|
| Ada·Bo 예약 후 Cy·Dana 신청 | Ada, Bo | Cy, Dana |
| Cy 중복 신청 | Ada, Bo | Cy, Dana |
| Cy 대기 취소 | Ada, Bo | Dana |
| Cy 재신청 | Ada, Bo | Dana, Cy |
| Ada 취소 | Bo, Dana | Cy |
| Bo 취소·미참여 Ada 취소 | Dana, Cy | 빈 목록 |
| Reset | 빈 목록 | 빈 목록 |

검증자는 [만석](prototype/state-logic/evidence/06-green-01-full-with-waitlist.png), [첫 승격](prototype/state-logic/evidence/06-green-02-first-promotion.png), [두 번째 승격과 무변경 취소](prototype/state-logic/evidence/06-green-03-second-promotion-and-noop.png), [Reset](prototype/state-logic/evidence/06-green-04-reset.png) PNG 4장을 모두 직접 열었다. 명단·인원·안내·이력이 원출력과 일치한다. Reset 뒤 이력은 초기 안내 한 항목으로 바뀐다.

`01-red-reserve.txt`는 첫 예약 후 빈 명단, `03-input-driver-failure.txt`·`04-input-focus-retry-failure.txt`는 Bo 선택이 Ada에 남은 입력 실패, `05-red-cancel.txt`는 Cy 취소 후 대기열이 변하지 않은 실패를 보존한다. 최종 원출력은 이들과 구분된 12개 상태와 PASS 행을 가진다. 입력 실패를 로직 성공 증거로 계산하지 않았다.

확인된 것은 고정 4명·정원 2명·한 탭에서 기록된 순차 조작이다. 동시 요청·저장·새로고침·미실행 분기는 결과 문서에서도 미확인으로 남아 있다. 실제 사용자의 규칙 승인·선호·채택은 없다.

### E4. 실제 SQLite 명령·원출력·DB

[결과와 공개 실행 안내](prototype/technical-feasibility/result.md), [probe.py](prototype/technical-feasibility/probe.py), [assert_case.py](prototype/technical-feasibility/assert_case.py), `wait.json`·`timeout.json`을 직접 읽었다. 스크립트는 실제 디스크 SQLite 파일을 만들고 별도 프로세스 A/B를 실행한다. A의 실제 `BEGIN IMMEDIATE` 잠금 획득 출력 뒤 B를 시작하며, 실제 트랜잭션·고유 키·잠금 오류를 관찰한다. 별도 DB 모킹은 없다. assertion은 공개 명령을 실행하고 stdout을 확인한다.

`evidence/`의 `red-wait`, `green-wait`, `red-timeout`, `final-wait`, `final-timeout` 각각에서 `command.json`, `stdout.json`, `stderr.txt`, `exit-status.txt`를 직접 읽었다. 원출력의 입력·자식 명령·이벤트·오류·시간과 결과 보고를 대조했다.

| 최종 증거 | B 대기 입력 | A 결과 | B의 실제 결과 | B 관찰 시간 | 최종 예약 |
|---|---:|---|---|---:|---|
| [final-wait stdout](prototype/technical-feasibility/evidence/final-wait/stdout.json) | 2000 ms | reserved | already_reserved / IntegrityError | 719.692 ms | room-1, A 한 건 |
| [final-timeout stdout](prototype/technical-feasibility/evidence/final-timeout/stdout.json) | 50 ms | reserved | database_locked / OperationalError | 79.767 ms | room-1, A 한 건 |

두 최종 probe 및 자식 프로세스 종료 코드는 0이고 stderr 파일은 0 bytes다. B의 충돌·잠금 오류는 JSON에 남아 있으므로 종료 코드만으로 예약 성공을 판단하지 않았다. 초기 `red-wait`는 not_implemented, `red-timeout`은 B의 실제 잠금 오류 traceback과 종료 코드 1을 보존한다. 과거 assertion 자체의 종료 코드와 probe의 종료 코드를 혼동하지 않았다.

존재하는 DB 4개(`green-wait`, `red-timeout`, `final-wait`, `final-timeout`)는 Python `sqlite3.connect(<file URI> + '?mode=ro', uri=True)`로만 열었다. 각각 다음을 직접 확인했다.

- 스키마: `resource TEXT PRIMARY KEY`, `owner TEXT NOT NULL`인 reservations 테이블.
- `SELECT resource, owner FROM reservations ORDER BY resource`: 모두 `('room-1', 'A')` 한 행.
- `PRAGMA integrity_check`: 모두 `ok`.
- 조회 전후 SHA-256: 모두 불변. 원본 DB를 쓰기 연결로 열거나 probe에 다시 전달하지 않았다.

이 증거는 현재 호스트·SQLite·실제 파일·두 입력에서 예약 한 건 유지와 서로 다른 B 실패 경로를 뒷받침한다. 실제 서비스 대신 고정 A/B·자원 하나와 인위적 700 ms 지연을 썼다는 대체 범위가 보고에 있다. 50 ms를 엄격한 벽시계 상한이라고 주장하지 않으며 처리량·장애 복구·제품 정책은 미확인이다.

### E5. 원문 대응

[source-map.md](source-map.md)의 규칙별 경로·위치를 원문과 직접 대조했다. [Matt prototype](../../docs/matt-skills/prototype/SKILL.md)의 질문 우선·보존, [UI](../../docs/matt-skills/prototype/UI.md)의 기본 3안·사용자 비교, [LOGIC](../../docs/matt-skills/prototype/LOGIC.md)의 상태·조작·관찰, [pstack](../../docs/pstack/skills/poteto-mode/playbooks/prototype.md)의 작은 화면/스크립트·출력·시간 관찰, [Superpowers](../../docs/superpowers/brainstorming/SKILL.md)의 판단 주체·최소 테스트·대화 복귀가 대응한다. [ask-matt](../../docs/matt-skills/ask-matt/SKILL.md)의 독립 도구와 [PHASE-BOUNDARIES](../../docs/matt-skills/ask-matt/PHASE-BOUNDARIES.md)의 현재 세션 우선 판단도 확인했다.

직접 호출 전용·단일 UI 1안·사용자 종료·`.goal` 보관·부모 단계 커밋·자동 제품 반영 배제는 로컬 조정으로 구분돼 있다. 원문의 테스트 생략을 작은 측정 허용으로 조정한 이유도 기록한다. [writing-skills](../../docs/superpowers/writing-skills/SKILL.md)의 적용·변형·정보 누락 평가를 참고했지만 세 사례의 수량과 별도 시나리오 제외는 로컬 합의로 구분한다. 원문을 방법의 효과 실증으로 사용하지 않았다. 실제 적용 근거는 E2–E4다.

### E6. Git 범위와 보존 상태

직접 사용한 주요 Git 명령 범위는 다음과 같다. 티켓·handoff 본문을 출력하는 `git show`나 diff는 실행하지 않았다.

```sh
git status --short
git log --format='%h %ad %s' --date=iso-strict 5b5da04..6198de7
git log --format='%h %s' --name-status 5b5da04..6198de7
git diff --name-status 5b5da04 6198de7
git diff 5b5da04 6198de7 -- .goal/workflow-prototype/goal.md .goal/workflow-prototype/skill-draft.md .agents/skills/workflow-prototype/SKILL.md .agents/skills/workflow-prototype/agents/openai.yaml
git diff --name-status 6198de7 -- .goal/workflow-prototype .agents/skills/workflow-prototype
```

| 커밋 | 실제 변경 목록에서 확인한 범위 |
|---|---|
| `d1805fa` | 새 스킬 두 파일, source-map, 해당 티켓 경로 |
| `275a86f` | technical-feasibility 사례 폴더, 해당 티켓 경로 |
| `cd469d8` | ui-comparison 사례 폴더, 해당 티켓 경로 |
| `ef0ea4b` | state-logic 사례 폴더, 해당 티켓 경로 |
| `6198de7` | 이 목표의 handoff 경로만 변경 |

허용 구간에 기존 단계 스킬·AGENTS.md·제품 코드·다른 목표 경로의 변경이 없다. 다른 목표의 미커밋 변경은 시작부터 존재했으며 판정자는 수정·스테이징하지 않았다. 검증 시작 시 이 목표와 새 스킬의 파일은 `6198de7`과 달라진 내용이 없었다.

추가로 `git show 5b5da04:<경로>`로 읽은 `goal.md`·`skill-draft.md`는 현재 파일과 바이트가 같았다. `git diff --exit-code <각 산출물 커밋> 6198de7 -- <해당 산출물 경로>`로 스킬·세 사례가 각 위 커밋 이후 변하지 않았음도 확인했다. 기준점에 목표 문서가 있다는 사실만으로 그 이전 Define 커밋 시점이나 Round 중 커밋 부재를 추정하지 않았다.

## Evaluation별 판정

### R1 — 지원 범위: PASS

- **근거:** E2의 목록·카드·보드 3안과 실제 필터·상세 상태, E3의 공개 조작에 따른 대기열·승격·초기화, E4의 공개 CLI 입력·실제 프로세스 경쟁·출력·DB가 각각 질문에 답한다. 세 사례 모두 질문·실행 안내·산출물·관찰·한계가 지정 폴더에 있다.
- **Gap/한계:** UI 선호와 제품 규칙 채택은 사용자 선택 대기다. 이는 세 유형의 관찰 증거 부재와 구분한다. 실제 사용자 아이디어가 없을 때 작은 사례를 에이전트가 선택할 수 있다는 D4 범위에서 판정했다.

### R2 — 독립 사용과 복귀: PASS

- **근거:** E1은 독립 스킬·명시 호출 정책과 원래 논의 복귀를 명시한다. 세 `result.md`의 실제 적용 요청 기록은 모두 스킬 경로와 명시 적용 요청을 제시하고, 결과를 부모 Execute/원래 논의로 반환하며 다음 단계나 제품 구현으로 진행하지 않는다. E6에서 기존 단계 연결·스킬 변경이 없다.
- **Gap/한계:** 실제 호출 기록은 사용자 승인 평가를 위한 **명시 위임의 에이전트 수행 사례**다. 사용자가 새 세션의 선택기에서 스킬을 호출한 런타임이나 Analysis·Define·단독 요청의 모든 경로를 실행했다고 판정하지 않았다. 미실행 경로는 본문·설정 대조 범위다.

### R3 — 작은 제작과 피드백: PASS

- **근거:** E2는 같은 다섯 작업의 3안, E3는 정원 2·참가자 4명의 단일 HTML 조작부, E4는 자원 한 개·두 프로세스의 표준 라이브러리 CLI다. 각 기록은 정해진 질문·폴더를 활용해 추가 질문 없이 진행했고, 결과·원자료가 그 작은 질문에 대응한다. E1은 필요한 결정만 질문하고 고정 시간·총 반복 수·별도 제품 goal/ticket·제품 테스트 체계를 공통 조건으로 요구하지 않는다. 실제 산출물도 별도 제품 구조나 테스트 프레임워크를 만들지 않았다.
- **Gap/한계:** 실제 사용자 피드백은 없다. 세 결과는 피드백·종료·채택을 대기로 남긴다. R4가 허용한 대기 처리를 피드백 획득으로 바꾸지 않았다. 단일 아이디어 1안, 모호한 질문 재질문 등 미실행 분기는 E1의 본문으로만 확인했다. 별도 시나리오는 추가하지 않았다.

### R4 — 확인한 만큼만 보고: PASS

- **근거:** E2의 배치·5→2 필터·상세 보고는 9장 PNG와 12개 상태에, E3의 FIFO·취소·중복·Reset 보고는 12개 원출력과 4장 PNG에 일치한다. E4의 최종 한 건·B의 충돌/잠금 오류·측정값은 명령·JSON·DB와 일치한다. 보고는 headless·고정 데이터·미실행 분기와 대체 조건을 명시하며 UI 속도 우위·운영 성능을 주장하지 않는다. 실패 자료도 성공으로 계산하지 않는다.
- **Gap/한계:** 사용자 응답은 보존 자료에 없으며 세 보고도 사용자 선호·규칙 승인·채택을 확정하지 않는다. 과거 실패 원인의 세부 진단·전체 과거 실행 시점은 독립 확정한 범위가 아니다. 현재 판정은 질문에 답하는 관찰과 대응 보고의 일치에 한정한다.

### C1 — 근거 추적: PASS

- **근거:** E5의 대응표는 질문 우선·UI 3안·상태 조작·기술 관찰·최소 측정·사용자 판단·복귀·보존·정식 재사용·정책을 원문과 연결한다. 로컬 조정과 원문 규칙을 구분하며 E1의 승인 문구 일치와 E2–E4의 실제 적용이 뒷받침한다. 공식 정책은 직접 연 공식 문서로 확인했다.
- **Gap/한계:** 시간 절감·판단 정확도·장기 효과는 원문이나 사례로 실증하지 않았고 목표의 범위도 아니다. 원문의 모든 구현 방식을 일괄 채택했다고 해석하지 않았다.

### C2 — 단계 원칙 유지: PASS

- **근거:** E1은 다음 단계·제품 구현을 사용자 요청에 두고 탐색과 Evaluation 판정을 구분한다. 세 결과는 사례 관찰과 사용자 선택 대기를 반환하며 최종 Verify 또는 제품 구현을 수행했다고 보고하지 않는다. E6의 실제 변경은 새 스킬·평가 사례·목표 내부 기록뿐이며 기존 단계 스킬과 AGENTS.md가 바뀌지 않았다.
- **Gap/한계:** 허용 구간 밖 전체 과거 대화의 단계 이동은 감사하지 않았다. 이번 산출물·진행 기록과 허용 Git 범위에서 자동 단계/제품 반영의 증거는 없다.

### C3 — 현재 문서·커밋 규칙: UNKNOWN

- **확인한 근거:** `goal.md`, `skill-draft.md`, `source-map.md`, 세 사례 및 본 Verify가 `.goal/workflow-prototype/`에 있다. E6에서 기준점의 목표·확정 문구 스냅샷이 현재와 같고, 이후 커밋이 이 목표에 한정돼 다른 목표를 포함하지 않음을 확인했다.
- **Gap:** 필요한 **Define 완료 커밋과 그 시점의 변경 목록**, Define·Plan **Round 경계와 커밋 시점의 대응**은 `5b5da04` 이후 허용 이력으로 확인할 수 없다. `goal.md`의 Define 완료 문구나 기준점에 파일이 있다는 사실만으로 과거 절차 준수를 PASS로 만들 수 없다. 위반도 확인되지 않아 FAIL로 단정하지 않는다.
- **후속:** 이 항목을 확정할 필요가 있으면 기존 Define 커밋·변경 목록과 Round 경계를 확인할 수 있는 당시 근거를 허용 입력으로 추가한 뒤 C3만 다시 평가한다. 구현·실험을 다시 수행해 해결할 항목은 아니다.

### C4 — 직접 호출과 사용자 판단: PASS

- **근거:** E1의 정책 파싱은 false이고 공식 설정과 일치한다. 설명·본문은 사용자 직접 호출을 명시하고 허용 작업은 재확인 없이 수행하며 방향·확대·추가 실험·종료·채택은 사용자에게 둔다. E2–E4는 명시 적용을 요청한 위임 평가로 진행했고, 작은 사례의 에이전트 선택을 사용자 제품 합의로 기록하지 않았다. 실제 사용자 선호·승인·채택은 선택 대기다.
- **Gap/한계:** 설정 대조와 위임된 명시 적용을 확인했다. Codex 런타임의 암시적 호출 차단이나 실제 사용자의 선택기 호출을 동적으로 시험하지 않았다. 이는 goal.md가 구분한 미관찰 범위이며 별도 비호출/범위 확대 시나리오를 추가하지 않았다.

### C5 — 보관·격리·커밋: PASS

- **근거:** E2–E4의 세 폴더에 질문·안내·HTML/스크립트·입력·실패/최종 원자료·캡처/DB가 보존돼 있다. 공개 실행 안내와 스크립트가 대응하고 이전 증거와 다른 이름/새 DB로 실행하도록 안내한다. E6에서 각 사례는 부모 Execute의 해당 사례 커밋에 들어갔고 다른 목표를 포함하지 않았다. 사용자의 실험 종료·채택이 대기여도 단계 중 평가 사례이므로 부모 단계 커밋 규칙을 적용한다. E1은 기본 현재 작업 공간, 필요한 경우만 worktree/새 세션, 단독 실험의 사용자 종료 후 커밋을 명시한다.
- **Gap/한계:** 이번 사례에서 독립된 단독 실험의 종료 판단·커밋, worktree 이동 조건은 실행하지 않았으므로 본문 규칙으로만 확인했다. 새로운 worktree·세션·커밋을 검증을 위해 만들지 않았다. 검증자는 원본 증거를 삭제·덮어쓰기하지 않았다.

### C6 — 탐색과 정식 구현: PASS

- **근거:** E1은 작은 검사·측정을 허용하고 제품 테스트를 공통 조건으로 요구하지 않으며, 정식 재사용에는 기존 품질 기준을 적용한다. E2·E3의 공개 조작 확인과 E4의 두 조건·시간·실제 오류 측정이 작은 질문에 대응한다. E6에는 제품 반영 변경이 없고 사례들은 결과를 원래 논의에 반환한다. 모든 코드를 반드시 삭제/재사용하라는 규칙도 없다.
- **Gap/한계:** 이번 목표는 제품 재사용을 구현하지 않으므로 재사용 품질 규칙은 본문 검토만으로 확인했다. 실제 제품 품질·운영 적합성을 이 탐색의 통과로 보장하지 않는다.

## 미충족·추가 확인과 적절한 후속 단계

| 구분 | 남은 사항 | 적절한 처리 |
|---|---|---|
| 평가 증거 Gap | C3의 Define 완료 커밋·Round 시점 자료가 허용 범위 밖 | 과거 근거가 허용되면 Verify에서 C3만 보완 판정한다. 현재로서는 UNKNOWN을 유지한다. |
| 사용자 판단 대기 | UI 선호, 상태 규칙 적합성, 기술 결과의 충분성, 추가 실험·종료·채택 | 원래 논의에서 사용자 판단을 받는다. 없는 피드백을 만들거나 이번 검증의 새로운 필수 사례로 늘리지 않는다. |
| 합의된 관찰 한계 | 앱 런타임 호출 차단, 단일 UI 예외, 미실행 로직 분기, 다른 환경의 SQLite·운영 성능 등 | 본문·설정 검토와 실제 실행 범위를 구분해 유지한다. 추가 실험은 사용자가 필요성을 판단한 뒤 별도 범위로 정한다. |
| 구현 수정 | 이번 증거 대조에서 확정된 FAIL 없음 | 새 기능·제품 반영·자동 단계 이동을 하지 않는다. |

이 판정은 스킬과 세 작은 적용 사례가 합의된 지원·진행·보고·보존 규칙을 충족한다는 증거를 확보한 것이다. C3의 과거 절차를 확인할 수 없어 **목표 전체의 무조건 PASS는 보류**한다. 실제 사용자 선호·종료·채택, 방법의 장기 효과나 제품 완성도는 판정하지 않았다. 판정자는 `verify.md`만 작성했으며 스테이징·커밋은 하지 않았다.
