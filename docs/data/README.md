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




- Exploração de dados
    - Excluir coluna de observação e corrigir menção no texto
    - Dados externos: direcionar para o apêndice que explicará a dinâmica de atualização das bases e anexará o excel de ingestão
    - Enxugar seção de feature engineering
    - Excluir tabela de variáveis remanescentes que repete funil

- Discussões e resultados
    - Deve incluir os quadrinhos da Jéssica


Quero que sejam revistas todas as figuras da documentação. Abaixo estão citadas, por página específica da doc, as alterações imprescindíveis a serem realizadas em algumas imagens em especial:
- Público 
    - as duas primeiras figuras apresentam o subtítulo se sobrepondo aos headers das categorias das tabelas abaixo; além disso, a linha que separa os valores totais parece duplicada
    - a terceira figura necessita de um ajuste de contraste. Coma a tonalidade de azul escolhida para o background das células o efeito do heatmap se perde (mesmo problema na figura 4) além do fundo tornar-se muito escuro em alguns casos, impedindo a leitura do valor representado na célula da tabela;

- Variável resposta
    - A figura 1 apresnta uma inversão das faixas 81-85 e 76-80 no ponto referente a janela de 2 meses que não condiz com os dados de fato. Utilizar os dados presentes em X para produzir as curvas adequadas

- Desenvolvimento do modelo
    - Figura 1 deve utilizar os dados disponívies no notebook para reproduzir as curvas da figura (conforme se vê, parece mais um eletrocardiograma!) e o corte que intersecciona as 3 curvas e marca o valor no gráfico deve ser traçado no valor 50 e não no 140
    - A figura 2 deve trazer os valores de importância em % do SHAP acumulado total para cada grupo

- Definição dos níveis de risco
    - Figura 1 possui linhas de grade brancas paralelas ao eixo X que poluem a imagem o confundem a visualização. Excluí-las.

- Discussões e resultados
    - A tabela que conclui a seção de benchmarking deve dar ênfase aos valores da última coluna, seja destacando os valores com formatação negrito ou com realce de cor