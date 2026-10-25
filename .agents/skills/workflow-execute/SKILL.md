---
name: workflow-execute
description: Implement the tickets from the Plan phase, with the main session as orchestrator. Use for the Execute phase.
disable-model-invocation: true
---

You have been provided a goal: `.goal/<goal>/goal.md`. This goal should have tickets associated with it under `.goal/<goal>/tickets/`, describing how to implement the goal.

The aim is the entire goal implemented on the current branch, with every ticket marked done in its file.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to goal.md, the ticket file, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

You are the **orchestrator**: you pick the next tickets, hand them out, record their status, and commit them.

Work each ticket by its **Owner**: do `main` tickets yourself, give `subagent` tickets to implementer subagents, and work `HITL` tickets with the user, asking for what they need to do and checking the result. When a `main` ticket changes code, call the Skill tool with `tdd` to build it.

Run tickets at the same time only when they are on the frontier and marked **Parallel: yes**; run the rest one at a time.

## Steps

1. Read goal.md and the tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Use **implementer subagents** to implement each `subagent` ticket. Each implementer subagent:
   - calls the Skill tool with `tdd` to build the ticket when the ticket changes code;
   - changes only its ticket's Files, and reports anything it notices outside them instead of fixing it;
   - runs its ticket's Checks and reports the evidence, without committing.

4. Once a ticket completes, check the evidence for its Checks, write its status and Check results into the ticket file, and commit only the ticket's Files and the ticket file.

5. If this changes the **frontier** of available tickets, start the newly available tickets. This allows for maximum concurrency.

6. Report each ticket's status and Check results, and anything implementers reported outside their Files.

If a ticket turns out wrong, fix the ticket files yourself when no user decision is involved; otherwise stop and tell the user to return to Define and update goal.md.

Done when every ticket file shows done, incomplete, or blocked, with its Check results.
