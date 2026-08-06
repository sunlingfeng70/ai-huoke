# ai-huoke

## Agent skills

### Issue tracker

Issues live in GitHub Issues at `sunlingfeng70/ai-huoke`, managed through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary — `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Development

Target interpreter is the system Python 3.9.6, so every module needs `from __future__ import annotations` before using `dict[str, str]`-style annotations.

Tests run under a project-local venv:

```bash
python3 -m venv .venv && .venv/bin/pip install pytest   # first time only
.venv/bin/pytest                                        # full suite
.venv/bin/pytest test_huoke.py -v                        # one file
```

The batch pipeline takes its comment source and its judgement step as function arguments, so the whole suite runs without network access or a model key.
