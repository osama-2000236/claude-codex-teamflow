#!/usr/bin/env python3
"""Create Claude/Codex teamflow handoff artifacts.

This script is intentionally conservative: it prepares review files outside the
target repo and optionally generates an AgentFlow pipeline, but it does not run
LLM agents or modify the repo.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_AGENTFLOW = Path.home() / ".agentflow" / ".venv" / "Scripts" / "agentflow.exe"
RUNS_ROOT = Path.home() / ".codex" / "teamflow" / "runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Claude/Codex teamflow artifacts.")
    parser.add_argument("--repo", required=True, help="Target repository path.")
    parser.add_argument("--plan", required=True, help="Plan markdown file to coordinate.")
    parser.add_argument("--run-id", default=None, help="Stable run id. Defaults to timestamp.")
    parser.add_argument("--claude-model", default="opus", help="Claude model label for handoff metadata.")
    parser.add_argument("--max-review-rounds", type=int, default=5, help="Maximum Claude review loops.")
    parser.add_argument(
        "--mode",
        choices=("handoff", "agentflow", "auto"),
        default="auto",
        help="handoff writes files only; agentflow also generates a pipeline; auto picks agentflow when available.",
    )
    return parser.parse_args()


def resolve_tool(name: str) -> str | None:
    return shutil.which(name)


def resolve_agentflow() -> str | None:
    found = shutil.which("agentflow")
    if found:
        return found
    if DEFAULT_AGENTFLOW.exists():
        return str(DEFAULT_AGENTFLOW)
    return None


def read_plan(plan_path: Path) -> str:
    if not plan_path.is_file():
        raise SystemExit(f"Plan file not found: {plan_path}")
    return plan_path.read_text(encoding="utf-8")


def run_dir_for(repo: Path, run_id: str) -> Path:
    return RUNS_ROOT / f"{repo.name}-{run_id}"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_handoff_files(
    run_dir: Path,
    repo: Path,
    plan_path: Path,
    plan_text: str,
    args: argparse.Namespace,
    tools: dict[str, str | None],
    effective_mode: str,
) -> None:
    metadata = {
        "repo": str(repo),
        "plan": str(plan_path),
        "run_id": args.run_id,
        "claude_model": args.claude_model,
        "max_review_rounds": args.max_review_rounds,
        "requested_mode": args.mode,
        "effective_mode": effective_mode,
        "tools": tools,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    write_text(
        run_dir / "01-plan.md",
        f"""# Teamflow Plan

```json
{json.dumps(metadata, indent=2)}
```

## Source Plan

{plan_text}
""",
    )

    write_text(
        run_dir / "02-codex-implementation.md",
        f"""# Codex Implementation Packet

Status: PENDING

Repo: `{repo}`
Plan: `{plan_path}`

## Codex Instructions

Implement the plan from `01-plan.md`, run focused QA, and replace this file with:

- Goal
- Changed files
- Diff summary
- QA evidence
- Known risks
- Blockers

Do not commit until Claude writes `APPROVED` or `LGTM` in `05-final-approval.md`.
""",
    )

    write_text(
        run_dir / "03-qa-report.md",
        """# QA Report

Status: PENDING

Record commands, outputs, browser/manual checks, skipped checks, and residual risk here.
""",
    )

    write_text(
        run_dir / "04-claude-review.md",
        f"""# Claude Review

Status: WAITING_FOR_CLAUDE

Claude Code Opus should review:

- `01-plan.md`
- `02-codex-implementation.md`
- `03-qa-report.md`
- Current repo diff at `{repo}`

Return exactly one status line:

- `STATUS: APPROVED`
- `STATUS: LGTM`
- `STATUS: CHANGES_REQUESTED`
- `STATUS: BLOCKED`

For `CHANGES_REQUESTED`, list actionable fixes. For `BLOCKED`, list the missing decision or evidence.
""",
    )

    write_text(
        run_dir / "05-final-approval.md",
        """# Final Approval

Status: PENDING

Claude approval must be copied here before Codex commits or moves to the next phase.
""",
    )


def generate_pipeline(run_dir: Path, repo: Path, plan_path: Path, args: argparse.Namespace) -> Path:
    script = Path(__file__).with_name("make_pipeline.py")
    cmd = [
        sys.executable,
        str(script),
        "--repo",
        str(repo),
        "--plan",
        str(plan_path),
        "--run-id",
        str(args.run_id),
        "--claude-model",
        args.claude_model,
        "--max-review-rounds",
        str(args.max_review_rounds),
        "--output",
        str(run_dir / "pipeline.py"),
    ]
    subprocess.run(cmd, check=True)
    return run_dir / "pipeline.py"


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    plan_path = Path(args.plan).resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repo directory not found: {repo}")

    if args.run_id is None:
        args.run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    plan_text = read_plan(plan_path)
    tools = {
        "claude": resolve_tool("claude"),
        "codex": resolve_tool("codex"),
        "agentflow": resolve_agentflow(),
    }

    effective_mode = args.mode
    if args.mode == "auto":
        effective_mode = "agentflow" if tools["agentflow"] and tools["claude"] else "handoff"

    run_dir = run_dir_for(repo, args.run_id)
    write_handoff_files(run_dir, repo, plan_path, plan_text, args, tools, effective_mode)

    pipeline_path = None
    if effective_mode == "agentflow":
        pipeline_path = generate_pipeline(run_dir, repo, plan_path, args)

    print(json.dumps(
        {
            "run_dir": str(run_dir),
            "effective_mode": effective_mode,
            "claude_available": bool(tools["claude"]),
            "codex_available": bool(tools["codex"]),
            "agentflow_available": bool(tools["agentflow"]),
            "pipeline": str(pipeline_path) if pipeline_path else None,
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
