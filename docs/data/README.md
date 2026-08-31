- LONGEVIDADE <br/>
    [ ] - Corrigir GHs do modelo 25-4 partindo dos equivalentes e migrando 3 -> 4 <br/>
    [ ] - Rodar notebook de deploy Lotus novamente (com FAARM) <br/>
    [ ] - Gerar nova tabela Ste dados externos para comparação <br/>
    [ ] - Mapear o necessário pra finalizar a Doc <br/>

<br/>
<br/>

- SUBSTITUIÇÃO BOOKS <br/>
    [ ] - Definir com Marco como mostrar os dados do estudo de impacto <br/>
    [ ] - Definir para as vars de FT/AU se os sentinelas estão trocados na base da Ste <br/>
    [ ] - Categorizar as transações das features de acordo com a tabela abaixo <br/>

<br/>
<br/>

- OUTROS <br/>
    [ ] - Gerar documentação Gallardo para envio validação <br/>
    [ ] - Ajustar meu ponto <br/>
    [ ] - Responder a menina de Riscos <br/>

<br/>
<br/>

| Transition | Interpretation |
|---|---|
| Same sentinel: `-1 → -1` | Stable encoding |
| Different sentinel: `-1 → -999` | Likely sentinel recoding |
| Sentinel → valid decile | New source recovered/calculated a value |
| Valid decile → sentinel | New source lost coverage or failed calculation |
| Sentinel ↔ `MISSING` | Null-handling difference |
| Decile → decile | Ordinary value/rank migration |