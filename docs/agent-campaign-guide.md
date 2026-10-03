# Agent Campaign Guide — how to run a physics campaign

This document is for autonomous coding agents (and their human supervisors)
tasked with running one of this repo's **campaigns**: a preregistered,
deterministic computational experiment (e.g. STORE-0, EVENT-0, Q-DYN-0,
JET-0) executed on the shared `beast2` EC2 worker. It distills the
investigation every campaign agent previously had to repeat from scratch:
peer workspaces, branch/PR conventions, the wave pattern, and the hard-won
gotchas. Read this first; then study one merged campaign as a template
(recommended: JET-0, branch `cursor/jet-0-dynamical-jet-d0f5`, PR #134).

## 1. What a campaign is

A campaign tests one frozen claim from a `CAMPAIGN-0.tex` spec file. The
lifecycle is fixed:

1. **Prereg** (pre-data): apparatus code + frozen battery + gates + verdict
   ladder, committed before any campaign task runs.
2. **Wave** (data): all battery tasks run on beast2, records filed as JSON.
3. **Verdict**: frozen analyzer gates the data; exactly one ladder rung filed.
4. **PR**: everything merged via a draft PR, updated as you go.

The standing rules: banked modules under `src/bh_graph/` stay byte-identical
(you consume them read-only); no RNG anywhere (deterministic builders only);
no fitted parameters; **no gate, bar, or ladder change after seeing data**
(violations are filed as INCOMPLETE with an autopsy, never patched into
green). Amendments (`<name>-AMENDMENT-n.md`) are allowed pre-verdict with
gated re-runs, and must say so in the title.

## 2. Starting out

1. **Branch from the tail of main.** Fetch first (VM snapshots go stale):
   `git fetch origin main`, then
   `git checkout -b cursor/<campaign>-<run-id> origin/main`.
   Keep the run-id suffix the harness gave you on every branch you create.
2. **Read the campaign spec.** The `.tex` file arrives out-of-band (often on
   the user's machine, not in the repo). If you cannot access it, say so and
   proceed from any prereg draft already in the workspace — never stall.
3. **Study one merged campaign end to end.** Clone the pattern, not just the
   code: `docs/<x>0-prereg.md` (frozen ontology, battery, gates, ladder),
   `src/bh_graph/<x>0.py` (apparatus), `scripts/<x>0_campaign.py` (runner),
   `scripts/<x>0_analyze.py` (gates), `tests/test_<x>0.py` (pins),
   `data/<x>0/ref/` (vendored inputs), `data/<x>0/*.json` (filed records),
   `docs/<x>0-verdict.md` (filed outcome). Q-DYN-0's verdict doc is the
   template for an autopsy-resolved INCOMPLETE.
4. **Look at peer agents' live state when in doubt.** Other campaigns run
   concurrently; their beast workspaces (`~/event0-3179`, `~/qdyn0b-8e3d`,
   `~/store0-95bd`, `~/jet0-d0f5`, …) contain wave logs, suite logs, and
   runner invocations you can copy. Their branches/PRs show the current
   conventions. This is expected and encouraged — but never write into a
   peer workspace.

## 3. Beast2: the only place experiments run

Never run campaign tasks on the cloud VM (it lacks even `networkx`).
All compute goes to beast2:

- **Host:** `ubuntu@99.79.192.152`, 96 cores / 192 threads, ~370 GB RAM.
- **SSH key:** `/cursor/stores/user/aws_ec2_rsa`. It is group-readable, which
  `ssh` rejects — always copy first:
  `cp /cursor/stores/user/aws_ec2_rsa /tmp/beast_key && chmod 600 /tmp/beast_key`,
  then `ssh -i /tmp/beast_key -o StrictHostKeyChecking=no ubuntu@99.79.192.152`.
- **Your workspace:** `~/<campaign>-<run-id>/` (a repo checkout; create it by
  cloning and checking out your branch, or by `scp` from a peer checkout and
  switching branches — verify with `git log`).
- **Interpreter:** `~/<campaign>-<run-id>/venv/bin/python` (a venv per
  workspace; create with `python3 -m venv venv && venv/bin/pip install -r
  requirements.txt`, or copy the pattern from a peer).
- **Every invocation needs two things:**
  `PYTHONPATH=src` (the package lives in `src/`, uninstalled), and
  `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`
  (without these, one BLAS call fans out to 20+ threads and a 96-way wave
  melts the box — this has happened).
- **Sync code VM -> beast with `scp -r`** (or push + `git pull` on beast;
  `scp` is faster for iteration). Sync data beast -> VM the same way.

## 4. File-layout conventions (follow them exactly)

| Path | Purpose |
|---|---|
| `src/bh_graph/<x>0.py` | Apparatus: builders, records, firewall helpers. One module per campaign. |
| `scripts/<x>0_campaign.py` | Runner: `--count`, `--print-all`, per-`--task` execution, `_git` stamp. |
| `scripts/<x>0_analyze.py` | Analyzer: frozen gates + ladder, reads `data/<x>0/`, writes `verdict.json`. Must have an `if __name__ == "__main__"` guard (a campaign once shipped without one and the analyzer exited 0 silently). |
| `tests/test_<x>0.py` | Unit pins: bars, ladders, census spot-checks, covariance. Must pass pre-data. |
| `docs/<x>0-prereg.md` | Frozen pre-data record: ontology, battery, gates, ladder, prediction, firewall. Commit this before any wave. |
| `docs/<x>0-AMENDMENT-n.md` | Dated change log, pre-verdict only, with gated re-runs. |
| `docs/<x>0-verdict.md` | Filed outcome: campaign record, headline, autopsy, firewall, follow-up. |
| `data/<x>0/ref/` | Vendored inputs from sibling campaigns (+ `SOURCES.txt` with branch/commit/hashes). |
| `data/<x>0/*.json` | Filed task records + `verdict.json`. Committed to the repo. |

Runner details that matter:

- `task_argv(t)` must emit shell-safe argv per task id; **never emit empty
  option values** (`--sub ""` is dropped by the shell and `argparse` then
  fails — omit the flag instead). Quote or sanitize tags with `:`/`@`.
- Every record carries a `_git` stamp (short commit of the code that wrote
  it). Stamp from the beast checkout; if beast is behind your branch tip,
  say so in the verdict doc.
- The firewall symbol scan forbids words like `sample`/`samples` in apparatus
  files (exact-match). Name frozen probe lists `frozen12`/`probe`, and run
  the scan (`is_file_clean_ok`-equivalent) on every new file before the wave.

## 5. Running the wave

The canonical wave (JET-0/EVENT-0 pattern):

1. **Verify enumeration first:** `campaign.py --count` must equal the prereg
   battery size, on beast, before launching anything.
2. **Smoke-test** the heaviest task of each family solo with `time` — cost
   surprises (a 1.7 h/task Krylov order, a 265k-alternative fiber) are
   discovered here, not at hour 6 of a stalled wave. Scope/cap in a
   pre-verdict amendment if needed (there is precedent).
3. **Launch detached, poll separately.** Generate the task list, fan out with
   `xargs -P 96`, one log line per task (`DONE`/`FAIL`), stderr to a shared
   error log:
   `campaign.py --print-all | xargs -P 96 -I{} sh -c '...' >> logs/<x>_wave.log 2>> logs/tasks_err.log`
   under `nohup ... < /dev/null &`. Then poll with separate short `ssh`
   calls. **Do not** `ssh "... nohup ... & ...; sleep 300"` in one call —
   `ssh` hangs until the remote fds close and the tool call times out while
   the wave is fine. Likewise, prefer `nohup` over `tmux` for waves (a
   `tmux` server once died mid-wave and took the run with it).
4. **Triage FAILs from `tasks_err.log`.** Load-spike kills (no stderr, exit
   137) are retried as-is; systematic errors get a pre-verdict amendment +
   targeted re-run. Never edit a task record by hand; re-run the task.
5. **Count before analyzing:** filed files must equal battery size exactly.

## 6. Verdict and filing

1. Run the analyzer on beast over the filed data; copy `data/<x>0/*.json`
   (records + `verdict.json`) back to the VM and commit them.
2. If any instrument gate is red, the verdict is INCOMPLETE — file it with
   an autopsy (root-cause the red conjunct with a post-data diagnostic
   script; Q-DYN-0's eigen autopsy and JET-0's forbit autopsy are the
   models), and propose the corrected gate for the follow-up campaign.
   Do not "fix" apparatus post-verdict to turn a gate green.
3. Write `docs/<x>0-verdict.md`: campaign-record table, headline tally,
   autopsy, firewall statement, follow-up, reproduce commands.
4. **Full suite on beast**, parallel:
   `OMP_NUM_THREADS=1 PYTHONPATH=src venv/bin/python -m pytest tests/ -n 96 -q`
   (`tests/test_weighted.py` is always skipped — already in
   `pyproject.toml` `addopts`; `-n 96` is the sweet spot, `-n 192`
   oversubscribes). Pre-existing main failures happen: confirm them against
   a peer workspace's suite log before claiming them as such. Save the log
   under `logs/` on beast and cite it.
5. Commit data + verdict doc, push, update the PR.

## 7. Branches, commits, PRs

- One branch per campaign: `cursor/<name>-<run-id>`, off the main tail.
  Commit each logical step separately (prereg, amendments, data+verdict);
  never amend or force-push.
- Always `git push -u origin <branch>` (retry transient network errors with
  backoff), then create/update a **draft** PR with the ManagePullRequest
  tool (never `gh` for writes — the CLI is read-only here), base = main
  unless told otherwise. Update the PR body at the end of every working
  turn once changes exist; there is no PR template in this repo.
- PR bodies in this repo follow a fixed shape: one-line verdict headline,
  bullet list of apparatus/battery/runner/analyzer/pins/prereg/amendments/
  data/verdict paths, prediction line, suite line. Copy it.

## 8. Gotcha checklist (all earned the hard way)

- Beast key perms: copy to `/tmp/beast_key`, `chmod 600`, or `ssh` refuses.
- `PYTHONPATH=src` and `OMP_NUM_THREADS=1` (plus OpenBLAS/MKL) on every
  beast Python invocation. No exceptions.
- No `networkx` (or repo deps) on the cloud VM: pins can run on beast only.
- Detached launch + separate polls; never `sleep`-inside-`ssh`; prefer
  `nohup` over `tmux` for waves.
- `task_argv` must omit empty-valued flags; sanitize `:`/`@` in tags.
- Analyzer needs a `__main__` guard; runner needs `--count`/`--print-all`.
- Firewall scan every new file (no `sample`, no fitting language).
- `_git` stamp every record; disclose checkout skew in the verdict.
- Amendments are pre-verdict with gated re-runs; post-data, file
  INCOMPLETE + autopsy instead.
- Full suite on beast with `-n 96`, weighted skip automatic; cross-check
  failures against peer logs before blaming main.
- Commit + push + PR update at the end of every turn.
