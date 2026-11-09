---
name: workflow-worktree
description: 사용자가 직접 불러, 지금 하던 goal 작업을 원래 폴더에서 옆 worktree로 옮겨 같은 세션에서 이어 하고, 끝나면 로컬 merge로 합치고 정리한다.
argument-hint: "<goal>"
disable-model-invocation: true
---

# Worktree

사용자 전용이다. AI는 이 skill을 먼저 부르거나 제안하지 않는다.
사용자가 부르는 것 자체가 지시다. 부르면 옮기거나 끝낸다.

worktree는 브랜치마다 따로 꺼낸 작업 폴더다. 이 skill은 goal 하나를 `../<저장소 폴더 이름>-<goal>` 폴더와 `goal/<goal>` 브랜치로 옮긴다.
그동안 원래 폴더는 다른 goal에 쓸 수 있다. 끝나면 원래 폴더의 브랜치에 `--no-ff`로 merge하고 worktree와 브랜치를 지운다. push는 하지 않는다.

## script

이 SKILL.md와 같은 폴더의 `worktree.py`가 검사와 순서를 모두 맡는다. 명령은 세 개다.

```
python3 <이 skill 폴더>/worktree.py status <goal> --json   # 다음 할 일. 아무것도 바꾸지 않는다
python3 <이 skill 폴더>/worktree.py create <goal> --json   # 만들기
python3 <이 skill 폴더>/worktree.py finish <goal> --json   # 끝내기. 원래 폴더에서만
```

- python3 3.9 이상과 git 2.38 이상이 필요하다(merge 미리보기 `git merge-tree --write-tree`)
- 저장소 안 어디서든 부른다. script가 원래 폴더와 worktree를 스스로 찾는다
- 종료 코드: 0 성공 · 2 멈춤(`stops`에 code와 이유) · 1 script 오류(`error`)
- 멈추면 그 단계는 아무것도 바꾸지 않았다. 끝내기의 `remove-refused`·`remove-incomplete`는 merge와 항목 되돌리기가 끝난 뒤에 날 수 있고, 다시 부르면 끝난 단계는 건너뛴다. `remove-incomplete`는 지울 수 있던 것은 이미 지운 상태다
- worktree 세션 안에서 원래 폴더 쪽 `worktree.py` 실행이 막히면, worktree 안의 같은 경로 파일을 실행한다. 저장소에 들어 있는 skill이면 worktree에도 같은 파일이 있다

## goal 고르기

goal은 `.goal/<goal>/` 폴더 이름과 같다. 사용자가 적었거나 지금 대화가 다루는 goal이 하나면 그것을 쓴다.
어느 goal인지 알 수 없을 때만 묻는다.

## 다음 할 일

`status <goal> --json`을 부르고 `action`대로 한다.

| `action` | 상황 | 할 일 |
| --- | --- | --- |
| `create` | 이 goal의 영수증이 없다 | 아래 "만들기" |
| `finish` | 이 skill이 만든 worktree 안에서 불렀다 | 아래 "끝내기" |
| `reenter` | 만든 뒤 원래 폴더에서 다시 불렀다(세션이 끊김 등) | 세션을 `worktree`로 옮겨 작업을 이어 한다. 사용자가 끝내기라고 했으면 끝내기 ③부터 한다 |
| `continue-finish` | 끝내기가 도중에 멈췄다 | 원래 폴더면 `finish`를 다시 부른다. worktree 안이면 끝내기 ①부터 한다 |
| `stop` | 시작할 수 없다 | `stops`의 code로 해결 표를 찾는다 |

## 만들기

### 1. 구분

script는 git이 추적하지 않는 항목을 모아 목록 파일과 대조한다. 목록에 없는 항목은 `status`의 `unlisted`에 기본값과 함께 나온다.
기본값: 무시되지 않은 새 파일은 `git`, gitignore된 것은 `skip`.

`unlisted` 항목마다 세 질문으로 방식을 고른다.

