---
name: workflow-plan
description: Break goal.md into a set of tracer-bullet tickets, each declaring its blocking edges, written as one file per ticket. Use for the Plan phase.
disable-model-invocation: true
---

# Plan

Break `goal.md` into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

## Process

### 1. Gather context

Work from `.goal/<goal>/goal.md`: read it in full. Do not interview the user. If a ticket would need a decision goal.md does not record, stop and tell the user to return to Define and update goal.md.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

Give each ticket an **Owner**: `main` when doing it directly is quicker, `subagent` when it can run alongside other tickets or needs enough reading to weigh down the main session, `HITL` when the user does it or does it with you.

Mark a ticket **Parallel: yes** only when it can finish on its own and touches no file another ticket touches.

Give each ticket **Checks**, each one a condition and how to check it. A ticket that changes code writes its Checks as tests at the seams goal.md's Evaluation names.

Every requirement in goal.md is covered by at least one ticket; list them under **Covers**.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work
- **Owner**: main, subagent, or HITL

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Write the tickets

Write the approved tickets.

Write one file per ticket under `.goal/<goal>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Covers:** the goal.md requirements this ticket serves.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Files:** the files this ticket changes.

**Owner:** main | subagent | HITL

**Parallel:** yes | no

**Status:** ready

**Checks:**

- [ ] <condition>: <how to check>
- [ ] <condition>: <how to check>

</local-ticket-template>

Avoid code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

Done when the user has approved the breakdown and every ticket file has Checks, or "No checks needed" with the reason.
