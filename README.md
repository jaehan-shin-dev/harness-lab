# assets/ — 외부 스킬 모음과 가이드 원본 보관

연구와 비교용으로 받아 둔 외부 자료다. 설치용이 아니라 참고용이며, 파일은 업스트림 그대로 두고 수정하지 않는다.

## 복사 규칙

- 스킬 모음은 `SKILL.md`가 있는 디렉터리만 복사했다. 업스트림의 스킬 루트(`skills/` 또는 저장소 루트) 기준 상대 경로를 그대로 유지했다.
- 저장소 스캐폴딩(테스트, 빌드 스크립트, 라이브러리 코드, CI 설정)은 복사하지 않았다.
- 2026-10-21에 추가한 다섯 폴더(superpowers, gstack, addy-osmani-skills, pstack, claude-feature-dev)에는 업스트림의 `README.md`와 라이선스 파일을 함께 넣었다. matt-skills에는 없다.
- 라이선스: superpowers(Jesse Vincent), gstack(Garry Tan), addy-osmani-skills(Addy Osmani), pstack(Lauren Tan)은 MIT. claude-feature-dev의 `LICENSE.md`는 MIT가 아니라 "© Anthropic PBC. All rights reserved"이며 Anthropic Commercial Terms of Service를 따른다. 재배포 전에 확인할 것.
- 가져온 날짜: 2026-10-21 (matt-skills만 2026-10-19).

## 목록

| 폴더 | 출처 | 커밋 (날짜) | SKILL.md 수 | 비고 |
|---|---|---|---|---|
| `matt-skills/` | [mattpocock/skills](https://github.com/mattpocock/skills) | 5beb35b (2026-10-19) 기준으로 내용 동일 확인 | 27 | 업스트림 `skills/engineering/`, `skills/productivity/`를 평탄화한 것. 업스트림에는 `in-progress/`, `misc/`에 11개가 더 있다(chief-of-staff, claude-handoff, loop-me, setup-ts-deep-modules, writing-beats, writing-fragments, writing-shape, git-guardrails-claude-code, migrate-to-shoehorn, scaffold-exercises, setup-pre-commit). 받지 않았다 |
| `superpowers/` | [obra/superpowers](https://github.com/obra/superpowers) | b739a8af570e10a95898f2bdf6cec97467fa6c12 (2026-10-20) | 15 | 업스트림 `skills/` 전부. 세션 시작 시 `using-superpowers`를 주입하는 `hooks/`는 복사하지 않았다 |
| `gstack/` | [garrytan/gstack](https://github.com/garrytan/gstack) | b616d6c53dd8fc0d8db210444b44a131b553b83e (2026-10-20) | 63 | 스킬 루트가 저장소 루트라서 최상위 스킬 디렉터리 56개 + 루트 `SKILL.md`(디스패처) + 중첩 6개(`browser-skills/`, `capy/`, `openclaw/`). 스킬이 호출하는 `bin/`, `lib/`(TypeScript, Playwright 브라우저)는 복사하지 않았으므로 그대로 실행되지 않는다 |
| `addy-osmani-skills/` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | aeac41d4d005999432bb7312f7ff06383a91d59d (2026-10-13) | 25 | 업스트림 `skills/` 전부. `commands/`, `agents/`, `hooks/`는 복사하지 않았다 |
| `pstack/` | [cursor/plugins › pstack](https://github.com/cursor/plugins/tree/main/pstack) (Lauren Tan, poteto) | 190d28736eff128ec94f502a22c7fe0c4b56cd37 (2026-10-20) | 59 | Cursor 플러그인 원본. `skills/` 56개 + `automations/benny/skills/` 3개 + `reflect` 스킬이 참조하는 `agents/`. `skills/poteto-mode/scripts/watch-pr/watch-pr`는 업스트림이 실행 권한을 붙여 배포하는 bun 스크립트다(여기서 만든 것 아님, 실행하지 않음). Claude Code·Codex·Pi용 포팅본 [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude)가 따로 있으나 스킬 구성이 갈라져(65개) 받지 않았다 |
| `claude-feature-dev/` | [anthropics/claude-code › plugins/feature-dev](https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev) | d014fc0fa64280540728772fc84063918ed185cc (2026-10-21) | 0 | Anthropic 공식 플러그인. `SKILL.md` 없이 `commands/feature-dev.md`와 `agents/`(code-explorer, code-architect, code-reviewer)로 구성되므로 플러그인 폴더 전체를 복사했다. 라이선스는 저장소 루트 `LICENSE.md`(All rights reserved, MIT 아님) |
| `ai-native-sdlc-playbook/` | [The AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook) (Anthropic) | 2026-08-21 게시 | - | `intent.md`가 나오는 플레이북 원문(Markdown 변환본, 공식 PDF, 그림). 자세한 건 폴더 안 README |
