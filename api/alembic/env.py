from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# 1. Adiciona a raiz do projeto ao Python Path para encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# 2. Carrega variáveis de ambiente
load_dotenv()

# 3. Importa o Base e os Modelos
# ATENÇÃO: A ordem aqui é o que corrige o erro de chave estrangeira!
from db.session import Base

# IMPORTANTE: Importe as CLASSES, não apenas os arquivos.
# Ordem: Primeiro quem não tem dependência (Pai), depois quem depende (Filho)
from models.municipio import Municipio       # <--- Principal (tem que ser o primeiro)
from models.evento import Evento             # Depende de Municipio
from models.datasus import Datasus           # Depende de Municipio
from models.previsao import Previsao         # Depende de Municipio
from models.dados_reais import EventosTotaisAnuais # Depende de Municipio
from models.ComparativoPrevisao import ComparativoPrevisao # Depende de Previsao e Dados Reais

config = context.config
fileConfig(config.config_file_name)

# 4. Configura a URL do Banco
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    # Fallback ou erro caso não ache no .env (Opcional: coloque uma string direta para testar)
    raise ValueError("DATABASE_URL não encontrado no arquivo .env")

# Garante que o driver psycopg2 seja usado se estiver escrito apenas "postgres://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 5. Define os metadados para o Alembic ler
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # compare_type=True ajuda a detectar mudanças de tipo (ex: String para Integer)
        compare_type=True, 
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()