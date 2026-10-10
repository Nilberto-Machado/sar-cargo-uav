---
id: REQ-011
type: requirement
project: SAR-CARGO-UAV
domain: Aerodynamics
status: preliminary
verification: inspection
---

# REQ-011 — Verificação aerodinâmica por CFD e OpenFOAM

## Requisito

O desenvolvimento deverá utilizar análises CFD em **OpenFOAM** como método de verificação aerodinâmica das configurações e pontos de operação relevantes.

## Critérios de aceitação

- Registrar configuração, geometria, malha, condições de contorno, solver, resultados e verificações de qualidade em notas EXP.
- Manter ligação entre os experimentos CFD, os requisitos avaliados, as decisões resultantes e as lições aprendidas.
- Casos obrigatórios, critérios de convergência, independência de malha e margens de aceitação: **TBD**.

## Observação

Este requisito define CFD/OpenFOAM como método de verificação, sem excluir ensaios físicos ou outros métodos complementares que venham a ser definidos.

## Rastreabilidade

- [[Requirements - Home]]
- [[REQ-004 - Cruzeiro baseline de 25 m-s]]
- [[REQ-005 - Cenário de alta velocidade de 200 km-h]]
- [[REQ-007 - Arquitetura conceitual de asa fixa pusher]]
- [[OpenFOAM - Home]]
- [[EXP-CFD-021 - Baseline 160804]]
- [[EXP-CFD-024 - L5 392471]]
- [[LES-CFD-004 - More Refinement Does Not Guarantee Better Mesh]]
- [[ADR-CFD-008 - Retessellate Geometry]]
