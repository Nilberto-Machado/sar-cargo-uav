"""Summarize a completed 20-core Xeon OpenFOAM run."""

from pathlib import Path
import re
import statistics
import sys


run = Path(sys.argv[1]).resolve()
log = (run / "log.foamRun").read_text(errors="replace")
timings = re.findall(
    r"ExecutionTime\s*=\s*([0-9.]+)\s*s\s+ClockTime\s*=\s*([0-9.]+)\s*s",
    log,
)
if not timings:
    raise SystemExit("No completed solver timing found")
execution_time, clock_time = map(float, timings[-1])

coeff_file = run / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat"
rows = []
for line in coeff_file.read_text(errors="replace").splitlines():
    text = line.strip()
    if text and not text.startswith("#"):
        rows.append([float(value) for value in text.split()])
window = rows[-min(100, len(rows)):]

def metric(column):
    values = [row[column] for row in window]
    return statistics.mean(values), statistics.pstdev(values)

cm, cm_std = metric(1)
cd, cd_std = metric(2)
cl, cl_std = metric(3)
iterations = int(rows[-1][0])
rate = iterations / clock_time
baseline_clock = 634.0
baseline_rate = 1500.0 / baseline_clock

print("# Resultado do benchmark Xeon — 20 núcleos")
print()
print(f"- Diretório: `{run}`")
print(f"- Iterações: {iterations}")
print(f"- ClockTime: {clock_time:.1f} s")
print(f"- ExecutionTime: {execution_time:.2f} s")
print(f"- Desempenho: {rate:.3f} iterações/s")
print(f"- Speedup contra Core 7 240H/10 ranks: {rate / baseline_rate:.3f}x")
print()
print("Média das 100 iterações finais:")
print()
print("| Coeficiente | Média | Desvio padrão |")
print("|---|---:|---:|")
print(f"| Cd | {cd:.8f} | {cd_std:.8f} |")
print(f"| Cl | {cl:.8f} | {cl_std:.8f} |")
print(f"| Cm | {cm:.8f} | {cm_std:.8f} |")
