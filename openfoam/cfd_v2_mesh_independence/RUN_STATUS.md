# Estado das execuções

Atualizado em 2026-09-24.

| Nível | Malha | `checkMesh` | Solução | Pós-processamento |
|---|---|---|---|---|
| coarse | 333.542 células em OF13 | padrão: `Mesh OK`; estrito: alerta de 13.246 células côncavas | smoke test serial de 2 iterações concluído; campanha não iniciada | `forceCoeffs` e estatísticas de `y+` executaram no smoke test |
| medium | somente bloco de fundo (58.240 células) | bloco: `Mesh OK`; snappy pendente | pendente | pendente |
| fine | somente bloco de fundo (127.296 células) | bloco: `Mesh OK`; snappy pendente | pendente | pendente |

O ambiente encontrado durante a implementação possui OpenFOAM 13 em
`/opt/openfoam13`. Os casos são destinados ao OpenFOAM 14, como a campanha
original; a validação de compatibilidade no OpenFOAM 13 é registrada aqui apenas
quando executada e não substitui a execução final em OF14.

## Resultado da validação de camadas no coarse

O `snappyHexMesh` OF13 concluiu sem erros e a malha final passou os controles
usuais de volume, face pyramids, skewness e não ortogonalidade. Porém, todas as
camadas solicitadas foram removidas pelo algoritmo de qualidade. Tentativas de
reter camadas — inclusive apenas uma — produziram faces invertidas e foram
rejeitadas. A configuração final não relaxa esses controles.

Consequentemente, a malha coarse gerada serve para validar a estrutura e o alvo
de células, mas ainda não é uma malha CFD v2 aceitável. O smoke test mediu
`y+ médio = 37.37` (`mín = 7.23`, `máx = 121.73`), coerente com a ausência de
camadas. A execução de produção fica bloqueada por `NO_PRISM_LAYERS` até que a
extrusão seja bem-sucedida no OpenFOAM 14 ou que a superfície seja preparada
em patches adequados para layer meshing.

O smoke test também confirmou carregamento de `kOmegaSST`, condições de
contorno, `forceCoeffs`, resíduos e os três objetos de estatística de `y+`.
