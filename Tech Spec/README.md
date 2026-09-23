# Tech Spec — UAV híbrido VTOL cargueiro/de resgate

Pacote consolidado em 22/09/2026.

## Conteúdo

- `Tech_Spec_UAV_Hybrid_VTOL.docx`: documento mestre para revisão.
- `TECH_SPEC.md`: especificação técnica controlada em texto.
- `BOM_Compras.csv`: lista mestra de compras.
- `Data sheets/`: uma ficha técnica para cada uma das 71 linhas da BOM.

## Regra de maturidade

Nenhum item marcado **compra bloqueada**, **TBD crítico**, **TBD** ou **sob medida** está liberado para pedido. “Arquitetura aceita” significa que a função foi aceita, não que a integração esteja certificada.

## Próximos gates

1. Fechar orçamento de massa, MTOW e centro de gravidade.
2. Medir empuxo/corrente/temperatura do conjunto VTOL.
3. Medir empuxo e consumo do motor a gasolina com hélice pusher.
4. Dimensionar pivôs, atuadores, travas e sensores de indexação.
5. Fechar balanço de energia e pack 12S.
6. Executar análise estrutural e prova de carga.
7. Atualizar CFD com camadas de parede e efeitos propulsivos.

O arquivo FreeCAD de referência permanece em `../uav_cargo_manufacturable/CargoUAV_HybridVTOL_Manufacturable.FCStd`.
