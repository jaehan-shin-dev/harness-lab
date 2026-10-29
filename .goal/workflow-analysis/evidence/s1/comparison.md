# S1 — 이미 준 정보 활용과 마무리

수정본은 S1의 행동 성공 조건을 모두 충족했다. 기존본도 기존 정보를 활용하고 자연스럽게 마무리했으나, 둘째 발화에서 확인된 이해와 남은 의문을 분석 기록에 반영하지 않았다. 이 판정은 이번 사례의 관찰이며 전체 목표의 최종 판정은 아니다.

## 실행 조건과 원본

- 기준: [티켓 02](../../tickets/02-s1-existing-context-and-close.md), [protocol](../shared/protocol.md), [manifest](../shared/manifest.json).
- 순서: baseline→revised. 유효한 실행은 [baseline attempt-02](baseline/attempt-02/meta.json)와 [revised attempt-01](revised/attempt-01/meta.json)이다.
- 두 버전 모두 pi 1.3.0, provider openai-codex, model gpt-6-sol, thinking medium, read/bash/edit/write. 4개 성공 응답에서 실제 assistant model도 gpt-6-sol이며 종료 코드 0과 agent_settled를 확인했다.
- 두 대화는 각각 새 빈 임시 폴더와 다른 UUID에서 시작했다. 같은 대화의 두 발화는 한 세션 파일의 사용자 메시지 2개로 이어졌고, 메시지·argv를 고정 입력과 대조했다.
- 각 첫 응답의 stdout.jsonl 5행 system addendum이 해당 버전의 전체 스킬과 일치한다. 다른 스킬·문맥 자동 로딩을 끈 명령은 execution.json에 보존했다. 도구 기록에는 자기 작업 폴더 조사와 분석 문서 생성·갱신만 있으며 비교 자료 조회는 없다.
- 실제 후보 응답은 [baseline 전사본](baseline/attempt-02/transcript.md), [revised 전사본](revised/attempt-01/transcript.md)에서 읽을 수 있다. 아래 행 번호는 전사본이 가리키는 원본 stdout.jsonl 기준이다.

## 항목별 판정

