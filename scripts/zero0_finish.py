#!/usr/bin/env python3
"""ZERO-0 missing-row finder: task file -> missing-lines file.

Parses --out= paths (expanduser for ~), emits lines whose outputs are
absent. Idempotent reruns consume the emitted file with xargs.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

OUT_RE = re.compile(r"--out=(\S+)")


def missing_lines(task_file: str) -> list:
    out = []
    with open(task_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = OUT_RE.search(line)
            if not m:
                continue
            if not os.path.exists(os.path.expanduser(m.group(1))):
                out.append(line)
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description="ZERO-0 missing-row finder")
    p.add_argument("--tasks", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    miss = missing_lines(a.tasks)
    with open(a.out, "w") as f:
        f.write("\n".join(miss) + ("\n" if miss else ""))
    print(f"missing {len(miss)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
