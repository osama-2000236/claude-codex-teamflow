# Teamflow Protocol

## Roles

- Claude Code Opus — team lead, planner, reviewer, final approver.
- Codex — implementation and QA.
- User — scope, commit authority, destructive actions, prod access.

## States

1. `PLAN_READY` — Claude or user supplies concrete plan.
2. `IMPLEMENTING` — Codex edits + runs QA.
3. `READY_FOR_REVIEW` — Codex publishes review packet.
4. `CHANGES_REQUESTED` — Claude returns concrete fixes; loop to (2).
5. `BLOCKED` — Claude flags missing decision/access; halt + surface.
6. `APPROVED` — Claude said `APPROVED` or `LGTM`. Commit only if user pre-authorized.

## Review packet (required fields)

Codex emits a fenced ```json block matching `references/schema.json`:

- `goal` — one paragraph.
- `plan_source` — file path or quoted summary.
- `changed_files[]` — `{path, subsystem, note?}`, grouped by subsystem.
- `diff_summary` — behavior-level, not raw patch.
- `qa[]` — `{command, result: pass|fail|skipped, evidence?}`.
- `risks[]` — migrations, data changes, user-visible changes.
- `questions[]` — only blockers Codex could not resolve from the repo.

Validate with: `python -c "import json,jsonschema; jsonschema.validate(json.load(open('packet.json')), json.load(open('references/schema.json')))"`.

## Claude response contract

Exactly one status line:

```text
STATUS: APPROVED
STATUS: LGTM
STATUS: CHANGES_REQUESTED
STATUS: BLOCKED
```

- `CHANGES_REQUESTED` — list required fixes as actionable bullets.
- `BLOCKED` — name the missing decision, access, or evidence.

## Approval rules

- Friendly review prose ≠ approval without `APPROVED`/`LGTM`.
- Codex re-implements + re-QAs after every `CHANGES_REQUESTED`.
- After `max-review-rounds`, stop and report unresolved items.
