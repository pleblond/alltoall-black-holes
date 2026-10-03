"""JET-0 forbit autopsy diagnostic (FROZEN JET-0 artifact, read-only).

Filed from the beast2 JET-0 workspace (~/jet0-d0f5/jet0_forbit_autopsy.py);
byte-identical below this header. Diagnostic only: not imported by any
JET-0 or JET-1 gate. Its finding (ours == vendored after the same
firing-at-least-once filter; zero per-rung mismatches; all vendored-only
keys all-False) is frozen JET-1 input (docs/jet1-prereg.md section 4).

"""

import json, sys
sys.path.insert(0, 'src')
import numpy as np
from bh_graph import jet0
from bh_graph.jet0 import (load_event0_orbits, _forbit_traj_spec, build_field_jet0,
    T_LADDER, DT_JET0, equiv_search, equiv_compat)
from bh_graph.ballistic import evolve_fixed, hamiltonian
import bh_graph.merge0 as m0

for key in ['traj_bare_ring-8_tiny_antibonding.json','traj_int_handbuilt_INT-hb-twospike.json']:
    spec = _forbit_traj_spec(key)
    kind, subname, ftag = spec['kind'], spec['sub'], spec.get('ftag')
    ladder = tuple(spec.get('ladder', T_LADDER)); dt = float(spec.get('dt', DT_JET0))
    sub = m0.build_substrate(subname)
    psi0 = np.asarray(build_field_jet0(sub, ftag), dtype=np.complex128)
    g, order = sub['g'], list(sub['order'])
    h = hamiltonian(g, order=list(order))
    n_steps = int(round(max(ladder)/dt))
    rows = evolve_fixed(psi0, h, dt, n_steps)['psi']
    rung_idx = [int(round(t/dt)) for t in ladder]
    sr = equiv_search(g, psi0, order, anchored=False)
    vend = spec['equiv']; vcomp = vend['compat']
    ours_keys, per_rung = set(), {}
    for ri, t in zip(rung_idx, ladder):
        psi_t = np.asarray(rows[ri], dtype=np.complex128)
        for cand in sr['cands']:
            rep = equiv_compat(g, psi_t, order, cand)
            per_rung.setdefault(cand['rkey'], []).append(bool(rep['compat']))
            if rep['compat']: ours_keys.add(cand['rkey'])
    vfilt = set(rk for rk,bl in vcomp.items() if any(bl))
    print('='*100); print(key)
    print('ours(%d) == vend-filtered(%d)?'%(len(ours_keys),len(vfilt)), ours_keys==vfilt)
    print('ours-only:', sorted(ours_keys-set(vcomp)))
    only_vend = sorted(set(vcomp)-ours_keys)
    print('vend-only(%d) all all-False?'%len(only_vend), all(not any(vcomp[rk]) for rk in only_vend))
    # per-rung bitwise on shared keys
    mism = [(rk, per_rung[rk], vcomp[rk]) for rk in sorted(ours_keys & set(vcomp)) if per_rung[rk]!=[bool(b) for b in vcomp[rk]]]
    print('per-rung bitwise mismatches on %d shared keys:'%(len(ours_keys & set(vcomp))), len(mism))
    for rk,a,b in mism[:4]: print('  ',rk,'ours=',a,'vend=',b)
