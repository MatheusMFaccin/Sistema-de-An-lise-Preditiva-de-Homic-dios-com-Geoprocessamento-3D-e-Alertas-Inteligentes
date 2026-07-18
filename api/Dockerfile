FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /code/api

# Copiar arquivos do projeto (contexto = ./api/)
COPY . /code/api
COPY requirements.txt /code/

# Instalar dependências
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN chmod +x /code/api/startup.sh

# Comando padrão: migra, popula se vazio, inicia servidor
CMD ["/bin/bash", "/code/api/startup.sh"]