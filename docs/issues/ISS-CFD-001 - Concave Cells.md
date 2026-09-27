---
id: ISS-CFD-001
type: issue
project: SAR-CARGO-UAV
domain: CFD
status: open
severity: high
tags:
  - CFD
  - OpenFOAM
  - mesh
---

# ISS-CFD-001 — Concave Cells

## Problema

As malhas atuais do SAR Cargo UAV apresentam milhares de células côncavas.

## Evidências

- [[EXP-CFD-021 - Baseline 160804]]
- [[EXP-CFD-024 - L5 392471]]
- [[EXP-CFD-026 - noSnap Diagnostic]]
- [[EXP-CFD-027 - Baseline 160573]]

## Interpretação atual

O problema não parece estar associado exclusivamente ao processo de snap.

A geometria superficial e a tesselação STEP → STL são atualmente os principais suspeitos.

## Lição relacionada

[[LES-CFD-008 - Concave Cells Exist Before Snap]]

## Decisão atual

[[ADR-CFD-008 - Retessellate Geometry]]
