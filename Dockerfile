# Usa uma imagem base Python oficial (versão 3.9 slim para ser mais leve)
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

COPY models/ models/

RUN mkdir -p data/raw

# Copia os arquivos CSV de dados brutos da sua pasta 'data/raw'
COPY data/raw/ data/raw/

# Expõe a porta em que a API será executada
EXPOSE 8000

# Define o comando para iniciar a aplicação quando o contêiner for executado
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]