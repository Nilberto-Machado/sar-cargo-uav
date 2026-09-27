---
id: EXP-CFD-027
type: experiment
project: SAR-CARGO-UAV
domain: CFD
status: investigation
date: 2026-09-27
case_path: openfoam/cfd_v2_alpha_p4_noNearBody
openfoam: 14
velocity_ms: 25
aoa_deg: 4
cells: 160573
concave_cells: 5108
concave_faces: 213
warped_faces: 8
max_non_orthogonality_deg: 49.57469
max_skewness: 2.21152
tags:
  - CFD
  - OpenFOAM
  - mesh
---

# EXP-CFD-027 — Baseline 160573

## Case físico

`openfoam/cfd_v2_alpha_p4_noNearBody`

## Resultado

| Métrica | Valor |
|---|---:|
| Cells | 160573 |
| Faces | 505925 |
| Points | 185655 |
| Aspect ratio máximo | 5.062653 |
| Non-orthogonality máxima | 49.57469° |
| Non-orthogonality média | 7.962141° |
| Skewness máxima | 2.21152 |
| Concave faces | 213 |
| Ângulo côncavo máximo | 58.4278° |
| Warped faces | 8 |
| Concave cells | 5108 |

## checkMesh

**FAILED — 1 mesh check**

## Arquivos de diagnóstico

Gerados com:

`checkMesh -allGeometry -allTopology -writeSurfaces -surfaceFormat vtk`

Resultados:

- `concaveCells.vtk`
- `concaveFaces.vtk`
- `warpedFaces.vtk`

## Disposição de engenharia

**INVESTIGATION ONLY**

Esta malha não deve ser tratada como baseline aerodinâmica final.

## Issue

[[ISS-CFD-001 - Concave Cells]]

## Decisão

[[ADR-CFD-008 - Retessellate Geometry]]
