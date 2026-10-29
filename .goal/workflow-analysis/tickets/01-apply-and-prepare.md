# 01: 확정 문구 적용과 문구 검토

**What to build:** 수용한 문구를 실제 Analysis 스킬에 적용하고 요구사항과 대조한다. 다음 세 티켓이 같은 조건에서 기존본과 수정본을 비교할 수 있도록 버전·입력·실행 규칙을 보존한다.

**Covers:** D1, D2, D3의 비교 준비; R1~R6, C1~C6의 문구·범위 검토.

**Blocked by:** None (can start immediately).

**Files:**

- `.agents/skills/workflow-analysis/SKILL.md`
- `.goal/workflow-analysis/evidence/shared/`의 `baseline.SKILL.md`, `revised.SKILL.md`, `text-review.md`, `protocol.md`, `environment.json`, `manifest.json`.
- 위 shared의 `cases/s1/`, `cases/s2/`, `cases/s3/` 각각에 `turn-01.txt`, `turn-02.txt`.
- 위 shared의 `cases/s3/data/request-log.csv`, `cases/s3/data/triage-policy.md`.
- 이 티켓의 Status와 완료 증거 링크.

**Owner:** main

**Parallel:** no

**Status:** done

**Checks:**

- [x] 원본을 먼저 보존한다: baseline의 SHA-256이 `change-proposal.md`의 `fe625a9044521877905576a23de557027e061c1e04d4572f6cb3b21dea9efe75`와 일치한다.
- [x] 확정 문구를 그대로 적용한다: 실제 스킬과 revised가 `change-proposal.md`의 전체 확정 문구와 바이트 단위로 일치한다. UTF-8·LF·마지막 개행을 유지한다.
- [x] 모든 R/C를 검토한다: `text-review.md`에 R1~R6, C1~C6 각각의 기준·해당 문구·PASS/FAIL/UNKNOWN·이유를 남긴다. 문구 PASS를 실제 행동 PASS로 확대하지 않는다.
- [x] 응답을 보기 전에 비교 입력을 고정한다: 02~04의 발화·S3 자료와 아래 protocol을 파일로 보존하고 `manifest.json`에 상대 경로·SHA-256을 기록한다.
- [x] 실행 조건을 재현할 수 있다: 아래 규칙을 `protocol.md`에 옮기고 목표 모델·CLI 버전·도구·비밀을 제외한 공통 설정을 `environment.json`에 기록한다. 실제 인증·모델 호출 가능 여부는 미확인으로 표시한다.
- [x] 범위를 지킨다: 다른 스킬·AGENTS.md·skill-eval·기존 분석 문서는 변경하지 않는다. 새 평가 프로그램이나 스킬의 분석 문서 읽기 의존성을 추가하지 않는다.

계획 승인 기록: 2026-10-29 사용자가 4개 티켓 구성·의존관계·분담에 “승인”으로 답했다. 01은 main, 02~04는 01 이후 병렬 실행하는 subagent 소유로 유지한다.

## 적용 기준

[goal.md](../goal.md)와 [change-proposal.md](../change-proposal.md)를 따른다. 원본 보존 후 확정된 32줄 전체 문구를 적용한다. 스킬 경로가 보호되면 실행 도구의 권한 절차를 따른다.

문구와 R/C가 충돌하면 근거를 남기고 Define에서 재검토할 사항으로 알린다. 확정 문구를 임의로 보강하지 않는다. 적용·문구 검토·비교 준비가 완료되어야 02~04를 시작한다.

기존 `analysis.md`·`analysis.html`은 참고 자료다. 새 예시 문서를 만들거나 후보 모델에게 기존 분석 문서를 읽히지 않는다. 실제 비교에는 아래 고정 발화만 사용한다.

## 공통 실행 규칙

### 비교 대상과 입력

