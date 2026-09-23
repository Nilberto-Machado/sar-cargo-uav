# Animação corrigida com cauda em V e motores basculantes

Esta revisão substitui a empenagem convencional por duas superfícies inclinadas a 40°
e adiciona basculamento aos quatro conjuntos elétricos.

Cada conjunto possui duas juntas independentes:

- `Joint_Tilt_*`: revolução em torno do eixo transversal local `+Y`, com curso de 0°
  na decolagem a −90° no cruzeiro.
- `Joint_Spin_*`: rotação da hélice em torno de `+Z` local ao pod. Como é filha do
  conjunto basculante, a direção desse eixo acompanha a inclinação do motor.

| Motor | Pivô de basculamento em mm | Eixo de tilt | Centro do rotor relativo ao pivô |
|---|---:|---:|---:|
| FL | `(600, -950, 53,4)` | `(0, 1, 0)` | `(0, 0, 167)` |
| FR | `(600, 950, 53,4)` | `(0, 1, 0)` | `(0, 0, 167)` |
| RL | `(1850, -950, 53,4)` | `(0, 1, 0)` | `(0, 0, 167)` |
| RR | `(1850, 950, 53,4)` | `(0, 1, 0)` | `(0, 0, 167)` |

Durante a transição, a hélice traseira acelera de 0 a 6000 rpm enquanto os pods passam
de 0° para −90° e os rotores elétricos reduzem de 1600 rpm até parar. No cruzeiro, os
discos elétricos ficam alinhados com o escoamento para reduzir a área frontal.

Para executar, abra `CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd` e rode
`RunVTailTiltRotorAnimation.FCMacro` em **Macro > Macros**. Use a macro `Stop...` para
parar e retornar à posição inicial.

Esta é uma verificação cinemática. O mecanismo real ainda necessita dimensionamento de
atuador, rolamentos, trava mecânica, velocidade de basculamento e análise de cargas.

