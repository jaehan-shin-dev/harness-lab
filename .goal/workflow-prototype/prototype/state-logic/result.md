# 상태·로직 적용 사례: 정원 2명의 예약과 대기열

2026-10-28에 에이전트가 수행한 탐색이다. 공개 조작부를 통한 12개 상태 관찰이 예상한 규칙과 일치했다. 이 기록은 이 사례의 관찰 결과이며, 목표 전체의 최종 Verify 판정이나 사용자의 채택 결정이 아니다.

## 실제 적용 요청과 질문

사용자가 승인한 실제 적용 평가를 부모 세션이 티켓 03으로 위임했다. 전달받은 명시 요청은 `Use $workflow-prototype at .agents/skills/workflow-prototype/SKILL.md explicitly for this user-authorized agent-run application case.`였다. 이번 수행에서 해당 스킬을 읽고 적용했다. 이는 사용자가 이 데모를 직접 조작했다는 기록이나, Codex의 암시적 호출 차단을 런타임으로 시험했다는 기록은 아니다.

사용자 아이디어가 별도로 제공되지 않아, 목표 D4가 허용한 범위에서 에이전트가 작은 사례를 선택했다. 확인할 질문은 **“정원이 찼을 때 대기 순서를 유지하면서 취소된 자리를 선두 대기자에게 줄 수 있는가?”**다.

다음은 이 실험의 가정이며 사용자와 합의한 제품 규칙이 아니다.

- 정원은 2명이고 참가자는 Ada, Bo, Cy, Dana로 고정한다.
- 빈자리가 있으면 확정하고, 만석이면 대기열 끝에 넣는다.
- 중복 신청으로 동일인이 두 번 들어가지 않는다.
- 대기자 취소는 확정자와 남은 대기 순서를 바꾸지 않는다. 다시 신청하면 맨 뒤로 간다.
- 확정자 취소는 현재 대기열의 선두 한 명을 즉시 승격한다.
- 참여하지 않은 사람의 취소는 명단을 바꾸지 않는다. Reset은 명단과 화면 이력을 비운다.

질문과 보관 폴더가 분명해 추가 질문 없이 제작·실행했다. 별도 제품 goal·ticket, 제품 테스트 프레임워크, 시간 제한이나 반복 횟수 조건을 만들지 않았다.

## 산출물과 실행 안내

[데모](index.html)는 외부 의존성 없는 HTML 한 파일이다. 파일을 브라우저에서 열고 참가자 라디오를 선택한 뒤 **Reserve seat**, **Cancel participation**, **Reset experiment**를 누른다. 확정 명단·대기 순서·인원수·직전 결과·행동 이력을 같은 화면에서 볼 수 있다.

- 수동 실행: 이 폴더의 `index.html`을 Chrome 등 브라우저에서 연다. 아래 표의 행동 순서로 재현할 수 있다.
- 자동 관찰: macOS의 `/Applications/Google Chrome.app`과 Node가 있는 환경에서 아래 명령을 실행한다. 실제 실행 환경은 Node `v26.5.0`, Chrome `156.0.8078.49`였다.

```sh
node /Users/sinjaehan/DEV/harness-lab/.goal/workflow-prototype/prototype/state-logic/observe.mjs
```

[observe.mjs](observe.mjs)는 매번 `/private/tmp/workflow-prototype-state-logic-*`에 새 프로필을 만들고, 독립된 headless Chrome을 `--remote-debugging-port=0`으로 실행한다. 이 실행이 만든 Chrome의 디버깅 연결만 사용하고, 끝나면 해당 프로세스를 종료한다. 새 의존성 설치는 필요 없다. 실행 환경에 따라 브라우저 앱 실행 권한이 필요할 수 있다. 임시 프로필 폴더는 자동 삭제하지 않는다.

현재 디렉터리의 공개 라디오·버튼에 Chrome CDP의 마우스 입력을 전달한다. 검사값은 화면에 렌더링된 목록·인원수·상태 문구에서 읽는다. 데모 내부 함수나 상태 변수를 직접 호출하지 않는다. 기대 명단은 위 가정에서 도출한 고정 예시다. 출력은 터미널에 남고 화면은 `evidence/`에 시간 접두사로 저장된다. `--first-seat-only`는 초기 화면과 첫 예약만 관찰한다. `--capture-prefix=<이름>`은 캡처 접두사를 지정하며, 기존 증거와 다른 이름을 사용한다.

