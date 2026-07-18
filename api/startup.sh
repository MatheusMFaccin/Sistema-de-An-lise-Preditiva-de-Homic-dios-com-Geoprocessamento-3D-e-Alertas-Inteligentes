#!/bin/bash
set -e

echo ">>> Aguardando PostgreSQL ficar disponível..."

until python -c "
import models  # Carrega todos os models na ordem correta
from db.session import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
" 2>/dev/null; do
    echo "PostgreSQL não está pronto ainda. Aguardando..."
    sleep 2
done
echo "PostgreSQL pronto!"

echo ""
echo ">>> Rodando migrações Alembic..."
alembic -c /code/api/alembic.ini upgrade head

echo ""
echo ">>> Verificando se o banco está vazio..."

BANCO_STATUS=$(python -c "
import models
from db.session import SessionLocal
db = SessionLocal()
count = db.query(models.Municipio).count()
db.close()
print('EMPTY' if count == 0 else 'FILLED')
")

if [ "$BANCO_STATUS" = "EMPTY" ]; then
    echo ""
    echo ">>> Banco vazio. Iniciando carga de dados com insert_data.py..."
    cd /code/api
    python scripts/insert_data.py
    echo ">>> Carga de dados concluída!"
else
    echo ""
    echo ">>> Banco já populado. Pulando carga de dados."
fi

echo ""
echo ">>> Iniciando servidor FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
