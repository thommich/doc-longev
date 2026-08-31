---
title: "Exploração de Dados"
type: docs
sidebar_position: 4
---

# **EXPLORAÇÃO DE DADOS**

---

A fase de exploração dos dados disponíveis para modelagem do problema abrangeu o mapeamento e a análise de diferentes fontes de informação no intuito de avaliar a utilidade e disponibilidade dos dados presentes em cada uma. Após o mapeamento inicial e direcionado das fontes disponíveis, as tabelas candidatas possuindo cobertura completa do histórico de desenvolvimento e algum indicativo mínimo de potencial (mesmo que conceitual, em primeira análise) para discriminação do evento modelado, foram cruzadas com a base de público e submetidas a um pipeline de seleção de variáveis para determinar a composição do conjunto final de features explicativas do modelo. Em alguns casos, antes da realização do cruzamento das bases com o público de desenvolvimento, foi necessária a aplicação de técnicas de *feature engineering* aos dados puros da base de origem para que a informação pudesse ser utilizada no contexto de modelagem aplicado posteriormente. Abaixo descrevem-se os detalhes dos passos conduzidos durante o processo de Exploração de Dados e são fornecidos links para acesso às fontes quando aplicável.

<br/>

## **PREMISSAS**

Durante o processo de Discovery do projeto foi realizada uma revisão da literatura científica existente relacionada ao domínio do problema: desenvolvimento de modelos de Machine Learning para predição de evento de óbito. Os trabalhos analisados - discutidos em maior detalhe na sessão [Discussões e Resultados de Aplicação do Modelo](6_Discussoes_e_resultados_de_aplicacao_do_modelo.md) evidenciam uma diferença significativa nos patamares de discriminação obtidos por modelos que utilizam variáveis com indicativos diretos de saúde dos indivíduos (resultados de exames laboratoriais, diagnósticos de doenças pré existentes...) quando comparados a modelos treinados sem este tipo específico de informação. Tendo em vista esse fato e sabendo que os dados disponíveis para o desenvolvimento do Modelo de Longevidade no contexto do Banco Itaú-Unibanco não incluem este tipo de dado, decidiu-se direcionar a exploração das variáveis explicativas para 3 grandes grupos de dados:

- Essenciais/Demográficos: que caracterizam os indivíduos de acordo com sua identidade e ambiente;
- Padrões de consumo: tendências (e outras estatísticas) de gastos em determinadas categorias;
- Proxies de fragilidade: indicativos indiretos de piora no estado de saúde dos indivíduos;

<br/>

## **FONTES DE INFORMAÇÕES EXPLORADAS**

Durante o processo de exploração conduzido pelos cientistas de dados a busca não se limitou a avaliar somente os dados internos do Banco, disponibilizados e produtizados pelas diversas áreas de Produtos e Negócios que compõem sua estrutura organizacional. A busca teve seu horizonte expandido também a bases de dados públicas disponibilizadas por órgãos federais e institutos nacionais de pesquisa.

Abaixo encontram-se indicados os principais conjuntos de dados que foram avaliados no processo de definição das variáveis explicativas do modelo - um quadro focando nos dados internos do Banco e outro nos dados externos, de fontes públicas. Para cada um dos conjuntos são fornecidos maiores detalhes e indicadas as suas fontes quando aplicável. Além disso, foi incluída uma breve justificativa para os casos nos quais o conjunto dados não avançou da etapa de exploração para a fase seguinte de seleção de variáveis.

- **DADOS INTERNOS**

