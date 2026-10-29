# workflow-analysis Verify — 저장 위치 안내 변경 후 재판정

- 판정일: 2026-10-29.
- 판정 대상: Execute 완료 커밋 `a59b8b9`의 D1~D3와 [goal.md](goal.md)의 Evaluation 전체.
- 판정자: 구현을 맡지 않은 독립 판정 subagent `/root/verify_directory_followup`.
- 결과: **PASS — 현재 비교 조건에서 R1~R6·C1~C6 모두 PASS.** 필수 항목의 FAIL·UNKNOWN은 남지 않았다.
- 재판정 조건: 최초 S2의 경로 실패 뒤, 저장 위치 안내를 명확히 한 별도 동일 입력 비교를 추가했다. 이 PASS는 새 안내를 포함한 현재 조건의 충족을 뜻한다. 최초 S2 응답을 PASS로 바꾸거나 스킬 자체의 경로 처리 능력이 개선되었다는 뜻은 아니다.

## 판정 방식과 입력 경계

이번 판정은 다음 입력만 사용했다.

1. [goal.md](goal.md) 전체와 D1의 정확한 수용 문구를 정한 [change-proposal.md](change-proposal.md).
2. D1 [workflow-analysis/SKILL.md](../../.agents/skills/workflow-analysis/SKILL.md) 전체.
3. D2 [analysis.md](analysis.md), [analysis.html](analysis.html). 예시 보존과 내용·변경 여부를 확인했고, 링크된 다른 스킬·분석 문서로 이동하지 않았다.
4. D3 `evidence/`의 공통 protocol·manifest·환경·스킬 스냅샷·고정 발화·S3 자료, 모든 기존 시도의 실행 기록·stdout/stderr·세션·파일 목록과 스냅샷, 전사본·비교표·문구 검토표. 후속 `s2-dir-clarified/`도 같은 종류의 실제 기록을 확인했다.
5. 최초 Plan 끝 `9302dc3` 이후 `a59b8b9`까지의 Git 기록. 후속 입력 고정은 `2ed417b`, 담당자 조정은 `969e5c0`이다. diff/show에서 tickets와 기존 verify.md 본문을 제외했다.

**`tickets/`·`handoff.md`·기존 verify.md의 본문, 이전 main 대화와 구현자 완료 보고는 읽거나 판정에 재사용하지 않았다.** 비교표와 meta의 PASS·연결 확인·해시 일치 주장은 증거가 필요한 주장으로 취급했다. 표에 있는 티켓 링크는 따라가지 않았다. 기존 verify.md는 재작성 전부터 `a59b8b9`에 추적되어 있으므로 이전 보고서가 Git 이력에 보존된다.

원본 세션의 사용자 발화·system sections·실제 모델·도구 호출과 성공 결과를 직접 읽었다. 원본 write/edit의 내용을 읽기 전용으로 재구성해 응답 직후 스냅샷과 비교하고 파일 해시도 다시 계산했다. 새 모델 호출·브라우저·Aside·실험 입력 또는 스킬 변경은 하지 않았다. 이번 단계에서 작성한 파일은 이 verify.md뿐이다.

## D1~D3와 변경 범위

| 산출물 | 판정 | 직접 확인한 근거 |
|---|---|---|
| D1 | PASS | 현재 스킬은 change-proposal.md의 `교체할 파일 전체 확정 문구`와 마지막 개행까지 바이트 단위로 같다. SHA-256은 `4ffed4e4d6b11680be29b464ace3bc14975e5e1626b53e1b87b2ee2ce4aead31`. 이름 유지, description 포함 32줄 전체가 확정안과 일치한다. baseline 스냅샷도 `9302dc3`의 원문과 같다. |
| D2 | PASS | analysis.md와 analysis.html은 `9302dc3` 대비 각각 바이트 단위로 변경이 없다. 여섯 제안의 대화 예시가 남아 있고 가상 예시라는 표시도 유지한다. D1은 이 문서들을 읽도록 요구하지 않는다. HTML의 추가 디자인 변경도 없다. |
| D3 | PASS | 기존 S1~S3 및 별도 후속 S2의 고정 입력·버전·실행 환경·원본 응답·조사·세션·스냅샷·항목별 비교가 보존되어 있다. 기존 실행 오류·기록 경로 실패도 지워지지 않았다. 아래 원본 감사와 R/C 표가 최종 판정 근거다. |

