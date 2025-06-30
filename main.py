# main.py ou api.py - ATUALIZE ESTE ARQUIVO

from fastapi import FastAPI, HTTPException
import uvicorn
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


best_xgb_model = None
preprocessor = None
features_to_use = []
historical_weekly_avg = None 
unique_stores_depts_list = []
df_stores_load = None
last_historical_date = None

try:
    models_dir = 'models'
    model_path = os.path.join(models_dir, 'best_xgb_model.joblib')
    preprocessor_path = os.path.join(models_dir, 'preprocessor.joblib')

    best_xgb_model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    stores_file = os.path.join('', 'data/raw/stores data-set.csv')
    features_file = os.path.join('', 'data/raw/Features data set.csv')
    sales_file = os.path.join('', 'data/raw/sales data-set.csv')

    df_stores_load = pd.read_csv(stores_file)
    df_features_load = pd.read_csv(features_file)
    df_sales_load = pd.read_csv(sales_file)

    df_sales_load['Date'] = pd.to_datetime(df_sales_load['Date'], format='%d/%m/%Y', errors='coerce')
    df_features_load['Date'] = pd.to_datetime(df_features_load['Date'], format='%d/%m/%Y', errors='coerce')
    df_sales_load.dropna(subset=['Date'], inplace=True)
    df_features_load.dropna(subset=['Date'], inplace=True)

    df_sales_stores_load = pd.merge(df_sales_load, df_stores_load, on='Store', how='left')
    df_final_for_context = pd.merge(df_sales_stores_load, df_features_load, on=['Store', 'Date'], how='left')

    markdown_cols = ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5']
    for col in markdown_cols:
        if col in df_final_for_context.columns:
            df_final_for_context[col] = df_final_for_context[col].fillna(0)

    economic_cols = ['CPI', 'Unemployment']
    for col in economic_cols:
        if col in df_final_for_context.columns:
            df_final_for_context[col] = df_final_for_context[col].interpolate(method='linear', limit_direction='both')
            if df_final_for_context[col].isnull().any():
                df_final_for_context[col] = df_final_for_context[col].fillna(df_final_for_context[col].mean())

    df_final_for_context = df_final_for_context[df_final_for_context['Weekly_Sales'] > 0]
    df_final_for_context['Date'] = pd.to_datetime(df_final_for_context['Date'], errors='coerce')
    df_final_for_context.dropna(subset=['Date'], inplace=True)

    df_final_for_context['Year'] = df_final_for_context['Date'].dt.year
    df_final_for_context['Month'] = df_final_for_context['Date'].dt.month
    df_final_for_context['Week'] = df_final_for_context['Date'].dt.isocalendar().week.astype(int)
    df_final_for_context['Day'] = df_final_for_context['Date'].dt.day
    df_final_for_context['DayOfWeek'] = df_final_for_context['Date'].dt.dayofweek
    df_final_for_context['DayOfYear'] = df_final_for_context['Date'].dt.dayofyear

    if 'IsHoliday_x' in df_final_for_context.columns and 'IsHoliday_y' in df_final_for_context.columns:
        df_final_for_context.rename(columns={'IsHoliday_x': 'IsHoliday'}, inplace=True)
        df_final_for_context.drop(columns=['IsHoliday_y'], inplace=True)
    elif 'IsHoliday_x' in df_final_for_context.columns:
        df_final_for_context.rename(columns={'IsHoliday_x': 'IsHoliday'}, inplace=True)
    elif 'IsHoliday_y' in df_final_for_context.columns:
        df_final_for_context.rename(columns={'IsHoliday_y': 'IsHoliday'}, inplace=True)

    if 'IsHoliday' in df_final_for_context.columns:
        df_final_for_context['IsHoliday_Flag'] = df_final_for_context['IsHoliday'].astype(int)

    df_final_for_context['SuperBowl'] = ((df_final_for_context['Month'] == 2) & (df_final_for_context['Week'].isin([6, 7])) | \
                                         (df_final_for_context['Month'] == 9) & (df_final_for_context['Week'].isin([36])) | \
                                         (df_final_for_context['Month'] == 11) & (df_final_for_context['Week'].isin([47])) | \
                                         (df_final_for_context['Month'] == 12) & (df_final_for_context['Week'].isin([51, 52]))).astype(int)
    
    df_final_for_context['IsHoliday'] = df_final_for_context['IsHoliday_Flag'].astype(bool)

    df_final_for_context['LaborDay'] = ((df_final_for_context['Month'] == 9) & (df_final_for_context['Week'].isin([36])) & (df_final_for_context['IsHoliday'] == True)).astype(int)
    df_final_for_context['Thanksgiving'] = ((df_final_for_context['Month'] == 11) & (df_final_for_context['Week'].isin([47])) & (df_final_for_context['IsHoliday'] == True)).astype(int)
    df_final_for_context['Christmas'] = ((df_final_for_context['Month'] == 12) & (df_final_for_context['Week'].isin([51, 52])) & (df_final_for_context['IsHoliday'] == True)).astype(int)

    historical_weekly_avg = df_final_for_context.groupby('Week')[['Temperature', 'Fuel_Price', 'CPI', 'Unemployment']].mean().reset_index()
    unique_stores_depts_list = [tuple(x) for x in df_final_for_context[['Store', 'Dept']].drop_duplicates().values]
    last_historical_date = df_final_for_context['Date'].max()

    features_to_use = [
        'Store', 'Dept', 'Size', 'Temperature', 'Fuel_Price', 'CPI', 'Unemployment',
        'IsHoliday_Flag',
        'Year', 'Month', 'Week', 'Day', 'DayOfWeek', 'DayOfYear',
        'SuperBowl', 'LaborDay', 'Thanksgiving', 'Christmas',
        'TotalMarkDown', 'HasAnyMarkDown'
    ]
    for col in markdown_cols:
        if f'Has_{col}' not in features_to_use:
             features_to_use.append(f'Has_{col}')
        if col not in features_to_use:
            features_to_use.append(col)
    
    if 'Type' in df_final_for_context.columns and 'Type' not in features_to_use:
        features_to_use.append('Type')

    print(f"Modelo, pré-processador e contexto de dados carregados com sucesso. Última data histórica: {last_historical_date.strftime('%Y-%m-%d')}")