| INFORMAÇÃO | DATABASE | TABELA | DOMÍNIO | OBSERVAÇÃO |
| ---------- | -------- | ------ | ------- | ---------- |
| Demografia Cliente | `db_corp_modelagem_visaoclientecrm_sot_01` | `tbjq8_vsao_perf_clie` | E/D | |
| Sentinela (dados de imagens de satélite da região do cliente) | `db_corp_modelagem_siriusmodelagemcreditopf_spec01` | `tbdc6_book_sentinela` | E/D e PF | |
| Affordability (classificação de gastos do cliente) | `db_corp_visaodorelacionamentobancario_producerdrachma_spec_01` | `tbck_renda_affordability_visao_produto` | PC | |
| Renda | `db_corp_visaodorelacionamentobancario_producerdrachma_spec_01` |  | E/D | |
| Rede Hiperspectral (grafo de transações dos clientes) | `db_corp_modelagem_siriusmodelagemcreditopf_spec01` | `tbdc6_modelagem_relacionamentos_grafo` | PC | |
| Convênios | `db_corp_garantias_garantiasimoveis_spec_01` | `spec_relatorio_geral_pessoas` | PF | |
| Endereço Clientes | `db_corp_datacredriskdevops_sot_01` | `tbdc042_ende_brau_pfis` | E/D | |
| Ocorrências de Afastamentos | `db_corp_gestaodefinancas_esocial_spec_01` | `tb_oa7_s2200_normalizado` | PF | |
| Histórico de Doenças Graves | `database_db_compartilhado_consumer_bupjconsumer` | `tbl_ir6_pacotes_vi_co` | PF | |
| Benefícios INSS | `db_corp_modelagem_onesiriusrich_spec_01` | `tbdc6s1002_spec_inss_individuo` | PF | |
| Autorizações (transações cartão de crédito) | `db_corp_repositoriosdedados_cartoesdados_spec_01` | `tbgy6016_autr_tran_ccre_` | PC | |
| Autorizações (transações cartão de crédito) | `db_corp_modelagem_onesiriusrich_spec_01` | `tbdc6s1042_autorizacoes_individuo` | PC | |
| Produtos Contratados | `db_corp_modelagem_visaoclientecrm_sot_01` | `tbjq8_ctrt_cred` | PC | |
| Produtos Contratados | `db_corp_modelagem_onesiriusrich_spec_01` | `tbdc6s1034_posseprodutos_individuo` | PC | |
| Tipos de Seguros | `db_corp_modelagem_visaoclientecrm_sot_01` | `tbjq8_ctrt_segu` | PF | |
| Tipos de Seguros | `database_rt2` | `rt2_ai6_gura205_gu_base_oguhj2_001` | PF | Não foi possível obter acesso |
| Tipos de Seguros |  | `tbny5002_platcred_sot_cadastral` | PF | Não foi possível obter acesso |

- **DADOS EXTERNOS[^1]**

| INFORMAÇÃO | URL FONTE |
| ---------- | --------- |
| Tábuas atuariais de mortalidade (IBGE) | |
| Atlas da Violência (IPEA) | |
| Indicadores Municipais IBGE | |
| SUS - Dados Abertos | |
| Boletim Estatístico da Previdência Social | |

## **NECESSIDADE DE *FEATURE ENGINEERING***

Durante a etapa de Exploração de Dados é comum que sejam identificadas fontes nas quais os dados não encontram-se 100% prontos para serem utilizados no processo de modelagem. Isso pode ocorrer por diversos motivos: desde o próprio formato físico do dado na tabela de origem que precisa ser adaptado antes de alimentar algum algoritmo de Machine Learning que apresente restrições de tipagem nos inputs (por exemplo, transformar valores monetários em formato *string* `"R$1500,00"` para *doubles* `1500.00`) até transformações que resultam na criação de novas features no intuito de extrair maior valor a partir do dado original (por exemplo, criação de agregações - médias, somas, valor máximo...). Abaixo encontra-se descrito em maior detalhe o processo de *feature engineering* realizado em algumas fontes de dados para aplicação no Modelo de Longevidade.

### **BOOK LONGEVIDADE**

Em parceria com o time de Inovação Crédito PF da RT de Credit AI and Analytics (Comunidade de Crédito PF), foi desenvolvido um book de variáveis específico para aplicação no Modelo de Longevidade. O Book contém variáveis que agregam até 12 meses de transações de clientes classificadas em 9 diferentes categorias de consumo de acordo com as literais presentes nos extratos de conta corrente, faturas de cartão de crédito e boletos pagos no Banco Itaú-Unibanco. O Book, apesar de ter sido desenvolvido originalmente para aplicação no Modelo de Longevidade, foi posteriormente implementado em sua totalidade e disponibilizado para consumo geral das áreas de dados (acessível via Data Mesh, tabela: <!--database.table-->) e representa mais um entregável de valor desenvolvido no âmbito deste projeto.

### **VARIÁVEIS DE GASTOS NO CARTÃO**

Em abordagem similar à utilizada no desenvolvimento do Book Longevidade, para utilização das variáveis de autorizações de transações no cartão de crédito (com origem na tabela `db_corp_repositoriosdedados_cartoesdados_spec_01.tbgy6016_autr_tran_ccre_`) no processo de modelagem foram geradas agregações de gastos em diferentes categorias para cada indivíduo utilizando o campo `catgr_trnsc`. Mais especificamente, foi calculado o total (soma dos valores) de gastos realizados em cada categoria por mês de referência. Para o cruzamento final com a tabela de público considerou-se sempre os gastos categorizados computados no mês anterior à referência dé observação na base de público.