보존된 최종 실행 명령은 다음과 같다. 다시 실행할 때 기존 로그를 덮어쓰지 않도록 다른 출력 파일명과 캡처 접두사를 사용한다.

```sh
node /Users/sinjaehan/DEV/harness-lab/.goal/workflow-prototype/prototype/state-logic/observe.mjs --capture-prefix=06-green > .goal/workflow-prototype/prototype/state-logic/evidence/06-green-full.txt 2>&1
```

## 실제 공개 조작과 관찰

[최종 원출력](evidence/06-green-full.txt)에 각 단계의 화면 목록, 인원수, 결과 문구, 행동 이력이 기록돼 있다. 순서는 앞에서 뒤로 읽는다. `—`는 빈 목록이다.

| 단계 | 공개 조작 | 관찰된 확정 명단 | 관찰된 대기열 | 규칙과의 대조 |
| --- | --- | --- | --- | --- |
| 0 | 파일 열기 | — | — | 초기 인원 0 / 2, 대기 0 |
| 1 | Ada → Reserve seat | Ada | — | 빈자리 확정 |
| 2 | Bo → Reserve seat | Ada, Bo | — | 정원 2 도달 |
| 3 | Cy → Reserve seat | Ada, Bo | Cy | 만석이면 대기 |
| 4 | Dana → Reserve seat | Ada, Bo | Cy, Dana | 신청 순서대로 대기 |
| 5 | Cy → Reserve seat | Ada, Bo | Cy, Dana | 중복 대기 신청 무변경, 안내 표시 |
| 6 | Cy → Cancel participation | Ada, Bo | Dana | 대기 취소로 확정 명단 유지 |
| 7 | Cy → Reserve seat | Ada, Bo | Dana, Cy | 재신청은 대기열 끝 |
| 8 | Ada → Cancel participation | Bo, Dana | Cy | 현재 선두 Dana가 승격 |
| 9 | Bo → Cancel participation | Dana, Cy | — | 다음 선두 Cy가 승격 |
| 10 | Ada → Cancel participation | Dana, Cy | — | 미참여 취소 무변경, 안내 표시 |
| 11 | Reset experiment | — | — | 명단·인원수·행동 이력 초기화 |

명단과 인원수는 매 단계 비교했다. 중복 신청, 두 차례 승격, 미참여 취소, 초기화의 안내 문구도 관찰했다. 최종 출력은 `PASS {"observations":12,"mode":"full public-control scenario"}`이며 프로세스 종료 코드는 0이었다.

실제 캡처를 저장했고, 첫 승격과 Reset 캡처를 직접 열어 명단·상태 문구가 읽히는지 확인했다.

- [만석과 Cy, Dana 대기](evidence/06-green-01-full-with-waitlist.png)
- [Ada 취소 후 Dana 승격](evidence/06-green-02-first-promotion.png)
- [Bo 취소 후 Cy 승격, 미참여 취소](evidence/06-green-03-second-promotion-and-noop.png)
- [Reset 이후 빈 명단](evidence/06-green-04-reset.png)

## 작은 검사와 실패 기록

코드 변경에는 공개 Interface에서 필요한 작은 red → green 검사만 사용했다. 별도 테스트 프레임워크나 내부 함수 검사는 없다. `node --check observe.mjs`도 종료 코드 0이었다.

