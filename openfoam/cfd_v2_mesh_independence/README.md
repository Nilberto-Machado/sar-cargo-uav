# CFD v2 — independência de malha em cruzeiro

Este estudo preserva integralmente os casos legados em `openfoam/cruise_25ms_*` e
cria uma campanha independente para o ponto de referência de cruzeiro:

- velocidade: 25 m/s;
- ângulo de ataque: +4 graus;
- escoamento incompressível RANS;
- turbulência: `kOmegaSST`;
- `Aref = 2.604 m2`, `lRef = 0.6415 m`, `CofR = (1.07 0 0)`;
- geometria: cópia verificada do STL usado na campanha original;
- estratégia de parede: baixo Reynolds, alvo `y+` próximo de 1.

## Organização

```text
cfd_v2_mesh_independence/
├── geometry/                 STL comum e checksum
├── common/                   campos e dicionários compartilhados
├── cases/
│   ├── coarse/               alvo aproximado: 0.3 M células
│   ├── medium/               alvo aproximado: 1–2 M células
│   └── fine/                 alvo aproximado: 4–6 M células
├── scripts/extract_results.py
├── results/                  tabelas geradas pelo pós-processamento
├── Allmesh
└── Allrun
```

Cada caso possui seus próprios `blockMeshDict`, `snappyHexMeshDict`, malha,
resultados e logs. Nenhum script escreve nos casos anteriores.

Após o `snappyHexMesh`, `Allmesh` registra a última tabela de camadas em
`log.layerSummary`. Se nenhuma camada sobreviver aos controles de qualidade, cria
`NO_PRISM_LAYERS`; nesse estado `Allrun` bloqueia a solução para impedir que uma
malha sem a física pretendida seja confundida com CFD v2 válido. A variável
`ALLOW_NO_LAYERS=1` existe somente para testes diagnósticos explícitos.

## Refinamento e camadas

Os três níveis mantêm o mesmo domínio e a mesma geometria. A resolução cresce de
forma sistemática no fundo, na superfície e em caixas que cobrem asa, fuselagem,
empenagem e esteira próxima. As caixas se sobrepõem intencionalmente; prevalece o
maior nível local.

| Parâmetro | Coarse | Medium | Fine |
|---|---:|---:|---:|
| células do bloco de fundo | 40×32×24 | 52×40×28 | 68×52×36 |
| nível na superfície | 5 | 5 | 6 |
| nível asa/fuselagem/empenagem | 4 | 5 | 5 |
| nível na esteira próxima | 2 | 3 | 3 |
| camadas prismáticas solicitadas | 8 | 14 | 20 |
| limite global de células | 0.8 M | 3.0 M | 7.0 M |

A primeira camada tem espessura absoluta de `1.2e-5 m` e razão de expansão 1.25.
Com `nu = 1.48e-5 m2/s`, 25 m/s e Reynolds baseado em `lRef` de aproximadamente
1.08 milhão, essa altura é uma estimativa inicial para `y+ ≈ 1`. O valor efetivo
deve ser confirmado pelo campo `yPlus`; a altura deve ser corrigida na iteração
seguinte por `h_nova = h_atual / y+_medido` na região crítica.

## Execução

No WSL Ubuntu com OpenFOAM 14 carregado:

```sh
cd /mnt/c/GitHub/sar-cargo-uav/openfoam/cfd_v2_mesh_independence
. /opt/openfoam14/etc/bashrc
./Allmesh coarse
./Allrun coarse
```

Depois, repita para `medium` e `fine`, ou execute todos omitindo o argumento.
`Allrun` reutiliza uma malha existente; se ela não existir, chama `Allmesh`.
Antes de inicializar, recria `0/` a partir de `0.orig/`. `potentialFoam` é chamado
sem `-writePhi`, evitando a colisão entre `Phi` e `phi` no NTFS case-insensitive.
Cada solução usa 10 partições `scotch`.

## Critérios de qualidade

Antes de aceitar uma malha, conferir em `log.checkMesh`:

- `Mesh OK` no `checkMesh` padrão e nenhuma célula de volume negativo;
- não ortogonalidade máxima menor ou igual a 65 graus;
- skewness interna e de contorno menor ou igual a 4;
- determinante normalizado mínimo maior ou igual a 0.001;
- razão mínima de volume entre vizinhas maior ou igual a 0.01;
- camadas presentes nas superfícies principais e sem descontinuidades extensas;
- `y+` preferencialmente entre 0.5 e 2 na maior parte da asa e empenagem, com
  média de área próxima de 1; valores locais maiores devem ser inspecionados.

O script para ao detectar falha no `checkMesh` padrão. A varredura adicional
`-allGeometry -allTopology` é registrada em `log.checkMesh.full`; ela é
diagnóstica porque superfícies STL complexas podem produzir alertas de
concavidade mesmo quando os controles de volume, skewness, não ortogonalidade e
interpolação passam. A contagem real de células, e
não apenas o alvo nominal, é registrada pelo extrator.

## Convergência e comparação

`forceCoeffs` grava `Cd`, `Cl` e `CmPitch` a cada iteração. Por padrão,
`scripts/extract_results.py` usa as 100 amostras finais de cada malha, reportando
média, desvio padrão e variação percentual contra a malha imediatamente mais
fina. Também coleta estatísticas de `y+` quando disponíveis.

Uma malha pode ser considerada suficientemente independente quando, após
convergência iterativa em todos os níveis:

- a mudança de `Cl` e `Cm` entre medium e fine for menor que 1%;
- a mudança de `Cd` entre medium e fine for menor que 2%;
- os desvios nas janelas finais forem pequenos frente às diferenças entre malhas;
- a distribuição de `y+` continuar compatível com a estratégia wall-resolved;
- não houver mudança relevante no padrão de escoamento ou separação.

Como `Cd` é a grandeza mais sensível, ele governa a decisão. Comparar somente
soluções com resíduos estabilizados e coeficientes sem deriva na janela final.
Os critérios percentuais são metas de engenharia, não substituem uma análise de
ordem observada/GCI caso seja necessário quantificar a incerteza numérica.
