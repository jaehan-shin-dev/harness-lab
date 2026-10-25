## Workflow

Follow a dynamic workflow based on task requirements.

- Analysis: Understand the problem.
- Define: Specify goals and evaluation criteria.
- Plan: Design the execution process and its evaluation.
- Execute: Perform tasks, check progress, and adapt.
- Verify: Validate goal achievement with evidence.

### Principles
- Execute only necessary phases.
- Skip phases when their objectives are already satisfied.
- Revisit earlier phases when necessary.
- Verify outcomes using objective evidence.
- Proceed to another phase only when the user asks.

### Working documents
Keep working documents under `.goal/<goal>/` in the current working directory.
Each phase leaves its document there: `analysis.md`, `goal.md`, `tickets/`, `verify.md`.
Reuse the goal folder name agreed with the user; if the target is unclear, confirm it first.

### Commits
Commit when a phase meets its end condition: Analysis, Define, Plan, each ticket in Execute, and Verify. Do not ask first.
Stage only the files that phase changed (`git add <files>`, never `-A`). Do not commit mid-Round in Define or Plan.
If the directory is not a git repository, skip committing and say so.
Message: `<phase>(<goal>): <summary>`, for example `define(workflow-skill-fix-3): goal.md` or `execute(workflow-skill-fix-3): 03 <ticket title>`.
