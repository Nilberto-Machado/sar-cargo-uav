#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd -P)"
removed_processors=0
removed_times=0
removed_initial_copies=0
removed_auxiliary=0
removed_bytes=0

delete_tree() {
    local target="$1"
    local resolved bytes
    resolved="$(realpath -e -- "$target")"
    case "$resolved" in
        "$root"/*) ;;
        *) echo "Refusing target outside OpenFOAM root: $resolved" >&2; exit 2 ;;
    esac
    bytes="$(du -sb -- "$resolved" | cut -f1)"
    removed_bytes=$((removed_bytes + bytes))
    find "$resolved" -depth -delete
}

# Parallel decompositions are reproducible from decomposeParDict and are never
# needed after the latest time has been reconstructed.
while IFS= read -r -d '' directory; do
    delete_tree "$directory"
    removed_processors=$((removed_processors + 1))
done < <(find "$root" -type d -regextype posix-extended -regex '.*/processor[0-9]+' -print0)

# In every OpenFOAM case, retain time 0 and the greatest positive reconstructed
# time. Delete only the positive intermediate times directly under the case.
while IFS= read -r -d '' control_dict; do
    case_dir="$(dirname "$(dirname "$control_dict")")"
    mapfile -d '' numeric_dirs < <(
        find "$case_dir" -mindepth 1 -maxdepth 1 -type d \
            -regextype posix-extended -regex '.*/[0-9]+([.][0-9]+)?' -print0
    )
    latest=""
    latest_value="-1"
    for directory in "${numeric_dirs[@]}"; do
        name="$(basename "$directory")"
        if awk -v value="$name" -v latest="$latest_value" 'BEGIN { exit !(value > latest) }'; then
            latest="$directory"
            latest_value="$name"
        fi
    done
    for directory in "${numeric_dirs[@]}"; do
        name="$(basename "$directory")"
        if [[ "$name" != "0" && "$directory" != "$latest" ]]; then
            delete_tree "$directory"
            removed_times=$((removed_times + 1))
        fi
    done
done < <(find "$root" -type f -path '*/system/controlDict' -print0)

# A case with 0.orig can recreate its runtime 0 directory through Allrun. Keep
# 0.orig and delete only the redundant copied directory when a final time exists.
while IFS= read -r -d '' initial_template; do
    case_dir="$(dirname "$initial_template")"
    if [[ -d "$case_dir/0" ]] && find "$case_dir" -mindepth 1 -maxdepth 1 -type d \
        -regextype posix-extended -regex '.*/[1-9][0-9]*([.][0-9]+)?' -print -quit | grep -q .; then
        delete_tree "$case_dir/0"
        removed_initial_copies=$((removed_initial_copies + 1))
    fi
done < <(find "$root" -type d -name 0.orig -print0)

# These are reproducible decomposition/feature-extraction artifacts.
while IFS= read -r -d '' artifact; do
    resolved="$(realpath -e -- "$artifact")"
    case "$resolved" in "$root"/*) ;; *) exit 2 ;; esac
    bytes="$(du -sb -- "$resolved" | cut -f1)"
    removed_bytes=$((removed_bytes + bytes))
    if [[ -d "$resolved" ]]; then find "$resolved" -depth -delete; else find "$resolved" -delete; fi
    removed_auxiliary=$((removed_auxiliary + 1))
done < <(find "$root" \( -type f -name cellProc -o -type d -name extendedFeatureEdgeMesh \) -print0)

# Superseded exploratory meshes from the earlier noNearBody campaign.
for experiment in \
    "$root/cfd_v2_alpha_p4_noNearBody/baseline_before_noExplicitSnap" \
    "$root/cfd_v2_alpha_p4_noNearBody/test_L5_explicit_OFF" \
    "$root/cfd_v2_alpha_p4_noNearBody/test_L5_explicit_ON"; do
    if [[ -d "$experiment" ]]; then
        delete_tree "$experiment"
        removed_auxiliary=$((removed_auxiliary + 1))
    fi
done

# Promote the accepted coarse-mesh logs to the standard names, then discard
# logs belonging to rejected layer experiments.
coarse="$root/manufacturable_mesh_families/cases/coarse"
if [[ -f "$coarse/log.checkMesh.partitioned2" ]]; then
    cp -- "$coarse/log.blockMesh.partitioned2" "$coarse/log.blockMesh"
    cp -- "$coarse/log.checkMesh.partitioned2" "$coarse/log.checkMesh"
    cp -- "$coarse/log.snappyHexMesh.partitioned2" "$coarse/log.snappyHexMesh"
    cp -- "$coarse/log.surfaceFeatures.partitioned" "$coarse/log.surfaceFeatures"
fi
find "$coarse" -maxdepth 1 -type f \( \
    -name 'log.*.layers' -o -name 'log.*.relative' -o \
    -name 'log.*.partitioned' -o -name 'log.*.partitioned2' \
\) -delete

printf 'Removed processor directories: %d\n' "$removed_processors"
printf 'Removed intermediate time directories: %d\n' "$removed_times"
printf 'Removed reproducible runtime-0 copies: %d\n' "$removed_initial_copies"
printf 'Removed auxiliary decomposition/experiment artifacts: %d\n' "$removed_auxiliary"
awk -v bytes="$removed_bytes" 'BEGIN { printf "Space represented by removed trees: %.2f GiB\n", bytes/1073741824 }'
