# S2 — 저장 위치 안내 수정 후 비교

## 조건 변경과 보존

사용자의 저장 위치 수정·Verify 완료 요청에 따라 첫 안내만 명확히 했다. [새 입력·protocol](shared/protocol.md)은 Plan 커밋 2ed417b에 사전 고정됐다. 담당자 조정은 969e5c0이며 입력·조건에는 영향이 없다. 기존 첫 발화 본문·둘째 발화·두 스킬·모델·thinking·도구는 그대로다. [manifest](shared/manifest.json)로 해시를 대조했다.

기존의 “작업 폴더 이름은 s2” 대신 현재 cwd가 작업 폴더이고 goal 이름이 s2이며 결과가 cwd 기준 .goal/s2/analysis.md라는 안내를 사용했다. 기존 기록을 이동하거나 고쳐 쓰지 않았고 [기존 비교](../s2/comparison.md)와 최초 Verify 커밋 2cfe328의 실패 판정은 보존했다.

## 실제 실행

- revised→baseline, 독립 새 세션 두 개에서 고정 발화 두 개씩 실행했다. 총 네 호출 모두 openai-codex/gpt-6-sol/medium, 종료 코드 0, agent_settled, 시간 초과 없음이다.
- 스킬은 기존 shared의 원본·확정 수정본을 사용했다. 실제 addendum의 본문이 해당 파일과 일치한다. 각 원본 세션의 사용자 발화 두 개가 새 입력 파일과 정확히 같다.
- 초기 cwd는 빈 폴더였다. 두 버전 모두 첫 응답의 write와 둘째 응답의 edit로 cwd 기준 .goal/s2/analysis.md를 생성·갱신했다. 실행자는 해당 문서를 작성하거나 이동하지 않았다.
- 실행 전 대기 중이던 하위 에이전트의 권한 요청 두 건은 main 중단으로 취소됐다. 둘 다 실제 프로세스·meta·결과가 없었으며 실행 시도로 세지 않았다. 이후 main의 require_escalated 요청이 승인되어 네 호출을 수행했다. 사용자 승인 철회나 모델 품질 실패로 기록하지 않는다.
- 원본 stdout/stderr·argv·시각·종료 상태·세션·입력/버전 해시·발화별 파일 목록/해시·작업 폴더 스냅샷·전사본을 보존했다. 품질 재실행은 하지 않았다.

## 항목별 판정

아래 L은 연결된 stdout.jsonl의 1-based 행 번호다. 행동 조건은 수정본에 필수이며 baseline에도 같은 기준을 적용했다.

| 항목 | baseline | revised | 원본 증거 |
|---|---|---|---|
| 비교 유효성 | PASS | PASS | 각 meta 및 발화별 execution.json, 원본 세션의 같은 두 입력과 UUID 연결. 실제 모델·thinking·도구·addendum과 입력·스냅샷 해시를 대조했다. |
| R6 — 정확한 기록 위치 | PASS | PASS | baseline T1 L549 write, T2 L759 edit. revised T1 L540 write, T2 L1012 edit. 모두 .goal/s2/analysis.md를 대상으로 하며 성공 결과·각 files.json·workspace의 실제 파일과 일치한다. |
| R2 — 상황에 맞는 설명·질문 | PASS | PASS | baseline T1 L743, revised T1 L784는 초기 기준 누락과 결과를 통한 선호 발견을 설명하고 시점을 구별하는 질문을 했다. 배경·목표를 반복 수집하지 않았다. |
| R3 — 새 정보 반영과 변경 근거 | PASS | PASS | baseline T2 L935, revised T2 L1260은 독자·목적·길이가 이미 전달됐고 결과를 본 뒤 선호가 바뀌었다는 정보로 해석을 구체화한다. revised는 앞서 열어둔 요구 누락을 주된 설명에서 낮춘 이유를 직접 설명한다. |
| R3 — 양 극단 회피 | PASS | PASS | 같은 둘째 응답에서 더 자세한 최초 요구가 모든 수정을 없애지 않으며, 그렇다고 요구 명료화가 불필요한 것도 아니라고 설명한다. |
| R6·C3 — 기록 내용·경계 | PASS | PASS | 최종 analysis.md에 사용자 진술·현재 해석·남은 의문이 구분된다. 사용자 이해·동의를 확인한 것으로 꾸미거나 Define으로 자동 진행하지 않았다. |
| C4·C6 — 일반 사례·실제 증거·범위 | PASS | PASS | 문서 협업 사례를 그대로 사용했다. 새 평가 프로그램·기존 runner·스킬 변경 없이 일회성 호출의 원본 증거를 남겼다. |

## 원본 위치

- [revised meta](revised/attempt-01/meta.json), [전사본](revised/attempt-01/transcript.md), [T1](revised/attempt-01/turn-01/stdout.jsonl), [T2](revised/attempt-01/turn-02/stdout.jsonl), [최종 문서](revised/attempt-01/turn-02/workspace/.goal/s2/analysis.md).
- [baseline meta](baseline/attempt-01/meta.json), [전사본](baseline/attempt-01/transcript.md), [T1](baseline/attempt-01/turn-01/stdout.jsonl), [T2](baseline/attempt-01/turn-02/stdout.jsonl), [최종 문서](baseline/attempt-01/turn-02/workspace/.goal/s2/analysis.md).

## 해석의 한계

명확한 저장 위치 안내를 받은 새 조건에서는 두 버전 모두 기대 위치에 기록했다. 이전 조건의 실패를 삭제하거나 이전 응답을 PASS로 바꾼 것이 아니다. 스킬을 고치지 않았으므로 스킬 자체의 경로 처리 능력이 개선됐다는 주장도 하지 않는다. 단일 추가 비교로 이전 실패의 원인이 안내의 모호함 하나였다고 입증할 수 없다.

R2·R3의 핵심 행동은 이전과 이번 모두 두 버전에서 충족됐다. 전체 목표의 최종 판정은 독립 Verify에 맡긴다.
