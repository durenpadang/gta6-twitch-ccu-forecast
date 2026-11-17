"""Launch-day Twitch viewer forecaster.

For every ``*.in`` case in the input directory, standardise the hourly log
ratios of analogous launches, pool them into a shape, and blend that shape with
the per-hour empirical quantiles to produce a q05/q25/q50/q75/q95 fan for the
forecast hours. Results are written as ``<id>.out`` (compact JSON, one trailing
newline).

Directories come from ``MAKEFUN_INPUT_DIR`` (default ``/input``) and
``MAKEFUN_OUTPUT_DIR`` (default ``/output``).
"""

from __future__ import annotations

import json
import math
import os

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
FALLBACK_Z = (-1.6449, -0.6745, 0.0, 0.6745, 1.6449)
HOURS = range(2, 25)
CAP = 1e9
FLOOR = 0.01
MAD_SCALE = 1.4826
MIN_SPREAD = 1e-3


def quantile(values, tau):
    """Linear-interpolation quantile of an unsorted sample."""
    p = sorted(values)
    n = len(p)
    if n == 1:
        return float(p[0])
    k = tau * (n - 1)
    lo = math.floor(k)
    if lo + 1 >= n:
        return float(p[-1])
    return p[lo] + (p[lo + 1] - p[lo]) * (k - lo)


def round2(x):
    """Half-up rounding to two decimals; integral results become int."""
    scaled = math.floor(x * 100.0 + 0.5) / 100.0
    if scaled == int(scaled):
        return int(scaled)
    return scaled


def as_viewers(row):
    """Viewer count of a row, floored at 1.0 (missing/null/NaN -> 1.0)."""
    try:
        v = float(row.get("viewers"))
    except (TypeError, ValueError):
        return 1.0
    if not math.isfinite(v) or v < 1.0:
        return 1.0
    return v


def build_ratios(comp):
    """Log-ratios r[h] (h = 2..24) for one comparable, or None if unusable."""
    hourly = sorted(comp.get("hourly") or [], key=lambda row: row.get("from") or "")
    day_start = comp.get("day_start")
    if not isinstance(day_start, str):
        return None

    i0 = None
    for idx, row in enumerate(hourly):
        if row.get("from") == day_start:
            i0 = idx
            break
    if i0 is None:
        for idx, row in enumerate(hourly):
            frm = row.get("from")
            if isinstance(frm, str) and frm > day_start:
                if frm[:13] == day_start[:13]:
                    i0 = idx
                break
    if i0 is None or i0 < 1 or i0 + 23 >= len(hourly):
        return None

    base = as_viewers(hourly[i0])
    ratios = {}
    for h in HOURS:
        ratios[h] = math.log(as_viewers(hourly[i0 + h - 1]) / base)
    return ratios


def forecast_case(case):
    """Compute the fan for one case."""
    p1 = 1.0
    for row in case.get("known") or []:
        if row.get("hour") == 1:
            p1 = max(1.0, as_viewers(row))
            break

    comps = []
    for comp in case.get("comparables") or []:
        ratios = build_ratios(comp)
        if ratios is not None:
            comps.append(ratios)

    if not comps:
        return fallback(p1, case)

    emp = {}
    med = {}
    spr = {}
    for h in HOURS:
        vals = [c[h] for c in comps if h in c]
        if not vals:
            vals = [0.0]
        med[h] = quantile(vals, 0.5)
        emp[h] = [quantile(vals, LEVELS[j]) for j in range(len(LEVELS))]
        devs = [abs(x - med[h]) for x in vals]
        spr[h] = max(MIN_SPREAD, MAD_SCALE * quantile(devs, 0.5))

    pool = [(x - med[h]) / spr[h] for h in HOURS for x in (c[h] for c in comps if h in c)]
    if not pool:
        pool = [0.0]
    shape = [quantile(pool, lv) for lv in LEVELS]

    blend = {}
    for h in HOURS:
        blend[h] = [0.7 * emp[h][j] + 0.3 * (med[h] + shape[j] * spr[h])
                    for j in range(len(LEVELS))]

    sm = {}
    for h in HOURS:
        neigh = [k for k in (h - 1, h + 1) if k in blend]
        if not neigh:
            sm[h] = list(blend[h])
            continue
        sm[h] = [0.8 * blend[h][j] + 0.2 * (sum(blend[k][j] for k in neigh) / len(neigh))
                 for j in range(len(LEVELS))]

    hours = []
    for h in [r.get("hour") for r in (case.get("forecast") or [])]:
        row = sm[h]
        q = []
        run = 0
        for j in range(len(LEVELS)):
            val = round2(min(CAP, max(FLOOR, p1 * math.exp(row[j]))))
            if val > run:
                run = val
            q.append(run)
        hours.append({"hour": h, "q": q})
    return {"hours": hours}


def fallback(p1, case):
    """Widen a lognormal fan around p1 when no comparable is usable."""
    hours = []
    for h in [r.get("hour") for r in (case.get("forecast") or [])]:
        q = []
        run = 0
        for j, z in enumerate(FALLBACK_Z):
            val = round2(min(CAP, max(FLOOR, p1 * math.exp(z * 0.15 * math.sqrt(h - 1)))))
            if val > run:
                run = val
            q.append(run)
        hours.append({"hour": h, "q": q})
    return {"hours": hours}


def main():
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    for name in sorted(os.listdir(in_dir)):
        if not name.endswith(".in"):
            continue
        with open(os.path.join(in_dir, name), encoding="utf-8") as fh:
            case = json.load(fh)
        result = forecast_case(case)
        dest = os.path.join(out_dir, name[:-3] + ".out")
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(result, fh, separators=(",", ":"), allow_nan=False)
            fh.write("\n")


if __name__ == "__main__":
    main()