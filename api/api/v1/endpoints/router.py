from collections import defaultdict
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from models import Municipio, ComparativoPrevisao
from core.config import settings

api_router = APIRouter()


@api_router.get("/config")
def get_config():
    """Retorna configuracoes do frontend (token Cesium, etc)."""
    return {
        "cesium_token": settings.CESIUM_TOKEN,
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG,
    }


def normalizar_para_slug(texto: str) -> str:
    """Transforma 'São Gabriel' em 'sao-gabriel'."""
    if not texto:
        return ""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sem_acentos = texto_normalizado.encode('ascii', 'ignore').decode("utf-8")
    return texto_sem_acentos.lower().replace(' ', '-')


@api_router.get("/mapa/dados-classificacao")
def dados_classificacao(db: Session = Depends(get_db)):
    """Retorna dados de classificacao agrupados por ano para o mapa."""
    resultados = (
        db.query(
            Municipio.nome,
            ComparativoPrevisao.classificacao,
            ComparativoPrevisao.ano,
        )
        .join(Municipio, ComparativoPrevisao.municipio_id == Municipio.id)
        .all()
    )

    dados_por_ano = defaultdict(list)
    for nome, classificacao, ano in resultados:
        if nome and ano:
            dados_por_ano[str(ano)].append({
                "municipio": nome,
                "classificacao": classificacao,
            })

    return dict(dados_por_ano)


@api_router.get("/municipios/{slug}")
def detalhes_municipio(slug: str, db: Session = Depends(get_db)):
    """Retorna dados detalhados de um municipio para o grafico."""
    # Busca o municipio pelo slug
    todos = db.query(Municipio).all()
    municipio_encontrado = None
    for mun in todos:
        if normalizar_para_slug(mun.nome) == slug:
            municipio_encontrado = mun
            break

    if not municipio_encontrado:
        raise HTTPException(status_code=404, detail="Municipio nao encontrado")

    # Busca os dados comparativos ordenados por ano
    comparativos = (
        db.query(ComparativoPrevisao)
        .filter(ComparativoPrevisao.municipio_id == municipio_encontrado.id)
        .order_by(ComparativoPrevisao.ano)
        .all()
    )

    labels_anos = []
    data_reais = []
    data_previsoes = []
    tabela = []

    for item in comparativos:
        labels_anos.append(item.ano)
        data_reais.append(item.total_vitimas_ano)
        data_previsoes.append(item.previsao_homicidios)
        tabela.append({
            "ano": item.ano,
            "total_vitimas_ano": item.total_vitimas_ano,
            "previsao_homicidios": item.previsao_homicidios,
            "classificacao": item.classificacao,
            "margem_erro_k": item.margem_erro_k,
        })

    return {
        "municipio": {
            "id": municipio_encontrado.id,
            "nome": municipio_encontrado.nome,
            "uf": municipio_encontrado.uf,
        },
        "grafico": {
            "labels_anos": labels_anos,
            "data_reais": data_reais,
            "data_previsoes": data_previsoes,
        },
        "tabela": tabela,
    }
