# Baseline de desempenho — Core 7 240H

Data: 2026-09-27

## Ambiente

- CPU do host: Intel Core 7 240H, 10 núcleos / 16 processadores lógicos;
- CPU exposta ao WSL2: 8 núcleos / 16 threads;
- memória disponível no WSL2: 15 GiB;
- sistema: WSL2 Ubuntu 22.04;
- OpenFOAM: versão 14;
- ranks MPI: 10, com `--oversubscribe`;
- malha: 160.471 células;
- solver: `incompressibleFluid`, RANS `kOmegaSST`;
- iterações: 1.500.

## Tempo

- `ClockTime` informado pelo solver: 254 s;
- `ExecutionTime` informado pelo processo principal: 194,22 s;
- desempenho baseado em tempo de parede: 5,91 iterações/s;
- tempo por iteração: 0,169 s;
- throughput de referência: aproximadamente 0,948 milhão de células-iteração/s.

Para comparação entre máquinas, usar o `ClockTime`, o mesmo número de ranks, a
mesma malha e a mesma quantidade de iterações. O tempo de preparação, decomposição
e reconstrução não está incluído no tempo do solver acima.

## Resultado aerodinâmico

Média das 100 iterações finais:

| Coeficiente | Média | Desvio padrão | Mínimo | Máximo |
|---|---:|---:|---:|---:|
| `Cd` | 0,045821 | 0,000509 | 0,045275 | 0,046852 |
| `Cl` | 0,280022 | 0,006313 | 0,270416 | 0,289223 |
| `Cm` | -0,029070 | 0,006476 | -0,045466 | -0,020834 |

Os coeficientes ainda apresentam oscilação na janela final. A execução serve como
baseline de desempenho e resultado preliminar, não como solução aerodinâmica final.

## Parede

- `y+` mínimo: 18,48;
- `y+` máximo: 379,02;
- `y+` médio no último passo do solver: 129,94;
- `y+` médio recalculado após reconstrução: 134,65.

A malha não possui camadas prismáticas; esses valores confirmam que uma malha de
parede de maior fidelidade será necessária para o resultado final.
