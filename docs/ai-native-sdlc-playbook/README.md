# The AI-native SDLC playbook (원본 보관)

Anthropic이 2026-08-21에 공개한 "The AI-native SDLC playbook" 원문을 보관하는 폴더다.
`intent.md`는 이 플레이북이 제안하는 첫 번째 산출물(artifact)이다. 독립된 문서가 아니라 플레이북 안의 한 플레이(Stage 1 Plan)이므로, 플레이북 전체를 원본으로 보관한다.

## 출처

- 원문: <https://claude.com/resources/articles/the-ai-native-sdlc-playbook>
  (블로그 주소 <https://claude.com/blog/the-ai-native-sdlc-playbook> 는 여기로 리다이렉트된다)
- 저자: Louis Claxton (Anthropic) · 2026-08-21 · 40분 분량
- 가져온 날짜: 2026-10-21

## 파일 구성

| 파일 | 내용 |
|---|---|
| `playbook.md` | 웹 원문을 Markdown으로 변환한 것. 본문, 코드 블록 13개, 표를 원문 그대로 담았다. frontmatter에 출처와 이미지 원본 URL이 있다 |
| `playbook.pdf` | Anthropic 공식 PDF (54쪽). 수정 없음 |
| `images/fig-01~04.png` | 본문 그림 4장 (assets.claude.com 원본) |

변환하면서 바꾼 것: 웹 전용 UI(Copy 버튼, 목차 앵커)는 제거했고, "Traditional / AI-native" 비교 박스와 "Getting started", "How to measure it" 박스는 굵은 라벨과 목록으로 바꿨다. 본문 안의 단계 이동 링크(`#sd-s1` 등)는 Markdown 제목 앵커(`#01-plan` 등)로 바꿨고, "Prefer a PDF?" 상자는 이 폴더의 `playbook.pdf`를 가리키게 했으며, 페이지 하단의 "Related articles"는 사이트 UI라서 넣지 않았다. 문장과 코드 블록은 손대지 않았다.

## intent.md란

- 아이디어를 낸 사람(originator)이 Claude와 브레인스토밍해서 "무엇을, 왜, 어떤 제약 아래서" 원하는지 자기 말로 적은 proto-spec이다. proto-spec은 정식 설계서(spec) 이전 단계의 요구 메모를 뜻한다.
- 해결책이 아니라 문제를 담는다. 구성은 문제(Problem) → 기대 결과(Proposed outcome) → 영향받는 사용자와 시스템 → 제약(Constraints) → 열린 질문(Open questions) 순이다.
- git에 커밋해 두고 product owner가 검토, 승인하면 다음 단계(`spec.md`)로 넘어간다. 커밋 이력 자체가 감사 기록(audit trail)이 된다.
- 주의: `CLAUDE.md`처럼 Claude Code가 자동으로 읽는 파일이 아니다. 팀이 합의해서 쓰는 워크플로 산출물이다.

## playbook.md에서 intent.md가 나오는 곳

| 섹션 | 줄 | 내용 |
|---|---|---|
| The shifts across the six stages (표) | 80, 85, 87 | Plan 행과 Maintain 행, 그리고 단계마다 커밋되는 산출물 체인(intent → spec → plan → diff → PR) |
| 01 Plan › Capture as intent.md | 115~178 | 핵심 플레이. 실행 5단계, 예시 intent.md, 거버넌스, 측정 지표(leading: 첫 대화에서 커밋까지 시간, lagging: product owner가 승인한 비율) |
| 02 Design › Requirements and design | 203~222 | `intent.md`를 첨부해 `spec.md`를 만들고, 둘을 쌍으로 커밋한다. 지표는 intent 커밋과 spec 커밋 사이 시간 |
| 03 Build › Claude Code plan mode | 239~255 | `intent.md` + `spec.md` → `plan.md`. 예시 plan.md 헤더가 "(from intent.md 2026-06-02)" |
| 03 Build › Legacy systems and the source of truth (사이드바) | 289~303 | intent 저장소(intent home)와 Jira 같은 기존 시스템 중 어느 쪽을 source of truth로 둘지. Plan 섹션에서 참조한다 |
| 06 Maintain › Closing the loop | 810~861 | 모니터링에서 잡힌 이상을 새 `intent.md`로 써서 Stage 1부터 다시 돌린다 |
| 06 Maintain › Recurring codebase scans | 884, 894 | 스캔 결과가 패치 하나보다 크면 `intent.md`로 작성해 Plan에서 시작한다 |

## 주의

- 151~169줄의 `# Intent: claims status self-service` 블록은 공식 템플릿이 아니라 플레이북의 **예시**다. 플레이북은 "조직이 합의한 intent.md 템플릿"을 전제할 뿐, 템플릿 자체는 제공하지 않는다.
