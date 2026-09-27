# Cargo UAV — malha refinada

Caso derivado de `manufacturable_vtol`, preservando o baseline de 160.471 células.

- fundo: 52 x 40 x 28 células;
- superfície e arestas do UAV: nível 5;
- região próxima ao corpo: nível 2;
- limite global: 3 milhões de células;
- camadas prismáticas ainda desativadas para isolar o efeito do refinamento;
- solver: `incompressibleFluid`, RANS `kOmegaSST`;
- ponto: 25 m/s e +4 graus;
- execução: 1.500 iterações, 10 ranks MPI.

Os resultados devem ser comparados com `manufacturable_vtol` usando a média das
100 iterações finais e o tempo de parede informado pelo solver.

A execução concluída e a comparação estão documentadas em
`REFINED_MESH_REPORT.md`; os mesmos números estão disponíveis em formato legível
por máquina em `refined_results.json`.

## Execução no Xeon de 20 núcleos

Com OpenFOAM 14 disponível em `/opt/openfoam14`, execute:

```sh
bash run_xeon_20cores.sh 1500 xeon_20cores
```

O script usa 20 ranks MPI, fixa um rank por núcleo, registra a configuração de
hardware, mede somente o solver e gera `XEON_RESULT_SUMMARY.md`. Cada execução é
isolada em `benchmark_runs/` e não sobrescreve resultados existentes.
