# Animação cinemática do UAV híbrido VTOL

O arquivo `CargoUAV_HybridVTOL_Animated.FCStd` apresenta uma sequência visual de 16 s:

1. aceleração dos quatro rotores VTOL;
2. decolagem vertical;
3. transição com partida da hélice pusher;
4. redução dos rotores elétricos;
5. voo sustentado pela asa com rotores VTOL estacionados.

Esta animação verifica vínculos, sentidos de rotação, folgas visuais e sequência de
operação. Ela não calcula forças, potência, estabilidade, vibração ou trajetória física.

## Como executar

1. Abra `CargoUAV_HybridVTOL_Animated.FCStd` no FreeCAD 1.1.
2. Use **Macro > Macros**.
3. Selecione `RunHybridVTOLAnimation.FCMacro` e pressione **Execute**.
4. Acompanhe `AnimationState` na árvore para ver fase, altitude, atitude e RPM comandada.
5. Execute `StopHybridVTOLAnimation.FCMacro` para parar e retornar ao solo.

Copie os dois arquivos `.FCMacro` para a pasta de macros do FreeCAD se quiser que eles
apareçam permanentemente na lista de macros.

## Vínculos e pontos de rotação

Sistema de eixos do CAD: `+X` para a cauda, `+Y` para a direita e `+Z` para cima.
Consequentemente, o deslocamento de voo para a frente ocorre em `-X`.

| Conjunto | Pivô local em mm | Eixo | Sentido na animação | Vínculo |
|---|---:|---:|---|---|
| VTOL dianteiro esquerdo | `(600, -950, 220)` | `(0, 0, 1)` | positivo | revolução, 1 GDL |
| VTOL dianteiro direito | `(600, 950, 220)` | `(0, 0, 1)` | negativo | revolução, 1 GDL |
| VTOL traseiro esquerdo | `(1850, -950, 220)` | `(0, 0, 1)` | negativo | revolução, 1 GDL |
| VTOL traseiro direito | `(1850, 950, 220)` | `(0, 0, 1)` | positivo | revolução, 1 GDL |
| Hélice pusher | `(2960, 0, 20)` | `(1, 0, 0)` | positivo | revolução, 1 GDL |
| Corpo da aeronave | CG `(1350, 0, 0)` | pitch `(0, 1, 0)` | variável | corpo rígido |

Os rotores diagonais usam o mesmo sentido e os pares adjacentes usam sentidos opostos,
reduzindo o torque líquido durante o voo vertical. Em cada junta de rotor, as três
translações e as duas rotações fora do eixo estão bloqueadas. Todos os rotores são filhos
de `AircraftAssembly`; portanto, acompanham a translação e o pitch do corpo, mantendo a
rotação própria em torno do pivô local.

Os marcadores amarelos mostram os pivôs e eixos de hélice. O marcador vermelho mostra o
CG preliminar e o eixo de pitch. Os valores também podem ser inspecionados no grupo
`KinematicJoints` do documento.

## Sequência representada

| Tempo | Fase | VTOL | Pusher | Movimento ilustrativo |
|---:|---|---:|---:|---|
| 0–2 s | Spin-up | 0 → 1600 rpm | parado | solo |
| 2–6 s | Decolagem vertical | 1600 rpm | parado | subida até 1,5 m |
| 6–10 s | Transição | 1600 → 250 rpm | 0 → 6000 rpm | aceleração e pitch de -7° |
| 10–16 s | Cruzeiro | estacionados | 6500 rpm | voo em `-X` |

A velocidade visual de rotação é reduzida para evitar aliasing na tela; os campos RPM
em `AnimationState` registram os valores comandados da sequência.