### **VARIÁVEIS DE SEGUROS E DO SENTINELA**

Durante a fase de exploração dos dados percebeu-se um padrão sazonal muito claro ao estudar a distribuição dos valores dos dados de Seguros (provenientes de xxx) e das features do Sentinela (origem em xxx). Ambos apresentavam uma oscilação na distribuição de seus valores com um período bem característico de 12 meses (anual) e essa dinâmica ainda causava um aumento no valor de IEP de suas variáveis - medido safra a safra - para patamares acima dos limites máximos definidos como aceitáveis no processo de Seleção de Variáveis. Para estes 2 conjuntos de dados foram aplicadas técnicas de dessazonalização (diferenciação e médias móveis) no intuito de remover esta componente da série de dados e o processamento realmente atenuou bastante a oscilação dos dados. Infelizmente, para ambos os conjuntos de dados, a falta de histórico das bases impossibilitou o tratamento do período completo da sazonalidade e a consequente mitigação total dos efeitos dessa componente nos dados de origem.

### **VARIÁVEIS EXTERNAS DO SUS**

<!-- Nenhum texto desta subseção aparece nas fotos. -->

## **SELEÇÃO DE VARIÁVEIS**

As fontes de informação aprovadas após análise durante a exploração de dados e transformadas utilizando técnicas de *feature engineering* quando necessário foram cruzadas com o público de desenvolvimento obtido conforme a descrição detalhada na seção [Definição de Público](<!--LINK-->). O processo de extração de dados e cruzamento com a tabela de público pode ser consultado no Notebook [1 - Feature extraction](<!--LINK-->).

O dataset utilizado como input para o processo de Seleção de Variáveis é composto de 746.029 linhas (volumetria da base final amostrada do público de desenvolvimento) e 1618 colunas compreendendo 1572 colunas de variáveis candidatas e 46 colunas que englobam diferentes características úteis para segmentação e análise dos resultados além de colunas de identificação dos registros e da variável resposta. O objetivo final deste processo é a seleção de um subconjunto das 1572 variáveis candidatas garantindo que as features selecionadas forneçam ao modelo treinado informação de qualidade para inferir a variável resposta a partir dos dados enquanto concomitantemente atendendo a certos requisitos necessários ou desejáveis à sua aplicação no treinamento do modelo final.

Devido ao papel central que a informação a respeito da idade ocupa no domínio do problema de predição de óbito, o processo de Seleção de Variáveis foi aplicado adotando uma estratégia de coortes: o público amostrado de desenvolvimento foi dividido em 8 grupos de acordo com a segmentação correntista/não correntista e a sua faixa etária (4 quebras, abrangendo uma faixa de 5 anos cada) e cada um dos critérios do pipeline de Seleção de Variáveis foi aplicado grupo a grupo individualmente. Na avaliação final de cada critério as variáveis foram mantidas no conjunto de candidatas somente quando verificado o preenchimento dos requisitos mínimos para todos os 8 grupos ao mesmo tempo.

Abaixo encontra-se descrita cada etapa do pipeline de Seleção de Variáveis aplicado no desenvolvimento do Modelo de Longevidade seguindo a ordem de aplicação.

| Etapa | Critério |
| ----- | -------- |
| Avaliação de Preenchimento Histórico | dados disponíveis em todas as referências temporais do público de desenvolvimento, sem a existência de falhas de preenchimento em alguma safra específica |
| Avaliação de Estabilidade Temporal | média dos valores de IEP (Índice de Estabilidade Populacional) calculado safra a safra (referentes a safra inicial) inferior a 10% |
| Avaliação de Preenchimento Mínimo | percentual de valores preenchidos na coluna superior a 1% |
| Avaliação de Variância | variância dos valores preenchidos na coluna superior a 0 (que os valores preenchidos não sejam todos iguais) |
| Avaliação de Correlação [^2] | correlação de Spearman (em valor absoluto) entre duas variáveis inferior a 0,7 |
| Decisão Julgamental | avaliação caso a caso, mas geralmente descartadas devido a baixa relação com o domínio do problema ou identificação de alguma característica indesejada após avaliação visual da distribuição das variáveis via ferramenta [Pytinela](<!--LINK-->) ([resultados](<!--LINK-->)) |
| *Recursive Feature Elimination* (com validação cruzada) | seleciona o conjunto de variáveis para o qual o valor médio da métrica de performance atinge seu máximo (média sobre os dados de validação nos diferentes folds) |

