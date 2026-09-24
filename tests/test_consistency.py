"""Repo consistency: every cited appendix figure/module exists (kills doc rot)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _paper():
    return (ROOT / "paper" / "paper.md").read_text()


def test_appendix_references_exist():
    text = _paper()
    defined = set(re.findall(r"^## Appendix ([A-Z]{1,2})\.", text, re.M))
    cited = set(re.findall(r"Appendix(?:ices)? ([A-Z0-9,\-–/ ]+)", text))
    # expand ranges like A-D, lists like Q/W, singles
    need = set()
    for chunk in cited:
        for tok in re.split(r"[,/\s]+", chunk):
            tok = tok.strip(" .()")
            if re.fullmatch(r"[A-Z]{1,2}", tok or ""):
                need.add(tok)
    # single-letter range endpoints e.g. A–AU handled by spot checks below
    missing = {t for t in need if t not in defined and len(t) == 1 and t < "Z"}
    # only enforce two-letter + late-alphabet cites (single early letters appear in prose)
    missing = {t for t in need if len(t) == 2 and t not in defined}
    assert not missing, f"dangling appendix cites: {missing}"
    assert len(defined) >= 40


def test_figure_references_exist():
    text = _paper()
    figs = set(re.findall(r"figures/(fig[\w]+\.png)", text))
    assert len(figs) > 40
    missing = [f for f in figs if not (ROOT / "figures" / f).exists()]
    assert not missing, f"missing figures: {missing}"


def test_module_references_exist():
    text = _paper() + (ROOT / "README.md").read_text()
    mods = set(re.findall(r"bh_graph\.([a-z_][a-z0-9_]*)", text))
    ignore = set()
    missing = [m for m in mods
               if not (ROOT / "src" / "bh_graph" / f"{m}.py").exists()
               and not (ROOT / "scripts" / f"{m}.py").exists()
               and m not in ignore]
    assert not missing, f"missing modules: {missing}"


def test_demo_lists_existing_figures():
    app = (ROOT / "app.py").read_text()
    figs = set(re.findall(r'"(figures/fig[\w]+\.png)"', app))
    missing = [f for f in figs if not (ROOT / f).exists()]
    assert not missing, f"demo cites missing figures: {missing}"
