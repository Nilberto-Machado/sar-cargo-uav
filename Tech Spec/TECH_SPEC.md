# Especificação técnica consolidada

## Configuração
- **Tipo:** UAV cargueiro/de resgate híbrido VTOL de asa fixa
- **Status:** Configuração conceitual consolidada; não liberada para fabricação ou compra integral
- **Envergadura:** 4,20 m
- **Comprimento:** 2,85 m (envelope atual; requisito inicial 2,6–3,0 m)
- **Área alar:** 2,604 m²
- **Corda raiz / ponta:** 0,820 m / 0,420 m
- **Afilamento:** 0,512
- **Corda aerodinâmica média:** 0,6415 m
- **Alongamento geométrico:** AR ≈ 6,77
- **Empenagem:** Cauda em V, ângulo consolidado de 40°
- **Carga útil:** Até 5 kg — meta
- **Alcance:** 400 km — meta a validar por ensaio de consumo e reserva
- **Velocidade CFD de referência:** 25 m/s, α = 0°
- **Centro de gravidade alvo:** x ≈ 1,05–1,085 m; referência de momentos x = 1,07 m
- **Propulsão VTOL:** 4 motores elétricos 12S em naceles inclináveis
- **Pivôs dianteiros:** x = 0,600 m; inclinação de cruzeiro para frente: −90°
- **Pivôs traseiros:** x = 2,000 m; inclinação de cruzeiro para trás: +90°
- **Propulsão de cruzeiro:** Motor traseiro a gasolina em configuração pusher
- **Geração elétrica:** Starter-generator dedicado; motores VTOL não são assumidos como geradores nesta revisão
- **MTOW:** TBD — gate obrigatório antes da compra de motores, ESCs, pack, tilt, estrutura e paraquedas

## Conceito operacional

A aeronave decola e pousa verticalmente com quatro rotores elétricos. Após atingir altura e condições seguras, o motor traseiro a gasolina é acionado pelo sistema starter-generator e assume o cruzeiro. O starter-generator pode alimentar o barramento e recarregar a bateria dentro dos limites do pack. Os motores VTOL não são considerados geradores nesta revisão, evitando arrasto, controle complexo e riscos de overspeed.

## Intertravamento obrigatório dos tilt-rotors

A nacele só pode iniciar o movimento quando, para aquele rotor, houver confirmação independente de: comando de torque zero; RPM abaixo do limite; hélice na janela angular indexada; trava da posição atual liberada; trajetória livre; e alimentação do atuador válida. Ao chegar à nova posição, a trava mecânica deve engatar e dois sinais coerentes devem confirmar posição/trava antes de liberar potência ao motor.

Sequência de falha: qualquer discordância congela a transição, mantém ou retorna à última posição mecanicamente segura e impede reenergização do rotor afetado. Os rotores dianteiros giram para frente; os traseiros giram para trás. É proibido girar naceles com hélices em rotação livre significativa.

## Estado da validação CFD

Caso base OpenFOAM 14, 25 m/s e α=0°, malha de 269.773 células. Resultado preliminar médio entre passos 140–150: Cd≈0,06546, Cl≈−0,01247 e Cm≈0,01091. A malha ainda não possui camadas de parede nem representação das hélices; os coeficientes não liberam o projeto.

## Gates de liberação de compras

- G1 Massa/CG: MTOW, centros de massa e envelopes fechados.
- G2 VTOL: razão empuxo/peso ≥1,5 e margens elétricas/térmicas medidas.
- G3 Cruzeiro: potência, consumo, alcance de 400 km e reserva demonstrados.
- G4 Tilt: cargas, folgas, indexação, travas e análise de falha aprovadas.
- G5 Energia: pack, proteção, redundância e starter-generator validados.
- G6 Estrutura: cargas limite/última, FEA e provas estáticas concluídas.
- G7 Segurança/operação: paraquedas, failsafes, regulamentação e plano de ensaios aprovados.

## Rastreabilidade e ressalvas

As dimensões acima vêm do modelo paramétrico atual. Cálculos antigos do documento Arduino (como asa de 3 m e massas de 10/19 kg) são históricos e foram superados quando conflitantes. Modelos comerciais listados são candidatos técnicos, não autorização de compra. Confirme revisão, disponibilidade, homologação e ficha oficial diretamente com o fabricante no momento da aquisição.
