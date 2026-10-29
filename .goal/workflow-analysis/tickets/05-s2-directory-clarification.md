# 05: S2 저장 위치 안내 수정과 실제 재비교

**What to build:** cwd와 goal 이름을 구분한 안내로 S2를 다시 비교해, 분석 문서가 약속한 경로에 생성되는지와 반론 반영 행동이 유지되는지를 확인한다.

**Covers:** D3; R2, R3, R6, C3, C4, C6. D1 문구·D2·기존 증거는 유지한다.

**Blocked by:** 03 — 반론 이후 설명 수정 확인 — S2 (done).

**Files:**

- .goal/workflow-analysis/evidence/s2-dir-clarified/shared/의 입력·protocol·manifest (Plan에서 사전 고정, Execute에서는 읽기 전용).
- .goal/workflow-analysis/evidence/s2-dir-clarified/revised/, baseline/의 원본 응답·세션·실행 상태·스냅샷·전사본.
- .goal/workflow-analysis/evidence/s2-dir-clarified/comparison.md.
- 이 티켓의 Status와 Check results.

**Owner:** main

**Parallel:** no

**Status:** done

**Checks:**

- [x] 입력은 새 응답 전에 고정된다: shared manifest를 재계산하고 첫 발화의 안내만 바뀌었으며 본문·둘째 발화·스킬 두 버전이 기존과 같음을 확인한다.
- [x] 유효한 비교다: protocol의 같은 조건에서 revised→baseline 각 두 발화를 실행하고 실제 모델·시스템 지시·세션 연결·원본 도구 결과·스냅샷을 대조한다.
- [x] R6 기록 위치: 수정본이 두 응답 뒤 모두 cwd 기준 .goal/s2/analysis.md를 실제 도구로 작성·갱신하며 실행자가 파일을 옮기거나 대신 쓰지 않는다.
- [x] R2·R3: 반론 이후 새 정보에 따라 해석과 근거를 반영하고 요구 명료화와 선호 변화의 역할을 구별한다.
- [x] R6·C3: 현재 이해·남은 의문·미확인을 구분하고 사용자 이해·동의를 가정하거나 Define으로 진행하지 않는다.
- [x] C4·C6 및 비교 기록: 일반 사례와 실제 기록으로 항목별 두 버전 판정을 남기고 기존 실패·조건 변경·한계를 보존한다.

## 범위와 승인

사용자의 “dir 만 수정…그렇게 진행해주고 verify 끝내자”를 저장 위치 안내 수정→영향받은 S2 쌍 재실행→독립 Verify까지 진행하는 승인으로 반영한다. 새 요구나 스킬 문구 변경은 없다. 원래 4개 티켓의 완료 기록과 최초 Verify는 git에 보존한다.

실행은 ../evidence/s2-dir-clarified/shared/protocol.md를 따른다. 기본 실행 방식은 기존 shared/protocol.md를 참조한다. 판정용 subagent에는 이 티켓이나 Execute 완료 주장을 넘기지 않는다. Verify는 이 실행 커밋 뒤 별도 단계로 수행한다.

## 실행 담당 조정

모델 호출 전 권한 요청 두 건이 메인 중단으로 취소됐고 실제 프로세스·결과 파일은 생성되지 않았다. 같은 권한 절차를 메인 세션에서 직접 요청하도록 Owner를 main으로 바꾼다. 입력·모델·성공 조건은 그대로다. 이는 사용자 승인 철회나 모델 응답 실패가 아니며, 실행 전 대기 중단으로 기록한다.

## Check results

수정본의 6개 Checks 모두 PASS이며 기존본도 같은 관찰 조건을 충족했다. main이 원본 응답 4개, 독립 세션 2개의 연결, 실제 write/edit 성공, 두 응답 뒤의 기대 경로 파일, 입력·스킬·스냅샷 해시를 확인했다. 이전 조건의 실패는 그대로 보존했다. [comparison.md](../evidence/s2-dir-clarified/comparison.md)에 항목별 판정과 원본 위치를 남겼다. 전체 목표의 최종 판정은 독립 Verify에 맡긴다.
