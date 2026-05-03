---
name: claude-codex-teamflow
description: Strict Claude-led, Codex-implemented review loop. Trigger when user wants Claude Code Opus to plan and review, Codex to implement and QA, with explicit APPROVED/LGTM gating before commit or next phase. Triggers also include Claude/Codex review loops, AgentFlow pipeline generation, structured handoff files, multi-agent implementation cycles, and LGTM gates.
---

# Claude Codex Teamflow

Roles: Claude = plan + review. Codex = implement + QA. User = scope + commit authority.
Loop: plan → implement → QA → review → rework until Claude says `APPROVED` or `LGTM`.

## Run

```powershell
python C:\Users\osama\.codex\skills\claude-codex-teamflow\scripts\teamflow.py --repo <repo> --plan <plan.md> --mode auto
```

Pipeline-only: same args, `scripts\make_pipeline.py`.
Artifacts: `C:\Users\osama\.codex\teamflow\runs\<repo>-<ts>\`.

## Load references on demand

- `references/protocol.md` — state machine, review-packet shape, Claude response contract. Load before any review or rework cycle.
- `references/templates.md` — exact prompts for plan / implement / review / rework. Load when prompting an agent.

## AgentFlow

Resolve from PATH or `C:\Users\osama\.agentflow\.venv\Scripts\agentflow.exe`. Validate generated pipelines with `agentflow validate <pipeline.py>`. Skip `agentflow doctor` and `check-local` on Windows (path-escaping bugs).

Modes: `handoff` (no Claude CLI, files only) · `agentflow` (executable pipeline) · `auto` (pick agentflow if present).

## Hard rules

- No commit unless user explicitly authorized.
- Passing tests ≠ approval. Only `APPROVED` or `LGTM` from Claude approves.
- `CHANGES_REQUESTED` → apply, rerun focused QA, new packet, new review.
- `BLOCKED` → stop, surface blocker to user.
- Run artifacts live outside the target repo.
- Newest user instruction overrides older plan text.
- Never weaken tests to obtain approval.
