# 기술 가능성 사례: 로컬 SQLite의 프로세스 간 예약 경쟁

## 실제 적용 요청과 질문

이 사례는 사용자가 승인한 `workflow-prototype` Execute의 실제 적용 평가를 main이 위임한 **에이전트 수행 사례**다. main → subagent의 명시 요청은 다음과 같다.

> Use $workflow-prototype at .agents/skills/workflow-prototype/SKILL.md explicitly for this user-authorized agent-run application case.

같은 요청에서 현재 환경에서 실행할 작은 질문 선택을 위임했다. 새로운 사용자 아이디어나 사용자 응답을 만들어 기록하지 않았다. 읽고 적용한 스킬은 [workflow-prototype](../../../../.agents/skills/workflow-prototype/SKILL.md)이며, 코드 관찰은 `goal.md`의 공개 명령·입력·출력 Interface에 한정했다. `tdd`의 공개 Interface·red → green 원칙을 작은 assertion 두 건에 적용했다. 추가 질문·제품용 goal·제품 테스트 프레임워크는 필요하지 않았다.

**선택한 질문:** 현재 설치된 Python/SQLite와 이 작업 폴더의 실제 파일에서, 서로 다른 두 프로세스가 같은 자원 하나를 예약하면 예약을 한 건으로 유지할 수 있는가? 두 번째 프로세스의 잠금 대기 시간이 충분하거나 짧을 때 어떤 실제 결과가 나오는가?

## 실행한 조건과 대체한 조건

| 구분 | 실제 사용 / 대체 범위 |
|---|---|
| 실행 환경 | Python 3.9.6, SQLite 3.51.0, macOS 26.6.2 arm64. 최종 출력의 `environment`에서 런타임 값을 읽었다. |
| 데이터베이스 | 이 사례의 `evidence/<run>/reservations.sqlite`에 생성한 실제 디스크 파일. 실제 SQLite 연결·트랜잭션·잠금·고유 키 제약을 사용했다. 메모리 DB·DB 모킹은 사용하지 않았다. |
| 경쟁 실행 | 별도 Python 프로세스 A/B를 실제 실행했다. A가 `BEGIN IMMEDIATE` 잠금 획득 이벤트를 출력한 뒤 B를 시작했다. A가 700 ms 동안 트랜잭션을 유지하도록 의도적으로 지연해 경쟁 조건을 만들었다. |
| 예약 규칙 | `reservations(resource TEXT PRIMARY KEY, owner TEXT NOT NULL)`에 A/B가 같은 `room-1`을 INSERT했다. 성공 후 commit, 충돌 또는 잠금 오류 후 rollback했다. |
| 대기 설정 | B의 실제 `sqlite3.connect(..., timeout=...)`에 2000 ms 또는 50 ms를 주었다. 기본 rollback journal의 실제 관찰 값은 `delete`다. |
| 대체한 부분 | 실제 예약 제품·실제 사용자 요청 대신 작은 고정 입력의 A/B와 자원 한 개를 사용했다. 실제 서비스 트래픽 대신 인위적으로 잠금을 유지했다. 이 대체를 실제 서비스 성능·제품 검증으로 해석하지 않는다. |
| 사용하지 않은 조건 | 외부 API·인증·네트워크·브라우저·별도 DB 서버는 필요하지 않은 질문으로 골랐다. 이들의 권한이나 동작을 확인한 사례가 아니다. |

## 공개 Interface와 재실행

저장소 루트에서 Python 3 표준 라이브러리만 사용한다. 설치·네트워크 접근·공유 포트는 필요 없다.

기본 공개 명령은 다음과 같다. `--database`는 아직 없는 파일 경로여야 하며 부모 디렉터리는 존재해야 한다. 이전 DB를 자동으로 덮어쓰지 않는다.

```sh
python3 .goal/workflow-prototype/prototype/technical-feasibility/probe.py --input .goal/workflow-prototype/prototype/technical-feasibility/wait.json --database .goal/workflow-prototype/prototype/technical-feasibility/evidence/manual-wait.sqlite
```

