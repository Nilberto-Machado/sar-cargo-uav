# UAV cargueiro híbrido VTOL - revisão aerodinâmica fundamentada

Esta pasta contém uma nova variante paramétrica. Ela preserva os modelos anteriores e
aplica critérios de projeto conceitual, aerodinâmica de asa e estabilidade extraídos das
referências técnicas fornecidas pelo usuário.

## Alterações principais

- asa de 4,20 m mantida, com área reduzida de 2,604 para 2,268 m²;
- alongamento aumentado de 6,77 para 7,78;
- taper alterado de 0,512 para 0,459, próximo ao valor recomendado para asa reta;
- perfil simétrico substituído por NACA 2415 na raiz, transicionando para NACA 2412;
- incidência de +2° na raiz e 0° na ponta, criando 2° de washout;
- cauda em V aumentada e inclinada a 38°, com volumes equivalentes aproximados
  `Vh = 0,50` e `Vv = 0,041`;
- CG preliminar consolidado em X=1,070 m, com envelope X=1,010-1,120 m;
- naceles de cruzeiro suavizadas e hélice pusher aumentada de 0,54 para 0,60 m;
- fuselagem preserva o volume central, mas recebe nariz e cone de cauda mais suaves.

## Arquivos gerados

- `CargoUAV_Refined_CFD.FCStd`: modelo nativo FreeCAD;
- `exports/CargoUAV_Refined_airframe.step`: sólido externo watertight;
- `exports/CargoUAV_Refined_airframe.stl`: superfície para `snappyHexMesh`;
- `exports/CargoUAV_Refined_with_pusher.step`: fuselagem e disco pusher separado;
- `exports/CargoUAV_Refined_complete.step`: airframe e cinco discos separados;
- `validation_report.json`: validade geométrica e métricas calculadas.

## Regeneração

```powershell
& "E:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" build_refined_uav.py
```

## Estado de maturidade

Este é um candidato conceitual, não um projeto liberado para fabricação. A alteração de
asa invalida a malha CFD anterior. Antes de congelar a geometria, são obrigatórios:

1. nova malha OpenFOAM com camadas prismáticas e estudo de independência;
2. polar incluindo transição/estol e avaliação de `y+`;
3. VLM ou CFD para ponto neutro, margem estática e autoridade dos ruddervators;
4. fechamento real de massa/CG em todas as condições de combustível e carga;
5. dimensionamento estrutural, aeroelasticidade, flutter e ensaios dos tilt-rotors.