`9302dc3..a59b8b9`의 tickets·verify.md·handoff.md 제외 변경 파일은 D1과 `evidence/`뿐이다. 다른 스킬·AGENTS.md·skill-eval·새 평가 프로그램은 변경하지 않았다. `784978f..a59b8b9`에서 D1과 기존 shared·S1·S2·S3의 diff는 비어 있으며, 후속 shared도 `2ed417b` 이후 그대로다.

## 비교 유효성 감사

- **사전 고정:** 기존 입력·스킬·protocol·manifest는 `88ef439`(2026-10-29 05:55:58 UTC)에 남아 있으며 첫 모델 실행보다 앞선다. goal.md의 세 상황과 R/C 성공 조건도 실행 이전에 확정되어 있다. 후속 입력·protocol은 `2ed417b`(07:41:52 UTC)에 고정됐고 새 실행은 08:00:44 UTC부터다. 제외한 티켓에만 있는 추가 조건은 판정 입력으로 사용하지 않았다.
- **입력·버전:** shared manifest의 모든 파일 및 후속 manifest의 입력·참조 해시를 재계산해 일치를 확인했다. 각 유효 대화의 argv와 원본 세션에 있는 사용자 발화 두 개는 해당 고정 파일과 정확히 같다. 각 system addendum은 해당 baseline 또는 revised 스킬 전체에 공통 `<addendum>` 래퍼만 더한 내용이다.
- **모델·도구·컨텍스트:** 기존 여섯 대화와 후속 두 대화의 argv·model_change·thinking 기록·실제 assistant 모델은 `openai-codex / gpt-6-sol / medium`과 일치한다. `read,bash,edit,write`, `--no-context-files`, `--no-skills`, `--no-extensions`, `--no-mcp`가 공통이다. 모든 세션의 preamble·tools·rules·docs 섹션 해시도 같고 addendum·cwd만 실행별로 다르다. pi 버전은 공통 환경/meta에 1.3.0으로 기록되어 있다. 이 증거로 서버 내부의 고정 모델 스냅샷이나 실행 바이너리의 해시까지 확인한 것은 아니다.
- **분리·연결:** 유효한 대화 여덟 개는 모두 다른 UUID와 cwd에서 시작한다. S1·S2·후속 S2의 첫 bash 결과는 빈 cwd를, S3는 고정 자료 두 개만 보여 준다. 각 세션의 사용자 메시지는 두 개이며 parentId 연결이 끊기지 않는다. 도구 호출은 자기 cwd 조사·제공 자료 조회·분석 기록 작성/갱신뿐이고 다른 버전의 응답·티켓·goal·비교표를 읽은 기록은 없다.
- **실제 종료·파일:** 유효한 16개 호출은 모두 종료 코드 0·시간 초과 없음·`agent_settled`와 `aborted:false`를 남겼다. raw write/edit를 재구성한 파일 내용은 16개 응답 직후 스냅샷 모두와 같고 files.json의 해시도 일치했다. 원본 도구 성공 결과로 후보가 문서를 생성·갱신했음을 확인했다. 기존 S2의 잘못된 경로도 그대로 재현된다.
- **실패 시도:** 기존 S2 revised attempt-01과 S3 baseline attempt-01은 stderr에 설정/인증 lock 생성 EPERM, stdout에는 세션 시작만 있고 assistant 응답이 없다. 기존 S1 baseline attempt-01은 stdout/stderr가 비어 있고 실행 기록에 중단·종료 코드 미확정·argv 복원이라는 제한이 명시되어 있다. 이 S1 중단의 인증 원인은 raw 출력만으로 독립 확인할 수 없지만 성공 응답으로 세지 않았다. 새 세션에서 완료된 시도만 행동 비교에 사용했고 이전 기록을 보존했다.
- **부분 도구 오류:** S3 baseline의 첫 bash는 존재하지 않는 `.goal` 검색으로 코드 1을 냈지만, 별도 정책·CSV read는 둘 다 성공했다. 이후 write/edit와 두 응답도 정상 완료되어 R4의 자료 접근 실패로 보지 않는다.

주요 대화의 원본은 다음과 같다. 아래 평가표의 약칭은 이 파일을 가리키며 L은 1-based JSONL 행 번호다.

