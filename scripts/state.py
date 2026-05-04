"""Machine-readable handoff state for claude-codex-teamflow runs.

A single ``meta.json`` file lives in each run directory next to the five
markdown handoff files. It tracks the workflow state machine so external
tooling can reason about it without parsing prose.

Schema (stable):

    {
      "run_id": str,
      "repo": str,           # absolute repo path
      "plan": str,           # absolute plan file path
      "claude_model": str,
      "max_rounds": int,
      "round": int,          # number of completed Claude reviews
      "state": str,          # one of STATES
      "last_status": str,    # one of STATUSES or "" (empty until first review)
      "tools": dict,
      "requested_mode": str,
      "effective_mode": str,
      "created_at": str,     # ISO-8601 seconds
      "updated_at": str,     # ISO-8601 seconds
      "schema_version": int
    }
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
SKILL_VERSION = "0.3.0"

STATES = (
    "PLAN_READY",
    "IMPLEMENTING",
    "READY_FOR_REVIEW",
    "CHANGES_REQUESTED",
    "BLOCKED",
    "APPROVED",
    "MAX_ROUNDS_REACHED",
)

STATUSES = ("APPROVED", "LGTM", "CHANGES_REQUESTED", "BLOCKED")

META_NAME = "meta.json"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def meta_path(run_dir: Path) -> Path:
    return run_dir / META_NAME


def load(run_dir: Path) -> dict[str, Any]:
    p = meta_path(run_dir)
    if not p.is_file():
        raise FileNotFoundError(f"meta.json not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save(run_dir: Path, meta: dict[str, Any]) -> None:
    meta["updated_at"] = now_iso()
    p = meta_path(run_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=False)
        fh.write("\n")


def initial_meta(
    *,
    run_id: str,
    repo: Path,
    plan: Path,
    claude_model: str,
    max_rounds: int,
    tools: dict[str, str | None],
    requested_mode: str,
    effective_mode: str,
) -> dict[str, Any]:
    ts = now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "skill_version": SKILL_VERSION,
        "run_id": run_id,
        "repo": str(repo),
        "plan": str(plan),
        "claude_model": claude_model,
        "max_rounds": int(max_rounds),
        "round": 0,
        "state": "PLAN_READY",
        "last_status": "",
        "tools": tools,
        "requested_mode": requested_mode,
        "effective_mode": effective_mode,
        "created_at": ts,
        "updated_at": ts,
    }


def record_review(run_dir: Path, status: str) -> dict[str, Any]:
    """Increment round counter and apply status transition.

    Caller is responsible for max-rounds enforcement before calling.
    """
    if status not in STATUSES:
        raise ValueError(f"Unknown status: {status!r}. Expected one of {STATUSES}.")
    meta = load(run_dir)
    meta["round"] = int(meta.get("round", 0)) + 1
    meta["last_status"] = status
    if status in ("APPROVED", "LGTM"):
        meta["state"] = "APPROVED"
    elif status == "BLOCKED":
        meta["state"] = "BLOCKED"
    else:  # CHANGES_REQUESTED
        if meta["round"] >= int(meta.get("max_rounds", 0)):
            meta["state"] = "MAX_ROUNDS_REACHED"
        else:
            meta["state"] = "CHANGES_REQUESTED"
    save(run_dir, meta)
    return meta


def can_continue(run_dir: Path) -> tuple[bool, str]:
    """Return (ok, reason) for whether another review round is allowed."""
    meta = load(run_dir)
    if meta["state"] in ("APPROVED", "BLOCKED", "MAX_ROUNDS_REACHED"):
        return False, f"Run already at terminal state: {meta['state']}"
    if int(meta.get("round", 0)) >= int(meta.get("max_rounds", 0)):
        return False, "round counter at max_rounds"
    return True, ""
