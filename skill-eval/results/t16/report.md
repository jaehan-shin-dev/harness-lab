# 보고서: workflow-define

## 머리말

- 작성: 2026-10-23T09:34:47
- 모델: ['openai-codex/gpt-6-sol']
- thinking: {'candidate': 'medium', 'mock_user': 'low', 'judge': 'medium'}
- pi 버전: ['1.3.0']
- 스킬 버전: `.agents/skills`·AGENTS.md 마지막 커밋 4a54524, 변경 없음
- 회차: 완료 18, 실패 0, 오염 의심 2
- 모의 사용자: ['llm']

## 과제·팔별 요약

평균 ± 표준편차. 오염 의심·실패 회차는 평균에서 뺀다. 과정은 8점 만점, 심판 루브릭은 10점 만점. 과제 3(workflow-skill-fix)의 회수율·심판 사실 판정은 참고 값이다(한계 참고).

| 과제 | 팔 | 회차(완료/깨끗) | 종료 사유 | 과정 | 회수율(키워드) | 심판 사실 판정 | 심판 루브릭 |
|---|---|---|---|---|---|---|---|
| requests-2317 | control | 3/2 | 자연 종료 3 | 1.00 ± 0.00 (n=2) | 0.50 ± 0.00 (n=2) | 0.50 ± 0.00 (n=2) | 9.00 ± 0.00 (n=2) |
| requests-2317 | skill | 3/3 | 종료 3 | 7.00 ± 0.00 (n=3) | 0.50 ± 0.17 (n=3) | 0.44 ± 0.19 (n=3) | 10.00 ± 0.00 (n=3) |
| requests-retry | control | 3/2 | 자연 종료 3 | 1.00 ± 0.00 (n=2) | 0.71 ± 0.00 (n=2) | 0.71 ± 0.00 (n=2) | 6.00 ± 1.41 (n=2) |
| requests-retry | skill | 3/3 | 종료 2, 미종료 1 | 7.33 ± 1.15 (n=3) | 0.71 ± 0.00 (n=3) | 0.71 ± 0.00 (n=3) | 10.00 ± 0.00 (n=3) |
| workflow-skill-fix | control | 3/3 | 자연 종료 2, 미종료 1 | 3.33 ± 0.58 (n=3) | 0.80 ± 0.00 (n=3) | 0.80 ± 0.00 (n=3) | 9.67 ± 0.58 (n=3) |
| workflow-skill-fix | skill | 3/3 | 종료 2, 미종료 1 | 6.67 ± 0.58 (n=3) | 0.80 ± 0.20 (n=3) | 0.80 ± 0.00 (n=3) | 9.33 ± 0.58 (n=3) |

## 과정 검사 통과율

| 검사 | requests-2317/control | requests-2317/skill | requests-retry/control | requests-retry/skill | workflow-skill-fix/control | workflow-skill-fix/skill |
|---|---|---|---|---|---|---|
| 1 goal.md가 .goal/<이름>/ 아래 | 0/2 | 3/3 | 0/2 | 3/3 | 3/3 | 3/3 |
| 2 여섯 절 | 0/2 | 3/3 | 0/2 | 3/3 | 0/3 | 3/3 |
| 3 질문 번호·추천 답 | 0/2 | 3/3 | 0/2 | 3/3 | 3/3 | 3/3 |
| 4 한 턴에 한 라운드, 묻고 기다림 | 2/2 | 3/3 | 2/2 | 3/3 | 3/3 | 3/3 |
| 5 라운드마다 goal.md 갱신 | 0/2 | 0/3 | 0/2 | 2/3 | 0/3 | 0/3 |
| 6 합의·미결정·가정 표기 | 0/2 | 3/3 | 0/2 | 3/3 | 1/3 | 3/3 |
| 7 .goal/ 밖 수정 없음 | 0/2 | 3/3 | 0/2 | 3/3 | 0/3 | 3/3 |
| 8 끝내기 전 사용자 확인 | 0/2 | 3/3 | 0/2 | 2/3 | 0/3 | 2/3 |

