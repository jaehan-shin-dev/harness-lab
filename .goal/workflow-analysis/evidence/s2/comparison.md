# S2: 반론 이후 설명 수정 — 실제 대화 비교

2026-10-29 Execute 티켓 03의 증거다. 전체 목표의 최종 Verify 판정은 아니다.

## 실행과 원본

- 고정 입력·모델·도구: [shared protocol](../shared/protocol.md), [environment](../shared/environment.json), [manifest](../shared/manifest.json). 양쪽 모두 pi 1.3.0, provider `openai-codex`, model `gpt-6-sol`, thinking `medium`, read·bash·edit·write.
- 순서: revised 성공 대화 → baseline 성공 대화. 두 버전은 서로 다른 UUID·빈 임시 작업 폴더·세션 폴더에서 시작했다. 같은 대화의 두 호출은 같은 세션을 이어 갔다.
- revised [attempt-02 meta](revised/attempt-02/meta.json), [전사본](revised/attempt-02/transcript.md), [첫 원본 V1](revised/attempt-02/turn-01/stdout.jsonl), [둘째 원본 V2](revised/attempt-02/turn-02/stdout.jsonl).
- baseline [attempt-01 meta](baseline/attempt-01/meta.json), [전사본](baseline/attempt-01/transcript.md), [첫 원본 B1](baseline/attempt-01/turn-01/stdout.jsonl), [둘째 원본 B2](baseline/attempt-01/turn-02/stdout.jsonl).
- 원본 assistant 응답 위치: V1 918행, V2 891행, B1 1037행, B2 1431행. 아래 표의 V1·V2·B1·B2는 이 원본을 가리킨다.
- 두 성공 대화의 네 호출 모두 종료 코드 0, 시간 초과 없음, `agent_settled` 존재. 원본에 실제 provider·model이 요청값으로 기록됐다. 원본 세션에서 같은 고정 사용자 발화 두 개가 순서대로 이어졌음을 별도로 확인했다.
- 각 `turn-0N/execution.json`에 argv·cwd·세션 ID·시작 시각·소요 시간·종료 상태, `files.json`과 `workspace/`에 응답 직후의 파일 목록·해시·원문이 있다. 스냅샷 파일 해시를 재계산해 기록과 일치함을 확인했다.

## 항목별 판정

