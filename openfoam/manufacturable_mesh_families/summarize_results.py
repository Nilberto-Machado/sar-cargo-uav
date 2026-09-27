#!/usr/bin/env python3
"""Summarize the three mesh-family runs without external dependencies."""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"


def last_match(path: Path, pattern: str, cast=float):
    matches = re.findall(pattern, path.read_text(errors="replace"), re.MULTILINE)
    if not matches:
        raise RuntimeError(f"No match for {pattern!r} in {path}")
    return cast(matches[-1])


def coefficient_stats(path: Path, start: float = 901.0):
    rows = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        values = [float(value) for value in line.split()]
        if values[0] >= start:
            rows.append(values)
    if not rows:
        raise RuntimeError(f"No coefficient samples at t >= {start} in {path}")
    columns = {"Cm": 1, "Cd": 2, "Cl": 3}
    return {
        key: {
            "mean": statistics.fmean(row[index] for row in rows),
            "stdev": statistics.stdev(row[index] for row in rows),
        }
        for key, index in columns.items()
    } | {"samples": len(rows)}


def summarize_case(name: str):
    case = CASES / name
    check = case / "log.checkMesh"
    solver = case / "log.foamRun"
    walltime = case / "log.walltime"
    yplus = case / "log.foamPostProcess"
    coeffs = case / "postProcessing/forceCoeffs/0/forceCoeffs.dat"
    return {
        "cells": last_match(check, r"^\s*cells:\s+(\d+)", int),
        "max_non_orthogonality_deg": last_match(
            check, r"Mesh non-orthogonality Max:\s*([0-9.eE+-]+)"
        ),
        "max_skewness": last_match(check, r"Max skewness\s*=\s*([0-9.eE+-]+)"),
        "solver_clock_s": last_match(solver, r"ClockTime\s*=\s*(\d+)\s+s", int),
        "wall_time": last_match(
            walltime, r"^\s*Elapsed \(wall clock\) time .*\):\s*(\S+)\s*$", str
        ).strip(),
        "max_rss_kib": last_match(
            walltime, r"Maximum resident set size \(kbytes\):\s*(\d+)", int
        ),
        "yplus_airframe_avg": last_match(
            yplus, r"patch aircraft_airframe y\+ .*?average\s*=\s*([0-9.eE+-]+)"
        ),
        "coefficients_last_100": coefficient_stats(coeffs),
    }


def main():
    data = {name: summarize_case(name) for name in ("coarse", "medium", "fine")}
    fine = data["fine"]["coefficients_last_100"]
    for values in data.values():
        coeffs = values["coefficients_last_100"]
        values["difference_from_fine_percent"] = {
            key: 100.0 * (coeffs[key]["mean"] - fine[key]["mean"]) / abs(fine[key]["mean"])
            for key in ("Cd", "Cl", "Cm")
        }
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