입력은 [wait.json](wait.json) 또는 [timeout.json](timeout.json)이다. 자원·예약자 이름, A의 잠금 유지 시간, B의 대기 시간을 공개 JSON에서 바꿀 수 있다. stdout JSON은 환경, 적용한 입력, 실행한 실제 자식 명령, 각 프로세스의 이벤트·종료 코드·오류·대기 측정, 최종 예약 목록을 제공한다. 예상한 예약 충돌/잠금 오류를 관찰하면 구조화된 결과를 내고 명령은 0으로 끝난다. 따라서 종료 코드 0만으로 B의 예약 성공을 판단하면 안 된다.

공개 명령을 실행하고 출력 파일을 보존하는 최소 assertion은 다음 두 명령이다. `--out-dir`는 새 폴더여야 한다. 이미 사용했다면 다른 새 이름을 준다.

```sh
python3 .goal/workflow-prototype/prototype/technical-feasibility/assert_case.py --case wait --out-dir .goal/workflow-prototype/prototype/technical-feasibility/evidence/rerun-wait
python3 .goal/workflow-prototype/prototype/technical-feasibility/assert_case.py --case timeout --out-dir .goal/workflow-prototype/prototype/technical-feasibility/evidence/rerun-timeout
```

`assert_case.py`는 내부 함수를 import하거나 DB를 별도로 조회하지 않는다. 문서화한 `probe.py --input ... --database ...`를 실행하고 그 stdout만 확인한다. 기대값은 두 입력에 대한 독립적인 결과 명세인 `[["room-1", "A"]]`, `already_reserved` / `database_locked`다. 각 실행 폴더의 `command.json`은 실행한 정확한 명령, `stdout.json`·`stderr.txt`·`exit-status.txt`는 **probe 명령**의 실제 출력·종료 코드다. assertion 실행 자체의 결과는 아래 실행 이력에 구분했다.

## 관찰한 결과

최종 코드에서 실행한 공개 assertion 두 건은 모두 성공했다. 아래 시간은 각 한 번의 관찰값이며 부하 시험이나 지연 상한 보장이 아니다.

| 최종 실행 | B 설정 | A 결과 | B의 실제 결과 / 오류 | B의 관찰 대기 | 최종 예약 | 전체 시간 |
|---|---:|---|---|---:|---|---:|
| [final-wait/stdout.json](evidence/final-wait/stdout.json) | 2000 ms | `reserved` | `already_reserved`, `IntegrityError: UNIQUE constraint failed: reservations.resource` | 719.692 ms | `[["room-1", "A"]]` | 810.568 ms |
| [final-timeout/stdout.json](evidence/final-timeout/stdout.json) | 50 ms | `reserved` | `database_locked`, `OperationalError: database is locked` | 79.767 ms | `[["room-1", "A"]]` | 791.873 ms |

두 최종 probe 명령과 모든 최종 자식 프로세스의 종료 코드는 0이며 stderr는 비었다. 실제 충돌 오류는 JSON의 `error_type`·`error`로 보존했다. 50 ms 설정에서 관찰 시간이 79.767 ms였으므로 설정값을 엄격한 벽시계 상한으로 설명하지 않는다. 프로세스 스케줄링·측정·오류 처리 비용이 포함될 수 있고 그 원인을 분리 측정하지 않았다.

이 환경·두 입력에서 **동시 경쟁 후 예약을 한 건으로 유지할 수 있었다**. 충분한 대기에서는 B가 A의 commit 뒤 잠금을 획득하고 실제 고유 키 제약에 걸렸다. 짧은 대기에서는 B가 실제 SQLite 잠금 오류를 받았고 A의 예약은 남았다. 중복 방지에 성공하더라도 두 요청이 모두 예약 성공으로 끝나는 것은 아니며, 잠금 대기와 예약 충돌은 서로 다른 결과다.

## 최소 assertion 실행 이력

실행 순서에 따라 한 조건씩 red → green으로 진행했다. red의 코드는 최종 구현 전 상태이며, 보존한 출력은 당시 실행 기록이다.

