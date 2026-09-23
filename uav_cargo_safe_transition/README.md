# Transição segura dos motores basculantes

Esta macro substitui a sequência anterior, que inclinava os motores enquanto as hélices
ainda giravam. O novo intertravamento impede qualquer movimento de tilt enquanto a RPM
dos rotores elétricos for diferente de zero ou a trava das pás não estiver confirmada.

## Sequência

| Tempo | Operação | VTOL | Tilt | Pusher |
|---:|---|---:|---:|---:|
| 0–6 s | Spin-up e decolagem | até 1600 rpm | 0° | parada |
| 6–9 s | Partida da pusher | 1600 rpm | 0° | 0→5200 rpm |
| 9–11 s | Transferência de sustentação | 1600→0 rpm | 0° | 5200→6200 rpm |
| 11–12 s | Indexação transversal das pás | 0 rpm | 0° | 6200 rpm |
| 12–14 s | Basculamento após travamento | 0 rpm e travado | 0→−90° | 6200→6500 rpm |
| 14–20 s | Cruzeiro | parado e travado | −90° | 6500 rpm |

As pás são estacionadas a 90° no eixo local, ficando transversais ao boom antes do
basculamento. O estado pode ser acompanhado nas propriedades `RotorLock` e
`TiltPermission` de `AnimationState`.

Este intertravamento é apenas lógico/cinemático. Um mecanismo real também deve possuir
sensor de RPM zero, encoder de posição, pino de trava redundante, detecção de trava,
limites mecânicos e procedimento de retorno caso alguma unidade não confirme a posição.

