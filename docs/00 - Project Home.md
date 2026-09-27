---
type: project-home
project: SAR-CARGO-UAV
status: active
---

# SAR Cargo UAV

> Base de conhecimento e mem�ria t�cnica do projeto.

## Master Record

[[SAR Cargo UAV Engineering Master Record]]

## Project Definition

- [[Requirements - Home]]
- [[Architecture - Home]]

## Engineering

- [[Decisions - Home]]
- [[Lessons Learned - Home]]
- [[Engineering Issues - Home]]

## CFD / OpenFOAM

- [[OpenFOAM - Home]]
- [[CFD Experiments - Home]]
- [[Mesh Quality]]
- [[Geometry Preparation]]

## Numerical Wind Tunnel

- [[Numerical Tank - Home]]
- [[Compute Nodes]]
- [[Benchmarks]]
- [[Job Queue]]

## Propulsion

- [[Propulsion - Home]]

## Avionics

- [[Avionics - Home]]

## Aerodynamics

- [[Aerodynamics - Home]]

---

# Current CFD Baseline

Case:

`openfoam/cfd_v2_alpha_p4_noNearBody`

| M�trica | Valor |
|---|---:|
| Cells | 160573 |
| Concave cells | 5108 |
| Concave faces | 213 |
| Warped faces | 8 |
| Max non-orthogonality | 49.57469� |
| Max skewness | 2.21152 |

Problema atual:

[[ISS-CFD-001 - Concave Cells]]

Decis�o atual:

[[ADR-CFD-008 - Retessellate Geometry]]

## Current CFD Workflow

STEP  
? Geometry validation  
? Controlled tessellation  
? STL  
? surfaceFeatureExtract  
? blockMesh  
? snappyHexMesh  
? checkMesh  
? Mesh independence  
? Validated aerodynamic polar

## Current Priorities

1. Confirmar STEP mestre.
2. Corrigir/validar geometria.
3. Gerar tessela��o controlada.
4. Repetir baseline compar�vel.
5. Investigar concave cells.
6. Executar mesh independence.
7. Reexecutar polar aerodin�mica.
8. Dimensionar propuls�o e combust�vel.
