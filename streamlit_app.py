import streamlit as st
import datetime
import requests
import pandas as pd
import google.generativeai as genai
import os

st.set_page_config(
    page_title="Sistema de Previsão de Vendas Varejistas",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Previsão de Vendas e Insights")
st.markdown("Use esta ferramenta para obter previsões de vendas semanais e dicas estratégicas para sua loja e departamento.")

#Configuração da Gemini API
#A chave da API é carregada de .streamlit/secrets.toml
try:
    gemini_api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    gemini_api_key = os.environ.get("GOOGLE_API_KEY")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model_gemini = genai.GenerativeModel('gemini-2.5-flash')
    st.sidebar.success("Gemini API configurada com sucesso!")
else:
    st.sidebar.error("Chave de API do Gemini não encontrada! Por favor, configure-a em .streamlit/secrets.toml ou como variável de ambiente.")
    model_gemini = None


API_BASE_URL = "https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app"

#Entrada de Dados
st.header("Dados para Previsão")

with st.form("prediction_form"):
    store_id = st.number_input("ID da Loja", min_value=1, max_value=45, value=1, step=1,
                                help="Insira o ID da loja (entre 1 e 45).")
    department_id = st.number_input("ID do Departamento", min_value=1, value=1, step=1,
                                    help="Insira o ID do departamento. (Ex: 1, 3, 5, 7, etc.)")
    
    default_start_date = datetime.date(2013, 1, 4)
    start_date = st.date_input("Data de Início da Previsão", value=default_start_date,
                                help="Selecione a data de início da previsão (deve ser uma sexta-feira e futura, ex: 2013-01-04).")

    submit_button = st.form_submit_button("Gerar Previsão e Insights")

#Seção de Resultados
st.header("Resultados da Previsão")

if submit_button:
    payload = {
        "store_id": store_id,
        "department_id": department_id,
        "start_date": start_date.strftime('%Y-%m-%d')
    }

    prediction_url = f"{API_BASE_URL}/previsao-vendas"
    
    st.info(f"Chamando a API de previsão em: {prediction_url}")
    
    predictions_data = None
    try:
        response = requests.post(prediction_url, json=payload)
        response.raise_for_status()

        predictions_data = response.json()
        
        st.success("Previsão gerada com sucesso!")
        
        predictions_df = pd.DataFrame(predictions_data['predictions'])
        predictions_df['predicted_sales'] = predictions_df['predicted_sales'].map('${:,.2f}'.format)
        st.dataframe(predictions_df, hide_index=True, use_container_width=True)
        
        st.session_state['predictions_data_for_llm'] = predictions_data
        
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get('detail', 'Erro desconhecido da API')
        st.error(f"Erro na API: {e.response.status_code} - {error_detail}")
        st.session_state['predictions_data_for_llm'] = None
    except requests.exceptions.ConnectionError:
        st.error("Erro de conexão: A API pode não estar rodando ou a URL está incorreta.")
        st.session_state['predictions_data_for_llm'] = None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao chamar a API: {e}")
        st.session_state['predictions_data_for_llm'] = None

    #Seção da LLM
    if predictions_data and model_gemini:
        st.header("Insights e Dicas da Inteligência Artificial")
        with st.spinner("Gerando insights com a LLM..."):
            try:
                prompt_content = f"""
                Analise as seguintes previsões de vendas semanais para a Loja {predictions_data['store_id']}, Departamento {predictions_data['department_id']}:

                Previsões:
                """
                for pred in predictions_data['predictions']:
                    prompt_content += f"- Data: {pred['date']}, Vendas Previstas: ${pred['predicted_sales']:,.2f}\n"

                prompt_content += """

                Com base nessas previsões, forneça um resumo conciso (em apenas 1 parágrafos) do cenário de vendas para as próximas 4 semanas.
                Em seguida, ofereça 2 dicas acionáveis e estratégicas para o gerente da loja ou departamento, focando em:
                1. Otimização de Estoque (com base nos picos/vales de vendas).
                2. Estratégias de Vendas/Marketing (aproveitando picos ou impulsionando vales).
                3. Qualquer outra observação relevante que possa ser inferida dos números.

                Se houver um feriado nas semanas previstas (ex: vendas atípicas para uma semana de feriado, mesmo que não explicitly marcada), mencione e dê uma dica específica sobre ele.
                """
                
                response_gemini = model_gemini.generate_content(prompt_content)
                
                #Exibindo a resposta da LLM
                st.write(response_gemini.text)

            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar insights com a LLM: {e}")
                st.warning("Verifique sua chave de API Gemini e se o modelo está acessível.")

st.markdown("---")
st.caption("Desenvolvido para otimização de vendas e estoque.")