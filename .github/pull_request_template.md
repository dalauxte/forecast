## Summary

Describe the change and why it improves the project.

## What Changed

- [ ] HTML report replaces CSV export
- [ ] Live simulation server (YAML ↔ Report)
- [ ] Limits per project/month + sequential budget burn
- [ ] Report improvements (tables, units, diagrams, tooltips)
- [ ] Documentation updates (requirements, arc42, manual)

## How to Test

1. `PYTHONPATH=src python3 -m forecast.cli --config config/config.yml --outdir output`
2. `PYTHONPATH=src python3 -m forecast.server` and open `http://127.0.0.1:8765`

## Checklist

- [ ] Squash and merge with the commit message provided in PR body
- [ ] Docs updated

