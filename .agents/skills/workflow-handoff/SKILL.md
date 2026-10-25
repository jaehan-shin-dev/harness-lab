---
name: workflow-handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to `.goal/<goal>/handoff.md`, overwriting any previous one.

**You own a clean stop. Leave a checkpoint a cold-start agent can resume from.**

1. Stop at a safe boundary. Finish the current atomic step or back out of it. Start nothing new, and cancel any nested subagents.
2. Take no irreversible action to pause. No PR and no push unless you already had one out.
3. Make the work durable. Commit uncommitted edits as one clear `wip:` commit on the current branch so nothing is lost, staging only the files you changed (`git add <files>`, never `-A`). If the tree is broken, say so in the commit body in one line.
4. Write the handoff document off-context. Capture intent, what you were doing, the decisions made and why, progress and what's verified, current state, next steps, key files, and gotchas.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (`goal.md`, `plan.md`, specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

End the document with the "How to resume" section below, copied verbatim.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

**Reply:** where you are in the loop, what's on disk versus still in your head (paths, no diff dumps), the commits you made and whether the tree is clean, and the first action on resume. This is a pause, not a final report. End the reply with the line the user pastes into the new session: `Read .goal/<goal>/handoff.md and continue.`

```markdown
## How to resume

**You own the resume point. Read the prior trail, don't redo it.**

1. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
2. Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative.
3. Route the remaining work to the suggested skills above. The pickup ends here. The routed skill owns the rest.
4. Verify the inherited claims against the original goal on the real artifact. A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
```
