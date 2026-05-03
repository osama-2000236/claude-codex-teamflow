# Claude Codex Teamflow

Codex skill for a Claude-led engineering workflow:

1. Claude Code Opus creates or refines the plan.
2. Codex implements the plan and runs QA.
3. Claude Code Opus reviews the work.
4. Codex repeats fixes until Claude explicitly says `APPROVED` or `LGTM`.

## Install

Copy this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . C:\Users\osama\.codex\skills\claude-codex-teamflow
```

Then invoke:

```text
Use $claude-codex-teamflow to run a Claude-led Codex implementation and review loop.
```

## Tools

- `scripts/teamflow.py` creates structured handoff artifacts outside a repo.
- `scripts/make_pipeline.py` generates an AgentFlow pipeline.
- `references/protocol.md` defines the Claude approval gate.
- `references/templates.md` contains reusable prompts.

The skill works without a Claude CLI by using structured handoff files. If AgentFlow is installed, generated pipelines can be validated with:

```powershell
agentflow validate path\to\pipeline.py
```