except FileNotFoundError:
    print(f"Erro: Modelos ou dados de contexto não encontrados. Certifique-se de que os arquivos existem.")
    print("A API será iniciada, mas as funções de previsão não funcionarão sem os modelos e contexto.")
except Exception as e:
    print(f"Erro inesperado ao carregar modelos/contexto de dados: {e}")
    print("A API será iniciada, mas as funções de previsão podem ser afetadas.")

#Instanciando o aplicativo FastAPI
app = FastAPI(
    title="API de Previsão de Vendas",
    description="API para prever vendas semanais por departamento e loja.",
    version="1.0.0"
)

#Endpoint de saúde
@app.get("/health", summary="Verifica a saúde da API")
async def health_check():
    """
    Retorna o status de saúde da API.
    """
    if best_xgb_model is not None and preprocessor is not None and historical_weekly_avg is not None and unique_stores_depts_list and last_historical_date is not None:
        status_message = "API is healthy and models/context are loaded."
        status_code = 200
    else:
        status_message = "API is running, but models/context failed to load or are incomplete."
        status_code = 500
    return {"status": status_message, "model_loaded": best_xgb_model is not None, "preprocessor_loaded": preprocessor is not None, "context_loaded": historical_weekly_avg is not None and unique_stores_depts_list is not None and last_historical_date is not None}


#Definição dos Modelos Pydantic para Entrada e Saída
class PredictionRequest(BaseModel):
    store_id: int = Field(..., description="ID da loja para a previsão.")
    department_id: int = Field(..., description="ID do departamento para a previsão.")
    start_date: str = Field(..., description="Data de início da previsão no formato 'YYYY-MM-DD'.")

class WeeklyPrediction(BaseModel):
    date: str = Field(..., description="Data da semana da previsão (YYYY-MM-DD).")
    predicted_sales: float = Field(..., description="Vendas semanais previstas para a loja e departamento.")

class PredictionResponse(BaseModel):
    store_id: int
    department_id: int
    predictions: list[WeeklyPrediction]

