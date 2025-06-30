# Sistema de Predicción y Optimización de Ventas Minoristas

## Visión General del Proyecto

Este proyecto implementa un sistema de Machine Learning para predecir las ventas semanales de cada departamento en 45 tiendas de una cadena minorista. Además de las predicciones, el sistema genera insights accionables y recomendaciones estratégicas para la optimización de stock y campañas promocionales, culminando en una API para una consulta fácil.

## 1. Motivación del Negocio

La cadena minorista busca optimizar sus ventas y la gestión de stock en un mercado competitivo. La predicción de ventas manual o limitada resultaba en:
* **Pérdida de Oportunidades:** Quiebre de stock ante una alta demanda.
* **Exceso de Stock:** Acumulación de productos, generando costos.
* **Promociones Subutilizadas:** Falta de claridad sobre el impacto real de los descuentos.

## 2. Objetivo del Proyecto

El objetivo principal es predecir las ventas de cada departamento de cada tienda para el año siguiente y proponer acciones recomendadas con el mayor impacto en el negocio.

**Métricas de Éxito (A dónde queremos llegar):**
* Reducción del quiebre de stock a menos del 5% en departamentos clave.
* Reducción del exceso de stock a menos del 10% en períodos de baja demanda.
* Aumento del ROI promedio de las promociones en un 10% a través de recomendaciones basadas en datos.
* MAPE (Mean Absolute Percentage Error) inferior al 10% en las predicciones semanales de ventas.

## 3. Estructura del Proyecto

El proyecto está organizado con la siguiente estructura de directorios:
```
├── main.py                   # Código de la API FastAPI
├── Dockerfile                # Archivo para compilar la imagen Docker de la API
├── requirements.txt          # Dependencias Python del proyecto
├── README.md                 # Este archivo
├── .gitignore                # Archivo para control de versión (ignora archivos temporales)
├── data/                     # Datos del proyecto
│   └── raw/                  # Datos crudos originales
│       ├── stores data-set.csv
│       ├── Features data set.csv
│       └── sales data-set.csv
├── models/                   # Modelos de ML y pre-procesadores guardados (artefactos)
│   ├── best_xgb_model.joblib   # Modelo XGBoost entrenado
│   └── preprocessor.joblib   # Pre-procesador (ColumnTransformer) entrenado
└── notebooks/
  ├── 01_Data_Preparation_and_EDA.ipynb
  ├── 02_Model_Training_and_Prediction.ipynb
  ├── 03_API_Development_and_Testing.ipynb
  └── 04_Insights_and_Recommendations.ipynb
```

## 4. Requisitos

Para configurar y correr el proyecto, necesitarás tener instalado:

* **Python 3.9+**
* **pip** (gestor de paquetes de Python)
* **venv** (para entornos virtuales, ya incluido en Python 3.3+)
* **Docker Desktop** (o motor de Docker)

## 5. Configuración del Entorno Local

Seguí estos pasos para configurar tu entorno de desarrollo e instalar las dependencias:

1.  **Cloná el Repositorio:**
    ```bash
    git clone 'ESTE REPO'
    cd proyecto_prediccion_ventas
    ```
2.  **Creá y Activá el Entorno Virtual:**

3.  **Instalá las Dependencias:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```


## 6. Ejecutando la API Localmente (vía Docker)

Para probar la API en tu entorno local usando Docker:

1.  **Compilá la Imagen de Docker:**
    * Asegurate de que Docker Desktop esté corriendo.
    * En la terminal (en el directorio raíz del proyecto):
        ```bash
        docker build -t prediccion-ventas-api .
        ```
2.  **Ejecutá el Contenedor de Docker:**
    ```bash
    docker run -p 8000:8000 prediccion-ventas-api
    ```
    La API estará accesible en `http://127.0.0.1:8000`.

## 7. Accediendo y Probando la API

Con la API corriendo localmente (Docker) o deployada en Cloud Run, podés probarla:

* **Documentación Interactiva (Swagger UI):**
    * Local: `http://127.0.0.1:8000/docs`
    * Cloud Run: `https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/docs`
* **Endpoint de Salud (`GET /health`):**
    ```bash
    curl "[https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/health](https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/health)"
    ```
* **Endpoint de Predicción (`POST /previsao-vendas`):**
    ```bash
    curl -X POST "[https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/previsao-vendas](https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app/previsao-vendas)" \
    -H "Content-Type: application/json" \
    -d '{
      "store_id": 1,
      "department_id": 1,
      "start_date": "2013-01-04"
    }'
    ```
    *Reemplazá por la URL local (`http://127.0.0.1:8000`) o por la URL de tu servicio en Cloud Run (`https://previsao-vendas-api-staging-dtm4k4jetq-rj.a.run.app`).*

## 8. Insights y Recomendaciones Generados

El proyecto no solo predice ventas, sino que también genera insights accionables para la optimización de stock y promociones. Podés encontrar la lógica para estos insights en los notebooks o en la salida de los scripts de desarrollo.

* **Análisis de Rendimiento del Modelo:** Métricas como MAPE, MAE y RMSE en el conjunto de test para entender la precisión del modelo.
* **Recomendaciones de Stock:** Sugerencias para `Aumentar`, `Reducir` o `Mantener` stock en semanas/tiendas/departamentos específicos, basándose en los desvíos de las ventas predichas.
* **Recomendaciones de Promociones:** Análisis del impacto histórico de diferentes `MarkDowns` y feriados en las ventas, con sugerencias estratégicas para optimizar campañas futuras.

## 9. Próximos Pasos

Para mejorar aún más y operacionalizar el sistema en un entorno de producción completo, se pueden considerar los siguientes puntos:

* **Autenticación y Autorización de la API:** Implementar mecanismos de seguridad (ej: claves de API, OAuth2) para restringir el acceso a la API.
* **Dashboards de Monitoreo:** Crear paneles interactivos en Cloud Monitoring o herramientas de BI para monitorear el rendimiento del modelo en producción y la salud de la API.
* **Pipeline de Re-entrenamiento:** Automatizar el proceso de re-entrenar el modelo con nuevos datos periódicamente para mantener la precisión y evitar la degradación del modelo a lo largo del tiempo.
* **Simulación de Escenarios:** Desarrollar la capacidad de simular el impacto de diferentes estrategias de `MarkDown` en el futuro.