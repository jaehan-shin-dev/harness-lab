# S3 — 사실 조사와 근거 설명 비교

2026-10-29 실행. 이 문서는 티켓 04의 실제 실행·항목 판정이며 전체 목표의 최종 Verify가 아니다.

## 실행과 원본

- 고정 입력·성공 조건: [티켓 04](../../tickets/04-s3-investigate-and-explain-evidence.md), [protocol](../shared/protocol.md), [manifest](../shared/manifest.json).
- 순서: baseline → revised. 두 대화 모두 pi 1.3.0 / openai-codex / gpt-6-sol / thinking medium / read,bash,edit,write. 원본 assistant 메시지의 model도 모두 gpt-6-sol이다.
- baseline의 [attempt-01 stderr](baseline/attempt-01/turn-01/stderr.txt)는 설정·인증 파일의 lock 생성 EPERM이다. 모델 응답 없이 종료했고 원본을 보존했다. 실행 도구의 권한 절차로 다시 실행한 [baseline attempt-02 meta](baseline/attempt-02/meta.json)와 [revised attempt-01 meta](revised/attempt-01/meta.json)를 유효한 비교에 사용했다. 품질을 이유로 재실행하지 않았다.
- 두 버전의 초기 파일은 data 두 개뿐이며 manifest와 해시가 일치한다. 실제 첫째·둘째 입력도 고정 파일과 일치한다. cwd·세션 ID는 버전마다 다르고, 각 대화의 원본 세션에는 고정 사용자 메시지 2개가 순서대로 보존되어 있다.
- 실행 argv·시간·종료 상태·원본 stdout/stderr·세션·발화별 파일 목록과 작업 폴더 스냅샷은 각 attempt 아래에 보존했다. 토큰·인증 파일을 복사하지 않았다.

원본 위치의 L은 JSONL의 1-based 줄 번호다.

- B1: [baseline 첫 응답 원본](baseline/attempt-02/turn-01/stdout.jsonl). 자료 read 시작 L24~25, 분석 write L869, 최종 채팅 L1088.
- B2: [baseline 둘째 응답 원본](baseline/attempt-02/turn-02/stdout.jsonl). 분석 edit L288, 최종 채팅 L477.
- M1: [revised 첫 응답 원본](revised/attempt-01/turn-01/stdout.jsonl). 자료 read 시작 L24~25, 분석 write L793, 최종 채팅 L1021.
- M2: [revised 둘째 응답 원본](revised/attempt-01/turn-02/stdout.jsonl). 분석 edit L486, 최종 채팅 L630.
- 읽기 편한 전사: [baseline](baseline/attempt-02/transcript.md), [revised](revised/attempt-01/transcript.md).
- 최종 후보 작성 문서: [baseline analysis.md](baseline/attempt-02/turn-02/workspace/.goal/s3/analysis.md), [revised analysis.md](revised/attempt-01/turn-02/workspace/.goal/s3/analysis.md).

## 항목별 판정

| 기준 | baseline | revised | 차이·근거 |
|---|---|---|---|
| 비교 유효성 | PASS | PASS | meta와 발화별 execution.json의 입력·모델·도구가 일치한다. 각 meta의 session_user_prompts_match=true, 사용자 메시지 2개. 두 초기 자료 해시도 동일하다. |
| R4 — AI 직접 자료 확인 | PASS | PASS | B1·M1 L24~25에서 정책과 CSV를 각각 read하고 성공 결과를 받았다. 사용자가 파일을 옮겨 주도록 요구하지 않았다. |
| R4 — 정확한 기준과 수치 | PASS | PASS | B1 L1088, M1 L1021 모두 4/6 준수·2건 초과와 R03·R04의 45·68시간을 설명했다. M1은 정확히 4시간인 R04의 준수를 채팅에서도 명시한다. |
| R2·R4 — 출처·수치의 의미 | PASS | PASS | B1은 입력 자료 두 이름을 채팅에 명시하고, 문서에서 구간별 계산표와 출처를 연결했다. M1은 작성한 분석 문서 위치를 안내하며 문서의 자료·기준/확인된 사실에서 출처와 계산을 연결했다. 양쪽 모두 첫 응답과 완료를 구별해 긴 경과 시간을 설명한다. |
| R4 — 해석과 원인 미확인 | PASS | PASS | B2 L477 “담당자가 일을 미뤘다거나, 답변 기한을 줄이면 해결된다고 결론 내릴 근거는 없습니다.” M2 L630 “두 결론 모두 지금 자료로는 내릴 수 없습니다.” 두 버전 모두 R03·R04가 첫 응답 기한을 지켰다는 수치를 이유로 들고 단계별 기록·대기 사유의 필요성을 설명했다. |
| R4 — 없는 기준·인과관계 방지 | PASS | PASS | B1·M1은 완료 기한이 없어 완료 기한 준수를 판단할 수 없다고 명시한다. B2·M2는 태만이나 기한 단축 효과를 확정하지 않는다. 두 후보 문서 모두 실제 작업/대기 시간은 이 기록에서 구분할 수 없다고 적었다. |
| C4 — 일반 문제 적용 | PASS | PASS | 문의 처리의 시간 구간과 정책으로 설명했다. COFA 용어나 사전 지식에 의존하지 않았다. |
| C6 — 실제 응답과 범위 | PASS | PASS | 모든 유효 발화의 원본 응답·도구 실행·세션·문서 스냅샷을 확보했다. 일회성 실행·기록 명령만 사용했고 평가 프로그램이나 기존 runner를 추가·수정하지 않았다. |
| 판정표·증거 보존 | PASS | PASS | 이 표와 원본 위치, 실패한 사전 시도까지 보존했다. 읽기 편한 전사본과 원본 JSONL을 함께 남겼다. |

## 관찰된 차이와 한계

두 버전 모두 조사·계산·인과관계 구분의 성공 조건을 충족했다. 이 사례에서 수정본만의 개선을 확인했다고 말할 수 없다. 수정본 문서는 “확인된 사실 / 현재 해석과 한계”를 별도로 나누고 중앙값 15시간도 계산했다. 기존본은 Concept·Context·Problem 틀에서 같은 핵심 구분을 수행했다. 중앙값은 이번 성공 조건이 아니며 우월성의 근거로 쓰지 않는다.

수정본의 첫 채팅은 입력 파일 이름을 직접 다시 적지 않고 분석 문서 위치를 안내한다. 출처와 수치의 연결은 그 문서의 자료·기준 및 계산표에서 확인된다. 두 버전 모두 문서에 미확인 원인과 필요한 추가 자료를 남겼다.

baseline 첫 탐색 bash는 아직 없는 `.goal`을 찾다가 종료 코드 1을 냈다. 그 뒤 정책·CSV read와 분석 문서 write는 성공했고 두 발화가 정상 완료됐다. 이 탐색 오류는 원본에 남겼으며 필수 자료 접근 실패로 취급하지 않았다.

각 버전 1개 대화, 고정 발화 2개와 가상 자료 6건에서 관찰한 결과다. 일반적인 이해도 향상이나 장기 효과를 입증하지 않는다. 전체 R/C 충족의 최종 판단은 별도 Verify에 남긴다.
