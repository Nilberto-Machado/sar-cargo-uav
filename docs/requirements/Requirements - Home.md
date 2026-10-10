---
type: requirements-home
project: SAR-CARGO-UAV
status: active
baseline: preliminary
date: 2026-09-27
---

# Requirements — Home

> Primeira baseline de requisitos de engenharia do SAR Cargo UAV. Os itens marcados como `preliminary` ainda precisam de validação; campos `TBD` não devem ser interpretados como decisões fechadas.

## Missão e desempenho

- [[REQ-001 - Operação SAR e humanitária]]
- [[REQ-002 - Payload alvo de 5 kg]]
- [[REQ-003 - Alcance alvo de aproximadamente 400 km]]
- [[REQ-004 - Cruzeiro baseline de 25 m-s]]
- [[REQ-005 - Cenário de alta velocidade de 200 km-h]]

## Configuração e propulsão

- [[REQ-006 - Propulsão a gasolina com partida elétrica]]
- [[REQ-007 - Arquitetura conceitual de asa fixa pusher]]

## Navegação e segurança

- [[REQ-008 - Navegação com fusão sensorial e EKF]]
- [[REQ-009 - Segurança e fail-safe]]

## Engenharia e verificação

- [[REQ-010 - Rastreabilidade de engenharia]]
- [[REQ-011 - Verificação aerodinâmica por CFD e OpenFOAM]]

## Estado da baseline

| ID | Resumo | Status |
|---|---|---|
| [[REQ-001 - Operação SAR e humanitária|REQ-001]] | Operação SAR/humanitária | preliminary |
| [[REQ-002 - Payload alvo de 5 kg|REQ-002]] | Payload alvo de 5 kg | preliminary |
| [[REQ-003 - Alcance alvo de aproximadamente 400 km|REQ-003]] | Alcance alvo ~400 km; interpretação TBD | preliminary |
| [[REQ-004 - Cruzeiro baseline de 25 m-s|REQ-004]] | Cruzeiro baseline 25 m/s (~90 km/h) | preliminary |
| [[REQ-005 - Cenário de alta velocidade de 200 km-h|REQ-005]] | Cenário de estudo ~200 km/h | study |
| [[REQ-006 - Propulsão a gasolina com partida elétrica|REQ-006]] | Gasolina e partida elétrica | preliminary |
| [[REQ-007 - Arquitetura conceitual de asa fixa pusher|REQ-007]] | Asa fixa/pusher; VTOL em estudo | preliminary |
| [[REQ-008 - Navegação com fusão sensorial e EKF|REQ-008]] | GNSS, IMU, Pitot, barômetro e magnetômetro | preliminary |
| [[REQ-009 - Segurança e fail-safe|REQ-009]] | Comportamento seguro diante de falhas | preliminary |
| [[REQ-010 - Rastreabilidade de engenharia|REQ-010]] | Ligações com ADR, EXP e LES | preliminary |
| [[REQ-011 - Verificação aerodinâmica por CFD e OpenFOAM|REQ-011]] | CFD/OpenFOAM como método de verificação | preliminary |

## Convenções

- `preliminary`: requisito proposto para a baseline inicial, ainda sujeito a validação e congelamento.
- `study`: cenário ou hipótese de engenharia; não constitui requisito congelado.
- `TBD`: definição, critério ou interpretação ainda pendente.

## Navegação

- [[00 - Project Home]]
- [[OpenFOAM - Home]]
- [[Numerical Tank - Home]]
- [[ADR-CFD-008 - Retessellate Geometry]]
- [[EXP-CFD-021 - Baseline 160804]]
- [[LES-CFD-004 - More Refinement Does Not Guarantee Better Mesh]]