A Figura X mostra a estrutura do pipeline de Seleção de Variáveis aplicado evidenciando a quantidade de features remanescentes após cada etapa.

<!-- FIGURA -->

## **VARIÁVEIS FINALISTAS DO MODELO**

A tabela a seguir traz a listagem das variáveis finalistas do modelo acompanhada de uma breve descrição:

<div align="center" markdown>

| Variável | Descrição |
| -------- | --------- |
| `P25_VLR_SAUDE_AGRUPADO_U6_FATS` | Quartil inferior do valor de gastos na categoria de Saúde nos últimos 6 meses |
| `LAST_VLR_SAUDE_AGRUPADO_U12_FATS` | Valor mais antigo de gasto na categoria de Entretenimento nos últimos 12 meses |
| `SKEW_VLR_SAUDE_AGRUPADO_U6_FATS` | Assimetria dos valores gastos em Saúde nos últimos 6 meses |
| `COUNTM_VLR_VIAGEM_AGRUPADO_RATIO_U6_U12` | Razão da quantidade total de gastos na categoria Viagem nos últimos 6 meses sobre os gastos em Viagem nos últimos 12 meses |
| `P25_VLR_CASA_AGRUPADO_U12_FATS` | Quartil inferior do valor de gastos na categoria Casa nos últimos 12 meses |
| `TAXA_HOMICIDIOS_PAF_MUNI_IPEA` | Taxa de homicídios por armas de fogo a cada 100.000 habitantes por município de residência |
| `LAST_VLR_ALIMENTACAO_AGRUPADO_U6_FATS` | Valor mais antigo de gasto na categoria de Alimentação nos últimos 6 meses |
| `SLOPE_VLR_VIAGEM_AGRUPADO_U6_FATS` | Tendência do valor gasto na categoria Finanças nos últimos 6 meses |
| `MAX_VLR_FINANCAS_AGRUPADO_RATIO_U9_U12` | Razão do valor máximo de gastos na categoria Finanças nos últimos 9 meses sobre o valor máximo nos últimos 12 meses |
| `SKEW_VLR_SAUDE_AGRUPADO_U12_FATS` | Assimetria dos valores gastos na categoria Saúde nos últimos 12 meses |
| `TAXA_SUICIDIO_PAF_MUNI_IPEA` | Taxa de suicídio por armas de fogo a cada 100.000 habitantes por município de residência |
| `IQR_VLR_SAUDE_AGRUPADO_U3_FATS` | Amplitude interquartil dos valores de gastos em Saúde nos últimos 3 meses |
| `RENDA_ELEITA` | Valor de renda declarada (quando disponível) ou estimada pelo modelo Aureus |
| `CV_VLR_ENTRETENIMENTO_AGRUPADO_U9_FATS` | Coeficiente de variação dos valores gastos em Entretenimento nos últimos 9 meses |
| `INVALIDEZ_INTERNACAO_SUS` | Taxa de internação no SUS para indivíduos com mais de 60 anos de idade por município no caso de recebimento de benefício INSS por invalidez |
| `P75_VLR_VIAGEM_AGRUPADO_U9_FATS` | Quartil superior do valor de gastos na categoria Viagem nos últimos 9 meses |
| `LAST_VLR_ALIMENTACAO_AGRUPADO_RATIO_U6_U12` | Razão do valor mais antigo de gastos na categoria Alimentação nos últimos 6 meses sobre o valor mais antigo nos últimos 12 meses |
| `CV_VLR_ALIMENTACAO_AGRUPADO_U3_FATS` | Coeficiente de variação dos valores gastos em Alimentação nos últimos 3 meses |
| `PROB_DE_MORTE_IBGE` | Valor de probabilidade de óbito por idade para os cidadãos brasileiros obtido das Tabelas Atuariais do IBGE |
| `SLOPE_VLR_ENTRETENIMENTO_AGRUPADO_U12_FATS` | Tendência do valor gasto na categoria Entretenimento nos últimos 12 meses |
| `KURT_VLR_ENTRETENIMENTO_AGRUPADO_U9_FATS` | Curtose dos valores gastos na categoria de Entretenimento nos últimos 9 meses |
| `COUNTM_VLR_VIAGEM_AGRUPADO_U12_FATS` | Razão da quantidade total de gastos na categoria de Casa nos últimos 9 meses sobre os últimos 12 meses |

<!-- As linhas originais 138–149 não aparecem em nenhuma das fotos fornecidas. -->

