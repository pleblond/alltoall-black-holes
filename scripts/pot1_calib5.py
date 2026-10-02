"""POT-1 Amendment-3 verification round 2 (pre-freeze, beast): path
turn-on tau=16/T=24 (1D standing lingerers need slower ramp than J2;
S/B parity argument). Both gaps, per-shell + inner-global.
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from pot1_calib4 import path_trial  # noqa: E402
from pot1_campaign import OM_PA, OM_PB  # noqa: E402


def main() -> int:
    res = {}
    for om, nm in ((OM_PA, "a"), (OM_PB, "b")):
        key = f"path_{nm}_tau16_T24"
        res[key] = path_trial(om, 16.0, T=24.0)
        print(key, json.dumps(res[key]), flush=True)
    json.dump(res, open("/tmp/pot1_calib5.json", "w"), indent=1)
    print("wrote /tmp/pot1_calib5.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
