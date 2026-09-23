# Cargo UAV — OpenFOAM 14 baseline

Caso estacionário RANS da célula em cruzeiro, sem hélices ou disco atuador.

- Velocidade: 25 m/s
- Incidência: 0 graus
- Modelo: incompressível, `kOmegaSST`
- Área de referência: 2,604 m²
- Corda média: 0,6415 m
- Centro de momentos: (1,07 0 0) m
- Eixos: X longitudinal, Y envergadura, Z vertical

No Ubuntu/WSL:

```sh
source /opt/openfoam14/etc/bashrc
cd /mnt/c/Users/nilbe/.codex/.chatgpt-projects/g-p-6ab2deb0963c8191aae099dcf40ea6da/openfoam/cruise_25ms_alpha0
bash ./Allmesh
bash ./Allrun
```

Resultados dos coeficientes são gravados em `postProcessing/forceCoeffs`.

