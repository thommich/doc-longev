---
title: "Desenvolvimento do Modelo"
type: docs
sidebar_position: 5
---

# **DESENVOLVIENTO DO MODELO**

---

## **PROCESSO DE MODELAGEM ITERATIVO**

Ao longo da execução de um projeto de Ciência de Dados é comum adotar um processo iterativo de desenvolvimento do modelo onde soluções intermediárias vão sendo produzidas e cada nova versão traz melhorias ou corrige direcionamentos adotados em versões anteriores (framework CRISP-DM, por exemplo). No desenvolvimento do Modelo de Longevidade foram produzidas 4 grandes versões de modelo (*majors*) e a última delas é a que foi produtizada e sobre a qual discorre essa documentação. Abaixo encontram-se listados os principais fatores que diferenciam cada grande versão de suas anteriores:

<!-- FIGURA -->

## **OTIMIZAÇÃO DE HIPERPARÂMETROS**

Tendo definido o conjunto final de variáveis para compor o modelo, conforme detalhado na seção [Exploração de Dados](<!--LINK-->), deu-se seguimento ao processo de modelagem através da etapa de otimização de hiperparâmetros. Abaixo encontram-se listados os parâmetros de entrada utilizados pela ferramenta [Optuna](<!--LINK-->) durante o processo de otimização bem como os hiperparâmetros finais selecionados.

<!-- TABELA -->

Para obtenção de estimativas mais robustas de performance do modelo, o processo de otimização realiza uma validação cruzada no intuito de avaliar a métrica de performance em diferentes quebras do conjunto de dados de treinamento para cada combinação diferente de hiperparâmetros testados. Vale ressaltar que, por questões da dinâmica temporal inerente ao problema modelado e no intuito de evitar qualquer possibilidade de *data leakage*, os folds do processo de validação cruzada foram definidos de maneira a garantir que os dados utilizados para treinamento do modelo fossem anteriores aos dados utilizados na validação, em um padrão de janelas temporais crescentes, conforme sugere a literatura do tema [^1] [^2]. Ainda que o conjunto de dados de treinamento tenha sido corretamente controlado via deduplicação dos registros para que cada indivíduo fosse representado apenas uma vez no conjunto de dados completo, mitigando desta maneira o possível risco de treinar o modelo em dados futuros, a manutenção da ordenação temporal dos folds durante o processo de validação cruzada permite mitigar riscos com potencial origem no *shift* da distribuição de dados ou no conceito de variáveis que deterioram a performance em um regime de avaliação futuro e que podem ser descartados quando analisados sob um processo de validação cruzada utilizando folds definidos aleatoriamente.

O processo completo de otimização e seus outputs podem ser consultados acessando o Notebook [X - Modelagem](<!--LINK-->).

## **TREINAMENTO DO MODELO**

Foi treinado um modelo [LGBM](<!--LINK-->) (Light Gradient Boosting Machine) utilizando os hiperparâmetros ótimos selecionados na etapa descrita acima. Os quadros abaixo exibem as versões de cada biblioteca Python utilizada para o treinamento do modelo.

<!-- VERSÕES DAS LIBS PYTHON -->

Durante o processo de treinamento foram utilizadas as safras de 04 e 05/2025 como conjunto de dados de validação além de definidas 2000 rodadas de boosting com um parâmetro de *early-stopping* de 50 rodadas a fim de mitigar possíveis riscos de overfitting. O modelo final treinado é um ensemble composto de 750 árvores e apresenta métricas de performance conforme o quadro abaixo:

<!-- GINIS -->

Na Figura X são exibidas as curvas de aprendizado obtidas durante o treinamento do modelo para as métricas de AUC (métrica de performance) e de *binary-logloss* (métrica de otimização da função de perda) tanto para o conjunto de dados de treinamento quanto para o de validação. As curvas permitem afirmar que, apesar do gap de performance do modelo observado entre os conjuntos de treino/validação/teste, o modelo demonstra um comportamento de aprendizado saudável, sem a presença de quaisquer sinais óbvios de overfit. O treinamento é interrompido na 750ª iteração quando ambas as curvas de treinamento e validação estão atingindo seu plateau e não observa-se aumento de performance no conjunto de treinamento após estagnação ou inversão da curva de validação conforme espera-se de regimes clássicos de overfit.

## **AVALIAÇÃO DO MODELO NA BASE DE DESENVOLVIMENTO**

### - FEATURE IMPORTANCES

<!-- FIGURA -->

### - PERFORMANCE DO MODELO

<!-- FIGURA -->

### - DISCRIMINAÇÃO DO MODELO POR QUANTIL DO SCORE

<!-- FIGURA -->

[^1]: [https://arxiv.org/abs/2112.10078](https://arxiv.org/abs/2112.10078)

[^2]: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6336198](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6336198)
