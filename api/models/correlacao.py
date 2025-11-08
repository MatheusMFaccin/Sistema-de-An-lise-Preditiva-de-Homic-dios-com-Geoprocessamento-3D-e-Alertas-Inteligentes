from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base
from db.session import Base

Base = declarative_base() 

class Previsao(Base):
    """
    Model da tabela do banco de dados para armazenar os resultados das previsões.
    """
    
    # 1. Nome da Tabela
    __tablename__ = "previsoes" # Nome da tabela no banco de dados

    # 2. Coluna de Chave Primária
    # Uma ID simples, auto-incrementada, é a melhor prática.
    id = Column(Integer, primary_key=True, index=True)

    # 3. Colunas de Identificação
    # Marcamos municipio e ano_previsao como 'index=True' 
    # pois você provavelmente fará muitas consultas por eles.
    municipio = Column(String, nullable=False, index=True)
    ano_previsao = Column(Integer, nullable=False, index=True)

    # 4. Colunas de Previsão (Resultados Inteiros)
    previsao_mortes = Column(Integer, nullable=False)
    previsao_min = Column(Integer, nullable=False)
    previsao_max = Column(Integer, nullable=False)
    n_anos_dados = Column(Integer, nullable=False)

    # 5. Colunas de Estatística (Resultados Float)
    # Deixamos 'nullable=True' caso algum cálculo estatístico
    # falhe e retorne 'None' (NaN).
    
    # (Nome da coluna "limpo")
    margem_erro_k = Column(Float, nullable=True) 
    correlacao_temporal_r = Column(Float, nullable=True)
    erro_padrao_se = Column(Float, nullable=True)
    fator_penalidade_fr = Column(Float, nullable=True)

    # 6. Restrições (Constraints)
    # Isso garante que você NUNCA terá duas entradas para
    # o mesmo município e ano.
    __table_args__ = (
        UniqueConstraint('municipio', 'ano_previsao', name='_municipio_ano_uc'),
    )

