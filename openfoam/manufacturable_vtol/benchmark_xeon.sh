#!/usr/bin/env bash
set -e

case_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
openfoam_bashrc=${OPENFOAM_BASHRC:-/opt/openfoam14/etc/bashrc}
. "$openfoam_bashrc"
set -u

ranks=${1:-10}
end_time=${2:-1500}
label=${3:-"$(hostname)_${ranks}r_$(date -u +%Y%m%dT%H%M%SZ)"}

case "$ranks:$end_time" in
    *[!0-9:]*|:*|*:) echo "Ranks and endTime must be positive integers" >&2; exit 2 ;;
esac
if [ "$ranks" -lt 1 ] || [ "$end_time" -lt 1 ]; then
    echo "Ranks and endTime must be greater than zero" >&2
    exit 2
fi

run_dir="$case_dir/benchmark_runs/$label"
if [ -e "$run_dir" ]; then
    echo "Benchmark directory already exists: $run_dir" >&2
    exit 3
fi

mkdir -p "$run_dir"
cp -a "$case_dir/0.orig" "$run_dir/0"
cp -a "$case_dir/constant" "$run_dir/constant"
cp -a "$case_dir/system" "$run_dir/system"

foamDictionary "$run_dir/system/controlDict" -entry endTime -set "$end_time" >/dev/null
foamDictionary "$run_dir/system/decomposeParDict" -entry numberOfSubdomains -set "$ranks" >/dev/null

{
    echo "label=$label"
    echo "utc_start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "hostname=$(hostname)"
    echo "ranks=$ranks"
    echo "end_time=$end_time"
    echo "openfoam=$WM_PROJECT_VERSION"
    echo "kernel=$(uname -srmo)"
    echo
    lscpu
    echo
    free -h
} > "$run_dir/BENCHMARK_METADATA.txt"

cd "$run_dir"
potentialFoam > log.potentialFoam 2>&1
decomposePar -force > log.decomposePar 2>&1

echo "Running $end_time iterations with $ranks MPI ranks in $run_dir"
/usr/bin/time -v -o PERFORMANCE_TIME.txt \
    mpirun --oversubscribe -np "$ranks" foamRun -parallel > log.foamRun 2>&1

grep "^ExecutionTime" log.foamRun | tail -1 | tee SOLVER_TIME.txt
echo "utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> BENCHMARK_METADATA.txt
echo "Benchmark complete: $run_dir"
