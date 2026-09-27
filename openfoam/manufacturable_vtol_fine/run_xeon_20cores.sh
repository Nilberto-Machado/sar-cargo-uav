#!/usr/bin/env bash
set -e

case_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
openfoam_bashrc=${OPENFOAM_BASHRC:-/opt/openfoam14/etc/bashrc}
. "$openfoam_bashrc"
set -u

ranks=20
end_time=${1:-1500}
label=${2:-"xeon_20cores_$(date -u +%Y%m%dT%H%M%SZ)"}

case "$end_time" in
    *[!0-9]*|'') echo "endTime must be a positive integer" >&2; exit 2 ;;
esac
if [ "$end_time" -lt 1 ]; then
    echo "endTime must be greater than zero" >&2
    exit 2
fi
if [ "$(nproc)" -lt "$ranks" ]; then
    echo "This host exposes only $(nproc) logical CPUs; 20 are required." >&2
    exit 3
fi

run_dir="$case_dir/benchmark_runs/$label"
if [ -e "$run_dir" ]; then
    echo "Run directory already exists: $run_dir" >&2
    exit 4
fi

mkdir -p "$run_dir"
cp -a "$case_dir/0.orig" "$run_dir/0"
cp -a "$case_dir/constant" "$run_dir/constant"
cp -a "$case_dir/system" "$run_dir/system"

foamDictionary "$run_dir/system/controlDict" -entry endTime -set "$end_time" >/dev/null
foamDictionary "$run_dir/system/decomposeParDict" -entry numberOfSubdomains -set "$ranks" >/dev/null

export OMP_NUM_THREADS=1
{
    echo "label=$label"
    echo "utc_start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "hostname=$(hostname)"
    echo "mpi_ranks=$ranks"
    echo "omp_threads=$OMP_NUM_THREADS"
    echo "end_time=$end_time"
    echo "cells=495958"
    echo "openfoam=$WM_PROJECT_VERSION"
    echo "kernel=$(uname -srmo)"
    echo
    lscpu
    echo
    free -h
} > "$run_dir/XEON_HARDWARE.txt"

cd "$run_dir"
echo "Initialising potential flow..."
potentialFoam > log.potentialFoam 2>&1
echo "Decomposing the 495,958-cell mesh into 20 domains..."
decomposePar -force > log.decomposePar 2>&1

echo "Running $end_time iterations on 20 pinned MPI ranks..."
/usr/bin/time -v -o XEON_PERFORMANCE_TIME.txt \
    mpirun -np "$ranks" --map-by core --bind-to core \
    foamRun -parallel > log.foamRun 2>&1

grep "^ExecutionTime" log.foamRun | tail -1 | tee SOLVER_TIME.txt
echo "Reconstructing the final fields..."
reconstructPar -latestTime > log.reconstructPar 2>&1
foamPostProcess -solver incompressibleFluid -func yPlus -latestTime > log.yPlus 2>&1
echo "utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> XEON_HARDWARE.txt

python3 "$case_dir/summarize_xeon_run.py" "$run_dir" | tee XEON_RESULT_SUMMARY.md
echo "Xeon run complete: $run_dir"