- 사례마다 baseline 1회, revised 1회, 총 6개 대화를 실행한다. 대화마다 고정 사용자 발화 2개를 사용하므로 정상 완료 시 후보 호출은 12번이다. 모의 사용자·별도 심판 모델은 사용하지 않는다.
- 02~04의 인용문을 각각 입력 파일로 그대로 보존한다. 첫 발화 앞에 공통 안내를 붙인다: “이번 대화의 작업 폴더 이름은 s1입니다. 한국어로 쉽게 설명해 주세요. 모든 파일 작성은 이 작업 폴더 안에서 해 주세요.” S2·S3는 이름만 s2·s3로 바꾼다. 안내와 인용문을 합친 실제 첫 입력을 `turn-01.txt`에, 둘째 인용문을 `turn-02.txt`에 보존한다. 같은 사례의 두 버전에는 안내까지 같은 입력을 준다.
- 첫 응답의 질문 유무와 관계없이 고정된 둘째 발화를 전달한다. 응답에 맞춰 추가 답변·힌트·채점 기준을 보내지 않는다. 둘째 응답 후 추가 호출 없이 종료한다. 고정 발화 수는 실험 조건이며 스킬의 대화 순서 규칙이 아니다.
- 행동 성공 조건은 02~04의 Checks다. 같은 기준으로 양쪽을 판정하되 baseline의 FAIL 자체를 티켓 실패로 취급하지 않는다. revised의 FAIL·UNKNOWN은 미충족으로 남긴다. 응답을 본 뒤 조건·발화·자료를 바꾸지 않는다.

### 모델·세션·도구

- 설치된 `/opt/homebrew/bin/pi`를 직접 호출한다. 기존 skill-eval runner·Define용 suite는 사용하거나 수정하지 않는다. 복사·호출·기록은 실행 도구에서 일회성으로 처리하고 재사용할 runner를 만들지 않는다.
- 두 버전 모두 provider `openai-codex`, model `gpt-6-sol`, thinking `medium`으로 고정한다. `skill-eval/config.yaml`의 후보 설정을 참조한 값이며 가용성을 확인했다는 뜻은 아니다.
- 두 버전 모두 `--print`, `--mode json`, `--no-context-files`, `--no-skills`, `--no-extensions`, `--no-mcp`, `--tools read,bash,edit,write`를 사용한다. provider·model·thinking도 명시한다. 해당 버전의 전체 스킬 파일 하나를 `--append-system-prompt`로 주입한다.
- 사례·버전마다 새 UUID의 `--session-id`와 별도 `--session-dir`를 쓴다. 같은 대화의 두 발화는 같은 cwd·세션·설정으로 이어 간다. 원본 세션의 사용자 메시지에서 두 발화가 이어졌는지 확인한다.
- cwd는 저장소 밖의 새 임시 작업 폴더다. S1·S2는 빈 폴더, S3는 고정 `data/` 두 파일만 넣고 시작한다. 같은 사례의 두 버전은 초기 파일 목록·내용 해시가 같아야 한다. 경로·UUID는 달라도 된다.
- 후보에게 티켓·goal.md·판정표·다른 버전의 응답을 제공하지 않는다. 해당 스킬만 시스템 지시로 주입한다. 비교 자료를 조회한 흔적이 있으면 유효한 비교로 쓰지 않는다.
- stdin을 닫고 각 호출의 제한 시간은 900초로 둔다. 같은 pi 버전과 공통 설정·인증 환경을 사용한다. 토큰·인증 파일은 증거에 저장하지 않는다.

### 원본 기록과 오류 처리