| 기준 | baseline 결과·증거 | revised 결과·증거 | 관찰된 차이·한계 |
|---|---|---|---|
| 비교 유효성 | PASS. [meta](baseline/attempt-02/meta.json), 발화별 [실행 1](baseline/attempt-02/turn-01/execution.json)·[실행 2](baseline/attempt-02/turn-02/execution.json). 동일 고정 발화, 빈 초기 폴더, 새 세션, 실제 모델과 세션 연결 확인. | PASS. [meta](revised/attempt-01/meta.json), [실행 1](revised/attempt-01/turn-01/execution.json)·[실행 2](revised/attempt-01/turn-02/execution.json). 같은 조건과 연결 확인. | 경로·UUID·실행 시각만 실행별로 다르다. 제한된 첫 시도는 판정에서 제외했다. |
| R1 — 기존 정보에서 출발 | PASS. [첫 응답 원본](baseline/attempt-02/turn-01/stdout.jsonl) 768행: 공지의 존재와 필요한 순간에 찾기의 차이를 설명. [분석 기록](baseline/attempt-02/turn-01/workspace/.goal/s1/analysis.md)의 Context에 8명·월 1회·공지 구성·반복 질문·메시지 부담을 활용. 이미 답한 배경이나 목표를 재수집하지 않음. | PASS. [첫 응답 원본](revised/attempt-01/turn-01/stdout.jsonl) 688행과 [분석 기록](revised/attempt-01/turn-01/workspace/.goal/s1/analysis.md): 긴 공지와 한 달 간격을 가능한 해석에 연결. 질문은 공지를 못 봤는지 다시 찾기 어려운지에 관한 새 구분. | 양쪽 모두 충분한 입력에서 바로 탐색했다. |
| R2 — 상황에 맞는 설명·질문 | PASS. 첫 응답 768행에서 전달과 검색·확인의 차이, 공지 미열람·긴 글·변경 확인의 가능성을 설명. 사례 확인을 제안하지만 모든 수단을 강제하지 않음. | PASS. 첫 응답 688행에서 미열람과 필요 시 검색의 구분을 설명하고 어느 쪽인지 질문. 모든 수단의 나열·고정 인터뷰가 아님. | baseline은 설명·사례 제안, revised는 설명·해석 구분 질문을 골랐다. 질문 횟수 자체는 우열 근거가 아니다. |
| R6 — 현재 이해·남은 의문의 기록 | FAIL. [둘째 응답 원본](baseline/attempt-02/turn-02/stdout.jsonl) 51행은 효과 미확인을 인정하지만 도구 호출이 없다. [최종 분석](baseline/attempt-02/turn-02/workspace/.goal/s1/analysis.md)은 첫 응답 뒤 파일과 같은 해시이며, 둘째 발화에서 확인된 구분의 이해와 공지 집약의 효과에 대한 남은 의문을 반영하지 않았다. | PASS. [둘째 원본](revised/attempt-01/turn-02/stdout.jsonl) 33~34행 read, 213~214행 edit, 291행 마무리. [최종 분석](revised/attempt-01/turn-02/workspace/.goal/s1/analysis.md)의 ‘이번 대화에서 확인된 이해와 남은 불확실성’에 사용자가 이해했다고 말한 구분만 기록하고, 질문 감소 효과는 미확인으로 남김. | 이번에 관찰된 핵심 차이는 후속 반응을 분석 문서에 반영했는지다. baseline이 문서를 전혀 만들지 않았거나 사용자 동의를 조작했다는 뜻은 아니다. |
| R6·C3 — 마무리·이해 임의 확정·단계 경계 | PASS. 둘째 응답 51행: 효과는 아직 알 수 없다고 말하고 종료. 최종 분석에 ‘해결책이나 목표를 정하지 않습니다’. 이해 확인·승인 반복이나 Define 실행 없음. | PASS. 둘째 응답 291행: 효과는 가능성으로 남기고 목표·해결책을 정하지 않은 채 종료. 최종 기록도 원인·목표·해결책 미확정. | 양쪽 모두 이해나 동의를 추가로 가정하지 않고 마무리했다. revised만 후속 기록 갱신까지 수행했다. |
| C4 — 분야 독립성 | PASS. 독서 모임 공지 사례만으로 설명·기록함. | PASS. 같은 일반 사례에서 설명·질문·기록함. | COFA 지식이나 전용 절차를 사용하지 않았다. |
| C6 — 실제 실행·범위 | PASS. 원본 응답·도구 기록·세션·스냅샷을 보존. | PASS. 같은 종류의 실제 증거를 보존. | 새 평가 프로그램이나 기존 runner 변경 없이 일회성 프로세스 호출로 확보했다. |
| 판정 기록 | PASS. 미충족을 FAIL로 명시하고 원본 위치를 연결했다. | PASS. 모든 행동 항목을 실제 증거로 판정했다. | 최종 목표 판정과 verify.md 작성은 하지 않았다. |

## 제한된 첫 시도와 재시도

[baseline attempt-01](baseline/attempt-01/meta.json)은 샌드박스 안에서 첫 호출이 출력 없이 멈춘 시도다. 비밀을 제외한 인증 메타데이터에서 OAuth 만료를 확인했고, 다른 사례의 인증·설정 잠금 EPERM 보고와 함께 메인 지시에 따라 중단했다. 오케스트레이션 Python은 Ctrl-C로 종료했고, 남은 pi 프로세스 그룹은 해당 세션 UUID로만 찾아 SIGTERM했다. 원본 [stdout](baseline/attempt-01/turn-01/stdout.jsonl)·[stderr](baseline/attempt-01/turn-01/stderr.txt)는 모두 0바이트로 그대로 보존했다.

첫 시도의 [execution.json](baseline/attempt-01/turn-01/execution.json)은 중단 이유와 종료 신호를 기록하며, argv는 제출한 일회성 스크립트와 저장된 UUID에서 복원했다고 표시했다. 성공 종료 코드·모델 응답이 있는 것처럼 기록하지 않았다. [driver-interruption.txt](baseline/attempt-01/driver-interruption.txt)도 보존했다.

권한 절차를 거쳐 실제 대화 전체를 새 세션에서 재시도한 baseline attempt-02와, 뒤이어 같은 외부 실행 환경에서 수행한 revised attempt-01만 비교에 사용했다. 응답 품질 때문에 재실행하지 않았고 고정 발화·성공 조건·스킬 문구를 바꾸지 않았다.

## 관찰의 한계

각 버전 한 대화씩 관찰했다. 후속 기록 갱신의 차이는 확인했지만, 이를 일반적인 사용자 이해도 향상이나 장기 학습 효과의 증명으로 확대하지 않는다. 초기 설명과 단계 경계의 행동에는 두 버전 모두 충족한 부분이 있다.