1. worktree에서 고치나
2. 고친 것을 원래 폴더로 돌려줘야 하나
3. 그동안 원래 폴더에서도 고치나

| 방식 | 언제 | 만들 때 | 끝낼 때 |
| --- | --- | --- | --- |
| `git` | 이 goal의 작업물이고 커밋한다 | 미커밋 변경과 함께 worktree로 옮긴다 | 커밋 → merge |
| `link` | worktree에서 고치지 않는다 | 원래 폴더 항목을 가리키는 링크 | 링크를 지운다 |
| `copy` | 고치지만 돌려주지 않는다 | 복사 | 버리고, 바뀐 채로 버린 파일을 보고한다 |
| `sync` | 고쳐서 돌려주고, 원래 폴더도 그동안 고친다 | 복사하고 파일마다 시작 지문을 적는다 | 파일마다 3-way. 한쪽만 바뀐 파일은 그쪽을 따르고, 양쪽이 다르게 바뀌면 멈춘다 |
| `sync-empty` | `sync`인데 새로 생긴 것만 돌려준다(결과 폴더 등) | 빈 폴더로 시작 | 새로 생긴 것만 돌려준다. 같은 이름이 양쪽에 생기면 멈춘다 |
| `move` | 이 goal만 고친다 | 원래 폴더에서 옮긴다 | 되돌려 옮긴다. 같은 이름이 있으면 멈춘다 |
| `skip` | 다시 만들 수 있다(가상 환경·캐시) | 가져가지 않는다. 필요하면 준비 명령 | worktree와 함께 지운다. worktree 안의 gitignore된 파일도 이때 말없이 지워진다 |

기본값과 같게 구분했으면 묻지 않는다.
기본값과 다르게 구분한 항목이 있을 때만 `항목 · 기본값 · 고른 방식 · 이유` 표로 보이고 확인받는다.
확인되면 목록 파일에 적고 `status`를 다시 불러 `unlisted`가 기대와 같은지 본다.

### 2. 목록 파일 `.workflow-worktree`

저장소 맨 위의 추적 파일이다. 한 줄에 `<방식> <경로>` 하나.

```
# 주석과 빈 줄은 무시한다
link docs
move .goal/{goal}
link .goal/*
sync tools
sync-empty tools/results
skip **/__pycache__
setup cd tools && make deps
```

- 경로는 저장소 맨 위 기준. `{goal}` = goal 이름, `*` = 정확히 한 단계, `**` = 0단계 이상
- 경로마다 가장 구체적인 줄이 이긴다: 더 깊은 곳에서 맞는 줄 → 글자 그대로인 단계가 많은 줄 → 뒤에 적은 줄
  - 예: `.goal/goal-x`는 `move .goal/{goal}`을, `.goal/other`는 `link .goal/*`를 따른다. `tools/x/__pycache__`는 `skip`을 따른다
- `setup <명령>`은 만들기 끝에 worktree 안에서 실행한다. 실패해도 만들기는 성공하고 실패를 보고한다. 명령의 출력은 stderr로 나온다
- 목록 파일을 아직 커밋하지 않았으면, 목록 파일 자신도 새 파일로 worktree에 옮겨진다. worktree에서 커밋하면 끝낼 때 merge로 돌아온다

### 3. 만들고 옮기기

`create <goal> --json`을 부른다. 출력에서 `worktree`, `moved_by_git`(옮긴 미커밋 변경), `items`, `missing`(목록에 있지만 지금 없는 항목), `setup` 결과를 사용자에게 짧게 보인다.
그다음 아래 "세션 옮기기"로 세션을 `worktree`로 옮긴다.

옮긴 뒤에도 세션은 처음 읽은 skill·AGENTS.md를 쓴다. worktree에서 고친 skill을 써 보려면 worktree 폴더에서 새 세션을 연다.

## 끝내기