| 약칭 | 원본 |
|---|---|
| S1-B1 / S1-B2 | [기존본 첫째](evidence/s1/baseline/attempt-02/turn-01/stdout.jsonl) / [둘째](evidence/s1/baseline/attempt-02/turn-02/stdout.jsonl) |
| S1-R1 / S1-R2 | [수정본 첫째](evidence/s1/revised/attempt-01/turn-01/stdout.jsonl) / [둘째](evidence/s1/revised/attempt-01/turn-02/stdout.jsonl) |
| S2-old-B1 / S2-old-B2 | [최초 기존본 첫째](evidence/s2/baseline/attempt-01/turn-01/stdout.jsonl) / [둘째](evidence/s2/baseline/attempt-01/turn-02/stdout.jsonl) |
| S2-old-R1 / S2-old-R2 | [최초 수정본 첫째](evidence/s2/revised/attempt-02/turn-01/stdout.jsonl) / [둘째](evidence/s2/revised/attempt-02/turn-02/stdout.jsonl) |
| S2-new-B1 / S2-new-B2 | [새 기존본 첫째](evidence/s2-dir-clarified/baseline/attempt-01/turn-01/stdout.jsonl) / [둘째](evidence/s2-dir-clarified/baseline/attempt-01/turn-02/stdout.jsonl) |
| S2-new-R1 / S2-new-R2 | [새 수정본 첫째](evidence/s2-dir-clarified/revised/attempt-01/turn-01/stdout.jsonl) / [둘째](evidence/s2-dir-clarified/revised/attempt-01/turn-02/stdout.jsonl) |
| S3-B1 / S3-B2 | [기존본 첫째](evidence/s3/baseline/attempt-02/turn-01/stdout.jsonl) / [둘째](evidence/s3/baseline/attempt-02/turn-02/stdout.jsonl) |
| S3-R1 / S3-R2 | [수정본 첫째](evidence/s3/revised/attempt-01/turn-01/stdout.jsonl) / [둘째](evidence/s3/revised/attempt-01/turn-02/stdout.jsonl) |

## Evaluation 전체 판정

아래 PASS는 확정 문구와 현재 유효 비교 증거를 함께 대조한 결과다. 실제 대화 확인이 지정되지 않은 R5·C1·C2·C5도 문구 전체로 판정했다.

