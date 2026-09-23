# Relatório da primeira validação CFD

## Caso executado

- OpenFOAM 14 no WSL Ubuntu 22.04
- Escoamento externo estacionário e incompressível
- Velocidade: 25 m/s
- Ângulo de ataque geométrico: 0°
- Turbulência: RANS `kOmegaSST`
- Hélices e forças propulsivas: não incluídas
- Área de referência: 2,604 m²
- Corda média: 0,6415 m
- Centro de momentos: X = 1,07 m

## Geometria

- STL: 10.258 triângulos
- Dimensões: 2,85 × 4,20 × 0,904 m
- Superfície fechada, uma região conectada
- Nenhum triângulo ilegal ou aresta aberta

## Malha preliminar

- 269.773 células
- Não ortogonalidade: máxima 60,45°, média 7,36°
- Skewness máxima: 3,981
- Aspect ratio máximo: 6,19
- `checkMesh` padrão: `Mesh OK`
- Sem camadas prismáticas nesta primeira rodada
- A verificação `-allGeometry -allTopology` registra 8.799 células côncavas;
  esta limitação precisa ser reduzida na malha de fidelidade seguinte.

## Resultado preliminar

Média das iterações 140–150:

| Coeficiente | Média | Faixa observada |
|---|---:|---:|
| CM | 0,010913 | 0,000069 |
| CD | 0,065456 | 0,000029 |
| CL | -0,012470 | 0,000078 |

O valor de sustentação próximo de zero é coerente com o caso a 0° e com a
incidência geométrica atual. Estes números ainda não devem ser usados para
dimensionamento, pois faltam estudo de independência de malha, camadas de parede,
avaliação de `y+`, varredura de ângulo de ataque e modelagem propulsiva.

## Próximas validações

1. Gerar malha com camadas prismáticas consistentes e reduzir células côncavas.
2. Executar incidências de -4° a 12° em passos de 2°.
3. Comparar malhas grossa, média e fina.
4. Verificar `y+` e ajustar a primeira altura de camada.
5. Acrescentar o pusher como disco atuador ou região MRF.
6. Tratar o modo VTOL em caso transiente separado.

