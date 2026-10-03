"""TIME-Q-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/timeq0/*.json (frozen battery records), evaluates every
preregistered gate (TIMEQ0-PREREG section 5), writes verdict.json.
No bar/ladder/outcome may change post-data: failures file as genuine
or design-error autopsies.

Ladder (TIMEQ0-PREREG section 6, partition order):
  INCOMPLETE > UNIQUE > TIMING > REDUCED > NULL.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import info0 as i0  # noqa: E402
from bh_graph import merge0 as m0  # noqa: E402
from bh_graph import split0 as s0  # noqa: E402
from bh_graph import store0 as st0  # noqa: E402
from bh_graph import time0 as t0  # noqa: E402
from bh_graph import timeq0 as q0  # noqa: E402
from bh_graph import ug  # noqa: E402

BAR_LEDGER = q0.BAR_LEDGER


def load(outdir: str):
    recs = []
    for path in sorted(glob.glob(os.path.join(outdir, "*.json"))):
        if path.endswith("verdict.json"):
            continue
        with open(path) as f:
            d = json.load(f)
        d["_path"] = os.path.basename(path)
        recs.append(d)
    return recs


def by_kind(recs):
    out = {}
    for r in recs:
        k = r.get("meta", {}).get("kind", "?")
        out.setdefault(k, []).append(r)
    return out


# ---------------------------------------------------------------------------
# B-gate transport helpers (analyzer-side; frozen STORE transports only)
# ---------------------------------------------------------------------------

def relabel_enlarged(X: dict, perm: dict) -> dict:
    h, psi2, order2 = ug.permute_state(X["g"], X["psi"], X["order"], perm)
    Q2 = {}
    for k, e in X["Q"].items():
        full = dict(perm)
        full.setdefault(e["frame"]["i"], e["frame"]["i"])
        full.setdefault(e["frame"]["j"], e["frame"]["j"])
        nq, nf = st0.transport_store_perm(e["q"], e["frame"], full)
        nk = perm[k] if k in perm else k
        nf = dict(nf)
        nf["k"] = nk
        Q2[nk] = {"frame": nf, "q": nq}
    return q0.make_enlarged(h, psi2, order2, Q2)


def phase_enlarged(X: dict, alpha: float) -> dict:
    ph = complex(math.cos(alpha), math.sin(alpha))
    Q2 = {}
    for k, e in X["Q"].items():
        Q2[k] = {"frame": dict(e["frame"]),
                 "q": st0.transport_store_u1(e["q"], alpha)}
    return q0.make_enlarged(X["g"], np.asarray(X["psi"]) * ph,
                             X["order"], Q2)


def swap_enlarged(X: dict) -> dict:
    Q2 = {}
    for k, e in X["Q"].items():
        nq, nf = st0.swap_store(e["q"], e["frame"])
        Q2[k] = {"frame": nf, "q": nq}
    return q0.make_enlarged(X["g"], X["psi"], X["order"], Q2)


def _rev_perm(nodes) -> dict:
    s = sorted(nodes)
    return {v: s[len(s) - 1 - t] for t, v in enumerate(s)}


def _walk_phys_equal(w1, w2) -> bool:
    if len(w1) != len(w2):
        return False
    return all(q0.is_enlarged_equiv_ok(a, b) for a, b in zip(w1, w2))


def _n_split_products(Xm: dict) -> tuple:
    """Max over labeled merge successors of #Q-split successors.

    Q-determinism: every merge successor carries exactly its stored entry,
    so exactly one split successor exists. Returns (max_n, n_merge_succs).
    """
    ms = q0.merge_successors(Xm)
    mx = 0
    for Y, _ in ms:
        mx = max(mx, len(q0.split_successors(Y)))
    return mx, len(ms)


def _task_from_meta(meta: dict, T: int):
    k = meta.get("kind")
    if k == "roundtrip":
        return ("roundtrip", meta["graph"], int(T))
    if k == "multicover":
        cell = meta.get("cell", "")
        if cell.startswith("j2/"):
            return ("multicover", "j2", cell.split("/", 1)[1])
        g, f = cell.split("/", 1)
        return ("multicover", "tiny", g, f)
    return None


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/timeq0"
    recs = load(outdir)
    K = by_kind(recs)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    want = {}
    for t in q0.all_tasks():
        want[t[0]] = want.get(t[0], 0) + 1

    # ---- counts (exact census) ----
    for kk in ("wait", "merge1", "split1", "roundtrip", "detcore",
               "multicover", "disjoint", "seqrev", "timing", "hidden",
               "hiddenq", "sched", "forward", "toy", "horizon"):
        gate(f"count-{kk}", len(K.get(kk, [])) == want.get(kk, -1),
             f"got={len(K.get(kk, []))} want={want.get(kk, '?')}")
    fw = K.get("fw", [])
    fw_ok = len(fw) == 1
    gate("count-fw", fw_ok, f"got={len(fw)} want=1")
    fwr = fw[0] if fw else {}
    counts_ok = all(c["ok"] for c in gates if c["gate"].startswith("count-"))

    boundary = [r for r in recs
                if r.get("meta", {}).get("kind") not in ("fw", "forward")]

    # ---- A: regressions (live, frozen modules) ----
    try:
        from collections import Counter
        uni = t0.tiny_universe()
        tra = t0.canonical_transitions(uni)
        byn = t0.universe_by_n(uni())
        c = Counter(r["cid"][0] for r in uni)
        a_uni = (dict(c) == {1: 1, 2: 1, 3: 2, 4: 6, 5: 21, 6: 112}
                 and len(uni) == 143)
        a_toy = (t0.count_walks_from(t0.toy_chain_adj(), 0, 2).get(2, -1) == 1
                 and t0.count_walks_from(t0.toy_diamond_adj(), 0, 2).get(2, -1) == 2)
        (n2,) = [x for x in tra["cids"] if x[0] == 2]
        a_c1 = sorted(k for _, k in tra["adj"][n2]) == ["C", "I", "S", "S"]
        cen = t0.boundary_census(t0.toy_diamond_adj(),
                                 [0, "1a", "1b", 2], 2)
        a_cen = cen["n_pairs"] == 16 and cen["matrix"][("0", "2")] == 2
        a_time0 = bool(a_uni and a_toy and a_c1 and a_cen)
    except Exception as e:  # noqa: BLE001
        a_time0 = False
        a_cen = f"exc={e}"
    gate("A-time0", a_time0, f"uni/toy/C1/census ({a_cen})")

    try:
        ok = True
        for gname in ("edge2", "path3", "triangle"):
            Xm, Xp, _ = q0._merge1_pair(gname)
            ms = [Y for Y, _ in q0.merge_successors(Xm)
                  if q0.is_enlarged_equiv_ok(Y, Xp)]
            if not ms:
                ok = False
                break
            Y = ms[0]
            ss = q0.split_successors(Y)
            if len(ss) != 1:
                ok = False
                break
            Z, _ = ss[0]
            if not st0.is_exact_equiv_ok(
                    {"g": Z["g"], "psi": Z["psi"], "order": Z["order"]},
                    {"g": Xm["g"], "psi": Xm["psi"], "order": Xm["order"]}):
                ok = False
                break
            if dict(Z["Q"]):
                ok = False
                break
            ac = q0.event_accounting(Xm, Y, {"kind": "C",
                                             "edge": list(sorted(Xm["g"].edges()))[0]})
            ac2 = q0.event_accounting(Y, Z, {"kind": "S",
                                             "k": list(Y["Q"])[0]})
            if abs(float(ac.get("close_merge", 1.0))) >= BAR_LEDGER:
                ok = False
                break
            if abs(float(ac2.get("close_split", 1.0))) >= BAR_LEDGER:
                ok = False
                break
            if abs(float(ac2.get("invert_err", 1.0))) >= BAR_LEDGER:
                ok = False
                break
        gate("A-store", bool(ok), "EV-subset roundtrips")
    except Exception as e:  # noqa: BLE001
        gate("A-store", False, f"exc={e}")

    try:
        ok = all(i0.waiting_placements(T, L)["C"] == math.comb(T, L)
                 for T in range(7) for L in range(T + 1))
        uni2 = t0.tiny_universe()
        tra2 = t0.canonical_transitions(uni2)
        cids = tra2["cids"][:6]
        for a in cids:
            for b in cids:
                for T in (1, 2, 3):
                    d = i0.history_pair_decomposition(tra2["adj"], a, b, T)
                    ok = ok and bool(d["identity_ok"])
        gate("A-info", bool(ok), "waiting + timed-vs-skeleton")
    except Exception as e:  # noqa: BLE001
        gate("A-info", False, f"exc={e}")

    try:
        ok = True
        for graph, field, k in q0.DETCORE_CELLS[:2]:
            Xm, Xp = q0._detcore_pair(graph, field, int(k), "split")
            ss = q0.split_successors(Xm)
            if len(ss) != 1:
                ok = False
                break
            Z, _ = ss[0]
            if not st0.is_exact_equiv_ok(
                    {"g": Z["g"], "psi": Z["psi"], "order": Z["order"]},
                    {"g": Xp["g"], "psi": Xp["psi"], "order": Xp["order"]}):
                ok = False
                break
            ms = [Y for Y, _ in q0.merge_successors(Xp)
                  if q0.is_enlarged_equiv_ok(Y, Xm)]
            if not ms:
                ok = False
                break
        gate("A-split", bool(ok), "FIB-subset predecessor/roundtrip")
    except Exception as e:  # noqa: BLE001
        gate("A-split", False, f"exc={e}")

    # ---- B: canonicalization (live spots) ----
    try:
        spots = [(("wait", "path3", "on", 2), True),
                 (("merge1", "path3", 1), True),
                 (("wait", "triangle", "qpersist", 2), True)]
        ok = True
        for t, _ in spots:
            b = q0.boundary_for_task(t)
            Xm, Xp, T = b["Xm"], b["Xp"], int(b["T"])
            n0 = int(q0.count_histories_Q(Xm, Xp, T)["N"])
            Xr_m = relabel_enlarged(Xm, _rev_perm(Xm["g"].nodes()))
            Xr_p = relabel_enlarged(Xp, _rev_perm(Xp["g"].nodes()))
            if not q0.is_enlarged_equiv_ok(Xm, Xr_m):
                ok = False
                break
            if not q0.is_enlarged_equiv_ok(Xp, Xr_p):
                ok = False
                break
            n1 = int(q0.count_histories_Q(Xr_m, Xr_p, T)["N"])
            if n1 != n0:
                ok = False
                break
        gate("B-relabel", bool(ok), f"spots={len(spots)}")
    except Exception as e:  # noqa: BLE001
        gate("B-relabel", False, f"exc={e}")

    try:
        spots = [(("merge1", "path3", 1), 0.7),
                 (("wait", "triangle", "qpersist", 2), 2.1)]
        ok = True
        for t, alpha in spots:
            b = q0.boundary_for_task(t)
            Xm, Xp, T = b["Xm"], b["Xp"], int(b["T"])
            n0 = int(q0.count_histories_Q(Xm, Xp, T)["N"])
            Xr_m = phase_enlarged(Xm, alpha)
            Xr_p = phase_enlarged(Xp, alpha)
            if not q0.is_enlarged_equiv_ok(Xm, Xr_m):
                ok = False
                break
            if not q0.is_enlarged_equiv_ok(Xp, Xr_p):
                ok = False
                break
            n1 = int(q0.count_histories_Q(Xr_m, Xr_p, T)["N"])
            if n1 != n0:
                ok = False
                break
        gate("B-u1", bool(ok), f"spots={len(spots)}")
    except Exception as e:  # noqa: BLE001
        gate("B-u1", False, f"exc={e}")

    try:
        spots = [(("merge1", "path3", 1),),
                 (("hiddenq", "path3", "stored"),)]
        ok = True
        for (t,) in spots:
            b = q0.boundary_for_task(t)
            Xm, Xp, T = b["Xm"], b["Xp"], int(b["T"])
            n0 = int(q0.count_histories_Q(Xm, Xp, T)["N"])
            Xs_m = swap_enlarged(Xm)
            Xs_p = swap_enlarged(Xp)
            if not q0.is_enlarged_equiv_ok(Xm, Xs_m):
                ok = False
                break
            if not q0.is_enlarged_equiv_ok(Xp, Xs_p):
                ok = False
                break
            n1 = int(q0.count_histories_Q(Xs_m, Xs_p, T)["N"])
            if n1 != n0:
                ok = False
                break
        gate("B-swap", bool(ok), f"spots={len(spots)}")
    except Exception as e:  # noqa: BLE001
        gate("B-swap", False, f"exc={e}")

    try:
        spots = [(("wait", "edge2", "on", 2),),
                 (("merge1", "edge2", 2),),
                 (("roundtrip", "edge2", 2),),
                 (("roundtrip", "triangle", 2),)]
        ok = True
        det = []
        for (t,) in spots:
            b = q0.boundary_for_task(t)
            Xm, Xp, T = b["Xm"], b["Xp"], int(b["T"])
            nq = int(q0.count_histories_Q(Xm, Xp, T)["N"])
            ex = q0.explicit_histories_Q(Xm, Xp, T, cap=5000)
            if not ex.get("complete"):
                ok = False
                det.append(f"{t}:incomplete")
                break
            if int(ex["N"]) < nq:
                ok = False
                det.append(f"{t}:labeled<{nq}")
                break
            groups = 0
            seen = []
            for w in ex["walks"]:
                if any(_walk_phys_equal(w, z) for z in seen):
                    continue
                seen.append(w)
                groups += 1
            det.append(f"{t}:lab={ex['N']}/phys={groups}/dp={nq}")
            if groups != nq:
                ok = False
                break
        gate("B-nolabel", bool(ok), "; ".join(det))
    except Exception as e:  # noqa: BLE001
        gate("B-nolabel", False, f"exc={e}")

    # ---- C: battery ----
    w = K.get("wait", [])

    def _n_merge_classes(gname: str) -> int:
        spec = q0.tiny_graph_by_name(gname)
        X = q0.make_enlarged(spec["g"], q0.zero_psi(len(spec["order"])),
                              spec["order"], {})
        reps = []
        for Y, _ in q0.merge_successors(X):
            if not any(q0.is_enlarged_equiv_ok(Y, Z) for Z in reps):
                reps.append(Y)
        return len(reps)

    try:
        c_wait = True
        for r in w:
            wk = r["meta"].get("wk")
            if wk == "off":
                c_wait = c_wait and (r["N_Q"] == 0)
            elif wk in ("on", "qpersist"):
                c_wait = c_wait and (r["N_Q"] >= 1 and r["S_vec_Q"][0] == 1)
                if wk == "on":
                    c_wait = c_wait and (r["S_vec_Q"][2]
                                         == _n_merge_classes(
                                             r["meta"]["graph"]))
        c_wait = c_wait and len(w) > 0
        gate("C-wait", bool(c_wait), f"n={len(w)}")
    except Exception as e:  # noqa: BLE001
        gate("C-wait", False, f"exc={e}")
    gate("C-roundtrip", all(r["N_Q"] >= 1 for r in K.get("roundtrip", []))
         and len(K.get("roundtrip", [])) > 0,
         f"n={len(K.get('roundtrip', []))}")
    gate("C-detcore", all(r["N_Q"] >= 1 for r in K.get("detcore", []))
         and len(K.get("detcore", [])) > 0,
         f"n={len(K.get('detcore', []))}")
    gate("C-multicover", all(r["N_Q"] >= 1 for r in K.get("multicover", []))
         and len(K.get("multicover", [])) > 0,
         f"n={len(K.get('multicover', []))}")
    gate("C-hidden", all(r["N_Q"] >= 1 for r in K.get("hidden", []))
         and len(K.get("hidden", [])) > 0,
         f"n={len(K.get('hidden', []))}")
    gate("C-disjoint", all(r["N_Q"] >= 1 for r in K.get("disjoint", []))
         and len(K.get("disjoint", [])) > 0,
         f"n={len(K.get('disjoint', []))}")
    try:
        sq = K.get("seqrev", [])
        drained = True
        for r in sq:
            if r["meta"].get("dk") != "reverse":
                continue
            t = ("seqrev", r["meta"]["name"], r["meta"]["ftag"], "reverse")
            b = q0.boundary_for_task(t)
            if dict(b["Xp"]["Q"]):
                drained = False
        gate("C-seqrev", all(r["N_Q"] >= 1 and r.get("sym_ok", False)
                             for r in sq) and drained and len(sq) > 0,
             f"n={len(sq)} drained={drained}")
    except Exception as e:  # noqa: BLE001
        gate("C-seqrev", False, f"exc={e}")

    # ---- D: census ----
    try:
        need = ("N_Q", "S_vec_Q", "N_skel_Q", "expect_timed_Q", "red")
        ok = all(all(k in r for k in need) and "N_red" in r["red"]
                 for r in boundary) and len(boundary) > 0
        ok = ok and all("forward_Q" in r and "forward_red" in r
                        for r in K.get("forward", []))
        gate("D-computed", bool(ok), f"n={len(boundary)}")
    except Exception as e:  # noqa: BLE001
        gate("D-computed", False, f"exc={e}")
    v0 = [r for r in boundary if r.get("V0")]
    gate("D-skel-identity", all(r.get("skel_identity_ok", False) for r in v0)
         and len(v0) > 0, f"nV0={len(v0)}")

    # ---- E: reduced vs full ----
    v0c = [r for r in v0 if r.get("red", {}).get("complete", True)]
    viol = [r["_path"] for r in v0c if r["N_Q"] > r["red"]["N_red"]]
    gate("E-compare", len(viol) == 0 and len(v0c) > 0,
         f"viol={len(viol)} cov={len(v0c)}/{len(v0)} {viol[:3]}")
    g_pre = {c["gate"]: c["ok"] for c in gates}
    gate("E-reduction", bool(g_pre.get("D-computed", False)),
         "pooled reduction filed")

    # ---- F: product collapse ----
    try:
        prod = K.get("multicover", []) + K.get("roundtrip", [])
        n_pass = 0
        for r in prod:
            t = _task_from_meta(r["meta"], r["T"])
            b = q0.boundary_for_task(t)
            mx, _ = _n_split_products(b["Xm"])
            n_pass += int(mx == 1)
        frac = (n_pass / len(prod)) if prod else 0.0
        gate("F-collapse", bool(frac >= q0.PRODUCT_RESOLVE_MIN),
             f"{n_pass}/{len(prod)}={frac:.3f}")
        product_resolve = float(frac)
    except Exception as e:  # noqa: BLE001
        gate("F-collapse", False, f"exc={e}")
        product_resolve = 0.0

    # ---- G/N: timing (excursion-aware: M,S,M detours count; the timing
    # claim is single one-event skeleton S_1==1 with N_Q>1 surviving) ----
    tim = K.get("timing", [])
    n_g = sum(1 for r in tim if r["S_vec_Q"][1] == 1 and r["N_Q"] > 1)
    frac_g = (n_g / len(tim)) if tim else 0.0
    gate("G-survive", bool(frac_g >= q0.TIMING_SURVIVE_MIN),
         f"{n_g}/{len(tim)}={frac_g:.3f}")
    timing_frac = float(frac_g)
    gate("N-timing", all(r["N_Q"] > 1 and r["S_vec_Q"][1] == 1 for r in tim)
         and len(tim) > 0, f"n={len(tim)}")

    # ---- H: scheduler ----
    try:
        dis = K.get("disjoint", [])
        n_m = 0
        for r in dis:
            sub = m0.build_substrate(r["meta"]["sub"])
            psi = np.asarray(m0.build_field(sub, r["meta"]["ftag"]),
                             dtype=np.complex128)
            rep = i0.sequential_orders_for_subset(
                sub["g"], psi, sub["order"],
                [tuple(r["meta"]["ea"]), tuple(r["meta"]["eb"])])
            n_m += int(bool(rep.get("all_match", False)))
        frac_a = (n_m / len(dis)) if dis else 0.0
        sch = [r for r in (K.get("disjoint", []) + K.get("sched", []))
               if r.get("V0") and r.get("red", {}).get("complete", True)]
        n_b = sum(1 for r in sch if r["N_Q"] == r["red"]["N_red"])
        frac_b = (n_b / len(sch)) if sch else 0.0
        gate("H-sched", bool(frac_a >= q0.SCHED_PRESERVE_MIN
                             and frac_b >= q0.SCHED_PRESERVE_MIN),
             f"m!={n_m}/{len(dis)} eq={n_b}/{len(sch)}")
        sched_frac = float(frac_b)
    except Exception as e:  # noqa: BLE001
        gate("H-sched", False, f"exc={e}")
        sched_frac = 0.0

    # ---- I: hidden-store load bearing ----
    try:
        hq = K.get("hiddenq", [])
        pairs = {}
        for r in hq:
            pairs.setdefault(r["meta"]["graph"], {})[r["meta"]["variant"]] = r
        ok = len(pairs) > 0
        for gname, d in pairs.items():
            if "empty" not in d or "stored" not in d:
                ok = False
                break
            a, b = d["empty"], d["stored"]
            same = (a["N_Q"] == b["N_Q"]
                    and a["S_vec_Q"] == b["S_vec_Q"]
                    and json.dumps(a.get("proj", []), sort_keys=True)
                    == json.dumps(b.get("proj", []), sort_keys=True))
            if same:
                ok = False
                break
        gate("I-load", bool(ok), f"pairs={len(pairs)}")
    except Exception as e:  # noqa: BLE001
        gate("I-load", False, f"exc={e}")

    # ---- J: reversal ----
    gate("J-rev", all(r.get("sym_ok", False) and r.get("rev_ok", False)
                      for r in boundary) and len(boundary) > 0,
         f"n={len(boundary)}")

    # ---- K: accounting ----
    try:
        ok = all(r.get("acct_ok", False) for r in boundary)
        for gname in ("edge2", "path3"):
            spec = q0.tiny_graph_by_name(gname)
            e = sorted(tuple(sorted(x)) for x in spec["g"].edges())[0]
            if st0.classify_deficit_support(spec["g"], *e)["class"] \
                    != "one-neighborhood-local":
                ok = False
        gate("K-res", bool(ok) and len(boundary) > 0,
             f"n={len(boundary)}")
    except Exception as e:  # noqa: BLE001
        gate("K-res", False, f"exc={e}")

    # ---- L/M/O: filed legs ----
    hor = K.get("horizon", [])
    gate("L-ladder", all("N_Q" in r for r in hor) and len(hor) > 0,
         f"n={len(hor)}")

    def _class(r):
        if r["N_Q"] <= 1:
            return "unique/zero"
        if r["N_skel_Q"] == 1:
            return "timing/waiting"
        if r["meta"]["kind"] in ("disjoint", "sched"):
            return "scheduler/order"
        if r.get("V0") and r["meta"]["kind"] in ("roundtrip", "multicover",
                                                 "merge1", "split1"):
            return "product/skeleton"
        if not r.get("V0"):
            return "field-routing/other"
        return "skeleton/other"

    ana = {}
    for r in boundary:
        c = _class(r)
        ana[c] = ana.get(c, 0) + 1
    gate("M-class", len(boundary) > 0, json.dumps(ana, sort_keys=True))

    fwd = K.get("forward", [])
    gate("O-fwd", all("forward_Q" in r and "forward_red" in r for r in fwd)
         and len(fwd) > 0, f"n={len(fwd)}")

    # ---- P: controls ----
    toy = K.get("toy", [])
    gate("P-unique", all(r["N_Q"] == 1 for r in toy
                         if r["meta"].get("dk") == "unique")
         and any(r["meta"].get("dk") == "unique" for r in toy),
         f"n={len(toy)}")
    gate("P-zero", all(r["N_Q"] == 0 for r in toy
                       if r["meta"].get("dk") == "zero")
         and any(r["meta"].get("dk") == "zero" for r in toy),
         f"n={len(toy)}")

    # ---- X: firewall ----
    if fw_ok:
        gate("X-nosample", fwr.get("roundtrips_exact") is True
             and fwr.get("n_roundtrips", 0) > 0
             and fwr.get("fiber0_verdict") == "FIBER0-DEBT"
             and fwr.get("rivals_valid") is True,
             str(fwr.get("rivals_detail", ""))[:120])
        gate("X-firewall", fwr.get("fitted_params") == 0
             and fwr.get("no_tuning") is True
             and fwr.get("no_measure") is True, "")
        gate("X-notrigger", fwr.get("no_trigger") is True, "")
    else:
        gate("X-nosample", False, "fw record missing")
        gate("X-firewall", False, "fw record missing")
        gate("X-notrigger", False, "fw record missing")

    # ---- pooled stats (headline V0; TOY/FW excluded) ----
    head = [r for r in v0 if r["meta"].get("kind") != "toy"]
    comp = [r for r in head if r["N_Q"] > 0]
    f_u = (sum(1 for r in comp if r["N_Q"] == 1) / len(comp)) if comp else 0.0
    f_c = (len(comp) / len(head)) if head else 0.0
    by_t = {}
    for r in head:
        by_t.setdefault(int(r["T"]), []).append(r)
    per_t = {}
    for T, rs in sorted(by_t.items()):
        cc = [r for r in rs if r["N_Q"] > 0]
        per_t[T] = (sum(1 for r in cc if r["N_Q"] == 1) / len(cc)) if cc else 0.0
    worst = min(per_t.values()) if per_t else 0.0
    ts = sorted(per_t)
    if len(ts) >= 2:
        d = per_t[ts[-1]] - per_t[ts[0]]
        trend = "strengthens" if d > 0.1 else ("proliferates" if d < -0.1
                                               else "stable")
    else:
        trend = "stable"
    redc = [r for r in head if r.get("red", {}).get("complete", True)]
    redp = [r for r in redc if r["red"]["N_red"] > 0]
    f_red = (sum(1 for r in redp if r["red"]["N_red"] == 1) / len(redp)) \
        if redp else 0.0
    skp = [r for r in head if r["N_skel_Q"] > 0]
    f_skel = (sum(1 for r in skp if r["N_skel_Q"] == 1) / len(skp)) \
        if skp else 0.0
    med_q = float(sorted(r["N_Q"] for r in comp)[len(comp) // 2]) \
        if comp else 0.0
    med_r = float(sorted(r["red"]["N_red"] for r in redp)[len(redp) // 2]) \
        if redp else 0.0

    census = {"gates": {c["gate"]: c["ok"] for c in gates},
              "pooled_f_unique_Q": float(f_u),
              "worst_T_f_unique_Q": float(worst),
              "pooled_f_compat_Q": float(f_c),
              "product_resolve": float(product_resolve),
              "pooled_f_unique_skel_Q": float(f_skel),
              "pooled_f_unique_red": float(f_red),
              "median_NQ": float(med_q),
              "median_Nred": float(med_r),
              "trend_T": trend}
    verdict = q0.verdict_from_census(census)
    gate("Z-report", verdict.get("verdict") in q0.VERDICT_LADDER,
         verdict.get("verdict", ""))

    g = {c["gate"]: c["ok"] for c in gates}
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict.get("verdict"), "reason": verdict,
           "n_gates": len(gates), "n_pass": n_pass, "gates": gates,
           "pooled": {"f_unique_Q": f_u, "f_compat_Q": f_c,
                      "worst_T": worst, "per_T": per_t, "trend_T": trend,
                      "f_unique_red": f_red, "f_unique_skel_Q": f_skel,
                      "median_NQ": med_q, "median_Nred": med_r,
                      "product_resolve": product_resolve,
                      "timing_frac": timing_frac, "sched_frac": sched_frac,
                      "n_head": len(head), "n_compat": len(comp)},
           "anatomy": ana, "counts_ok": bool(counts_ok)}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"[timeq0] pooled f_unique_Q={f_u:.4f} f_compat={f_c:.4f} "
          f"f_red={f_red:.4f} worst_T={worst:.4f} trend={trend}")
    print(f"[timeq0] verdict={verdict.get('verdict')} "
          f"{n_pass}/{len(gates)} ANALYZE_EXIT:0")


if __name__ == "__main__":
    main()