| 항목 | 판정 | 문구 및 직접 증거·판단 |
|---|---|---|
| R1 | PASS | D1 L8~9·19는 이미 제공한 생각·정보·의문에서 시작하고 재질문을 피한다. S1-R1 L688은 긴 공지와 마감 직전 질문을 활용해 미열람과 검색 어려움을 구분한다. [첫 기록](evidence/s1/revised/attempt-01/turn-01/workspace/.goal/s1/analysis.md) L3~20에 8명·월 1회·혼합된 공지·메시지 부담을 활용하며 목표를 재수집하지 않는다. 첫 입력의 “아직 무엇을 목표로 정할지는 모르겠다”에도 바로 탐색했다. |
| R2 | PASS | D1 L17~19는 다섯 수단의 선택과 관점·전제·해석 구분 질문을 허용한다. S1-R1 L688의 해석 구분 질문, S2-new-R1 L784의 기준 누락/선호 발견 설명과 시점 질문, S3-R1 L24~28의 실제 자료 조회와 L1021의 구간 설명은 상황에 맞는 선택이다. 모든 수단의 반복 실행·매 응답 질문은 없다. 최초 S2 수정본도 L918·둘째 L891에서 같은 핵심 행동을 보였다. |
| R3 | PASS | D1 L21~22. S2-new-R2 L1260은 이미 전달된 독자·목적·길이와 사후 선호 변화를 근거로 이전의 요구 누락 가설을 주된 설명에서 낮추었다고 명시하고, 요구 명료화 불필요라는 반대 극단도 거부한다. L1012~1013의 edit 성공과 [최종 기록](evidence/s2-dir-clarified/revised/attempt-01/turn-02/workspace/.goal/s2/analysis.md) L6~21에서 변경 이유·미확인을 확인했다. 최초 S2-old-R2 L891에서도 같은 수정이 관찰된다. |
| R4 | PASS | D1 L24~26. S3-R1 L24~28은 정책·CSV의 실제 read와 두 성공 결과다. L1021 및 [최종 기록](evidence/s3/revised/attempt-01/turn-02/workspace/.goal/s3/analysis.md) L3~28은 4시간 포함 기준·4/6건 준수·R03/R04의 첫 응답 이후 45/68시간을 정확히 구분하고 자료 파일과 연결한다. 완료 기한·대기 사유·태만·기한 단축 효과는 알 수 없다고 남겼다. S3-R2 L630은 근거 없이 사용자 인과 주장을 채택하지 않는다. |
| R5 | PASS | D1 L11~15는 Concept·Context·Problem을 유지하고 필요에 따라 오갈 탐색 관점이라고 명시한다. L21~22는 문제 해석의 재검토를 허용한다. 전체 문구에 세 요소의 고정 순서나 최초 문제 해석 유지 요구는 없다. |
| R6 | PASS | D1 L28~31의 현재 이해·남은 의문 기록, 이해/동의 비가정, 추가 반응 수용이 모두 있다. S1-R2 L33~34·213~214·291과 [최종 기록](evidence/s1/revised/attempt-01/turn-02/workspace/.goal/s1/analysis.md) L22~25는 사용자가 말한 구분의 이해만 기록하고 질문 감소 효과는 미확인으로 남긴다. 후속 S2-new-R1 L540~541 write와 S2-new-R2 L1012~1013 edit, 두 files.json·스냅샷은 cwd 기준 `.goal/s2/analysis.md` 생성·갱신을 입증한다. 최초 S2의 경로 FAIL은 아래에 별도로 유지한다. |
| C1 | PASS | D1 description L3과 목적 L8~9가 사용자 이해의 발전을 명시한다. 질문·조사·재검토·기록·마무리의 전체 문구에서 그 목적과 충돌하는 지시는 없다. 실제 사용자의 일반적 이해도 향상까지 검증했다는 뜻은 아니다. |
| C2 | PASS | D1 L15·19·30은 유연한 탐색과 고정 횟수·순서 및 반복 확인 요구의 배제를 명시한다. 전체 본문에 고정 인터뷰 절차가 없다. 실험의 고정 발화 두 개는 비교 조건이며 D1의 운영 규칙이 아니다. |
| C3 | PASS | D1 L32는 목표·범위 확정을 Define에 남긴다. S1-R2 L291과 최종 기록 L25는 미확정 상태로 사용자의 종료를 따른다. S1 및 후속 S2의 실제 도구/응답에는 Define 문서 작성·자동 단계 진행·승인 반복이 없다. |
| C4 | PASS | D1 전체에 COFA 사전 지식·전용 절차 요구가 없다. S1 독서 모임 공지, 최초/후속 S2 문서 협업, S3 문의 처리 사례는 해당 분야의 고정 입력만으로 설명·분석을 수행했다. |
| C5 | PASS | D1은 확정안과 정확히 같은 간결한 행동 원칙이다. description·목적·세 관점·행동 선택·반응 재검토·조사·기록과 경계를 직접 담고, 긴 해설·대화 예시·분석 문서 필수 읽기 참조가 없다. `.goal/<goal>/analysis.md`는 출력 위치다. D2 예시는 그대로 보존됐다. |
| C6 | PASS | Git 변경 범위에 새 평가 프로그램·runner 확장이 없다. S1~S3 및 후속 S2의 실제 assistant 메시지·조사/작성 도구 결과·연결된 세션·후보 파일이 있다. 문구 검토나 D2의 가상 대화를 실제 실행 대신 사용하지 않았다. 각 비교 문서에는 baseline/revised의 항목별 판정과 원본 위치가 있으며 원본 대조 결과와 부합한다. |

## 기존 관찰과 후속 조건의 차이

**S1:** 두 버전 모두 기존 정보에서 바로 탐색하고 마무리·Define 경계를 지켰다. 기존본은 둘째 발화 뒤 도구 호출 없이 종료했고 S1-B2 L51 및 [최종 파일](evidence/s1/baseline/attempt-02/turn-02/workspace/.goal/s1/analysis.md)은 첫 파일과 같아 사용자가 밝힌 이해·남은 의문을 기록하지 않았다. 이 R6 기록 갱신은 FAIL이다. 수정본은 S1-R2의 실제 edit로 두 내용을 반영했다. 이 한 사례에서는 후속 기록 행동의 차이가 관찰된다.

