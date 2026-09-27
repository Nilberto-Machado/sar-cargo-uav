# Validação inicial — montagem fabricável no OpenFOAM 14

## Geometria

- STL binário convertido de milímetros para metros;
- 84.446 triângulos e 42.225 vértices;
- dimensões: 2,850 x 4,200 x 0,905 m;
- superfície fechada, uma região conectada;
- nenhuma face ilegal, borda aberta ou borda não-manifold.

## Malha preliminar

- `blockMesh`: 58.240 células;
- `snappyHexMesh`: 160.471 células;
- patch do UAV: 10.198 faces;
- não ortogonalidade máxima: 46,28 graus;
- não ortogonalidade média: 7,90 graus;
- skewness máxima: 3,17;
- aspect ratio máximo: 5,45;
- volume mínimo: 4,51e-6 m3;
- `checkMesh`: `Mesh OK`.

## Smoke test

O solver `incompressibleFluid` com `kOmegaSST` completou 10 iterações em série,
confirmando a leitura da malha, das condições de contorno e do cálculo de forças.
Os coeficientes da iteração 10 foram `Cd = 0,02262`, `Cl = -0,01362` e
`Cm = 0,00395`. Esses valores são apenas transitórios e não representam uma
solução convergida.

O valor inicial de `y+` ficou entre 12,97 e 134,27, com média 51,82. Isso é
esperado porque esta primeira malha não possui camadas prismáticas; ela não deve
ser usada para dimensionamento aerodinâmico final.

## Execução completa

A campanha de 1.500 iterações foi concluída em 10 ranks MPI. O solver informou
`ClockTime = 254 s` e `ExecutionTime = 194,22 s`. A média das 100 iterações finais
foi `Cd = 0,045821`, `Cl = 0,280022` e `Cm = -0,029070`. Os respectivos desvios
padrão foram 0,000509, 0,006313 e 0,006476.

Os coeficientes permanecem oscilatórios na janela final, principalmente `Cl` e
`Cm`. A solução é adequada como baseline computacional e avaliação preliminar,
mas não deve ser tratada como resultado aerodinâmico convergido de alta fidelidade.

No passo 1.500, o solver registrou `y+` entre 18,48 e 379,02, com média de área
129,94. O pós-processamento do campo reconstruído calculou média 134,65.

Os detalhes reproduzíveis de hardware e desempenho estão em
`PERFORMANCE_BASELINE.md` e `baseline_core7_240h_10ranks.json`.

## Próxima etapa

Executar a solução até convergência e, em seguida, preparar uma malha de maior
fidelidade com camadas de parede. Para representar propulsão, os rotores devem ser
separados em patches próprios e modelados por disco atuador, MRF ou malha móvel.