## 회차별

| 회차 | 종료 | 라운드 | 과정 | 회수율 | 심판 루브릭 | 누출 검사 |
|---|---|---|---|---|---|---|
| requests-2317__control__r1 | 자연 종료 | 3 | 1/8 | 5/6 | 9 | 오염 의심: 4턴 bash 네트워크 명령 ['uv run --no-project --python /usr/bin/python3 --with']: uv run --no-project --python /usr/bin/python3 --with pytest python -m pytest -q test_requests.py -k bytes_method; 4턴 bash 네트워크 명령 ['uv run --no-project --python /usr/bin/python3 --with']: uv run --no-project --python /usr/bin/ |
| requests-2317__control__r2 | 자연 종료 | 3 | 1/8 | 3/6 | 9 | 깨끗 |
| requests-2317__control__r3 | 자연 종료 | 3 | 1/8 | 3/6 | 9 | 깨끗 |
| requests-2317__skill__r1 | 종료 | 4 | 7/8 | 2/6 | 10 | 깨끗 (회차 폴더 안 읽기 1회, 허용) |
| requests-2317__skill__r2 | 종료 | 4 | 7/8 | 4/6 | 10 | 깨끗 (회차 폴더 안 읽기 1회, 허용) |
| requests-2317__skill__r3 | 종료 | 3 | 7/8 | 3/6 | 10 | 깨끗 |
| requests-retry__control__r1 | 자연 종료 | 3 | 1/8 | 5/7 | 6 | 오염 의심: 3턴 bash 네트워크 명령 ['uv run --with']: uv run --with pytest --no-project python -m pytest -q test_retries.py; 3턴 bash 네트워크 명령 ['uv run --python /usr/bin/python3 --with']: uv run --python /usr/bin/python3 --with pytest --no-project python -m pytest -q test_retries.py; 3턴 bash 네트워크 명령 ['uv run --python /u (회차 폴더 안 읽기 2회, 허용) |
| requests-retry__control__r2 | 자연 종료 | 3 | 1/8 | 5/7 | 5 | 깨끗 |
| requests-retry__control__r3 | 자연 종료 | 4 | 1/8 | 5/7 | 7 | 깨끗 (회차 폴더 안 읽기 1회, 허용) |
| requests-retry__skill__r1 | 종료 | 5 | 8/8 | 5/7 | 10 | 깨끗 |
| requests-retry__skill__r2 | 미종료 | 5 | 6/8 | 5/7 | 10 | 깨끗 |
| requests-retry__skill__r3 | 종료 | 5 | 8/8 | 5/7 | 10 | 깨끗 |
| workflow-skill-fix__control__r1 | 자연 종료 | 5 | 3/8 | 4/5 | 9 | 깨끗 |
| workflow-skill-fix__control__r2 | 자연 종료 | 5 | 3/8 | 4/5 | 10 | 깨끗 |
| workflow-skill-fix__control__r3 | 미종료 | 5 | 4/8 | 4/5 | 10 | 깨끗 |
| workflow-skill-fix__skill__r1 | 미종료 | 5 | 6/8 | 4/5 | 10 | 깨끗 |
| workflow-skill-fix__skill__r2 | 종료 | 3 | 7/8 | 3/5 | 9 | 깨끗 |
| workflow-skill-fix__skill__r3 | 종료 | 4 | 7/8 | 5/5 | 9 | 깨끗 |

## 키워드와 심판이 다른 칸

사람이 읽을 칸. 키워드 판정 Y/N, 심판 판정 Y/N.

| 회차 | 사실 | 키워드 | 심판 | 심판 근거 |
|---|---|---|---|---|
| requests-2317__skill__r3 | U5 | Y ['2\\.6'] | N |  |
| workflow-skill-fix__skill__r2 | U2 | N [] | Y | `.agents/skills/workflow-define-eval/`과 `.agents/skills/workflow-plan-eval/`은 제거한다. |
| workflow-skill-fix__skill__r3 | U3 | Y ['중복\\s*(없|제거|금지)'] | N | 스킬 파일에 반복된 문장은 제거한다. |

## 스킬 로드 확인 (C4)

| 회차 | 1턴이 `<skill name=` | system skills 수 | project_context | 시험 대상 grill SKILL.md 읽음 | 시험 대상 SKILL.md 읽기 | 작업 폴더 SKILL.md 읽기 | 끄기 옵션 |
|---|---|---|---|---|---|---|---|
| requests-2317__control__r1 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-2317__control__r2 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-2317__control__r3 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-2317__skill__r1 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| requests-2317__skill__r2 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| requests-2317__skill__r3 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| requests-retry__control__r1 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-retry__control__r2 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-retry__control__r3 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-retry__skill__r1 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| requests-retry__skill__r2 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| requests-retry__skill__r3 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| workflow-skill-fix__control__r1 | 아니오 | 0 | 없음 | 아니오 | 0 | 11 | --no-skills --no-context-files |
| workflow-skill-fix__control__r2 | 아니오 | 0 | 없음 | 아니오 | 0 | 12 | --no-skills --no-context-files |
| workflow-skill-fix__control__r3 | 아니오 | 0 | 없음 | 아니오 | 0 | 11 | --no-skills --no-context-files |
| workflow-skill-fix__skill__r1 | workflow-define | 7 | AGENTS.md, AGENTS.md | 예 | 2 | 10 | 없음 |
| workflow-skill-fix__skill__r2 | workflow-define | 7 | AGENTS.md, AGENTS.md | 예 | 2 | 9 | 없음 |
| workflow-skill-fix__skill__r3 | workflow-define | 7 | AGENTS.md, AGENTS.md | 예 | 2 | 2 | 없음 |

## 실행 기록 평균 (점수에 쓰지 않음, goal.md R6)

| 과제 | 팔 | 턴 | 라운드 | 입력 토큰 | 출력 토큰 | 캐시 읽기 | 추론 | 비용($) | 최대 컨텍스트 | 도구 호출 | 실패 호출 | 압축 | 재시도 | 걸린 시간(초) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| requests-2317 | control | 4.0 | 3.0 | 21979.0 | 3821.3 | 190976.0 | 1313.0 | 0.120 | 5.5% | 23.7 | 2.0 | 0.0 | 0.0 | 113.3 |
| requests-2317 | skill | 4.7 | 3.7 | 21712.7 | 4193.0 | 109397.3 | 687.3 | 0.107 | 5.0% | 15.0 | 0.3 | 0.0 | 0.0 | 87.6 |
| requests-retry | control | 4.3 | 3.3 | 57049.0 | 9767.0 | 893269.3 | 3210.7 | 0.390 | 11.6% | 47.7 | 3.7 | 0.0 | 0.0 | 246.0 |
| requests-retry | skill | 6.0 | 5.0 | 27258.0 | 7372.3 | 230954.7 | 991.0 | 0.174 | 8.7% | 16.0 | 0.7 | 0.0 | 0.0 | 135.6 |
| workflow-skill-fix | control | 6.0 | 5.0 | 45162.7 | 10794.0 | 449920.0 | 2405.3 | 0.288 | 11.8% | 37.7 | 0.0 | 0.0 | 0.0 | 205.2 |
| workflow-skill-fix | skill | 5.0 | 4.0 | 23844.7 | 6353.0 | 127530.7 | 893.7 | 0.137 | 6.3% | 18.0 | 0.0 | 0.0 | 0.0 | 110.1 |

## 참고 기록 (점수 아님)

| 회차 | 알려 준 사용자 사실 | 수락 결정 일치 | 찾을 수 있는 사실을 물음 | 모름 대답 | 모의 사용자 출력 보정 |
|---|---|---|---|---|---|
| requests-2317__control__r1 | U1, U2, U3, U4, U6 | - | 0 | 1 | 0 |
| requests-2317__control__r2 | U1, U2, U6 | - | 0 | 1 | 0 |
| requests-2317__control__r3 | U1, U2, U6 | - | 0 | 1 | 0 |
| requests-2317__skill__r1 | U1, U2, U6 | - | 0 | 10 | 0 |
| requests-2317__skill__r2 | U1, U2, U3 | - | 0 | 9 | 0 |
| requests-2317__skill__r3 | U1, U2, U6 | - | 0 | 7 | 0 |
| requests-retry__control__r1 | U2, U4, U5, U6 | - | 0 | 0 | 0 |
| requests-retry__control__r2 | U2, U3, U4, U5, U6 | - | 0 | 0 | 0 |
| requests-retry__control__r3 | U2, U3, U4, U5, U6 | - | 0 | 0 | 0 |
| requests-retry__skill__r1 | U2, U3, U4, U5, U6 | A2, A3 | 0 | 4 | 0 |
| requests-retry__skill__r2 | U2, U3, U4, U5, U6 | - | 0 | 3 | 0 |
| requests-retry__skill__r3 | U2, U3, U4, U5, U6 | A2, A3 | 0 | 4 | 0 |
| workflow-skill-fix__control__r1 | U2, U4 | A11, A16, A9 | 0 | 3 | 0 |
| workflow-skill-fix__control__r2 | U1, U2, U4 | A1, A10, A11, A2 | 0 | 2 | 0 |
| workflow-skill-fix__control__r3 | O1, U1, U2, U4 | A11, A16, A9 | 0 | 2 | 0 |
| workflow-skill-fix__skill__r1 | O1, U2, U4 | A1, A10, A11, A14, A16, A2, A3, A4, A5 | 0 | 2 | 0 |
| workflow-skill-fix__skill__r2 | O1, U2, U4 | A1, A10, A11, A2, A3, A4, A5, A9 | 0 | 1 | 0 |
| workflow-skill-fix__skill__r3 | U1, U2, U4 | A1, A10, A11, A14, A16, A2, A3, A4, A5, A9 | 0 | 1 | 0 |

## 한계

- 심판은 후보와 같은 모델이다(goal.md C1). 자기 쪽에 후할 수 있다.
- 스킬 팔의 goal.md([합의] 등)와 질문 글(❓, ➡️)에는 흔적이 있어 심판에게 팔이 완전히 가려지지 않는다.
- 심판은 같은 입력에도 점수가 흔들린다(M1: 같은 goal.md 4회 호출에 루브릭 9~10점). 회차마다 1회만 부른다.
- 심판 입력에는 후보 글과 모의 사용자 대답이 함께 들어간다(2026-10-22 결정). 첫 메시지는 팔이 드러나지 않게 과제의 시작 요청으로 바꾼다.
- 공개 벤치마크(SWE-bench 이슈)는 모델이 외웠을 수 있다. 과제 3(workflow-skill-fix)은 비공개라 해당 없다.
- 과제 3의 스킬 팔은 시험 대상 스킬 자체가 그 과제의 결과물(스킬 7개)이라, 스킬을 읽으면 끝 모양을 볼 수 있다. M2에서 실제로 로드된 스킬을 고칠 대상으로 보고 "이미 됐다"고 적었다. 그래서 과제 3의 회수율·심판 사실 판정은 참고로만 보고, 과정 검사는 그대로 쓴다(2026-10-23 결정).
- 누출 검사는 회차 폴더 안(작업 폴더 + 설정 폴더) 읽기를 허용한다(2026-10-23 결정). 그 위·밖 경로와 쓰기는 오염 의심이다.
- 모의 사용자 대답 문장은 답변표의 문장을 이어 붙여 만든다. 모델은 어떤 사실로 대답할지만 고른다.
- 과제 3 작업 폴더의 옛 AGENTS.md는 스킬 팔에서 새 AGENTS.md와 함께 읽힌다(당시 조건). 이번 회차들: 작업 폴더 AGENTS.md 있음 6회.
