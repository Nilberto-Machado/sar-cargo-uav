---
id: LES-CFD-004
type: lesson
project: SAR-CARGO-UAV
domain: CFD
status: active
---

# LES-CFD-004 — More Refinement Does Not Guarantee Better Mesh

## Observação

Aumentar a malha de aproximadamente 160 mil para aproximadamente 392 mil células não eliminou as células côncavas.

## Evidência

[[EXP-CFD-024 - L5 392471]]

## Interpretação

Número de células não é, isoladamente, indicador de qualidade da malha.

## Impacto

Investigar geometria e tesselação antes de aumentar agressivamente o refinamento.
