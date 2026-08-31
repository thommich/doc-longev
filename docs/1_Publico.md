---
title: "Público"
type: docs
sidebar_position: 2
---

# **PÚBLICO**

---

O processo de definição do público do Modelo de Longevidade baseou-se em uma série de análises exploratórias iniciais aplicada à população brasileira. Cada um dos critérios definidos, que transformam o conjunto de dados iniciais na amostra final de desenvolvimento utilizada no treinamento e avaliação do modelo, ancora-se nos resultados obtidos a partir destas análises. Abaixo encontram-se detalhadas as principais decisões tomadas durante esse processo discutidas junto aos números que embasam sua aplicação.

<br/>

## **HISTÓRICO DE DESENVOLVIMENTO**

O histórico de desenvolvimento do Modelo de Longevidade abrangeu os meses de Junho de 2024 a Setembro de 2025 (16 safras). A definição dessa janela levou em consideração a recência dos dados, a disponibilidade histórica de informações provenientes de algumas fontes de dados e também a definição da [variável resposta](2_Variavel_resposta.md) do modelo que requer um período de 6 meses de maturação para determinação. Desse histórico, os 12 primeiros meses foram utilizados no treinamento do modelo enquanto os 4 meses finais compuseram o conjunto de dados de teste (out of time).

| Conjunto | Nº Meses | Safras |
| -------- | -------- | ------ |
| **Treino** | 12 meses | 202406 - 202505 |
| **Teste** | 4 meses | 202506 - 202509 |

<br/>

## **MARCAÇÕES DE SEGMENTAÇÃO DO PÚBLICO**

Tendo mapeado uma quantidade relevante da população ao longo de um período histórico abrangente o suficiente, buscou-se em outras fontes diferentes características dos indivíduos que possibilitassem a segmentação da base em uma série de dimensões de interesse analítico. A tabela abaixo resume as marcações de segmentação que foram adicionadas à base inicial, bem como a indicação de suas tabelas de origem. O processo de marcação da base pode ser consultado no detalhe acessando o Notebook [1 - Definição do Público](<!--LINK PARA O NOTEBOOK-->).

| Segmentação | Database | Tabela |
| ----------- | -------- | ------ |
| 6 Bancos | `database_db_compartilhado_consumer_cravisaoclientebupf` | `clusters_wtp_v2` |
| 6 Bancos | `database_db_compartilhado_consumer_cravisaoclientebupf` | `clusters_wtp_latest` |
| Idade | `db_corp_modelagem_datacredriskdevops_spec_01` | `tbdc6b010_cadpf_vis_indiv` |
| EP/OP Neoway | `database_rt2` | `rt2_ai6_dk5r0003_dk5_base_neofun_001` |
| EP/OP Neoway | `db_corp_modelagem_datacredriskdevops_sot_01` | `tbdc6039_empr_assc_coml` |
| OP SISPAG | `database_dm3` | `tbdm3193_csld_tran_pgto_sspg_salr_clie` |
| OP Assoc. Comercial | `db_corp_modelagem_datacredriskdevops_sot_01` | `tbdc6039_empr_assc_coml` |
| Proposta de Consignado | `db_corp_servicosdecontratacao_dataplataformpf_spec_01` | `tbln9_propostas_emprestimos_pf` |
| Contrato de Consignado | `db_corp_relatoriosregulatorios_plataformacreditoanalytics_spec_01` | `tbhn8_contratacao_consignado` |
| Performance Contratos Consignado | `db_corp_modelagem_datacredriskdevops_sot_01` | `tbdc6415_foucault_contratacao` |

<br/>

## **ESTUDO DA POPULAÇÃO**

