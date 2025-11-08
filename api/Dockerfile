FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /code

# Copiar arquivos do projeto
COPY ./api /code/api
COPY requirements.txt /code/requirements.txt

# Instalar dependências
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Comando padrão para iniciar o FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]