---
name: claude-codex-teamflow
description: Coordinate Claude Code Opus and Codex in a strict team-lead workflow. Use when the user wants Claude to create or refine a plan, Codex to implement and QA it, and Claude Code Opus to review, approve, or request modifications before Codex commits or moves to the next phase. Also use for Claude/Codex review loops, AgentFlow pipeline generation, structured handoff files, multi-agent implementation cycles, and strict LGTM gates.
---

# Claude Codex Teamflow

Use this skill to run a disciplined Claude-led implementation loop:

1. Claude Code Opus owns planning and final review.
2. Codex owns implementation, local QA, and fixes.
3. Work repeats until Claude explicitly says `APPROVED` or `LGTM`.
4. Codex commits only when the user explicitly requested commit permission.

## Quick Start

Create a handoff run outside the repo:

```powershell
python C:\Users\osama\.codex\skills\claude-codex-teamflow\scripts\teamflow.py `
  --repo C:\LinkedIn `
  --plan C:\path\to\plan.md `
  --mode auto
```

Generate only an AgentFlow pipeline:

```powershell
python C:\Users\osama\.codex\skills\claude-codex-teamflow\scripts\make_pipeline.py `
  --repo C:\LinkedIn `
  --plan C:\path\to\plan.md
```

Default artifacts are written to:

```text
C:\Users\osama\.codex\teamflow\runs\<repo-name>-<timestamp>
```

## Workflow

### 1. Intake the Claude Plan

Treat the user's plan as Claude-owned unless they say otherwise. If the plan is missing success criteria, QA expectations, or approval rules, create the handoff files first and mark those sections as open questions for Claude.

Read `references/protocol.md` when the workflow involves real implementation or review. Read `references/templates.md` when you need exact prompts for Claude, Codex, or rework cycles.

### 2. Prepare Codex Implementation

Codex should convert the plan into actionable engineering tasks, inspect the repo, implement changes, run the requested checks, and write a review packet that includes:

- Goal and plan reference.
- Changed files and diff summary.
- Tests and commands run.
- Known risks or skipped checks.
- Questions that block approval.

### 3. Request Claude Review

Send Claude the review packet, not just a summary. If `claude` is available on PATH, the workflow may call it. If not, write the packet to `04-claude-review.md` and ask the user or Claude Code workspace to fill it.

Claude must respond with one of:

- `APPROVED`
- `LGTM`
- `CHANGES_REQUESTED`
- `BLOCKED`

### 4. Rework Until Approval

If Claude returns `CHANGES_REQUESTED`, Codex applies those instructions, reruns focused QA, updates the review packet, and requests another Claude review.

If Claude returns `BLOCKED`, stop and surface the blocker to the user.

Do not commit or start the next phase until Claude says `APPROVED` or `LGTM`.

## AgentFlow Use

Prefer AgentFlow when it is available at either:

- `agentflow` on PATH
- `C:\Users\osama\.agentflow\.venv\Scripts\agentflow.exe`

Do not rely on `agentflow doctor` or `agentflow check-local` on Windows because they may fail on path escaping. Use `agentflow validate <pipeline.py>` for generated pipelines.

Use `--mode handoff` when Claude CLI is unavailable or when the user wants a manual review checkpoint. Use `--mode agentflow` only when the user wants an executable pipeline generated.

## Guardrails

- Keep run artifacts outside project worktrees by default.
- Do not dirty the repo with coordination files unless explicitly requested.
- Do not weaken tests to get approval.
- Do not treat passing tests as Claude approval.
- Do not commit unless the user explicitly asked for commit or the workflow prompt grants commit permission.
- Preserve the newest user instruction over older plan text.
