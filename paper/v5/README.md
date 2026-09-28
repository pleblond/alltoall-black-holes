# Paper v5 — journal cut (main + supplement)

v5 restructures the v4.1 living document (1758 lines, 68 appendices, 77 figures)
into a submittable pair (both compile; counts as of this commit):

- `main.tex` — journal text, 9pp preprint single-column 11pt (≈6pp two-column).
  Motivation, 3 claims in §2, gravity to 1PN + 2PN preview, UV + QI,
  one-family compact objects + gap-KN prediction, falsifiers + conclusion.
  4 figures (1 new survival matrix + 3 tested artifacts), 40 references.
- `supplement.tex` — methods, 9pp: parameter audit, gravity/QI/BU/BV methods,
  N-scale table (300→16000, 6 points), PPN ledger, archival ledger, O5 protocol
  summary, kill list, module map. 10 ported evidence figures (lensing, Mercury,
  UV-c, Page, N-scale, 2PN, p-fit, O5, healing, dispersion). Zero LaTeX warnings.

## What changed vs the uploaded V5-Rewrite draft

The uploaded `Paper-V5-Rewrite.md` had the right spine (falsifiers-first, ledger,
audit) but was telegraphic (~157 lines), hid inconsistencies, and mixed git notes
with paper text. v5/main.tex:

1. Adds motivation + roadmap + related-work paragraph (fuzzball/gravastar/quark/
   polymer/linear-foam distinguished).
2. Defines N/k/e_int/e_ext once; full prose with numbered equations.
3. Fixes tortuosity status: BH fit (1/2) superseded by BV derivation (0.44–0.60,
   zero tuning). Both on ledger, derivation adopted.
4. Fixes 2PN kill window: 0.92 ± 0.056 at N=1024 class (not [0.7,1.3]).
5. Fixes E_QG,2 to single value √8 E_P ≈ 3.4e19 GeV with convention note.
6. Softens title: keeps testable gap prediction in abstract/§5/§6 but does not
   lead the cover with "No Neutron Stars" until routing-stiffness NICER derivation
   lands. Title reverts to bold form if BU survives O5.
7. Moves install/streamlit/git notes to Data/Code availability; removes branch notes.
8. Maps 5 main figures to existing tested artifacts (no new untested figures).

## What changed vs v4.1

- No physics changes. All numbers identical (p=0.913±0.049, 0.93/0.94/0.91 at
  4k/8k/16k, 0.047 M☉, ~1/yr O5, 42.99", γ=1, E_QG,2=√8 E_P).
- v4.1 `paper.md` + `main.tex`/`main.pdf` untouched as extended record.
- Honesty ledger preserved and tightened (S1 table).

## Compile (verified under TeX Live 2023; zero warnings)

```bash
cd paper/v5
pdflatex main.tex && pdflatex main.tex            # main.pdf, 9pp
pdflatex supplement.tex && pdflatex supplement.tex # supplement.pdf, 9pp
```

Figures resolve via `../../figures/`.

## Next steps (for loop ticks)

- [x] Install texlive and verify page counts (main 9pp preprint ≈6pp journal; supp 5pp)
- [x] Add Fig.1 survival-matrix schematic (new TikZ, references ledger, no new claims)
- [x] Expand references to ~40 (EOS/NICER/GWTC/LVK-testing-GR/POSSIS/Rubin + neighbours)
- [x] Grow supplement toward ~12pp → reached 9pp with 10 ported figures (lensing/Mercury/UV-c/Page/N-scale/2PN/p-fit/O5/healing/dispersion)
- [x] Clear LaTeX warnings (tables → p-columns, code → quote+path, math allowbreaks; only sub-5pt overfulls remain)
- [ ] Prose polish pass on main.tex (read-through for typos, transitions, symbol consistency)
- [ ] Optional twocolumn pass if venue requires strict 6pp (currently honest preprint count)
- [ ] POSSIS band-mag refinement for red component (queued physics, not blocking)
- [ ] NICER routing-stiffness derivation (queued; sharpest post-O5 test)
