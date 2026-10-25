# 보고서: workflow-define

## 머리말

- 작성: 2026-10-23T09:34:47
- 모델: ['openai-codex/gpt-6-sol']
- thinking: {'candidate': 'medium', 'mock_user': 'low', 'judge': 'medium'}
- pi 버전: ['1.3.0']
- 스킬 버전: `.agents/skills`·AGENTS.md 마지막 커밋 4a54524, 변경 없음
- 회차: 완료 6, 실패 0, 오염 의심 2
- 모의 사용자: ['llm']

## 과제·팔별 요약

평균 ± 표준편차. 오염 의심·실패 회차는 평균에서 뺀다. 과정은 8점 만점, 심판 루브릭은 10점 만점. 과제 3(workflow-skill-fix)의 회수율·심판 사실 판정은 참고 값이다(한계 참고).

| 과제 | 팔 | 회차(완료/깨끗) | 종료 사유 | 과정 | 회수율(키워드) | 심판 사실 판정 | 심판 루브릭 |
|---|---|---|---|---|---|---|---|
| requests-2317 | control | 1/1 | 자연 종료 1 | 1.00 ± 0.00 (n=1) | 0.67 ± 0.00 (n=1) | 0.67 ± 0.00 (n=1) | 7.00 ± 0.00 (n=1) |
| requests-2317 | skill | 1/1 | 종료 1 | 7.00 ± 0.00 (n=1) | 0.50 ± 0.00 (n=1) | 0.50 ± 0.00 (n=1) | 10.00 ± 0.00 (n=1) |
| requests-retry | control | 1/0 | 자연 종료 1 | - | - | - | - |
| requests-retry | skill | 1/1 | 종료 1 | 7.00 ± 0.00 (n=1) | 0.71 ± 0.00 (n=1) | 0.71 ± 0.00 (n=1) | 8.00 ± 0.00 (n=1) |
| workflow-skill-fix | control | 1/0 | 자연 종료 1 | - | - | - | - |
| workflow-skill-fix | skill | 1/1 | 종료 1 | 7.00 ± 0.00 (n=1) | 0.80 ± 0.00 (n=1) | 0.60 ± 0.00 (n=1) | 9.00 ± 0.00 (n=1) |

## 과정 검사 통과율

| 검사 | requests-2317/control | requests-2317/skill | requests-retry/control | requests-retry/skill | workflow-skill-fix/control | workflow-skill-fix/skill |
|---|---|---|---|---|---|---|
| 1 goal.md가 .goal/<이름>/ 아래 | 0/1 | 1/1 | - | 1/1 | - | 1/1 |
| 2 여섯 절 | 0/1 | 1/1 | - | 1/1 | - | 1/1 |
| 3 질문 번호·추천 답 | 0/1 | 1/1 | - | 1/1 | - | 1/1 |
| 4 한 턴에 한 라운드, 묻고 기다림 | 1/1 | 1/1 | - | 1/1 | - | 1/1 |
| 5 라운드마다 goal.md 갱신 | 0/1 | 0/1 | - | 0/1 | - | 0/1 |
| 6 합의·미결정·가정 표기 | 0/1 | 1/1 | - | 1/1 | - | 1/1 |
| 7 .goal/ 밖 수정 없음 | 0/1 | 1/1 | - | 1/1 | - | 1/1 |
| 8 끝내기 전 사용자 확인 | 0/1 | 1/1 | - | 1/1 | - | 1/1 |

## 회차별

