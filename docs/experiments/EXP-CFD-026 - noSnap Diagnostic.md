---
id: EXP-CFD-026
type: experiment
project: SAR-CARGO-UAV
domain: CFD
status: diagnostic
cells: 160804
concave_cells: 7353
---

# EXP-CFD-026 — noSnap Diagnostic

## Objetivo

Determinar se o processo de snap era a principal origem das células côncavas.

## Configuração

Snap desabilitado.

## Resultado

| Métrica | Valor |
|---|---:|
| Cells | 160804 |
| Hexahedra | 149476 |
| Polyhedra | 11328 |
| Aspect ratio máximo | 1 |
| Non-orthogonality máxima | 25.2394° |
| Non-orthogonality média | 7.473587° |
| Skewness máxima | 0.3333333 |
| Concave cells | 7353 |

## checkMesh

**FAILED — 1 mesh check**

## Conclusão

As células côncavas já existem antes do processo de snap.

## Lição derivada

[[LES-CFD-008 - Concave Cells Exist Before Snap]]

## Issue relacionado

[[ISS-CFD-001 - Concave Cells]]
