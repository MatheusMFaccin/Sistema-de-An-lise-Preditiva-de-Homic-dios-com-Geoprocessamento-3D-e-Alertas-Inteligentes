from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from db.session import Base  # onde você definiu o Base
from models import evento, datasus    # importe todos os modelos aqui
import os
from dotenv import load_dotenv

config = context.config
fileConfig(config.config_file_name)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL não encontrado no .env")

# Configura a URL para o Alembic
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
