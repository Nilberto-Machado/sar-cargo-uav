---
id: REQ-008
type: requirement
project: SAR-CARGO-UAV
domain: Avionics
status: preliminary
verification: inspection-analysis-and-test
---

# REQ-008 — Navegação com fusão sensorial e EKF

## Requisito

O sistema de navegação deverá utilizar **GNSS, IMU, Pitot, barômetro e magnetômetro**, integrados por fusão sensorial baseada em **EKF**.

## Critérios de aceitação

- Confirmar por inspeção a presença e integração das classes de sensores definidas.
- Demonstrar por análise e ensaio que o EKF produz uma estimativa de estado adequada ao controle e à navegação.
- Arquitetura, quantidade de sensores, redundância, taxas, precisão e limites aceitáveis de erro: **TBD**.

## Rastreabilidade

- [[Requirements - Home]]
- [[REQ-001 - Operação SAR e humanitária]]
- [[REQ-009 - Segurança e fail-safe]]
