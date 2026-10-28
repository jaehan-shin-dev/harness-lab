# UI 비교 사례 — 같은 작업을 목록·카드·상태 보드로 보기

실행일: 2026-10-28 (KST). 이 기록은 `workflow-prototype`의 사용자 승인에 따른 에이전트 수행 적용 사례다. 최종 목표 달성 판정이나 UI 채택 결정은 포함하지 않는다.

## 실제 요청과 범위

부모 Execute의 실제 위임 요청에서 다음을 명시했다.

> Implement ticket 02 for /Users/sinjaehan/DEV/harness-lab. … Use $workflow-prototype at .agents/skills/workflow-prototype/SKILL.md explicitly for this user-authorized agent-run application case. … You may select a small case per the goal. … inspect real rendered captures, record actual request/actions/results/limits and re-run instructions in result.md. User preference/adoption stays pending.

이는 실제 제품 아이디어를 사용자가 제시한 대화라는 뜻이 아니다. [goal.md](../../goal.md)의 D4와 승인된 [티켓 02](../../tickets/02-ui-comparison-case.md)에 따라 에이전트가 작은 UI 질문을 선택했다. `workflow-prototype` 본문을 읽고 이 사례에 명시적으로 적용했다. 이 실행에서는 새 스킬의 자동 검색·암시적 호출 여부를 시험하지 않았다.

선택한 질문: **같은 작업 다섯 개에서 검토할 일을 찾고 내용을 열어 볼 때, 목록·카드·상태 보드가 각각 어떤 정보를 보여 주는가?**

가정과 최소 산출물:

- 모두 같은 다섯 작업, 프로젝트·상태·마감·담당자를 사용한다. 상태 보드는 상태로 묶으므로 작업의 화면상 순서는 달라진다.
- 검토가 필요한 작업은 `랜딩 페이지 문구 검토`와 `주간 리포트 확인` 두 개다.
- A 목록, B 카드, C 상태 보드의 3안을 하나의 정적 HTML에서 탭으로 전환한다. 각 안에서 `전체 5`, `검토 필요 2`, 작업 상세, `닫기`를 조작한다.
- 질문과 저장 폴더가 정해져 있어 다시 묻지 않았다. 별도 제품 goal/ticket·서버 의존성·제품 테스트 프레임워크를 만들지 않았다.
- 브라우저 확인 도중 사용자의 **Aside 재사용 금지**가 전달됐다. 이후 해당 명령·브라우저·프로필·연결을 사용하지 않고, 독립 Google Chrome과 새 임시 프로필로 전환했다.

## 제작·실행한 내용

산출물은 [index.html](index.html)과 [browser-check.mjs](browser-check.mjs)다. 외부 이미지·폰트·API·npm 패키지를 사용하지 않는다. 데이터 저장·수정·실제 업무 처리는 구현하지 않았다.

공개 확인 경계는 사용자가 보는 HTML의 탭·필터 버튼·작업 버튼·상세 대화상자다. Node 관찰기는 native `fetch`/`WebSocket`으로 독립 Chrome의 CDP에 연결한다. 버튼의 표시 이름으로 좌표를 얻어 **실제 `Input.dispatchMouseEvent`**를 보낸다. 화면의 표시 텍스트·작업 버튼·대화상자 상태를 읽고, Chrome이 렌더한 PNG와 접근성 트리를 저장한다. 내부 `render()`나 작업 데이터 변수에 직접 접근하거나 호출하지 않는다.

실제 환경:

- macOS, Node `v26.5.0`, Python `3.9.6`.
- `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`를 `--headless=new`로 별도 실행했다.
- 새 프로필: `/private/tmp/workflow-prototype-ui-chrome-20261028`. 기존 사용자 프로필이나 다른 브라우저에 붙지 않았다.
- Chrome `156.0.8078.49`, CDP protocol `1.3`, 1280 × 900, device scale factor 1. [실행 JSON](evidence/green-observations.json)에 실제 버전 응답이 있다.
- Python 서버가 배정받은 주소: `http://127.0.0.1:56130/`. Chrome의 별도 동적 CDP 포트는 `56291`이었다.

실제 실행 명령(저장소 루트에서):

```sh
python3 -m http.server 0 --bind 127.0.0.1 --directory .goal/workflow-prototype/prototype/ui-comparison
```

```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless=new --no-first-run --no-default-browser-check --disable-background-networking --disable-extensions --disable-sync --disable-gpu --user-data-dir=/private/tmp/workflow-prototype-ui-chrome-20261028 --remote-debugging-port=0 about:blank
```

```sh
node .goal/workflow-prototype/prototype/ui-comparison/browser-check.mjs /private/tmp/workflow-prototype-ui-chrome-20261028 http://127.0.0.1:56130/ red
node .goal/workflow-prototype/prototype/ui-comparison/browser-check.mjs /private/tmp/workflow-prototype-ui-chrome-20261028 http://127.0.0.1:56130/ green
```

