# Revisão fabricável dos rotores basculantes

O desenho anterior posicionava as juntas traseiras em `X=1850 mm` e inclinava todos os
pods para a frente. A análise geométrica encontrou colisão das pás traseiras a partir de
aproximadamente 75°, chegando a cerca de 200.000 mm³ de interpenetração em 90°.

Nesta revisão:

- rotores dianteiros: pivô em `X=600 mm`, basculamento para frente até `-90°`;
- rotores traseiros: pivô em `X=2000 mm`, na extremidade reforçada do boom;
- rotores traseiros basculam para trás até `+90°`;
- todas as hélices param, são indexadas a 90° e travadas antes do tilt;
- a animação impede tilt enquanto `VTOL_RPM` não for zero.

A trajetória foi verificada em incrementos de 5°. Não houve interpenetração e a menor
folga de pá encontrada foi superior a 100 mm na geometria corrigida.

Essa validação cobre somente interferência geométrica. A fabricação ainda exige projeto
do mancal, eixo, trava redundante, atuador, batentes, chicote flexível, cargas de inércia,
fadiga e tolerâncias de montagem.

