# NEXT: hero queue (run one at a time, in order)

Prereq: `RUNPOD_API_KEY` in env + SSH key registered (see `runpod/README.md`).
Each line is one pod (auto-terminates). Artifacts return to `data/`.

```bash
# HERO-3 (pod redo, only if the local backstop failed): 80 graphs @ N=8000
./runpod/launch.sh --per-shell 800 --beta 0.87 --graphs 80 --terminate
# expected: p ~0.92, ~35 min wall on 16 vCPU (or split 40+40 across two pods)

# HERO-4: beta scan @ N=16000 (log-linear says beta ~0.74)
./runpod/launch.sh --per-shell 1600 --betas 0.68,0.74,0.80 --graphs 4 --terminate
# expected: ~8 min wall; pick beta with stacked p closest to 0.92

# HERO-5: 80-graph production @ N=16000 (fill beta from HERO-4)
./runpod/launch.sh --per-shell 1600 --beta FILL --graphs 80 --terminate
# expected: ~50 min wall; artifact data/p80_n16000_beta0XX.json

# HERO-6 (optional): narrow-shape comparison, N=8000 as 100x80
./runpod/launch.sh --per-shell 100 --n-shells 80 --beta 0.87 --graphs 8 --terminate
# note: radii grid differs (79 pairs over [1.5,5.5]); p NOT comparable to
# wide-10. Compares cost/shape only, per the ceiling analysis.
```

Decision rules (no judgment calls needed):

- Beta pick: stacked p closest to 0.92; tie-break toward lower beta.
- Kill wires (stop the queue, report): any stacked kappa >= 0; production
  mean outside 0.85–1.00; beta(16000) <= 0.3 (log-linear breakdown —
  do NOT run HERO-5 blind, re-scan lower first).
- After each hero: commit `data/*.json` + figure/panel update, push, report
  verdict before launching the next (one at a time).
