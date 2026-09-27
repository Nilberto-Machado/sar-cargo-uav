$ErrorActionPreference = "Stop"

$Root = (Get-Location).Path

function Write-Note {
    param(
        [string]$Path,
        [string]$Content
    )

    $FullPath = Join-Path $Root $Path

    if (-not (Test-Path $FullPath)) {
        Set-Content -Path $FullPath -Value $Content -Encoding UTF8
        Write-Host "[CRIADO] $Path" -ForegroundColor Green
    }
    else {
        Write-Host "[EXISTE] $Path" -ForegroundColor Yellow
    }
}

# ============================================================
# ISSUE
# ============================================================

Write-Note "docs\issues\ISS-CFD-001 - Concave Cells.md" @'
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
'@

# ============================================================
# EXP 021
# ============================================================

Write-Note "docs\experiments\EXP-CFD-021 - Baseline 160804.md" @'
---
id: EXP-CFD-021
type: experiment
project: SAR-CARGO-UAV
domain: CFD
status: investigation
cells: 160804
concave_cells: 5416
---

# EXP-CFD-021 — Baseline 160804

## Resultado

| Métrica | Valor |
|---|---:|
| Cells | 160804 |
| Aspect ratio máximo | 5.208878 |
| Non-orthogonality máxima | 54.70829° |
| Non-orthogonality média | 8.046341° |
| Skewness máxima | 3.611411 |
| Concave faces | 178 |
| Concave cells | 5416 |

## checkMesh

**FAILED — 1 mesh check**

## Relacionado

[[ISS-CFD-001 - Concave Cells]]
'@

# ============================================================
# EXP 024
# ============================================================

Write-Note "docs\experiments\EXP-CFD-024 - L5 392471.md" @'
---
id: EXP-CFD-024
type: experiment
project: SAR-CARGO-UAV
domain: CFD
status: investigation
cells: 392471
concave_cells: 13893
---

# EXP-CFD-024 — L5 392471

## Objetivo

Verificar se um refinamento significativamente maior reduziria os problemas geométricos.

## Resultado

| Métrica | Valor |
|---|---:|
| Cells | 392471 |
| Concave cells | 13893 |
| Non-orthogonality máxima | ~45.7° |
| Skewness máxima | ~2.49 |

## Resultado do checkMesh

**FAILED — 1 mesh check**

## Conclusão

O aumento de aproximadamente 160 mil para 392 mil células não eliminou o problema.

## Lição derivada

[[LES-CFD-004 - More Refinement Does Not Guarantee Better Mesh]]

## Issue relacionado

[[ISS-CFD-001 - Concave Cells]]
'@

# ============================================================
# EXP 026 - noSnap
# ============================================================

Write-Note "docs\experiments\EXP-CFD-026 - noSnap Diagnostic.md" @'
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
'@

# ============================================================
# EXP 027 - última baseline
# ============================================================

Write-Note "docs\experiments\EXP-CFD-027 - Baseline 160573.md" @'
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
'@

# ============================================================
# LESSON 004
# ============================================================

Write-Note "docs\lessons\LES-CFD-004 - More Refinement Does Not Guarantee Better Mesh.md" @'
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
'@

# ============================================================
# LESSON 008
# ============================================================

Write-Note "docs\lessons\LES-CFD-008 - Concave Cells Exist Before Snap.md" @'
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
'@

# ============================================================
# ADR
# ============================================================

Write-Note "docs\decisions\ADR-CFD-008 - Retessellate Geometry.md" @'
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
'@

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " Knowledge graph CFD criado" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""