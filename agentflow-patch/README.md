# AgentFlow patch: `OutputRegexCriterion`

This skill's generated pipeline uses an `output_regex` success criterion so
the reviewer node can accept either `STATUS: APPROVED` or `STATUS: LGTM`
in a single criterion. Upstream AgentFlow only ships
`output_contains` / `file_*`, evaluated with AND semantics, which can't
express that OR.

## Apply to your local AgentFlow checkout

```powershell
cd $HOME\.agentflow
git checkout -b feat/output-regex-criterion
git apply .\path\to\0001-specs-success-add-OutputRegexCriterion.patch
.\.venv\Scripts\python.exe -c "from agentflow.specs import OutputRegexCriterion; print('ok')"
```

Then submit upstream to https://github.com/shouc/agentflow if you want it
merged.

## Fallback if you can't patch AgentFlow

In `scripts/make_pipeline.py`, replace the `success_criteria` list on the
`claude_review` node with:

```python
success_criteria=[
    {"kind": "output_contains", "value": "STATUS: APPROVED"},
],
```

…and instruct the reviewer prompt to use `APPROVED` only (drop `LGTM`
from the enum). Handoff mode still accepts `LGTM` because protocol-level
parsing happens in Python, not in AgentFlow.
