---
title: "Definição dos Níveis de Risco"
type: docs
sidebar_position: 6
---

# **DEFINIÇÃO DOS NÍVEIS DE RISCO**

---

## **OBTENÇÃO DOS PONTOS DE CORTE**

Os pontos de corte utilizados para determinação dos grupos de risco do Modelo de Longevidade foram obtidos a partir de um processo de otimização com o objetivo de transformar o score contínuo do modelo de risco em um conjunto reduzido de grupos ordenados, contíguos e temporalmente estáveis. A descrição completa da metodologia aplicada pode ser consultada acessando sua [Documentação](<!--LINK-->).

A solução foi implementada através da função `optimal_binning_with_prebins` que pode ser consultada acessando o arquivo [utils.py](<!--LINK-->). Esta implementação combina quatro decisões centrais:

- Pré-binning ponderado, para representar a população e reduzir o domínio de busca.
- Minimização do IEP dos níveis de risco ao longo do tempo como objetivo primário, para alinhar a otimização à métrica de estabilidade desejada.
- Otimização lexicográfica, que define a minimização do IEP como objetivo primário e a estabilidade das taxas de evento de óbito como objetivo secundário.
- Programação dinâmica como técnica de otimização, para preservar a dependência monotônica e alcançar o ótimo global no espaço discretizado dos pré-bins.

A adoção desta metodologia e a implementação específica utilizada seguindo os critérios acima produz uma solução mais consistente do ponto de vista estatístico, computacional e de governança do que abordagens baseadas em cortes manuais, algoritmos gulosos (exemplo do Auto GI) ou programação dinâmica com estados excessivamente comprimidos.

## **CARACTERIZAÇÃO DOS NÍVEIS DE RISCO**

### - DISTRIBUIÇÃO DOS NÍVEIS DE RISCO AO LONGO DO TEMPO

### - IEP AO LONGO DO TEMPO

### - TAXA DE ÓBITO POR NÍVEL DE RISCO AO LONGO DO TEMPO