| 기록 | 실제 결과 | 의미 |
| --- | --- | --- |
| [01-red-reserve.txt](evidence/01-red-reserve.txt) | 종료 1 | 조작부만 있던 첫 버전에서 Ada 예약을 눌러도 빈 명단이었다. 첫 예약 예상값과 불일치해 실패했다. |
| [02-green-reserve.txt](evidence/02-green-reserve.txt) | 종료 0 | 예약 구현 후 초기·첫 예약 2개 관찰 통과. |
| [03-input-driver-failure.txt](evidence/03-input-driver-failure.txt) | 종료 1 | 당시 native select에 키 입력을 보냈으나 Bo 선택이 Ada로 남았다. 로직 판정으로 사용하지 않았다. |
| [04-input-focus-retry-failure.txt](evidence/04-input-focus-retry-failure.txt) | 종료 1 | 포커스를 명시한 재시도도 대상자 변경을 확인하지 못했다. 로직 판정으로 사용하지 않았다. |
| [05-red-cancel.txt](evidence/05-red-cancel.txt) | 종료 1 | 참가자 선택을 공개 라디오로 바꿔 실제 마우스 입력을 확인했다. 예약·만석·중복 신청은 맞았고, 아직 구현하지 않은 Cy 대기 취소에서 실패했다. [당시 만석 화면](evidence/01-full-with-waitlist.png)도 보존했다. |
| [06-green-full.txt](evidence/06-green-full.txt) | 종료 0 | 취소·승격 구현 후 12개 관찰이 모두 일치했다. |

앞선 브라우저 연결 시도는 사용자 중단으로 화면 관찰에 이르지 않았으며 근거로 쓰지 않았다. 사용자가 이후 지정한 대로 독립 설치된 Chrome과 새 임시 프로필을 사용했다. 그 지시 이후 Aside 명령·프로필·연결은 사용하지 않았다. 위 근거는 모두 독립 Chrome 실행에서 얻었다.

RED 로그는 당시 미구현 버전의 기록이다. 현재 보존된 데모와 관찰 스크립트는 최종 GREEN 버전이므로 현재 명령을 실행하면 RED 실패를 의도적으로 재현하지 않는다. 이전 실패 로그와 캡처는 삭제하지 않았다.

## 알게 된 것, 한계와 남은 선택

이 단일 탭의 순차 조작 조건에서는 취소와 재신청 후의 **현재 대기 순서**가 승격에 사용됐다. “처음 신청했던 순서로 영구 우선권을 주는 방식”이 아니라는 점을 사용자가 직접 바꿔 보며 판단할 수 있다. 화면에서 확정 명단과 대기 순서를 나란히 보여 주므로 누구의 행동이 누구의 승격을 만들었는지 관찰할 수 있다.

확인 범위는 고정 4명·정원 2명·위 순서의 실제 마우스 조작이다. 서버, 실제 계정, 저장소, 동시 신청, 여러 탭, 알림, 시간 제한, 접근성 전반, 성능은 확인하지 않았다. 확정자의 중복 신청 분기와 대기자가 없는 확정 취소 분기는 코드에 있지만 이번 공개 조작 순서에서는 실행하지 않았다. 새로고침에 대한 별도 관찰도 수행하지 않았다. headless Chrome에서 완료한 관찰이며 사람이 데모를 사용한 결과는 없다.

사용자에게 남은 판단은 이 승격 규칙과 화면이 아이디어에 적합한지, 추가 실험이 필요한지, 종료·채택할지다. **사용자 선호·규칙 승인·채택은 모두 선택 대기**다. 추가 사람 작업을 이 사례의 실행 완료 조건으로 삼지 않았다. 정식 제품 구현이나 다음 단계로 진행하지 않으며, 결과를 원래 workflow-prototype 논의에 반환한다.

변경은 이 사례 폴더 안에만 남겼다. 스킬·설정·다른 사례·목표·티켓은 수정하지 않았고, 스테이징·커밋은 부모 세션이 처리한다.

## 실행 정리

- 에이전트는 전체 관찰과 결과 문서 작성 후 사용량 제한으로 종료됐다. main이 12개 상태의 실제 원출력, 구현·관찰 스크립트, 최종 캡처를 이어서 검토했다.
- main은 최종 만석·첫 승격 캡처를 직접 열고 원출력의 명단·상태 문구와 대조했다. 최종 출력의 12개 관찰과 FIFO 순서·중복 신청·취소·초기화 기록이 보고와 일치했다.
- 관찰 스크립트는 finally에서 자신이 띄운 Chrome만 종료한다. main의 2026-10-29 프로세스 조회에서도 이 사례의 임시 프로필을 사용하는 브라우저는 남아 있지 않았다.
- 사용자 지시 이후 Aside를 다시 사용하지 않았다. 최종 근거는 독립 Chrome에서 얻었으며 사용자 선호·규칙 승인·채택은 선택 대기다.