| 기준 | baseline | revised | 관찰된 차이·한계 |
|---|---|---|---|
| 비교 유효성 | PASS. [meta](baseline/attempt-01/meta.json)의 입력 해시 두 개가 manifest와 일치하고 원본 세션의 사용자 메시지 2개가 입력 파일과 정확히 같다. | PASS. [meta](revised/attempt-02/meta.json)의 같은 입력 해시·원본 메시지를 확인했다. | 스킬 해시·UUID·cwd·실행 시각 외 목표 조건이 같다. 실패한 사전 시도는 아래에 별도 보존했다. |
| R2: 해석을 구별하는 설명·예시·질문 | PASS. B1은 원래 기준 누락, 초안을 보고 선호를 알게 된 경우, 읽으며 방향이 바뀐 경우를 구분하고 “초안을 보기 전에도 원했나요”라고 묻는다. B2는 명료화와 선호 변화의 역할을 설명한다. | PASS. V1은 누락과 결과를 통한 기준 발견을 예시로 구분하고 무엇을 보고 바꾸었는지 질문한다. V2는 두 역할을 짧게 설명한다. | 양쪽 모두 질문만 이어 가지 않고 구분과 사례를 제공했다. 이 항목의 충족 차이는 관찰되지 않았다. |
| R3: 새 정보 반영 | PASS. B2는 “독자·목적·길이는 이미 전달됐고”와 결과를 읽은 뒤 선호가 바뀌었다는 점을 근거로 초기 요구만 자세히 쓰면 수정이 사라진다는 해석을 거부한다. | PASS. V2도 전달·이해가 이미 맞았다는 정보와 선호 변화를 근거로 초기 요구 누락을 주된 설명에서 낮춘다. | 두 버전 모두 반론을 해석에 반영했다. |
| R3: 무엇을 왜 수정·유지했는지 설명 | PASS. B1에서 세 가능성을 열고 B2에서 추가 정보에 따라 “요구를 못 써서 생긴 문제”만으로 해석할 필요가 없다고 구체화한다. [둘째 문서](baseline/attempt-01/turn-02/workspace/s2/.goal/draft-revision-understanding/analysis.md)에도 전달 실패와 선호 변화를 구별하고 새 정보에 맞는 해석을 적었다. | PASS. V2는 “앞서 제가 ‘처음 요구의 누락’도 가능성으로 제시했지만, 새 정보를 보면 이 사례의 주된 설명으로 보기는 어렵습니다”라고 변화와 이유를 직접 말한다. [둘째 문서](revised/attempt-02/turn-02/workspace/s2/.goal/s2/analysis.md)도 같은 판단을 반영한다. | revised는 이전 가설과 현재 판단의 연결을 응답에서 더 명시적으로 표현했다. baseline도 같은 판정 기준을 충족하므로 이를 행동 성공 여부의 차이로 확대하지 않는다. |
| R3: 근거 없는 동의·반대 극단 회피 | PASS. B2는 사전 명료화로 오해에 의한 수정을 줄일 수 있지만 이후 선호 변화는 별개라고 설명한다. | PASS. V2는 “요구를 명확히 할 필요가 없다는 뜻도 아닙니다”라며 알려진 조건과 후속 선호를 구별한다. | 양쪽 모두 사용자가 제시한 두 극단을 그대로 채택하지 않았다. |
| C4: 일반 문제 적용 | PASS. B1·B2는 기획 문서의 말투·강조점과 독자·목적을 다룬다. COFA 지식을 요구하지 않는다. | PASS. V1·V2도 일반적인 문서 협업만으로 설명한다. | 분야 의존성 차이는 관찰되지 않았다. |
| C6: 실제 응답과 범위 | PASS. 원본 JSONL·도구 조회/작성·세션·작업 폴더 스냅샷을 확보했다. | PASS. 같은 종류의 실제 증거를 확보했다. | 별도 모의 사용자·심판·새 runner 또는 기존 skill-eval 확장이 없다. 실행을 위한 일회성 도구 호출만 사용했다. |

R2·R3·C4·C6의 이 사례에 배정된 행동 항목은 두 버전 모두 PASS다. 스킬 변경이 이 행동을 새로 만들어 냈다거나 일반적인 학습 효과를 높였다는 결론은 내리지 않는다.

## 보존한 실행 실패

revised의 [attempt-01](revised/attempt-01/meta.json)은 실제 모델 응답 전에 종료됐다. [stderr](revised/attempt-01/turn-01/stderr.txt)에 홈 pi 설정·인증 파일의 lock 디렉터리 생성이 EPERM으로 차단된 기록이 있다. stdout에는 세션 시작 이벤트만 있고 assistant 응답은 없다.

실행 도구의 권한 절차 후 같은 조건·입력을 새 UUID의 attempt-02에서 실행했다. 실패한 시도를 덮어쓰지 않았으며 응답 품질을 이유로 재실행하지 않았다. 인증 파일·토큰은 증거에 복사하거나 출력하지 않았다.

## 범위 밖에서 관찰한 기록 경로

프로토콜은 작업 폴더 기준 `.goal/s2/analysis.md`의 존재를 기록하도록 정했다. 두 버전 모두 이 정확한 경로에는 파일을 만들지 않았다. revised는 `s2/.goal/s2/analysis.md`, baseline은 `s2/.goal/draft-revision-understanding/analysis.md`를 만들었다. 각 `files.json`의 `analysis_exists`는 false이고 실제 파일은 `workspace/`에 그대로 보존돼 있다.

S2 티켓은 R6의 정확한 기록 위치를 행동 성공 조건으로 배정하지 않았으므로 이 문제를 R3 FAIL로 바꾸지는 않았다. 다만 두 버전이 공통 시작 안내의 “작업 폴더 이름”을 추가 하위 폴더로 해석한 흔적이 있어 main에 보고했다. 입력·출력·확정 스킬을 바꾸거나 파일을 올바른 위치로 대신 옮기지 않았다.
