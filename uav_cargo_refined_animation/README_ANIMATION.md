# Animação de missão - UAV refinado

O arquivo `CargoUAV_Refined_Flight_Animated.FCStd` representa a sequência cinemática:

1. checagem e acionamento dos rotores VTOL;
2. decolagem vertical;
3. partida do motor a gasolina por windmilling e aceleração;
4. parada, indexação a 90° e trava das hélices elétricas;
5. tilt seguro: naceles dianteiras para frente e traseiras para trás;
6. voo de cruzeiro sustentado pela asa e pelo pusher;
7. aproximação com rotores ainda parados;
8. retorno das naceles à vertical e confirmação das travas;
9. reinício dos rotores VTOL, descida vertical e pouso;
10. desligamento dos sistemas de propulsão.

## Como executar no FreeCAD

1. Abra `CargoUAV_Refined_Flight_Animated.FCStd`.
2. Acesse `Macro > Macros...`.
3. Abra ou selecione `Run_Flight_Animation.FCMacro` nesta pasta e clique em `Execute`.
4. Se o arquivo não aparecer, use `Create`/`Open` na janela de macros para selecioná-lo.

Abrir apenas o arquivo `.FCStd` não inicia a animação. Depois de executar o macro, a
aeronave é tornada visível automaticamente, a trajetória auxiliar é ocultada e a câmera
é enquadrada sobre o avião antes da decolagem.

Alternativamente, cole no console Python do FreeCAD:

```python
exec(open(r"C:\Users\nilbe\.codex\.chatgpt-projects\g-p-6ab2deb0963c8191aae099dcf40ea6da\uav_cargo_refined_animation\animate_flight.py", encoding="utf-8").read())
```

Durante a execução, selecione `AnimationController` na árvore para acompanhar fase,
altitude, velocidade, RPM, ângulos das naceles e estado dos intertravamentos.

Para pausar, continuar ou reiniciar pelo console:

```python
import builtins
builtins.UAV_FLIGHT_ANIMATION.pause()
builtins.UAV_FLIGHT_ANIMATION.start()
builtins.UAV_FLIGHT_ANIMATION.reset()
```

## Limite do modelo

Esta é uma animação cinemática e operacional. A trajetória, velocidades e rotações são
ilustrativas; não resultam da integração de equações 6-DOF, controle de voo, rajadas,
efeito solo ou modelo de hélices. Ela verifica sequência e vínculos, não segurança de voo.
