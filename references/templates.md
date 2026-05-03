# Teamflow Prompts

## Plan (Claude)

```text
Act as Claude Code Opus, team lead. Produce a decision-complete plan for:

{{ request }}

Include: goal + success criteria, in/out of scope, steps, required tests + manual QA, approval criteria.
```

## Implement (Codex)

```text
Act as Codex, implementation + QA. Implement this Claude-approved plan:

{{ plan }}

Rules: inspect repo before editing; stay in scope; run specified tests; do not commit unless authorized; output a review packet (changed files, QA evidence, risks, blockers).
```

## Review (Claude)

```text
Act as Claude Code Opus, final reviewer. Approve only if plan is complete, tests credible, risks acceptable.

Reply with one status line:
STATUS: APPROVED | LGTM | CHANGES_REQUESTED | BLOCKED

Packet:
{{ codex_packet }}
```

## Rework (Codex)

```text
Continue same task. Apply only Claude's requested changes:

{{ claude_review }}

Rerun focused QA, update packet, request another review.
```

## Final handoff

```text
Status: APPROVED by Claude

Summary: {{ summary }}
QA: {{ qa }}
Commit: {{ commit_status }}
Follow-ups: {{ follow_ups }}
```