| 회차 | 종료 | 라운드 | 과정 | 회수율 | 심판 루브릭 | 누출 검사 |
|---|---|---|---|---|---|---|
| requests-2317__control__r1 | 자연 종료 | 3 | 1/8 | 4/6 | 7 | 깨끗 (회차 폴더 안 읽기 1회, 허용) |
| requests-2317__skill__r1 | 종료 | 3 | 7/8 | 3/6 | 10 | 깨끗 (회차 폴더 안 읽기 1회, 허용) |
| requests-retry__control__r1 | 자연 종료 | 3 | 1/8 | 5/7 | 6 | 오염 의심: 3턴 bash: skill-eval 언급 (회차 폴더 안 읽기 1회, 허용) |
| requests-retry__skill__r1 | 종료 | 5 | 7/8 | 5/7 | 8 | 깨끗 |
| workflow-skill-fix__control__r1 | 자연 종료 | 5 | 3/8 | 4/5 | 10 | 오염 의심: 6턴 bash: 작업 폴더 밖 ['/tmp/workflow-skill-smoke.XXXXXX', '/tmp/pi-lab-workflow-smoke-path']; 6턴 bash: 작업 폴더 밖 ['/tmp/pi-lab-workflow-smoke-path']; 6턴 bash: 작업 폴더 밖 ['/tmp/pi-lab-workflow-smoke-path', '~/notes']; 6턴 read: 작업 폴더 밖 ['/tmp/workflow-skill-smoke.INVALID']; 6턴 bash: 작업 폴더 밖 ['/tmp/pi-lab-work |
| workflow-skill-fix__skill__r1 | 종료 | 5 | 7/8 | 4/5 | 9 | 깨끗 (회차 폴더 안 읽기 1회, 허용) |

## 키워드와 심판이 다른 칸

사람이 읽을 칸. 키워드 판정 Y/N, 심판 판정 Y/N.

| 회차 | 사실 | 키워드 | 심판 | 심판 근거 |
|---|---|---|---|---|
| workflow-skill-fix__skill__r1 | U1 | Y ['1\\s*[·,、]\\s*2\\s*[·,、]\\s*3\\s*[·,、]\\s*4', '(?<!\\d)1\\s*[~\\-–]\\s*4(?!\\d)'] | N |  |

## 스킬 로드 확인 (C4)

| 회차 | 1턴이 `<skill name=` | system skills 수 | project_context | 시험 대상 grill SKILL.md 읽음 | 시험 대상 SKILL.md 읽기 | 작업 폴더 SKILL.md 읽기 | 끄기 옵션 |
|---|---|---|---|---|---|---|---|
| requests-2317__control__r1 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-2317__skill__r1 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| requests-retry__control__r1 | 아니오 | 0 | 없음 | 아니오 | 0 | 0 | --no-skills --no-context-files |
| requests-retry__skill__r1 | workflow-define | 7 | AGENTS.md | 예 | 2 | 0 | 없음 |
| workflow-skill-fix__control__r1 | 아니오 | 0 | 없음 | 아니오 | 0 | 13 | --no-skills --no-context-files |
| workflow-skill-fix__skill__r1 | workflow-define | 7 | AGENTS.md, AGENTS.md | 예 | 7 | 1 | 없음 |

## 실행 기록 평균 (점수에 쓰지 않음, goal.md R6)

| 과제 | 팔 | 턴 | 라운드 | 입력 토큰 | 출력 토큰 | 캐시 읽기 | 추론 | 비용($) | 최대 컨텍스트 | 도구 호출 | 실패 호출 | 압축 | 재시도 | 걸린 시간(초) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| requests-2317 | control | 4.0 | 3.0 | 20071.0 | 3666.0 | 176512.0 | 1296.0 | 0.112 | 4.8% | 24.0 | 2.0 | 0.0 | 0.0 | 142.7 |
| requests-2317 | skill | 4.0 | 3.0 | 14167.0 | 3147.0 | 76928.0 | 515.0 | 0.075 | 4.7% | 15.0 | 0.0 | 0.0 | 0.0 | 106.3 |
| requests-retry | control | 4.0 | 3.0 | 60143.0 | 10028.0 | 715136.0 | 3428.0 | 0.364 | 11.1% | 40.0 | 2.0 | 0.0 | 0.0 | 323.8 |
| requests-retry | skill | 6.0 | 5.0 | 53223.0 | 6981.0 | 255744.0 | 822.0 | 0.227 | 9.7% | 14.0 | 1.0 | 0.0 | 0.0 | 234.2 |
| workflow-skill-fix | control | 6.0 | 5.0 | 81548.0 | 15005.0 | 1006336.0 | 3187.0 | 0.514 | 15.3% | 55.0 | 1.0 | 0.0 | 0.0 | 699.1 |
| workflow-skill-fix | skill | 6.0 | 5.0 | 18426.0 | 7144.0 | 162432.0 | 1350.0 | 0.141 | 6.1% | 19.0 | 0.0 | 0.0 | 0.0 | 246.2 |

## 참고 기록 (점수 아님)

| 회차 | 알려 준 사용자 사실 | 수락 결정 일치 | 찾을 수 있는 사실을 물음 | 모름 대답 | 모의 사용자 출력 보정 |
|---|---|---|---|---|---|
| requests-2317__control__r1 | U1, U2, U5, U6 | - | 0 | 0 | 0 |
| requests-2317__skill__r1 | U1, U2, U6 | - | 0 | 4 | 0 |
| requests-retry__control__r1 | U2, U3, U4, U5, U6 | - | 0 | 0 | 0 |
| requests-retry__skill__r1 | U2, U3, U4, U5, U6 | A2 | 0 | 6 | 0 |
| workflow-skill-fix__control__r1 | O1, U2, U4 | A1, A11, A4, A5, A9 | 0 | 2 | 0 |
| workflow-skill-fix__skill__r1 | O1, U1, U2, U4 | A1, A10, A12, A2, A3, A4, A5, A8 | 0 | 3 | 0 |

## 한계

- 심판은 후보와 같은 모델이다(goal.md C1). 자기 쪽에 후할 수 있다.
- 스킬 팔의 goal.md([합의] 등)와 질문 글(❓, ➡️)에는 흔적이 있어 심판에게 팔이 완전히 가려지지 않는다.
- 심판은 같은 입력에도 점수가 흔들린다(M1: 같은 goal.md 4회 호출에 루브릭 9~10점). 회차마다 1회만 부른다.
- 심판 입력에는 후보 글과 모의 사용자 대답이 함께 들어간다(2026-10-22 결정). 첫 메시지는 팔이 드러나지 않게 과제의 시작 요청으로 바꾼다.
- 공개 벤치마크(SWE-bench 이슈)는 모델이 외웠을 수 있다. 과제 3(workflow-skill-fix)은 비공개라 해당 없다.
- 과제 3의 스킬 팔은 시험 대상 스킬 자체가 그 과제의 결과물(스킬 7개)이라, 스킬을 읽으면 끝 모양을 볼 수 있다. M2에서 실제로 로드된 스킬을 고칠 대상으로 보고 "이미 됐다"고 적었다. 그래서 과제 3의 회수율·심판 사실 판정은 참고로만 보고, 과정 검사는 그대로 쓴다(2026-10-23 결정).
- 누출 검사는 회차 폴더 안(작업 폴더 + 설정 폴더) 읽기를 허용한다(2026-10-23 결정). 그 위·밖 경로와 쓰기는 오염 의심이다.
- 모의 사용자 대답 문장은 답변표의 문장을 이어 붙여 만든다. 모델은 어떤 사실로 대답할지만 고른다.
- 과제 3 작업 폴더의 옛 AGENTS.md는 스킬 팔에서 새 AGENTS.md와 함께 읽힌다(당시 조건). 이번 회차들: 작업 폴더 AGENTS.md 있음 2회.
