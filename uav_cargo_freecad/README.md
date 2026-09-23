# UAV cargueiro paramétrico — FreeCAD / OpenFOAM

Modelo conceitual simplificado de uma aeronave cargueira não tripulada, de asa fixa,
para CFD externo. A geometria evita antenas, dobradiças, entradas de ar, parafusos e
outras escalas pequenas que encarecem o `snappyHexMesh` sem ajudar na análise global.

> Este é um modelo aerodinâmico conceitual, não um projeto estrutural, de estabilidade,
> propulsão ou certificação. As metas de 5 kg e 400 km são requisitos de missão ainda
> não demonstrados por este CAD.

## Arquivos

- `CargoUAV_CFD.FCStd` — documento nativo FreeCAD com parâmetros, sólido principal e
  disco atuador opcional.
- `build_uav.py` — fonte paramétrica; altere `PARAMS` e execute novamente para regenerar.
- `exports/CargoUAV_airframe.step` — aerofólio/fuselagem/empenagem unidos em um sólido.
- `exports/CargoUAV_with_propeller_disk.step` — sólido principal mais o disco opcional.
- `exports/CargoUAV_airframe.stl` — superfície triangulada principal para OpenFOAM.
- `exports/CargoUAV_propeller_disk.stl` — disco separado para modelo atuador/MRF.
- `validation_report.txt` — verificação de validade, fechamento, sólidos e dimensões.

## Dimensões principais

| Parâmetro | Valor |
|---|---:|
| Comprimento da fuselagem | 2,850 m |
| Envergadura | 4,200 m |
| Corda da asa, raiz / ponta | 0,620 / 0,340 m |
| Perfil da asa | NACA 0012 simétrico simplificado |
| Envergadura do estabilizador horizontal | 1,350 m |
| Altura da deriva | 0,620 m |
| Diâmetro do disco da hélice pusher | 0,900 m |
| Largura / altura máximas da fuselagem | 0,520 / 0,600 m |
| Meta de carga útil | 5 kg |
| Meta de alcance | 400 km |

Sistema de eixos: `+X` para a cauda, `+Y` para a asa direita e `+Z` para cima. O CAD e
os STEP/STL estão em milímetros.

## Parametrização e nova exportação

1. Edite somente o dicionário `PARAMS` no início de `build_uav.py`.
2. Execute no Prompt/PowerShell:

   ```powershell
   & "E:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" build_uav.py
   ```

3. Abra `CargoUAV_CFD.FCStd` para inspeção visual. O objeto `Parameters` registra os
   valores usados; a fonte de verdade para regeneração é `build_uav.py`.

No FreeCAD GUI, uma exportação manual equivalente é: selecione `Airframe`, use
**File > Export**, escolha STEP ou STL e mantenha milímetros. Para o STL fornecido, a
deflexão linear usada é 1,0 mm e a angular é 0,15 rad.

## Uso no OpenFOAM / snappyHexMesh

1. Copie `CargoUAV_airframe.stl` para `constant/triSurface/`.
2. Como o OpenFOAM normalmente trabalha em metros, aplique escala `0.001` ao importar
   (por exemplo, com `surfaceTransformPoints -scale '(0.001 0.001 0.001)'`). Confirme a
   sintaxe exata da sua versão do OpenFOAM.
3. Rode `surfaceCheck constant/triSurface/CargoUAV_airframe.stl`. O resultado esperado
   é uma superfície fechada, sem bordas abertas e com uma região principal.
4. No `snappyHexMeshDict`, use o STL como `triSurfaceMesh`, marque a superfície como
   `wall` e posicione `locationInMesh` no domínio externo, longe da aeronave.
5. Comece com 2–3 níveis de refinamento na aeronave, adicione caixas de refinamento na
   esteira e faça estudo de independência de malha. Refine bordo de ataque, bordo de
   fuga e ponta de asa conforme o objetivo aerodinâmico.
6. Para uma primeira simulação de célula limpa, ignore o arquivo do disco. Para empuxo
   simplificado, importe o disco separadamente e configure-o segundo o modelo atuador,
   `fvOptions` ou região rotativa compatível com sua versão do OpenFOAM.

O sólido principal foi unido por Boolean e salvo como um único corpo fechado. O disco
da hélice é deliberadamente separado porque não faz parte da parede estanque do avião.

