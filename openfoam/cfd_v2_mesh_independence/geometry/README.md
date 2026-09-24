# Geometria de referência

`CargoUAV_cruise_m.stl` é uma cópia byte a byte da geometria usada no caso
legado `openfoam/cruise_25ms_alpha_p4`.

- tamanho: 512984 bytes;
- SHA-256: `C6BF225E55AC5508AFF6530E5CC6247A3192A43C772AB01ACD68AFDCFA699FCF`;
- triângulos: 10258;
- bounding box: `(0 -2.1 -0.31651)` a `(2.85 2.1 0.587835)` m;
- superfície fechada, uma região, sem triângulos ilegais segundo `surfaceCheck`.

A campanha v2 não altera nem regenera este STL, garantindo que as diferenças
entre casos sejam apenas de malha e solução numérica.

