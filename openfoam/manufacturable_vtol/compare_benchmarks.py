"""Compare Xeon benchmark runs with the saved Core 7 240H baseline."""

from pathlib import Path
import json
import re
import sys


HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "baseline_core7_240h_10ranks.json").read_text())


def read_run(path):
    path = Path(path)
    log = (path / "log.foamRun").read_text(errors="replace")
    matches = re.findall(r"ExecutionTime\s*=\s*([0-9.]+)\s*s\s+ClockTime\s*=\s*([0-9.]+)\s*s", log)
    if not matches:
        raise RuntimeError(f"No completed solver timing found in {path}")
    _, clock = map(float, matches[-1])
    metadata = {}
    for line in (path / "BENCHMARK_METADATA.txt").read_text(errors="replace").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            metadata[key] = value
    iterations = int(metadata.get("end_time", BASELINE["iterations"]))
    ranks = int(metadata.get("ranks", 0))
    return metadata.get("label", path.name), ranks, iterations, clock


rows = [(
    "Core7_240H_baseline",
    BASELINE["mpi_ranks"],
    BASELINE["iterations"],
    BASELINE["solver_clock_time_s"],
)]
rows.extend(read_run(argument) for argument in sys.argv[1:])
baseline_rate = BASELINE["iterations"] / BASELINE["solver_clock_time_s"]

print("| Execução | Ranks | Iterações | ClockTime (s) | Iterações/s | Speedup vs Core 7 |")
print("|---|---:|---:|---:|---:|---:|")
for label, ranks, iterations, clock in rows:
    rate = iterations / clock
    print(f"| {label} | {ranks} | {iterations} | {clock:.1f} | {rate:.3f} | {rate / baseline_rate:.3f}x |")
