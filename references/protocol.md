# Claude Codex Teamflow Protocol

## Roles

- Claude Code Opus: team lead, planner, reviewer, final approver.
- Codex: full-stack implementation team and QA engineer.
- User: product owner and authority for scope, commits, destructive actions, and production access.

## State Machine

1. `PLAN_READY`: Claude or the user provides a concrete plan.
2. `IMPLEMENTING`: Codex makes changes and runs QA.
3. `READY_FOR_REVIEW`: Codex writes a review packet.
4. `CHANGES_REQUESTED`: Claude returns concrete modifications; Codex loops back to implementation.
5. `BLOCKED`: Claude identifies a blocker that needs user input or external access.
6. `APPROVED`: Claude says `APPROVED` or `LGTM`; Codex may proceed to commit only if the user granted commit permission.

## Review Packet

Every Claude review request must include:

- Goal: one paragraph.
- Plan source: file path or quoted plan summary.
- Changed files: grouped by subsystem.
- Diff summary: behavior-level, not a raw patch dump.
- QA evidence: commands, pass/fail result, and skipped checks.
- Risk notes: known risks, migrations, data changes, or user-visible changes.
- Questions: only blockers that Codex could not resolve from the repo.

## Claude Response Contract

Claude should respond with exactly one status line:

```text
STATUS: APPROVED
```

or:

```text
STATUS: LGTM
```

or:

```text
STATUS: CHANGES_REQUESTED
```

or:

```text
STATUS: BLOCKED
```

For `CHANGES_REQUESTED`, Claude must list required fixes as actionable bullets. For `BLOCKED`, Claude must name the missing decision, access, or evidence.

## Approval Rules

- Passing tests does not equal approval.
- A friendly review summary does not equal approval unless it includes `APPROVED` or `LGTM`.
- Codex must repeat implementation and QA after every `CHANGES_REQUESTED` response.
- Codex stops after `max-review-rounds` and reports unresolved review items.
