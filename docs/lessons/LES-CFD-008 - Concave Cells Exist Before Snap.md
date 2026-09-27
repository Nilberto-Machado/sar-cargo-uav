---
id: LES-CFD-008
type: lesson
project: SAR-CARGO-UAV
domain: CFD
status: active
---

# LES-CFD-008 — Concave Cells Exist Before Snap

## Observação

O experimento `noSnap` apresentou 7353 células côncavas mesmo com o snap desabilitado.

## Evidência

[[EXP-CFD-026 - noSnap Diagnostic]]

## Interpretação

O snap não é a causa exclusiva do problema.

A interação entre castellation e representação superficial deve ser investigada.

## Impacto

Esta evidência suporta:

[[ADR-CFD-008 - Retessellate Geometry]]
