# workflow-analysis 인계

## 의도와 멈춘 지점

사용자의 생각에서 출발하고 반응에 따라 설명·문제 해석을 수정하도록 `workflow-analysis`를 개선하는 작업이다. 목표·요구사항·평가 기준·Q1~Q4 합의는 [goal.md](goal.md), 정확한 32줄 확정 문구와 diff는 [change-proposal.md](change-proposal.md)를 따른다. 여기서 복제하거나 다시 정의하지 않는다.

Define은 완료했다. 사용자가 `$workflow-plan`을 호출한 뒤 아래 티켓 구성을 제안했고, **아직 승인받지 않은 상태에서 handoff를 요청했다. 현재 재개 지점은 Plan 구성 승인 대기다.** `tickets/`와 Plan 완료 커밋은 없다. 실제 스킬 적용과 대화 비교도 하지 않았다.

재개 첫 행동은 아래 구성을 짧게 다시 보여 주고 티켓 크기·의존관계·병합/분할에 대한 승인이나 수정을 받는 것이다. 승인 후에만 `workflow-plan`으로 티켓 파일을 작성한다. Execute로 자동 진행하지 않는다.

## 미승인 4개 티켓 제안

이 제안은 아직 다른 산출물에 없으므로 여기 보존한다.

| 번호 | 티켓 | Blocked by | Owner | 범위 |
|---|---|---|---|---|
| 01 | 확정 문구 적용과 문구 검토 | 없음 | main | 확정 32줄 적용, R/C 문구 검토, 비교할 기존·수정 버전과 검증용 입력 보존. |
| 02 | 이미 준 정보 활용과 마무리 확인 — S1 | 01 | subagent | 충분한 입력 활용, 현재 이해와 남은 의문 기록, 사용자 이해·동의의 임의 확정 및 Define 자동 진행 여부 비교. |
| 03 | 반론 이후 설명 수정 확인 — S2 | 01 | subagent | 반론·새 정보 후 설명·문제 해석 수정과 근거 설명 비교. |
| 04 | 사실 조사와 근거 설명 확인 — S3 | 01 | subagent | AI 직접 자료 확인, 사실·해석·불확실성 구분 비교. |

02~04는 병렬 가능하며 서로 다른 증거 폴더에 기록하는 구상이다. 같은 모델·입력·도구 조건, 별도 세션에서 기존·수정 스킬을 비교하고 원본 응답·도구 기록·항목별 판정을 남긴다. 구체적인 발화·고정 자료·실행 수단·증거 파일 구성은 Plan에서 정한다. 최종 판정은 별도의 Verify 단계다. **이 구성과 분담은 미승인이다.**

## 디스크와 git 상태

- 브랜치 `main`. 이 작업의 커밋: `501e65e`(Analysis 기록) → `323a684`(분석 HTML) → `170bb9f`(goal.md) → `ebbf42a`(확정 변경 문구). 인계 문서 작성 전 기준 HEAD는 `ebbf42a`다. 이 문서를 담은 `wip:` 커밋이 인계 체크포인트다.
- 실제 `.agents/skills/workflow-analysis/SKILL.md`는 적용 전이다. 인계 전 메인 세션에서 원본 SHA-256이 `change-proposal.md`의 기준 해시와 일치하고 `tickets/`가 없음을 확인했다.
- 인계 전 이 작업에는 미커밋 변경이 없었다. 이번 체크포인트에는 이 `handoff.md`만 추가하며, 다른 작업의 변경은 포함하지 않는다.
- 실행 중 하위 에이전트는 없다. 이전 `analysis_eval_options`는 완료 상태다.
- 전체 트리는 다른 작업의 기존 변경 때문에 깨끗하지 않다. 아래 파일은 수정·스테이지·커밋하지 않는다.
  - 수정됨: `.goal/workflow-handoff/plan.md`
  - 미추적: `.goal/workflow-handoff/c1-table.md`, `.goal/workflow-handoff/trial-kit.md`, `.goal/workflow-handoff/trial-untracked.txt`, `.goal/workflow-handoff/verify.md`, `.goal/workflow-intent/handoff.md`, `.goal/workflow-skill-fix-3/handoff.md`

## 검증 범위와 주의사항

문서 확정과 원문 미적용 상태를 확인했을 뿐 실제 행동 검증은 없다. **행동 개선을 PASS로 기록하면 안 된다.** 기존 skill-eval의 Define용 한계와 근거는 [goal.md](goal.md)의 ‘검증 수단에 대해 확인한 사실’을 참조한다. 새 평가 프레임워크나 runner 확장은 범위 밖이다.

앞선 Plan 준비에서 `/opt/homebrew/bin/pi`가 설치되어 있고 `pi --help`에 `--mode json`, `--print`, `--session-id`/`--session-dir`, `--no-context-files`, `--no-skills`, `--no-extensions`, `--no-mcp`, `--append-system-prompt`가 있음을 확인했다. 도움말 재조사는 필요 없다. 도움말 실행도 홈의 `.pi/agent/trust.json.lock` 접근으로 샌드박스 EPERM이 발생해 승인 후 완료했다. **도움말 승인은 실제 모델 실행 권한·인증 확인과 별개다.** 실제 인증·모델 가용성·API 호출은 검증하지 않았고 모델 호출도 하지 않았다.

[pi.py](../../skill-eval/skilleval/drivers/pi.py), [pi_process.py](../../skill-eval/skilleval/pi_process.py), [events.py](../../skill-eval/skilleval/events.py), [config.yaml](../../skill-eval/config.yaml)은 실행·원본 기록 방법의 참고로 읽었다. 사용자는 쉬운 한국어(ELI10)를 선호하며 Aside 스킬은 사용하지 말라고 했다. 분석 HTML은 이미 있어 재생성할 필요 없다. 수정 대상인 `.agents/skills/`는 환경에서 읽기 전용으로 보호될 수 있으므로 실제 수정 시 도구의 권한 절차를 따른다.

## 핵심 파일과 다음 행동

- [AGENTS.md](../../AGENTS.md): 사용자가 요청할 때만 단계 전환. 단계 완료 시 해당 변경만 커밋한다.
- [goal.md](goal.md): 목표·범위·합의·Evaluation의 기준.
- [change-proposal.md](change-proposal.md): 적용할 정확한 문구·기준 원문 해시·diff.
- [analysis.md](analysis.md), [analysis.html](analysis.html): 완료된 분석과 참고 예시.
- [실제 스킬 원문](../../.agents/skills/workflow-analysis/SKILL.md): 아직 적용 전인 대상.

구성 승인 → workflow-plan으로 티켓 작성·Plan 완료 조건 확인·커밋이 다음 순서다. 실제 적용·비교·최종 검증은 이후 사용자 요청에 따라 진행한다.

## suggested skills

- `workflow-plan`: 재개 직후 사용. 먼저 미승인 구성을 확인받고 승인 후 티켓 작성을 이어 간다.
- `workflow-execute`, `workflow-verify`: 이후 사용자가 해당 단계를 요청할 때 사용한다.
- `workflow-define`: 새로운 사정으로 목표나 확정 범위를 바꿔야 할 때만 사용한다.

## How to resume

**You own the resume point. Read the prior trail, don't redo it.**

1. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
2. Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative.
3. Route the remaining work to the suggested skills above. The pickup ends here. The routed skill owns the rest.
4. Verify the inherited claims against the original goal on the real artifact. A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
