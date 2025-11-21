🚀 Guia de Instalação e Execução
Este tutorial descreve como configurar o ambiente e rodar o projeto de análise de dados de segurança pública (DataSUS vs Eventos de Segurança).

📋 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:

Git

Docker e Docker Compose (Para o banco de dados)

Python 3.10+

🛠️ 2. Instalação
2.1. Clone o Repositório
Bash

git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
2.2. Crie o Ambiente Virtual (Recomendado)
Isso isola as bibliotecas do projeto do seu sistema global.

Linux/Mac:

Bash

python3 -m venv venv
source venv/bin/activate
Windows (PowerShell):

PowerShell

python -m venv venv
.\venv\Scripts\Activate
2.3. Instale as Dependências
Bash

pip install -r requirements.txt
(Nota: Se você ainda não criou esse arquivo, gere-o agora com pip freeze > requirements.txt)

⚙️ 3. Configuração de Ambiente (.env)
O projeto utiliza variáveis de ambiente para credenciais sensíveis.

Crie um arquivo chamado .env na raiz do projeto.

Copie o conteúdo abaixo e ajuste conforme necessário:

Ini, TOML

# .env
# Ajuste usuário, senha, host e nome do banco conforme seu Docker
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/nome_do_banco
🐳 4. Subindo o Banco de Dados
Utilizamos Docker para rodar o PostgreSQL.
Bash
docker-compose up --build -d
Aguarde alguns segundos para o banco iniciar.

🔄 5. Migrações (Alembic)
Agora precisamos criar as tabelas (eventos, datasus, previsoes, comparativo, etc.) no banco de dados usando o Alembic.

entre no conteiner do fastapi com o comando docker exec -it <id do conteiner> bash

Certifique-se de que está na raiz do projeto.

Execute as migrações:

Bash

alembic upgrade head

alembic revision --autogenerate -m "criando as tabelas do banco"

alembic upgrade head
Se não houver erros, seu banco de dados está pronto e estruturado.

📊 6. Executando a Carga e Análise de Dados
Para popular o banco de dados, gerar previsões e salvar os comparativos, execute o script principal de ETL.

entre no conteiner do fastapi com o comando docker exec -it <id do conteiner> bash
Bash

python scripts/insert_data.py
O que este script fará (resumo):

Lerá os arquivos CSV/Excel originais.

Limpará os dados.

Inserirá os dados brutos nas tabelas eventos e datasus.

Calculará as previsões (Regressão Linear) e salvará em previsoes.

Comparará os dados reais vs previstos e salvará em comparativo_previsoes.


🌐 7. Executando a Aplicação Web

entre na pasta app pelo terminal

execute os seguintes comandos

bash

docker-compose up --build -d

docker exec -it <id do conteiner> bash

python manage.py instadb consultas > models.py

exit 

entre na url http://localhost:8001/mapa/