1. worktree 안에서 `status`의 `uncommitted`를 본다. 목록 항목은 빠져 있다. 남은 미커밋 작업이 있으면 끝내기 전에 커밋한다. 커밋 규칙은 그 저장소 지침을 따른다
2. 세션을 원래 폴더로 옮긴다(아래 "세션 옮기기"). worktree는 남겨 둔다
3. 원래 폴더에서 `finish <goal> --json`을 부른다. script가 멈춤 조건을 모두 먼저 검사한 뒤 merge → 항목 되돌리기 → worktree 지우기 → 브랜치 지우기 순서로 한다
4. `merge_commit`, `synced`(sync로 돌려준 파일), `copy_changed`(바뀐 채로 버린 사본), `removed`를 사용자에게 짧게 보인다

worktree 안에서 `finish`를 부르면 `run-from-main`으로 멈춘다. 원래 폴더에서만 부른다.

## 세션 옮기기

도구에 세션 작업 폴더를 바꾸는 기능이 있으면 그것으로 옮긴다. 없으면 대상 폴더에서 새 세션을 연다.

| 도구 | worktree로 들어가기 | 원래 폴더로 나오기 |
| --- | --- | --- |
| Claude Code | AI가 `EnterWorktree(path=<worktree>)` | AI가 `ExitWorktree(action="keep")` |
| Codex | 사용자가 턴 사이에 `/cd <worktree>` 입력 | 사용자가 `/cd <원래 폴더>` 입력 |
| 기능이 없는 도구 | 사용자가 `<worktree>`에서 새 세션을 연다 | 사용자가 원래 폴더에서 새 세션을 연다 |

사용자가 입력해야 하는 경우, AI는 입력할 내용을 그대로 보이고 기다린다. 옮겨지면 하던 단계를 이어 한다.
새 세션을 여는 경우는 다음과 같이 안내한다.
- 만들기 뒤 worktree에서 연 새 세션: 이 skill을 다시 부르지 않고 작업을 이어 한다. worktree 안에서 이 skill을 부르면 끝내기가 시작된다
- 끝내기 ① 뒤 원래 폴더에서 연 새 세션: 이 skill을 "끝내기"라고 함께 적어 부른다. `status`는 `reenter`를 내지만 끝내기 ③부터 한다

worktree 세션 안에서는 원래 폴더의 파일을 링크로 고치거나 원래 폴더를 대상으로 git 명령을 쓰지 않는다. 원래 폴더의 일은 세션을 옮긴 뒤 한다.

## 멈췄을 때

멈추면 code와 `paths`를 사용자에게 보이고, 아래 표의 선택지로 해결 방법을 함께 정한다.
해결한 뒤 같은 명령을 다시 부른다. script는 처음부터 다시 검사하고 이미 끝난 단계는 건너뛴다.
`--force`, 브랜치 강제 삭제, 원래 폴더 작업의 stash·되돌리기는 하지 않는다.