| `P50_VLR_ALIMENTACAO_AGRUPADO_RATIO_U9_U12` | Razão da mediana do valor de gastos em Alimentação no mês anterior sobre a mediana dos gastos nos últimos 12 meses |
| `SLOPE_VLR_SAUDE_AGRUPADO_U12_FATS` | Tendência do valor gasto na categoria finanças nos últimos 3 meses |
| `IQR_VLR_CASA_AGRUPADO_U12_FATS` | Amplitude interquartil dos valores de gastos em Casa nos últimos 12 meses |
| `P50_VLR_ENTRETENIMENTO_AGRUPADO_RATIO_U6_U12` | Razão da mediana do valor de gastos em Entretenimento nos últimos 6 meses sobre a mediana dos gastos nos últimos 12 meses |
| `DELTAPCT_VLR_ENTRETENIMENTO_AGRUPADO_U3_FATS` | Variação percentual do valor de gastos em Entretenimento nos últimos 3 meses |
| `LAST_VLR_ALIMENTACAO_AGRUPADO_RATIO_U9_U12` | Razão do valor mais antigo de gastos em Alimentação nos últimos 9 meses sobre o valor mais antigo nos últimos 12 meses |
| `LAST_VLR_ALIMENTACAO_AGRUPADO_U3_FATS` | Valor mais antigo de gasto em Alimentação nos últimos 3 meses |
| `MIN_VLR_FINANCAS_AGRUPADO_RATIO_U9_U12` | Razão do valor mínimo dos gastos em Finanças nos últimos 9 meses sobre o valor mínimo nos últimos 12 meses |
| `LAST_VLR_ENTRETENIMENTO_AGRUPADO_U6_FATS` | Valor mais antigo de gasto em Entretenimento nos últimos 6 meses |
| `IQR_VLR_CASA_AGRUPADO_U6_FATS` | Amplitude interquartil dos valores de gastos em Casa nos últimos 6 meses |
| `MIN_VLR_ENTRETENIMENTO_AGRUPADO_U9_FATS` | Valor mínimo de gasto com Entretenimento nos últimos 9 meses |
| `SLOPE_VLR_CASA_AGRUPADO_U3_FATS` | Tendência do valor gasto na categoria finanças nos últimos 3 meses |
| `P75_VLR_CASA_AGRUPADO_U9_FATS` | Quartil superior do valor de gastos na categoria de entretenimento no mês anterior |
| `VALOR_TOTAL_BENS_DIGITAIS_CARTOES` | Valor total de gastos na categoria de Bens Digitais no mês anterior |
| `LAST_VLR_ENTRETENIMENTO_AGRUPADO_U12_FATS` | Último valor de gasto categorizado na categoria de entretenimento avaliado nos últimos 12 meses |
| `LAST_VLR_VIAGEM_AGRUPADO_U9_FATS` | Último valor de gasto categorizado na categoria de entretenimento avaliado nos últimos 12 meses |
| `LAST_VLR_SAUDE_AGRUPADO_U9_FATS` | Último valor de gasto categorizado na categoria de entretenimento avaliado nos últimos 12 meses |

</div>

[^1]: Para os dados externos que, eventualmente, foram selecionados entre o conjunto final de features explicativas para o Modelo de Longevidade, foi criado um pipeline de ingestão específico e estes dados encontram-se atualmente democratizados e disponíveis para utilização em ambiente modernizado. Este processo de ingestão ficou a cargo dos Engenheiros de Dados da Comunidade de Crédito PF e pode ser consultado através deste [Repositório](<!--LINK-->).

[^2]: Durante a avaliação de correlação as variáveis são analisadas par a par e é necessário decidir qual das 2 variáveis do par deve ser a variável descartada quando o valor aferido de correlação ultrapassa o critério definido. No contexto do Modelo de Longevidade foi desenvolvido um "score de qualidade" geral das variáveis que foi calculado previamente à aplicação da avaliação de correlação permitindo ordená-las relativamente umas às outras e descartar a de menor valor quando comparadas par a par. Esse "score de qualidade" é uma métrica que avalia as features univariadamente de acordo com cinco quesitos: poder preditivo (média do gini ao longo do tempo), estabilidade (IEP máximo ao longo do tempo), estabilidade da relação preditiva (desvio padrão do gini ao longo do tempo), robustez da relação preditiva (média da correlação de postos de Spearman ao longo do tempo) e a robustez preditiva nos coortes (gini do pior grupo). Um peso é atribuído a cada um dos quesitos para geração de um score final. A definição da função de escoragem pode ser consultada [AQUI](<!--LINK utils.py-->).
