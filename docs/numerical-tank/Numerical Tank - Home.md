---
type: index
project: SAR-CARGO-UAV
domain: numerical-computing
---

# Numerical Wind Tunnel

## Objetivo

Infraestrutura de computação dedicada às campanhas CFD do SAR Cargo UAV.

## Compute Nodes

[[Compute Nodes]]

## Jobs

[[Job Queue]]

## Benchmarks

[[Benchmarks]]

## Arquitetura

Aurora / Workstation  
→ Git Repository  
→ CFD Nodes Linux  
→ Job Queue  
→ OpenFOAM  
→ Results  
→ ParaView / Engineering Analysis

## Princípios atuais

- Linux nativo preferencial para compute nodes.
- Distribuir inicialmente casos independentes entre máquinas.
- Definir Hyper-Threading por benchmark.
- Registrar node, número de processos e runtime em toda simulação.
