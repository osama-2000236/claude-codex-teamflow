# Claude Codex Teamflow

Codex skill: Claude Code Opus plans + reviews, Codex implements + runs QA, loop continues until Claude returns `STATUS: APPROVED` (or `LGTM` in handoff mode). No commit without explicit user authorization.

## Install

```powershell
Copy-Item -Recurse . $HOME\.codex\skills\claude-codex-teamflow
```

Invoke: `Use $claude-codex-teamflow ...`

## Layout

| Path | Purpose |
|------|---------|
| `SKILL.md` | Trigger doc + run command + hard rules |
| `scripts/teamflow.py` | Writes 5 handoff files + `meta.json` to a run dir outside the repo |
| `scripts/make_pipeline.py` | Emits an AgentFlow pipeline (`pipeline.py`) for the same loop |
| `scripts/state.py` | `meta.json` reader/writer + state-machine helpers |
| `references/protocol.md` | State machine, review-packet shape, response contract |
| `references/templates.md` | Plan / implement / review / rework prompts |
| `references/schema.json` | JSON schema for the Codex review packet |

## Validate generated pipeline

```powershell
agentflow validate path\to\pipeline.py
```

Skip `agentflow doctor` and `check-local` on Windows (path-escape bugs).

## Run dir contents

`$HOME\.codex\teamflow\runs\<repo>-<hash>-<run_id>\` → `01-plan.md`, `02-codex-implementation.md`, `03-qa-report.md`, `04-claude-review.md`, `05-final-approval.md`, `meta.json`. Re-runs refuse to clobber unless `--force`.
