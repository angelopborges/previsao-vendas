> [!NOTE]
> Site com chamada da API de previsão e análise de LLM [Streamlit](https://previsao-vendas-streamlit-app-115310441149.southamerica-east1.run.app/).

# Sistema de Previsão e Otimização de Vendas Varejistas

## Visão Geral do Projeto

Este projeto implementa um sistema de Machine Learning para prever as vendas semanais de cada departamento em 45 lojas de uma rede varejista. Além das previsões, o sistema gera insights acionáveis e recomendações estratégicas para otimização de estoque e campanhas promocionais, culminando em uma API para fácil consulta.

## 1. Motivação de Negócio

A rede varejista busca otimizar suas vendas e a gestão de estoque em um mercado competitivo. A previsão de vendas manual ou limitada resultava em:
* **Perda de Oportunidades:** Ruptura de estoque em alta demanda.
* **Excesso de Estoque:** Acúmulo de produtos, gerando custos.
* **Promoções Subutilizadas:** Falta de clareza sobre o impacto real dos descontos.

## 2. Objetivo do Projeto

O objetivo principal é prever as vendas de cada departamento de cada loja para o ano seguinte e propor ações recomendadas com maior impacto no negócio.

**Métricas de Sucesso (Onde queremos chegar):**
* Redução da ruptura de estoque para menos de 5% em departamentos chave.
* Redução do excesso de estoque para menos de 10% em períodos de baixa demanda.
* Aumento do ROI médio das promoções em 10% através de recomendações baseadas em dados.
* MAPE (Mean Absolute Percentage Error) inferior a 10% nas previsões semanais de vendas.

## 3. Estrutura do Projeto

O projeto está organizado na seguinte estrutura de diretórios:

```
├── main.py                       # Código da API FastAPI
├── Dockerfile                    # Arquivo para construir a imagem Docker da API
├── requirements.txt              # Dependências Python do projeto
├── README.md                     # Este arquivo
├── .gitignore                    # Arquivo para controle de versão (ignora arquivos temporários)
├── data/                         # Dados do projeto
│   └── raw/                      # Dados brutos originais
│       ├── stores data-set.csv
│       ├── Features data set.csv
│       └── sales data-set.csv
├── models/                       # Modelos de ML e pré-processadores salvos (artefatos)
│   ├── best_xgb_model.joblib     # Modelo XGBoost treinado
│   └── preprocessor.joblib       # Pré-processador (ColumnTransformer) treinado
└── notebooks/                    
├── 01_Data_Preparation_and_EDA.ipynb
├── 02_Model_Training_and_Prediction.ipynb
├── 03_API_Development_and_Testing.ipynb
└── 04_Insights_and_Recommendations.ipynb
```


## 4. Requisitos

Para configurar e rodar o projeto, você precisará ter instalado:

* **Python 3.9+**
* **pip** (gerenciador de pacotes Python)
* **venv** (para ambientes virtuais, já incluso no Python 3.3+)
* **Docker Desktop** (ou engine Docker)

## 5. Configuração do Ambiente Local

Siga estes passos para configurar seu ambiente de desenvolvimento e instalar as dependências:

1.  **Clone o Repositório:**
    ```bash
    git clone 'ESSE REPO'
    cd projeto_previsao_vendas
    ```
2.  **Crie e Ative o Ambiente Virtual:**

3.  **Instale as Dependências:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt


## 6. Executando a API Localmente (via Docker)

Para testar a API no seu ambiente local usando Docker:

1.  **Construa a Imagem Docker:**
    * Certifique-se de que o Docker Desktop está em execução.
    * No terminal (no diretório raiz do projeto):
        ```bash
        docker build -t previsao-vendas-api .
        ```
2.  **Execute o Contêiner Docker:**
    ```bash
    docker run -p 8000:8000 previsao-vendas-api
    ```
    A API estará acessível em `http://127.0.0.1:8000`.

## 7. Acessando e Testando a API

> [!NOTE]
> API de previsão [API Docs](https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/docs#/).

Com a API rodando localmente (Docker) ou implantada no Cloud Run, você pode testá-la:

* **Documentação Interativa (Swagger UI):**
    * Local: `http://127.0.0.1:8000/docs`
    * Cloud Run: `https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/docs`
* **Endpoint de Saúde (`GET /health`):**
    ```bash
    curl "https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/health"
    ```
* **Endpoint de Previsão (`POST /previsao-vendas`):**
    ```bash
    curl -X POST "https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/previsao-vendas" \
    -H "Content-Type: application/json" \
    -d '{
      "store_id": 1,
      "department_id": 1,
      "start_date": "2013-01-04"
    }'
    ```
    *Substitua pela URL local (`http://127.0.0.1:8000`) ou pela URL do seu serviço Cloud Run (`https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app`).*

## 8. Insights e Recomendações Gerados

O projeto não apenas prevê vendas, mas também gera insights acionáveis para otimização de estoque e promoções. Você pode encontrar a lógica para esses insights nos notebooks ou na saída dos scripts de desenvolvimento.

* **Análise de Desempenho do Modelo:** Métricas como MAPE, MAE e RMSE no conjunto de teste para entender a precisão do modelo.
* **Recomendações de Estoque:** Sugestões para `Aumentar`, `Reduzir` ou `Manter` estoque em semanas/lojas/departamentos específicos com base nos desvios das vendas previstas.
* **Recomendações de Promoções:** Análise do impacto histórico de diferentes `MarkDowns` e feriados nas vendas, com sugestões estratégicas para otimizar campanhas futuras.

## 9. Próximos Passos

Para aprimorar ainda mais e operacionalizar o sistema em um ambiente de produção completo, os seguintes pontos podem ser considerados:

* **Autenticação e Autorização da API:** Implementar mecanismos de segurança (e.g., chaves de API, OAuth2) para restringir o acesso à API.
* **Dashboards de Monitoramento:** Criar painéis interativos no Cloud Monitoring ou ferramentas de BI para monitorar a performance do modelo em produção e a saúde da API.
* **Pipeline de Re-treinamento:** Automatizar o processo de re-treinar o modelo com novos dados periodicamente para manter a precisão e evitar a degradação do modelo ao longo do tempo.
* **Simulação de Cenários:** Desenvolver a capacidade de simular o impacto de diferentes estratégias de `MarkDown` no futuro.