최소 red→green 확인은 필터 한 행동에 적용했다. 처음에는 필터 버튼의 선택 모양만 바꾸고 실제 필터는 연결하지 않았다. `검토 필요 2`를 누른 후 기대한 `2개 작업 표시` 대신 `5개 작업 표시`가 남아 assertion이 실패했다(exit 1). [red-observations.json](evidence/red-observations.json)에 전후 실제 화면 상태를 보존했다. 이후 필터 선택과 재표시를 연결했다. 현재 완성 코드에서 `red` 명령을 다시 실행하면 이 과거 실패를 재현하지 않는다.

첫 변경 후 실행에서도 수정 전 화면의 다섯 작업이 남아 실패했다(exit 1). [first-green-failure/green-observations.json](evidence/first-green-failure/green-observations.json), 당시 목록 PNG·접근성 트리를 별도로 보존했다. 이후 관찰기에서 `Network.setCacheDisabled`를 설정하고 다시 로드해 수정한 화면을 확인했다. 캐시 설정 후에는 모든 관찰과 assertion이 통과했다(exit 0).

실제 마지막 stdout:

```text
PASS: 3 views, 5→2 task filtering, correct detail open/close; no observed JS exceptions.
```

마지막으로 `node --check .goal/workflow-prototype/prototype/ui-comparison/browser-check.mjs`가 exit 0으로 끝났다. 이 확인은 관찰기 문법 확인이며, 화면 확인의 대체 근거가 아니다.

## 직접 본 화면과 관찰

아래 9개 PNG를 모두 `view_image`로 열어 확인했다. 소스·DOM·접근성 트리 확인만으로 시각 관찰을 대신하지 않았다.

| 보기 | 전체 5개 | 검토 2개 | 상세 대화상자 |
| --- | --- | --- | --- |
| A · 목록 | [화면](evidence/a-list-all.png) | [화면](evidence/a-list-review.png) | [화면](evidence/a-list-detail.png) |
| B · 카드 | [화면](evidence/b-cards-all.png) | [화면](evidence/b-cards-review.png) | [화면](evidence/b-cards-detail.png) |
| C · 상태 보드 | [화면](evidence/c-board-all.png) | [화면](evidence/c-board-review.png) | [화면](evidence/c-board-detail.png) |

각 PNG와 같은 이름의 `.ax.json`은 당시 접근성 트리다. [green-observations.json](evidence/green-observations.json)은 전체·검토·상세 열림·닫힘을 세 안에서 관찰한 12개 상태다.

| 안 | 화면에서 직접 관찰한 차이 | 실제 수행한 조작과 결과 |
| --- | --- | --- |
| A 목록 | 작업·프로젝트가 왼쪽, 상태·마감·담당자가 같은 행의 고정 열에 표시됐다. 다섯 작업이 세로 다섯 행에 있다. 이 viewport에서 하단 비교 안내는 첫 캡처 아래로 내려갔다. | 전체 5개 → 검토 2개. 두 행 모두 검토 배지·마감·담당자를 유지했다. 첫 작업을 누르자 문구·프로젝트·설명·상태·마감·담당자가 대화상자에 표시됐다. 닫은 후 필터와 두 작업이 유지됐다. |
| B 카드 | 전체는 3열·2행이고 각 카드 안에서 상태·작업명·프로젝트·마감·담당자가 보였다. 검토 필터 후에는 같은 두 카드가 첫 행에 나란히 놓였다. | 전체 5개 → 검토 2개. 같은 첫 작업의 상세를 열고 `닫기`로 돌아왔다. 종료 후 필터와 두 작업이 유지됐다. |
| C 상태 보드 | 예정 1·진행 중 2·검토 필요 2가 서로 다른 세 열에 표시됐다. 검토 두 작업은 오른쪽 열에 모였다. 필터 후 왼쪽 두 열은 0과 `표시할 작업 없음`, 오른쪽 열은 2로 표시됐다. | 전체 5개 → 검토 2개. 같은 첫 작업 상세를 열고 닫았다. 종료 후 필터와 두 작업이 유지됐다. |

모든 검토 화면의 실제 작업명은 `랜딩 페이지 문구 검토`, `주간 리포트 확인`이었다. 세 상세 화면의 제목은 `랜딩 페이지 문구 검토`였다. 마지막 실행 중 JavaScript `Runtime.exceptionThrown` 이벤트는 관찰되지 않았다. 이는 실행한 조작에 한정된 관찰이며 브라우저 전체 오류 부재를 뜻하지 않는다.

알게 된 것: 이 데이터와 viewport에서는 목록은 메타데이터를 세로로 정렬하고, 카드는 두 검토 작업을 가로로 놓으며, 보드는 검토 작업을 한 열에 모은다. 보드 필터는 빈 열 두 개를 남긴다. 세 형태를 실제로 전환·필터·상세 열기로 비교할 수 있는 산출물을 확보했다. 어느 안이 더 빠르거나 더 좋은지는 이 관찰로 입증하지 않았다.

## 한계와 남은 선택

