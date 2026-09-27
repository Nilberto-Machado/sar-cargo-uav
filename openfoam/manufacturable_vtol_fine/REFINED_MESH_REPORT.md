# Resultado da malha refinada

Data: 2026-09-27

## Configuração

- OpenFOAM 14 no WSL2;
- 25 m/s, incidência de +4 graus;
- `incompressibleFluid`, RANS `kOmegaSST`;
- 10 ranks MPI com `--oversubscribe`;
- 1.500 iterações;
- hélices e tilt-rotors tratados como superfícies estacionárias;
- sem camadas prismáticas.

## Qualidade da malha

| Métrica | Baseline | Refinada |
|---|---:|---:|
| Células | 160.471 | 495.958 |
| Razão de células | 1,00 | 3,091 |
| Faces no UAV | 10.198 | 39.474 |
| Não ortogonalidade máxima | 46,28 graus | 51,12 graus |
| Não ortogonalidade média | 7,90 graus | 8,04 graus |
| Skewness máxima | 3,17 | 2,52 |
| Aspect ratio máximo | 5,45 | 5,50 |
| `checkMesh` | `Mesh OK` | `Mesh OK` |

## Convergência e coeficientes

Média das 100 iterações finais:

| Coeficiente | Baseline | Refinada | Variação |
|---|---:|---:|---:|
| `Cd` | 0,045821 | 0,029255 | -36,15% |
| `Cl` | 0,280022 | 0,303722 | +8,46% |
| `Cm` | -0,029070 | -0,013720 | -52,80% em magnitude |

Estabilidade da malha refinada na janela final:

| Coeficiente | Média | Desvio padrão | Mínimo | Máximo |
|---|---:|---:|---:|---:|
| `Cd` | 0,029255 | 0,00000224 | 0,029251 | 0,029259 |
| `Cl` | 0,303722 | 0,0000268 | 0,303669 | 0,303764 |
| `Cm` | -0,013720 | 0,0000143 | -0,013742 | -0,013693 |

A solução refinada convergiu de modo muito mais estável. As diferenças grandes em
relação ao baseline mostram que a malha de 160 mil células não era independente e
que seus coeficientes não devem ser usados como referência aerodinâmica final.
Com `rho = 1,225 kg/m3`, 25 m/s e `Aref = 2,604 m2`, as médias refinadas equivalem
a aproximadamente 302,8 N de sustentação e 29,2 N de arrasto.

## Desempenho

- `ClockTime`: 634 s;
- `ExecutionTime`: 573,63 s;
- desempenho: 2,366 iterações/s;
- tempo por iteração: 0,423 s;
- throughput: 1,173 milhões de células-iteração/s;
- custo de parede: 2,496 vezes o baseline para 3,091 vezes mais células;
- throughput normalizado: 23,82% maior que no baseline.

## Parede

| Métrica `y+` | Baseline | Refinada |
|---|---:|---:|
| mínimo | 18,48 | 13,58 |
| máximo | 379,02 | 164,37 |
| média pós-processada | 134,65 | 94,78 |

O refinamento reduziu o `y+` médio em 29,61% e limitou melhor os picos, porém os
valores continuam altos para uma estratégia wall-resolved. A próxima malha deve
introduzir camadas prismáticas ou adotar explicitamente uma estratégia de funções
de parede compatível.