#Geração de Features Futuras para a API
def generate_future_features_for_api(store_id: int, dept_id: int, start_date_str: str, num_weeks: int = 4):
    try:
        req_start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use 'YYYY-MM-DD'.")

    if last_historical_date is None:
        raise HTTPException(status_code=500, detail="Última data histórica não carregada no contexto da API.")

    if req_start_date <= last_historical_date:
        raise HTTPException(status_code=400, detail=f"A data de início da previsão ({start_date_str}) deve ser posterior à última data nos dados históricos ({last_historical_date.strftime('%Y-%m-%d')}).")

    if (store_id, dept_id) not in unique_stores_depts_list:
        raise HTTPException(status_code=404, detail=f"Combinação de Loja ID {store_id} e Departamento ID {dept_id} não encontrada nos dados históricos.")

    future_dates = [req_start_date + timedelta(weeks=i) for i in range(num_weeks)]

    future_df_single_sd = pd.DataFrame({'Date': future_dates, 'Store': store_id, 'Dept': dept_id})

    future_df_single_sd['Year'] = future_df_single_sd['Date'].dt.year
    future_df_single_sd['Month'] = future_df_single_sd['Date'].dt.month
    future_df_single_sd['Week'] = future_df_single_sd['Date'].dt.isocalendar().week.astype(int)
    future_df_single_sd['Day'] = future_df_single_sd['Date'].dt.day
    future_df_single_sd['DayOfWeek'] = future_df_single_sd['Date'].dt.dayofweek
    future_df_single_sd['DayOfYear'] = future_df_single_sd['Date'].dt.dayofyear

    future_df_single_sd['IsHoliday'] = False

    #A lógica de feriados deve ser consistente com o treinamento
    future_df_single_sd['IsHoliday_Flag'] = ((future_df_single_sd['Month'] == 2) & (future_df_single_sd['Week'].isin([6, 7])) | \
                                            (future_df_single_sd['Month'] == 9) & (future_df_single_sd['Week'].isin([36])) | \
                                            (future_df_single_sd['Month'] == 11) & (future_df_single_sd['Week'].isin([47])) | \
                                            (future_df_single_sd['Month'] == 12) & (future_df_single_sd['Week'].isin([51, 52]))).astype(int)

    future_df_single_sd['IsHoliday'] = future_df_single_sd['IsHoliday_Flag'].astype(bool)

    future_df_single_sd['SuperBowl'] = ((future_df_single_sd['Month'] == 2) & (future_df_single_sd['Week'].isin([6, 7])) & (future_df_single_sd['IsHoliday'] == True)).astype(int)
    future_df_single_sd['LaborDay'] = ((future_df_single_sd['Month'] == 9) & (future_df_single_sd['Week'].isin([36])) & (future_df_single_sd['IsHoliday'] == True)).astype(int)
    future_df_single_sd['Thanksgiving'] = ((future_df_single_sd['Month'] == 11) & (future_df_single_sd['Week'].isin([47])) & (future_df_single_sd['IsHoliday'] == True)).astype(int)
    future_df_single_sd['Christmas'] = ((future_df_single_sd['Month'] == 12) & (future_df_single_sd['Week'].isin([51, 52])) & (future_df_single_sd['IsHoliday'] == True)).astype(int)


    if historical_weekly_avg is None:
        raise HTTPException(status_code=500, detail="Dados de contexto para features econômicas/climáticas não carregados.")

    future_df_single_sd = pd.merge(future_df_single_sd, historical_weekly_avg, on='Week', how='left')

    markdown_cols_existing = ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5']
    for col in markdown_cols_existing:
        if col in features_to_use:
            future_df_single_sd[col] = 0.0
        if f'Has_{col}' in features_to_use:
            future_df_single_sd[f'Has_{col}'] = 0
    if 'TotalMarkDown' in features_to_use:
        future_df_single_sd['TotalMarkDown'] = 0.0
    if 'HasAnyMarkDown' in features_to_use:
        future_df_single_sd['HasAnyMarkDown'] = 0

    if df_stores_load is None:
        raise HTTPException(status_code=500, detail="Dados de lojas (df_stores_load) não carregados.")

    store_info_df = df_stores_load[df_stores_load['Store'] == store_id]
    if store_info_df.empty:
        raise HTTPException(status_code=404, detail=f"Loja ID {store_id} não encontrada nos dados.")

    store_info = store_info_df[['Type', 'Size']].iloc[0]
    future_df_single_sd['Type'] = store_info['Type']
    future_df_single_sd['Size'] = store_info['Size']

    if 'Type' in future_df_single_sd.columns:
        future_df_single_sd['Type'] = future_df_single_sd['Type'].astype('category')

    final_future_X_raw = future_df_single_sd[features_to_use]

    return final_future_X_raw


#Endpoint Principal de Previsão
@app.post("/previsao-vendas", response_model=PredictionResponse, summary="Obtém a previsão de vendas para as próximas 4 semanas")
async def predict_sales(request: PredictionRequest):
    """
    Fornece as previsões de vendas semanais para uma loja e departamento específicos
    para as próximas 4 semanas a partir de uma data de início.

    - **store_id**: ID da loja.
    - **department_id**: ID do departamento.
    - **start_date**: Data de início da previsão (formato 'YYYY-MM-DD').
    """
    if best_xgb_model is None or preprocessor is None:
        raise HTTPException(status_code=500, detail="Modelos de ML não carregados. A API não está pronta para previsões.")
    if historical_weekly_avg is None or not unique_stores_depts_list:
        raise HTTPException(status_code=500, detail="Contexto de dados para features não carregado. A API não está pronta para previsões.")
    if df_stores_load is None:
        raise HTTPException(status_code=500, detail="Dados de lojas (df_stores_load) não carregados.")
    if last_historical_date is None:
        raise HTTPException(status_code=500, detail="Última data histórica não carregada. A API não está pronta para previsões.")


    try:
        future_X_raw_df = generate_future_features_for_api(
            store_id=request.store_id,
            dept_id=request.department_id,
            start_date_str=request.start_date,
            num_weeks=4
        )

        X_future_processed = preprocessor.transform(future_X_raw_df)

        if hasattr(X_future_processed, 'toarray'):
            X_future_processed = X_future_processed.toarray()

        predictions = best_xgb_model.predict(X_future_processed)

        predictions[predictions < 0] = 0

        response_predictions = []
        for i, pred_val in enumerate(predictions):
            current_date = datetime.strptime(request.start_date, '%Y-%m-%d') + timedelta(weeks=i)
            response_predictions.append(
                WeeklyPrediction(date=current_date.strftime('%Y-%m-%d'), predicted_sales=float(pred_val))
            )

        return PredictionResponse(
            store_id=request.store_id,
            department_id=request.department_id,
            predictions=response_predictions
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro durante a previsão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno durante a previsão: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)