- 순서는 S1 baseline→revised, S2 revised→baseline, S3 baseline→revised로 고정한다. 세 사례끼리는 병렬 실행할 수 있다.
- 발화별 stdout 원본 JSONL·stderr·argv·cwd·세션 ID·시작 시각·소요 시간·종료 코드·시간 초과 여부를 남긴다. 출력에 기록된 실제 모델도 요청한 값과 대조한다.
- 원본의 사용자·assistant·도구 실행 시작과 결과를 확인하고 `transcript.md`를 만든다. 전사본이 원본 기록을 대신하지 않는다.
- 매 응답 후 작업 폴더의 파일 목록·해시와 `.goal/sN/analysis.md`의 존재·내용을 보존한다. 문서가 없으면 없었다고 기록한다. 실행자가 분석 문서를 대신 쓰지 않는다.
- 인증·권한·모델 가용성은 Execute에서 실제 호출로 확인한다. 샌드박스에 막히면 실행 도구의 권한 절차를 따른다. 실행 불가·세션 단절·기록 유실·조건 불일치는 영향받은 항목을 UNKNOWN과 이유로 남긴다.
- 일시적 실행 오류는 해당 대화 전체를 새 세션에서 1회 재시도할 수 있다. 첫 시도도 보존한다. 응답 품질 FAIL을 지우기 위해 재실행하지 않는다. 모델 등 조건을 바꾸면 양쪽을 모두 같은 새 조건으로 실행하고 변경 이유와 이전 기록을 남긴다.
- `comparison.md`의 판정표에는 기준, baseline 결과·원본 위치, revised 결과·원본 위치, 차이와 한계를 적는다. 차이가 없으면 그대로 적는다. 조건이 갖춰졌는데 기대 행동을 하지 않은 경우는 FAIL이다.
- 각 티켓은 자기 사례 폴더와 자기 티켓만 변경한다. shared는 01 완료 후 읽기 전용 입력으로 취급한다. main이 티켓별로 커밋하여 병렬 작업의 git index 충돌을 피한다.

## 증거 폴더

각 사례의 `evidence/sN/`에 `comparison.md`와 `baseline/`, `revised/`를 둔다. 버전 폴더 안의 `attempt-01/`에 `meta.json`, `transcript.md`, `sessions/`, `turn-01/`, `turn-02/`를 보존한다. 재시도는 `attempt-02/`에 남긴다.

발화 폴더에는 `stdout.jsonl`, `stderr.txt`, `execution.json`, `files.json`, `workspace/`를 둔다. `workspace/`는 해당 응답 직후의 작업 폴더 스냅샷이다. `execution.json`은 명령·시간·종료 상태, `files.json`은 파일 목록·해시와 분석 문서 누락 여부를 담는다. `meta.json`은 스킬·입력·자료 해시, 실행 조건, 두 발화의 세션 연결 확인 결과와 최종 사용 시도를 담는다.

이것은 증거 파일의 약속이며 새 프로그램의 명세가 아니다. 각 사례의 항목 판정은 Execute에서 기록한다. 전체 목표의 최종 판정과 `verify.md` 작성은 사용자가 Verify를 요청할 때 수행한다.

## Check results

- 원본 보존 PASS: [baseline](../evidence/shared/baseline.SKILL.md)의 SHA-256이 확정 기준과 일치한다.
- 문구 적용 PASS: 실제 스킬·[revised](../evidence/shared/revised.SKILL.md)·변경안 전체 문구가 바이트 단위로 일치하며 32줄이다.
- 문구 검토 PASS: [text-review.md](../evidence/shared/text-review.md)에 R1~R6·C1~C6의 문구와 이유를 남겼다. 실제 행동은 미판정이다.
- 입력 고정 PASS: [manifest.json](../evidence/shared/manifest.json)의 12개 입력 해시를 다시 계산해 모두 일치했다.
- 실행 조건 준비 PASS: [protocol.md](../evidence/shared/protocol.md)와 [environment.json](../evidence/shared/environment.json)에 pi 1.3.0, 모델·도구·세션·오류·증거 규칙을 기록했다. 실제 호출은 다음 티켓에서 수행한다.
- 범위 PASS: 다른 스킬·AGENTS.md·skill-eval·기존 분석 문서 변경이 없다. 기존에 있던 다른 작업의 미커밋 변경은 그대로 둔다.
