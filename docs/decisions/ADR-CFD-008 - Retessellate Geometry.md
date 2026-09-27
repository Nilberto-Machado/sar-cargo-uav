---
id: ADR-CFD-008
type: decision
project: SAR-CARGO-UAV
domain: CFD
status: accepted
date: 2026-09-27
---

# ADR-CFD-008 — Retessellate Geometry

## Contexto

As malhas atuais apresentam milhares de células côncavas.

## Alternativas consideradas

1. Aumentar refinamento.
2. Alterar parâmetros de feature snapping.
3. Desabilitar snap.
4. Corrigir geometria e tesselação superficial.

## Evidências

- [[EXP-CFD-021 - Baseline 160804]]
- [[EXP-CFD-024 - L5 392471]]
- [[EXP-CFD-026 - noSnap Diagnostic]]
- [[EXP-CFD-027 - Baseline 160573]]

## Decisão

Executar o fluxo:

STEP  
→ validação/limpeza geométrica  
→ tesselação controlada  
→ STL  
→ surfaceCheck  
→ snappyHexMesh  
→ checkMesh

antes de aumentar significativamente a resolução volumétrica.

## Racional

O refinamento L5 não eliminou o problema.

O diagnóstico noSnap demonstrou que células côncavas aparecem antes do snap.

A tesselação superficial tornou-se portanto o principal alvo da investigação.

## Consequências positivas

- ataque à provável causa raiz;
- menor desperdício computacional;
- futura mesh independence sobre geometria mais confiável.

## Consequências negativas

- etapa adicional de preparação CAD.

## Revisar quando

Depois que um novo STL controlado for testado.
