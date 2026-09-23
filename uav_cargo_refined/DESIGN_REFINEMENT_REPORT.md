# Relatório de refinamento aerodinâmico

## Base de decisão

A revisão usa os princípios convergentes das referências fornecidas: arrasto induzido
decresce com o alongamento; taper próximo de 0,4-0,5 é apropriado para asas retas;
washout favorece estol iniciando na raiz; Reynolds e rugosidade devem ser compatíveis
com os dados de perfil; e a cauda deve ser dimensionada por volume e verificada por
margem estática e dinâmica.

## Comparação geométrica

| Parâmetro | Modelo anterior | Revisão |
|---|---:|---:|
| Envergadura | 4,20 m | 4,20 m |
| Área alar | 2,604 m² | 2,268 m² |
| Alongamento | 6,77 | 7,78 |
| Taper | 0,512 | 0,459 |
| Perfil | NACA 00xx simétrico | NACA 2415 -> 2412 |
| Twist geométrico | 0° | 2° de washout |
| Área verdadeira da cauda em V | 0,640 m² | 0,770 m² |
| Ângulo da cauda em V | 40° | 38° |
| Volume horizontal equivalente | ~0,29 | ~0,50 |
| Volume vertical equivalente | ~0,031 | ~0,041 |
| Referência de CG | conflitante: 1,07/1,35 m | alvo 1,070 m |

## Desempenho preliminar calculado

Com MTOW ainda preliminar de 21 kg e velocidade de cruzeiro de 21 m/s:

- carga alar: aproximadamente 90,8 N/m² (9,26 kg/m²);
- `Cl` de cruzeiro requerido: aproximadamente 0,337;
- velocidade de estol estimada: 10,7 m/s para `Clmax=1,3`;
- Reynolds de cruzeiro: aproximadamente 1,04 milhão na raiz e 0,48 milhão na ponta;
- área total dos quatro discos VTOL: aproximadamente 1,815 m².

Esses números são verificações de coerência, não garantias de desempenho.

## Relação com o CFD existente

A polar anterior mostrou crescimento de sustentação até +12°, aumento rápido de
arrasto acima de +8° e momento de arfagem progressivamente negativo. Ela continua útil
como referência do desenho anterior, mas não pode ser transferida para a nova asa. O
perfil cambrado, o washout, a área menor e a cauda maior exigem remalhamento completo.

## Gates antes de fabricação

- pesar todos os componentes e fechar MTOW/CG, incluindo combustível consumido;
- demonstrar margem estática positiva no envelope inteiro, com meta inicial de 10-18%;
- verificar controle em pitch/yaw e acoplamento adverso da cauda em V em 6-DOF;
- verificar que o estol começa na raiz e preserva autoridade dos ailerons;
- validar potência, hélices e transição VTOL em bancada e em testes progressivos;
- executar análise estrutural, cargas de rajada, fadiga e flutter.