| code | 뜻 | 해결 선택지 |
| --- | --- | --- |
| `not-git-repo` | git 저장소 안이 아니다 | 저장소 안에서 다시 부른다. 저장소가 아니면 이 skill을 쓸 수 없다 |
| `goal-invalid` | goal 이름을 브랜치·폴더 이름으로 쓸 수 없다 | `.goal/` 폴더 이름과 맞는 다른 이름을 사용자와 정한다 |
| `branch-exists` | `goal/<goal>` 브랜치가 이미 있다 | 다른 goal 이름을 쓰거나, 그 브랜치를 어떻게 할지 사용자가 정한다. AI가 지우지 않는다 |
| `folder-exists` | `../<저장소 폴더 이름>-<goal>` 폴더가 이미 있다 | 다른 goal 이름을 쓰거나, 그 폴더를 어떻게 할지 사용자가 정한다. AI가 지우지 않는다 |
| `git-busy` | 원래 폴더에서 merge·rebase·cherry-pick·revert가 진행 중이다 | 그 작업을 먼저 끝내거나 그만둘지 사용자가 정한다 |
| `list-invalid` | 목록 파일에 잘못된 줄이 있다(`lines`) | 그 줄을 사용자와 고친다 |
| `worktree-dirty` | worktree에 목록 항목이 아닌 미커밋 작업이 있다 | worktree에서 커밋하고 다시 부른다. 버릴 작업인지는 사용자가 정한다 |
| `base-moved` | 원래 폴더가 만들 때와 다른 브랜치에 있다 | 원래 폴더를 만들 때 브랜치로 돌려놓을 수 있을 때 다시 부른다. 다른 세션이 쓰는 중일 수 있으니 사용자가 정한다 |
| `sync-conflict` | sync 항목에서 양쪽이 다르게 바뀐 파일이 있다(`paths`) | 파일마다 어느 쪽을 남길지 사용자와 정해 한쪽을 다른 쪽과 같게 맞춘 뒤 다시 부른다 |
| `move-target-exists` | move를 되돌릴 자리에 같은 이름이 있다 | 원래 폴더의 그 항목을 어떻게 할지(이름 바꾸기·합치기) 사용자와 정한다. 지우지 않는다 |
| `merge-conflict` | merge 미리보기에서 충돌이 난다 | 세션을 worktree로 옮겨 그 안에서 원래 브랜치를 먼저 merge하고, 충돌을 사용자와 풀어 커밋한다. 원래 폴더로 나와 다시 부른다 |
| `main-dirty-overlap` | 원래 폴더의 미커밋 변경이 merge와 겹쳐 git이 거부했다 | 그 변경은 다른 세션이나 사용자의 작업일 수 있다. AI가 stash하거나 되돌리지 않는다. 주인이 커밋하거나 정리한 뒤 다시 부른다 |
| `remove-refused` | worktree를 지우려는데 예상 못 한 파일이 남았다 | 남은 파일을 보이고, 옮길지 지울지 사용자와 정해 치운 뒤 다시 부른다. merge는 다시 하지 않는다 |
| `remove-incomplete` | worktree를 지우다 도중에 실패해 파일이 남았다(`paths`). 어떤 프로세스가 연 파일(NFS의 `.nfs*`)이나 권한 때문이다 | 그 파일을 연 프로세스를 사용자와 찾아(`lsof <파일>`, `fuser -v <파일>`) 끄거나 권한을 고친다. 메시지가 "git 등록은 지워졌다"면 그 폴더는 더 이상 저장소가 아니다. 사용자 확인을 받아 남은 폴더를 지운다. 그다음 다시 부른다. merge는 다시 하지 않는다 |
| `run-from-main` | `finish`를 worktree 안에서 불렀다 | 세션을 원래 폴더로 옮긴 뒤 부른다 |
| `receipt-invalid` | 영수증을 읽을 수 없다 | 영수증 경로와 내용을 보이고 어떻게 할지 사용자가 정한다 |
| `worktree-missing` | 영수증은 있는데 worktree 폴더가 없다 | 누가 왜 지웠는지 사용자에게 확인하고 정리 방법을 정한다 |
| `create-incomplete` | 만들기가 도중에 멈췄다(`done`) | 끝난 단계를 사용자에게 보이고 정리 방법을 정한다 |
| `foreign-worktree` | 이 goal을 위해 이 skill이 만든 worktree가 아닌 곳에서 불렀다 | 세션을 원래 폴더로 옮겨 다시 부른다. 다른 goal의 worktree라면 goal 이름을 사용자와 확인한다 |
| `receipt-missing` | 영수증 없이 `finish`를 불렀다 | 이 skill로 만든 worktree가 아니거나 이미 끝냈다. `status`로 다음 할 일을 다시 본다 |

영수증은 `<git 공용 폴더>/workflow-worktree/<goal>.json`이다. 이 컴퓨터의 진행 상태라서 커밋되지 않는다.