**최초 S2:** 두 버전 모두 추가 정보로 해석을 수정하고 두 극단을 거부했다. 수정본은 이전 가설을 낮춘 이유를 더 명시적으로 설명했지만, baseline도 R3를 충족한다. 반면 정확한 경로는 두 버전 모두 FAIL이다. 수정본은 `s2/.goal/s2/analysis.md`, 기존본은 `s2/.goal/draft-revision-understanding/analysis.md`를 만들었다. 수정본의 두 [files.json](evidence/s2/revised/attempt-02/turn-01/files.json)·[files.json](evidence/s2/revised/attempt-02/turn-02/files.json)은 `analysis_exists:false`이며, 원본 도구와 [실제 최종 파일](evidence/s2/revised/attempt-02/turn-02/workspace/s2/.goal/s2/analysis.md)도 그 경로를 입증한다. 이 실패는 없어지지 않았다.

**후속 S2:** 새 [첫 입력](evidence/s2-dir-clarified/shared/turn-01.txt)은 cwd·goal 이름·출력 경로를 구별해 안내한다. 최초 발화의 사례 본문과 둘째 발화는 바이트 단위로 같고 두 스킬도 그대로다. 새 안내는 양쪽에 동일하게 전달됐다. 기존본 S2-new-B1 L549~550·B2 L759~760과 수정본 S2-new-R1 L540~541·R2 L1012~1013은 모두 `.goal/s2/analysis.md`에 직접 write/edit해 성공했다. 양쪽의 최종 문서는 실제 스냅샷 및 재구성한 도구 내용과 같으며 R2/R3도 계속 충족한다. 새 조건에서 수정본의 R6 경로 미충족은 해소됐고 baseline도 같은 결과다.

따라서 후속 실행은 **입력 안내가 달라진 별도 조건의 성공 관찰**이다. 최초 응답의 경로만 교정하거나 품질 결과가 나올 때까지 같은 조건을 반복한 것으로 다루지 않는다. 경로 처리의 개선을 스킬 변경 효과로 귀속할 근거는 없고, 단일 추가 실행으로 최초 실패의 원인이 안내의 모호함 하나였다고 입증할 수도 없다. 현재 R6 PASS는 S1의 기록/마무리 증거와 명확한 경로를 안내한 후속 S2 증거에 근거한다. 최초 조건에서의 실패 가능성은 역사적 반례로 남는다.

**S3:** 두 버전 모두 실제 자료 조회, 정확한 기한·수치, 원인·해결 효과 미확인의 구분을 수행했다. 수정본은 사실/해석을 별도 구획으로 기록했고 R04의 4시간 포함 기준을 채팅에서도 명시했다. 기존본도 같은 필수 행동을 충족했으므로 조사 행동이 수정본에서 새로 생겼다고 판정하지 않는다. 수정본의 첫 채팅은 입력 파일명을 다시 쓰지 않았지만 안내한 분석 문서 L3~18에서 출처와 계산을 연결한다.

## 남은 한계와 목표 충족 범위

- 현재 필수 Evaluation 항목의 미충족은 없다. 이전 S2의 경로 실패와 S1 baseline의 기록 갱신 실패는 삭제·완화하지 않았으며, 현재 수정본의 판정과 구분해 남겼다.
- 기존 세 사례와 후속 한 사례의 각 버전 한 대화씩, 두 고정 발화만 관찰했다. 입력 민감도·재현 확률·모델 확률 변동·일반적인 학습 효과를 추정할 수 없다.
- 스크립트에 고정된 사용자 발화는 실험 입력이다. S1의 “알겠어요”는 실제 사용자의 학습 향상 연구 결과가 아니다. 그 발화에서 드러난 범위만 기록했는지 평가했다.
- R3의 사용 경험은 사용자 진술로, S3의 자료는 제공된 가상 고정 자료로 취급했다. 모든 문서 수정의 실제 원인이나 실제 조직의 병목을 별도로 입증한 것이 아니다.
- 현재 PASS는 확정 문구의 적용·범위 준수와 명시된 비교 조건의 행동 증거를 종합한 목표 판정이다. 스킬 문구의 일반적 우월성, 명확하지 않은 모든 경로 안내에서의 안정성, 실제 사용자의 장기 이해도 향상을 주장하지 않는다.