Como passo inicial na determinação do público de modelagem, foi realizada uma caracterização da população com idade superior a 65 anos a nível Bureau/Brasil. Usando como origem o [Book de Público](https://github-pages-dev.cloud.itau.com.br/itau-dc6-doc-dados-credito-pessoa-fisica/docs/analitica/outros/book_publico/) (`db_corp_modelagem_onesiriusrich_spec_01.tbdc6s1020_publico_individuo`), buscou-se estudar os perfis de distribuição da volumetria e da taxa de óbito da população em diferentes segmentações.

Conforme é possível ver no quadro abaixo, a média mensal de CPFs únicos cresce a uma taxa praticamente constante ao longo de todas as referências analisadas. Duas marcações de segmentação do público que foram bastante importantes na jornada de desenvolvimento do modelo foram a de indivíduo com conta ativa no Banco (correntista) vs o oposto (os não correntistas), e a de contratação do produto de Crédito Consignado. Na figura abaixo verifica-se a distribuição da população brasileira como um todo ao longo da janela de tempo analisada bem como dentro das segmentações definidas. Para cada um dos grupos é trazido um valor de taxa de óbito que leva em conta a ocorrência do evento nos 6 meses seguintes a referência temporal anaisada.

![Volumetria População](data/volumetrias_populacao.png)
<p align="center">
  <bold>Figura 1:</bold> Volumetria da população avaliada nas quebras Correntista (com/sem contrato de Consignado) e Não Correntista e respectivas taxas de óbito por safra.
</p>

<br/>

## **AMOSTRAGEM DO PÚBLICO DE DESENVOLVIMENTO**

Tendo à disposição as análises da população deu-se seguimento ao processo de amostragem para obtenção do conjunto de dados de desenvolvimento. Foi definida a volumetria total de 1 milhão de indivíduos para essa amostra, garantindo assim um volume suficiente de dados para a aplicação do processo de modelagem. A amostra foi gerada buscando uma proporção de 50% correntistas e 50% não correntistas, intencionalmente aumentando a proporção amostral dos indivíduos para os quais o Banco possui mais informação disponível. Além disso, dentro do público correntista foram selecionados 250 mil indivíduos que adquiriram um contrato de Crédito Consignado ao longo das safras analisadas para permitir a avaliação do Modelo de Longevidade aplicado à concessão de um produto de crédito. Dentro de cada um dos grupos definidos a amostragem foi realizada de forma a espelhar a taxa de óbito observada por referência na população total.

![Volumetria Amostra 1MM](data/volumetrias_amostra_1MM.png)
<p align="center">
  <bold>Figura 2:</bold> Volumetria do público amostrado avaliado nas quebras Correntista (com/sem contrato de Consignado) e Não Correntista e respectivas taxas de óbito por safra.
</p>

<br/>

O público final de desenvolvimento do modelo é um subconjunto desta base amostrada, obtido após a eliminação de alguns registros justificada a partir de análises realizadas em segmentações específicas da base de 1 milhão de indivíduos. O primeiro corte realizado na base teve origem na observação das taxas de óbito quando avaliadas por faixa de idade e em diferentes janelas de tempo. Conforme evidenciado na Figura 3, tanto para os `correntistas` quanto para os `não correntistas`, observa-se que a partir de uma certa faixa de idade as taxas de óbito perdem sua ordenação intrínseca, deixando de correlacionar o aumento da idade com o aumento da taxa de óbito. O fato se deve à baixa volumetria de registros concentrados em faixas de idade muito altas que acabam gerando a distorção nas taxas observadas, além de eventuais problemas de marcação do evento de óbito na base de origem (evidenciado pela existência de casos de indivíduos com até 136 anos de idade, por exemplo). Para evitar a utilização destes dados e o aprendizado de padrões equivocados por parte do modelo durante a fase de treinamento, decidiu-se limitar o público de desenvolvimento somente aos indivíduos com até 90 anos de idade.

![Análise Limitação Idades](data/analise_limitacao_idade.png)
<p align="center">
  <bold>Figura 3:</bold> Taxa de óbito por faixa de idade e janela de avaliação do evento mostrado nas quebras Correntista/Não Correntista.
</p>

<br/>

Já a segunda (e última) alteração realizada na base de dados amostrada teve origem em uma análise das taxas de óbito avaliadas por faixa de idade dentro das marcações estratégicas de bancos. A Figura 4 traz os dados dessa análise, que evidenciam padrões inesperados nas taxas de óbito observadas para 2 grupos em especial: as marcações de banco Renúncia e Missing (vazio). Os números do banco Renúncia são os únicos que mostram uma inversão na taxa de óbito para a faixa de idades mais altas (86-90 anos) tanto no conjunto dos Correntistas quanto no dos Não Correntistas e os indivíduos com marcação de banco Missing (ou vazio) apresentam valores muito discrepantes especialmente no que diz respeito aos Correntistas. Novamente aqui as mesmas justificativas se aplicam, e estas divergências observadas nos dados têm origem muito provável na baixa volumetria ou preenchimento dessas categorias aliado a eventuais problemas de marcação do evento de óbito. Desta forma, decidiu-se seguir com a eliminação de registros com marcações de bancos Renúncia ou Missing na definição do público final de desenvolvimento do modelo.

![Análise Limitação Bancos](data/analise_limitacao_bancos.png)
<p align="center">
  <bold>Figura 4:</bold> Taxa de óbito por faixa de idade e marcação de banco mostrado nas quebras Correntista/Não Correntista.
</p>

<br/>

Com a realização destes ajustes, o público amostrado original de 1 milhão de exemplos foi reduzido em aproximadamente ~25%, atingindo uma volumetria final total de 746.029 indivíduos. A Figura 5 traz a distribuição dos 3 grandes segmentos do público conforme consolidados em cada um dos conjuntos de dados discutidos acima.

![Público Desenvolvimento](data/volumetrias_publico_desenv.png)
<p align="center">
  <bold>Figura 5:</bold> Volumetria, proporção e taxa de óbito das diferentes segmentações de público nas bases de dados inicial (visão população), intermediária (1MM de observações) e na base filtrada final de desenvolvimento do modelo.
</p>
