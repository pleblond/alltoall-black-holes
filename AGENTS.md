# AGENTS.md — instructions for coding agents in this repo

## Test execution

- **Never run the test suite locally unless explicitly told to.** The local
  VM has few CPUs and no `pytest-xdist`; the full suite takes ~6 minutes
  serially and wastes the run.
- **Always run gates on beast2** (192 threads): see
  `docs/agent-campaign-guide.md` §3 for SSH access, workspace conventions,
  and the canonical parallel pattern
  (`pytest tests/ -q -n 96`, `-n 192` for light batteries).
- The only local pytest allowed by default is `--collect-only` and single
  small pin files during editing; full-suite validation is beast-only.