- **사용자 선호·채택·종료 판단: 사용자 선택 대기.** 에이전트는 안을 선택하지 않았다. 사용자가 화면을 보고 어느 안을 선호하는지, 추가 실험이 필요한지는 답하지 않았다. 이 대기를 실행 증거 부재와 혼동하지 않는다.
- 정적 가상 데이터 다섯 개, 한 데스크톱 viewport와 Chrome headless 한 환경만 확인했다. 모바일·실제 창 화면·다른 브라우저·확대 배율·큰 작업 집합은 미확인이다.
- 포인터 조작과 닫기 버튼을 확인했다. 키보드의 탭 이동·방향키·Esc·스크린리더 사용성은 미확인이다. 현재 탭은 포인터 비교용이며 완전한 키보드 탭 패턴을 검증하지 않았다.
- 자세히 연 작업은 세 안에서 동일한 첫 검토 작업 한 개다. 다른 네 작업 상세, 실제 데이터 수정·저장·동기화는 확인하지 않았다.
- 작업 찾기 소요 시간이나 오류율을 측정하지 않았고 사용자 비교 실험도 하지 않았다. 배치에 대한 에이전트의 화면 관찰과 사용자의 선호를 구분한다.
- 최초 sandbox에서 localhost 서버 시작은 `PermissionError: [Errno 1] Operation not permitted`로 실패했다. 정상 범위의 실행 승인 후 서버·독립 Chrome·CDP를 사용했다. Chrome은 keychain/encryption·macOS display-link 경고를 냈지만 9개 캡처와 조작 관찰은 실제 완료됐다. 서버의 `/favicon.ico` 요청은 404였다.
- `apply_patch`의 관찰기 파일 생성 호출이 응답 없이 멈춰 중단했다. 파일 존재 여부를 확인하고 할당된 폴더에 따옴표로 고정한 heredoc으로 작성했다.

실험 결과는 부모 Execute에 돌려준다. 이 사례는 최종 Verify 판정·다음 단계 진입·제품 구현으로 진행하지 않았다. 커밋·스테이징은 하지 않았으며 부모가 자기 티켓과 이 폴더만 확인해 처리한다.

## 직접 보기와 재실행

[index.html](index.html)을 브라우저에서 열면 외부 의존성 없이 동작한다. A/B/C, `전체 5`/`검토 필요 2`, 작업, `닫기`를 직접 눌러 비교할 수 있다. 보존된 PNG만 보아도 세 안을 비교할 수 있다.

실제 브라우저 관찰을 다시 실행하려면 저장소 루트에서 서버를 포트 `0`으로 시작하고, 출력된 실제 포트를 사용한다. 다른 사례의 서버나 브라우저를 재사용하지 않는다.

```sh
python3 -m http.server 0 --bind 127.0.0.1 --directory .goal/workflow-prototype/prototype/ui-comparison
```

별도 터미널에서 새 임시 프로필의 독립 Chrome을 시작한다.

```sh
task_chrome_profile=$(mktemp -d /private/tmp/workflow-ui-chrome.XXXXXX)
printf '%s\n' "$task_chrome_profile"
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless=new --no-first-run --no-default-browser-check --disable-background-networking --disable-extensions --disable-sync --disable-gpu --user-data-dir="$task_chrome_profile" --remote-debugging-port=0 about:blank
```

Chrome 시작 전에 출력한 변수 값 또는 프로필 경로를 다음 명령의 `NEW_PROFILE`에 넣고, 서버의 실제 포트를 `SERVER_PORT`에 넣는다. `NEW_OUTPUT_DIRECTORY`도 이 사례 폴더 아래 새 이름으로 지정해 이번 기록을 덮어쓰지 않는다. Node의 native WebSocket을 지원하는 Node 26으로 실행했다. 추가 패키지 설치는 없다.

```sh
node .goal/workflow-prototype/prototype/ui-comparison/browser-check.mjs NEW_PROFILE http://127.0.0.1:SERVER_PORT/ green NEW_OUTPUT_DIRECTORY
```

관찰기는 공개 버튼을 누르고 PNG·접근성 트리·상태 JSON을 지정한 출력 폴더에 쓴다. 새 PNG를 직접 열어 확인한다. 서버와 Chrome을 시작한 각 터미널에서 Ctrl+C로 종료한다. 임시 브라우저 프로필은 증거 폴더에 포함하지 않았다.

## 실행 정리

- 에이전트는 관찰과 결과 문서 작성 후 사용량 제한으로 종료됐다. main이 보존된 12개 상태와 캡처, 구현·관찰 명령을 이어서 검토했다.
- 2026-10-29 main이 실험 프로필 경로와 HTTP 서버 디렉터리가 일치하는지 확인한 뒤 독립 Chrome PID 70840과 서버 PID 70352에만 SIGTERM을 보냈다.
- 종료 후 같은 PID 조회 결과는 `none`이었다. 사용자의 기존 Chrome이나 다른 서버는 종료하지 않았다. 캡처·관찰 기록·실험 프로필은 삭제하지 않았다.
- main도 세 안의 전체 화면과 목록의 검토·상세 캡처를 직접 열어 기록과 일치함을 확인했다. 승인된 UI 선호나 채택 의견은 여전히 없다.
