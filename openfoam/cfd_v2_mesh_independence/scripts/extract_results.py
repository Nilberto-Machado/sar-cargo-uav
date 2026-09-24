#!/usr/bin/env python3
"""Extract mesh counts, force coefficients and y+ metrics for the v2 campaign."""

from __future__ import annotations

import csv
import math
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("coarse", "medium", "fine")
WINDOW = 100


def latest_data_file(base: Path, preferred: tuple[str, ...]) -> Path | None:
    candidates: list[Path] = []
    if not base.exists():
        return None
    for name in preferred:
        candidates.extend(base.glob(f"**/{name}"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: float(p.parent.name) if p.parent.name.replace('.', '', 1).isdigit() else -1)


def numeric_rows(path: Path) -> tuple[list[str], list[list[float]]]:
    header: list[str] = []
    rows: list[list[float]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            cleaned = line.lstrip("# ").replace("(", "").replace(")", "")
            if cleaned.lower().startswith("time"):
                header = cleaned.split()
            continue
        try:
            rows.append([float(v) for v in line.replace("(", " ").replace(")", " ").split()])
        except ValueError:
            continue
    return header, rows


def coefficient_stats(case: Path) -> dict[str, float | int | str]:
    path = latest_data_file(case / "postProcessing" / "forceCoeffs", ("coefficient.dat", "forceCoeffs.dat"))
    if path is None:
        return {}
    header, rows = numeric_rows(path)
    if not rows:
        return {}
    cols = {name.lower(): i for i, name in enumerate(header)}
    indexes = {
        "Cd": cols.get("cd", 1),
        "Cl": cols.get("cl", 3),
        "Cm": cols.get("cmpitch", cols.get("cm", 5)),
    }
    tail = rows[-WINDOW:]
    result: dict[str, float | int | str] = {
        "samples": len(tail),
        "last_iteration": tail[-1][0],
        "force_file": str(path.relative_to(ROOT)),
    }
    for label, idx in indexes.items():
        values = [row[idx] for row in tail if len(row) > idx]
        if values:
            result[label] = statistics.fmean(values)
            result[f"{label}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
    return result


def mesh_cells(case: Path) -> int | None:
    log = case / "log.checkMesh"
    if not log.exists():
        return None
    matches = re.findall(r"^\s*cells:\s+(\d+)", log.read_text(encoding="utf-8", errors="replace"), re.MULTILINE)
    return int(matches[-1]) if matches else None


def yplus_value(case: Path, object_name: str) -> float | None:
    path = latest_data_file(case / "postProcessing" / object_name, ("surfaceFieldValue.dat",))
    if path is None:
        return None
    _, rows = numeric_rows(path)
    return rows[-1][1] if rows and len(rows[-1]) > 1 else None


def percent_change(coarser: float | None, finer: float | None) -> float | None:
    if coarser is None or finer is None or math.isclose(finer, 0.0, abs_tol=1e-14):
        return None
    return 100.0 * (coarser - finer) / abs(finer)


def fmt(value: object, digits: int = 6) -> str:
    if value is None or value == "":
        return "pending"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def main() -> None:
    records: list[dict[str, object]] = []
    for level in LEVELS:
        case = ROOT / "cases" / level
        record: dict[str, object] = {"level": level, "cells": mesh_cells(case)}
        record.update(coefficient_stats(case))
        record["yplus_min"] = yplus_value(case, "yPlusMin")
        record["yplus_avg"] = yplus_value(case, "yPlusAverage")
        record["yplus_max"] = yplus_value(case, "yPlusMax")
        records.append(record)

    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    fields = [
        "level", "cells", "samples", "last_iteration",
        "Cl", "Cl_std", "Cd", "Cd_std", "Cm", "Cm_std",
        "yplus_min", "yplus_avg", "yplus_max", "force_file",
    ]
    with (out_dir / "mesh_independence.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    lines = [
        "# Comparação de independência de malha", "",
        f"Médias e desvios calculados sobre até {WINDOW} amostras finais.", "",
        "| Malha | Células | Cl | σCl | Cd | σCd | Cm | σCm | y+ mín | y+ médio | y+ máx |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in records:
        lines.append("| " + " | ".join(fmt(r.get(k)) for k in (
            "level", "cells", "Cl", "Cl_std", "Cd", "Cd_std", "Cm", "Cm_std",
            "yplus_min", "yplus_avg", "yplus_max")) + " |")

    lines += ["", "## Variação em relação à malha imediatamente mais fina", "",
              "| Par | ΔCl | ΔCd | ΔCm |", "|---|---:|---:|---:|"]
    for a, b in zip(records, records[1:]):
        changes = [percent_change(a.get(key), b.get(key)) for key in ("Cl", "Cd", "Cm")]
        lines.append(f"| {a['level']} → {b['level']} | " + " | ".join(
            "pending" if value is None else f"{value:+.3f}%" for value in changes) + " |")
    lines += ["", "Sinal positivo significa que o valor da malha mais grossa é maior.", ""]
    (out_dir / "MESH_COMPARISON.md").write_text("\n".join(lines), encoding="utf-8")
    print(out_dir / "mesh_independence.csv")
    print(out_dir / "MESH_COMPARISON.md")


if __name__ == "__main__":
    main()

