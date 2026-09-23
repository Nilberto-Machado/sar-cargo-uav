# UAV híbrido VTOL — revisão geométrica fabricável

Esta revisão corrige a colisão dos rotores traseiros com os próprios booms durante o
basculamento.

## Geometria corrigida

- juntas dianteiras em `X=600 mm`, basculando para frente até `-90°`;
- juntas traseiras em `X=2000 mm`, instaladas na extremidade estrutural dos booms;
- conjuntos traseiros basculando para trás até `+90°`;
- cauda em V mantida, com painéis a 40°;
- hélices obrigatoriamente paradas, indexadas e travadas antes do movimento dos pods.

A trajetória das pás foi testada geometricamente em incrementos de 5°. O resultado foi:

- nenhuma interpenetração nos quatro conjuntos;
- folga mínima dos conjuntos dianteiros: aproximadamente 38 mm;
- folga mínima dos conjuntos traseiros: aproximadamente 107 mm;
- desenho anterior: colisão traseira a partir de aproximadamente 75°.

## Animação

Abra `CargoUAV_HybridVTOL_Manufacturable.FCStd` e execute
`RunManufacturableTransition.FCMacro`.

A sequência liga a pusher mantendo os pods verticais, transfere sustentação para a asa,
para os rotores elétricos, indexa as pás, confirma a trava e só então aplica tilt
espelhado. Use `StopManufacturableTransition.FCMacro` para retornar ao solo.

## Limite desta verificação

Ausência de colisão no CAD não torna o mecanismo pronto para fabricação. Ainda devem ser
dimensionados mancais, eixos, suportes, atuadores, batentes, pinos de trava, sensores de
posição, chicotes flexíveis, rigidez, fadiga e tolerâncias. A folga dianteira de 38 mm
deve ser ampliada ou justificada após considerar flexão estrutural e tolerâncias reais.