1. **wait RED** — `assert_case.py --case wait --out-dir .../evidence/red-wait`를 실행했다. 초기 CLI가 `{"status": "not_implemented"}`를 출력해 `AssertionError: {'status': 'not_implemented'}`로 assertion 명령이 1로 끝났다. [실제 probe 출력](evidence/red-wait/stdout.json), [정확한 probe 명령](evidence/red-wait/command.json)을 보존했다. 당시 probe 자체의 종료 코드는 0이다.
2. **wait GREEN** — 실제 DB와 두 프로세스를 구현한 후 `--out-dir .../evidence/green-wait`에서 assertion이 0으로 끝났다. 실제 출력은 `PASS wait: one reservation; contender sees the committed conflict`였으며, [실제 실행 결과](evidence/green-wait/stdout.json)에 B의 731.947 ms 대기와 고유 키 충돌이 남았다.
3. **timeout RED** — timeout 입력과 기대 결과를 추가한 후 `--case timeout --out-dir .../evidence/red-timeout`에서 assertion이 1로 끝났다. B의 실제 `sqlite3.OperationalError: database is locked`가 처리되지 않아 `worker_failed`였기 때문이다. [실제 출력](evidence/red-timeout/stdout.json)의 `contender.stderr`에 원래 traceback과 B 종료 코드 1을 보존했다. 이때도 A의 예약 한 건은 남았다.
4. **최종 GREEN** — 잠금 오류만 구분해 JSON으로 보고하도록 최소 보완했다. `--out-dir .../evidence/final-wait` 및 `.../evidence/final-timeout`의 두 assertion 명령은 각각 0으로 끝났고 다음을 출력했다.

```text
PASS wait: one reservation; contender=already_reserved
PASS timeout: one reservation; contender=database_locked
```

파일 편집 도구 `tools.apply_patch`가 출력 없이 대기해 해당 실행을 종료했다. 당시 대상 파일이 없음을 확인한 뒤 허용된 사례 폴더 안에 `exec_command`의 파일 쓰기로 전환했다. 이 도구 문제는 SQLite 조건을 대체하거나 실행 성공으로 계산하지 않았다.

## 한계와 남은 선택

- 이 결과는 현재 호스트·파일 위치·SQLite 버전·기본 journal·두 프로세스·자원 한 개에 한정한다. 다른 파일시스템·네트워크 드라이브·WAL·여러 호스트·다수 자원·대규모 동시 요청은 실행하지 않았다.
- 700 ms 지연은 경쟁을 만들기 위한 입력이며 실제 서비스 작업 시간의 추정값이 아니다. 시간 수치는 측정 위치가 제한된 단일 관찰이며 처리량·공정성·엄격한 timeout 보장은 미확인이다.
- 강제 프로세스 종료·전원 장애·디스크 오류·보안·사용자 인증·실제 서비스의 재시도/안내 정책은 확인하지 않았다. 입력 검증·제품 API·UI·운영용 테스트 체계는 이 질문에 필요하지 않아 만들지 않았다.
- 이 사례는 스킬을 명시 지정한 위임 요청을 실제 적용한 기록이다. Codex 런타임의 암시적 호출 차단을 동적으로 시험한 기록은 아니다. 사용자 화면 선호·사용성·실제 채택 의견도 확인하지 않았다.
- **사용자 판단 대기:** 이 관찰로 충분한지, 다른 조건을 추가로 볼지, 어떤 제품 방향을 택할지와 종료·채택은 사용자가 판단한다. 현재 사용자 피드백은 없다. 추가 인간 작업을 이 에이전트 수행 평가의 완료 조건으로 만들지 않는다.

탐색 결과를 main에 돌려주어 원래 Execute 논의로 복귀한다. 정식 제품 구현·최종 Verify 판정은 수행하지 않았다. 수정 범위는 이 사례 폴더뿐이며 스테이징·커밋은 하지 않았다. 부모 Execute의 티켓 확인·커밋은 main이 처리한다.
