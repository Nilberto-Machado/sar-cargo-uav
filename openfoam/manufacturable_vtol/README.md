# Cargo UAV fabricável — caso OpenFOAM 14

Caso preliminar de escoamento externo para a montagem completa em configuração
VTOL: fuselagem, asa, empenagem em V, quatro tilt-rotors e propulsor traseiro.

- geometria em metros: `constant/geometry/CargoUAV_manufacturable_m.stl`;
- velocidade de referência: 25 m/s;
- incidência: +4 graus;
- turbulência: RANS `kOmegaSST`;
- domínio: 26 x 20 x 14 m;
- fundo: 52 x 40 x 28 células;
- refinamento de superfície: nível 4;
- camadas prismáticas desativadas nesta primeira malha de validação.

No WSL Ubuntu:

```sh
cd /mnt/c/GitHub/sar-cargo-uav/openfoam/manufacturable_vtol
./Allmesh
```

Esta etapa verifica a malha da montagem completa. Uma campanha física de cruzeiro
deve posteriormente separar hélices/discos atuadores e acrescentar camadas de parede.

## Benchmark no Xeon

Copie o projeto para o Xeon com o diretório `constant/polyMesh` incluído e execute:

```sh
cd openfoam/manufacturable_vtol
bash benchmark_xeon.sh 10 1500 xeon_10ranks
```

O script cria um caso isolado em `benchmark_runs/`, registra CPU, memória, versão do
OpenFOAM e mede apenas o tempo do solver. Comece com 10 ranks para comparação direta
com o baseline do Core 7 240H; depois repita com outras contagens de ranks para medir
escalabilidade do Xeon.

Compare os resultados com:

```sh
python3 compare_benchmarks.py benchmark_runs/xeon_10ranks
```
