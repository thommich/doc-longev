---
title: "Variável Resposta"
type: docs
sidebar_position: 3
---

# **VARIÁVEL RESPOSTA**

---

## **MARCAÇÃO DO EVENTO DE ÓBITO**

Para marcação do evento de óbito na base de desenvolvimento foi utilizado o [Book de Público](https://github-pages-dev.cloud.itau.com.br/itau-dc6-doc-dados-credito-pessoa-fisica/docs/analitica/outros/book_publico/) (`db_corp_modelagem_onesiriusrich_spec_01.tbdc6s1020_publico_individuo`). O Book disponibiliza um campo que traz informação sobre o status atual do indivíduo perante a Receita Federal e, dentre os valores assumidos pelo mesmo, o critério `cod_situ_pess_fisi_rect_fedr = 3` marca os registros para os quais o órgão possui apontamento cadastral de óbito.

Após realizada a marcação inicial, foram verificadas algumas inconsistências no conjunto de dados obtido, tais quais indivíduos que apresentavam registro de óbito em mais de uma data e indivíduos que apresentavam status de CPF ativo mesmo após uma marcação de evento de óbito em data anterior. Para tratar esses casos de inconsistência foi adotada a regra de utilizar sempre a data da marcação mais antiga de óbito (ou a primeira) presente na base da Receita Federal como padrão. O procedimento completo de marcação do evento de óbito a partir das fontes de informação originais conforme realizado durante o processo de desenvolvimento do modelo pode ser consultado no seguinte Notebook: <!--[NOTEBOOK]-->.

<br/>

## **DEFINIÇÃO DO TARGET DO MODELO**

A definição da variável resposta do modelo buscou aproximar a tarefa de predição de óbito àquela de estimação de risco de crédito, permitindo a aplicação do mesmo arcabouço de métodos e ferramentas já bastante familiares aos cientistas de dados do Crédito PF à resolução do problema. Para tal, foi definida uma janela de tempo em meses (análoga à janela de performance para o risco de crédito) e a variável resposta do modelo definida de forma a assumir o valor 1 em caso de evento de óbito observado em um período de `N` meses a partir da data de referência de entrada do indivíduo na base de dados ou o valor 0 no caso contrário.

Foram realizados alguns experimentos para definição de um valor adequado para `N` - a quantidade exata de meses utilizados na construção da janela de observação da variável resposta. Conforme exposto na Figura abaixo, analisou-se a variação da taxa de óbito para diferentes faixas etárias ao longo de janelas abrangendo diferentes quantidades de meses. Observa-se que não foi constatada nenhuma tendência de estabilização da taxa de óbito conforme o aumento do número de meses, portanto a variável resposta foi definida com base na janela de performance na qual desejava-se discriminar o evento. No caso do Modelo de Longevidade decidiu-se então adotar a janela de 6 meses com a variável resposta do modelo assumindo o conceito de: `ocorrência de óbito nos 6 meses seguintes à referência de entrada do indivíduo na base de dados`.

<!-- [TABELA/GRÁFICOS ESTUDO EXCEL JANELA] -->

## **CARACTERIZAÇÃO DO EVENTO**

<!-- [TAXA DE ÓBITO POR REF] -->
