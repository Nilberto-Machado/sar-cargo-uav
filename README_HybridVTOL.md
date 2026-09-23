# UAV cargueiro híbrido VTOL — entrega FreeCAD e OpenFOAM

Modelo revisado para quatro motores elétricos de sustentação vertical, motor traseiro
a gasolina para cruzeiro e starter-generator. A geometria principal foi mantida simples
e fechada para CFD externo.

## Configuração desta revisão

| Parâmetro | Valor |
|---|---:|
| Envergadura | 4,20 m |
| Comprimento | 2,85 m |
| Área alar geométrica | 2,604 m² |
| Alongamento | 6,77 |
| Corda da asa, raiz / ponta | 0,82 / 0,42 m |
| Rotores VTOL | 4 × 0,76 m |
| Hélice pusher | 0,54 m |
| Carga útil alvo | 5 kg |
| MTOW preliminar | 21 kg |
| Bateria VTOL de referência | 12S, 800 Wh |
| Starter-generator de referência | 750 W |
| Tanque preliminar | 4 L |
| Alcance pretendido | 400 km |

Os valores de MTOW, potência elétrica, bateria, combustível e alcance ainda precisam
ser confirmados por orçamento de massa, ensaios e análise de desempenho.

## Conteúdo

- `uav_cargo_vtol/CargoUAV_HybridVTOL_CFD.FCStd`: modelo nativo FreeCAD.
- `uav_cargo_vtol/build_uav_vtol.py`: fonte paramétrica para uso no FreeCAD GUI.
- `build_uav_vtol_headless.py`: adaptador para regeneração com `FreeCADCmd`.
- `uav_cargo_vtol/exports/CargoUAV_HybridVTOL_airframe.step`: airframe em um sólido.
- `uav_cargo_vtol/exports/CargoUAV_HybridVTOL_airframe.stl`: superfície para CFD.
- `uav_cargo_vtol/exports/CargoUAV_HybridVTOL_complete.step`: airframe e cinco discos.
- `uav_cargo_vtol/exports/CargoUAV_HybridVTOL_pusher_disk.stl`: disco pusher separado.
- `uav_cargo_vtol/exports/CargoUAV_HybridVTOL_vtol_disks.stl`: quatro discos VTOL.
- `uav_cargo_vtol/validation_report.txt`: relatório geométrico.

O FCStd contém envelopes internos de referência para carga útil, bateria VTOL, tanque e
starter-generator. Eles não fazem parte dos STEP/STL de CFD.

## Regeneração paramétrica

Edite o dicionário `P` em `uav_cargo_vtol/build_uav_vtol.py`. Para gerar pelo console:

```powershell
& "E:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" build_uav_vtol_headless.py
```

Para validar os arquivos regenerados:

```powershell
& "E:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" uav_cargo_vtol\validate_delivery.py
```

## OpenFOAM

Use `CargoUAV_HybridVTOL_airframe.stl` no primeiro caso de cruzeiro. O arquivo está em
milímetros e deve ser convertido para metros com escala `0.001`. Execute `surfaceCheck`
antes do `snappyHexMesh`. Importe os discos separadamente somente para casos com disco
atuador ou região rotativa.

