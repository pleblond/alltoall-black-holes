"""Repo consistency: every cited v5-paper section/figure/module exists (kills doc rot)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _v5():
    return ((ROOT / "paper" / "v5" / "main.tex").read_text()
            + "\n" + (ROOT / "paper" / "v5" / "supplement.tex").read_text())


def test_supplement_sections_exist():
    main = (ROOT / "paper" / "v5" / "main.tex").read_text()
    supp = (ROOT / "paper" / "v5" / "supplement.tex").read_text()
    n_sections = len(re.findall(r"^\\section\{", supp, re.M))
    assert n_sections == 12, f"supplement has {n_sections} sections, want 12"
    cited = set(int(m) for m in re.findall(r"\bS(\d{1,2})\b", main))
    assert cited, "no supplement cites found in main.tex"
    missing = {s for s in cited if not 1 <= s <= n_sections}
    assert not missing, f"dangling supplement cites: {missing}"


def test_figure_references_exist():
    text = _v5()
    figs = set(re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", text))
    figs |= set(re.findall(r"figures/(fig[\w]+\.png)", text))
    figs = {f if f.endswith(".png") else f + ".png" for f in figs}
    assert len(figs) > 10, f"too few figures cited: {len(figs)}"
    missing = [f for f in figs if not (ROOT / "figures" / f).exists()]
    assert not missing, f"missing figures: {missing}"


def test_module_references_exist():
    text = (_v5() + (ROOT / "README.md").read_text()
            + (ROOT / "docs" / "model.md").read_text())
    mods = set(re.findall(r"bh_graph\.([a-z_][a-z0-9_]*)", text))
    mods |= set(re.findall(r"\\path\{([a-z_][a-z0-9_]*)\}", text))
    ignore = {"dev", "q", "figures", "paper", "main", "supplement"}
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
