# UAV cargueiro híbrido VTOL — FreeCAD e OpenFOAM

Revisão do modelo conceitual para a configuração consolidada: quatro motores elétricos
de sustentação vertical, motor traseiro a gasolina para cruzeiro e starter-generator.
O corpo principal continua simplificado e adequado a CFD externo.

## Configuração representada

| Parâmetro | Valor |
|---|---:|
| Envergadura | 4,20 m |
| Comprimento | 2,85 m |
| Área alar geométrica | 2,604 m² |
| Alongamento | 6,77 |
| Corda da asa, raiz / ponta | 0,82 / 0,42 m |
| Rotores VTOL | 4 × 0,76 m |
| Hélice pusher representada | 0,54 m |
| Carga útil alvo | 5 kg |
| MTOW preliminar | 21 kg |
| Bateria VTOL de referência | 12S, 800 Wh |
| Starter-generator de referência | 750 W |
| Tanque preliminar | 4 L |
| Alcance pretendido | 400 km |

O MTOW, potência dos motores, bateria e combustível ainda são parâmetros preliminares.
O CAD não demonstra desempenho, autonomia, resistência estrutural ou segurança de voo.

## Arquivos

- `CargoUAV_HybridVTOL_CFD.FCStd`: documento nativo FreeCAD.
- `build_uav_vtol.py`: fonte paramétrica e regenerável.
- `exports/CargoUAV_HybridVTOL_airframe.step`: sólido externo limpo, sem discos.
- `exports/CargoUAV_HybridVTOL_airframe.stl`: parede externa para `snappyHexMesh`.
- `exports/CargoUAV_HybridVTOL_complete.step`: airframe e cinco discos separados.
- `exports/CargoUAV_HybridVTOL_pusher_disk.stl`: disco do motor a gasolina.
- `exports/CargoUAV_HybridVTOL_vtol_disks.stl`: quatro discos elétricos.
- `validation_report.txt`: validade, fechamento, número de sólidos e dimensões.

O documento FreeCAD também contém envelopes internos ocultos para carga útil, bateria
VTOL, tanque de combustível e starter-generator. Esses objetos não são exportados para
os arquivos de CFD.

## Regeneração

Edite `P` no início de `build_uav_vtol.py` e execute:

```powershell
& "E:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" build_uav_vtol.py
```

Para conferir todos os arquivos depois da geração:

```powershell
& "E:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" validate_delivery.py
```

## Uso no OpenFOAM

Copie `CargoUAV_HybridVTOL_airframe.stl` para `constant/triSurface/`. Os arquivos estão
em milímetros; converta para metros com escala `0.001`. Execute `surfaceCheck` antes do
`snappyHexMesh`. Para CFD de cruzeiro limpo, use apenas o airframe. Importe os discos
separadamente somente em casos com modelo atuador ou região rotativa.

