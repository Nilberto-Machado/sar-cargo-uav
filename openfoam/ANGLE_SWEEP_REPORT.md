# Varredura preliminar de ângulo de ataque

## Configuração comum

- OpenFOAM 14 no WSL Ubuntu 22.04
- 25 m/s, escoamento incompressível RANS `kOmegaSST`
- malha preliminar: 269.773 células, sem camadas prismáticas
- execução paralela: 10 processos, decomposição `scotch`
- média dos coeficientes: 11 iterações finais de cada caso
- referência: `Aref = 2,604 m²`, `lRef = 0,6415 m`, `CofR = (1,07 0 0)`

## Resultados

| Ângulo | Cl médio | Cd médio | Cm médio | Estado |
|---:|---:|---:|---:|---|
| −4° | −0,363894 | 0,087563 | 0,038651 | concluído/reconstruído |
| 0° | −0,012470 | 0,065456 | 0,010913 | concluído/reconstruído |
| +4° | 0,335759 | 0,084304 | −0,005966 | concluído/reconstruído |
| +8° | 0,648753 | 0,132451 | −0,025637 | concluído/reconstruído |
| +10° | 0,775258 | 0,168051 | −0,046176 | concluído/reconstruído |
| +12° | 0,899104 | 0,212877 | −0,064946 | concluído/reconstruído |

Inclinação central preliminar da curva de sustentação entre −4° e +4°:
`dCl/dα ≈ 0,08746 por grau`. A incidência de sustentação nula inferida é
próxima de `−0,14°`.

## Correções aplicadas

- Para ângulos diferentes de zero, o patch externo `farfield` foi alterado de
  `slip` para `freestreamVelocity`/`freestreamPressure`.
- `k` e `omega` no farfield usam `inletOutlet` com valores de entrada definidos.
- Os vetores de força foram rotacionados com o escoamento.
- A simulação foi paralelizada em 10 partições muito bem balanceadas, com cerca
  de 27 mil células por processo.

## Limitações

Resultados preliminares: ainda faltam camadas de parede, avaliação de `y+`,
independência de malha e efeitos das hélices. Não usar estes coeficientes para
dimensionamento estrutural ou desempenho final.

## Leitura preliminar

A sustentação ainda cresce até +12°, sem platô claro de `Cl`; portanto, esta
varredura ainda não identifica o estol. O aumento de arrasto torna-se mais forte
nos ângulos altos: `Cl/Cd` é aproximadamente 4,90 em +8°, 4,61 em +10° e 4,22
em +12°. O momento de arfagem fica progressivamente mais negativo.

Como próximo passo, recomenda-se rodar +14° e +16° para procurar o início do
estol e, depois, repetir a região crítica com camadas prismáticas e estudo de
independência de malha.
