from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base
from db.session import Base

class Previsao(Base):
   
    __tablename__ = "previsoes" 

    
    id = Column(Integer, primary_key=True, index=True)

    
    municipio = Column(String, nullable=False, index=True)
    ano_previsao = Column(Integer, nullable=False, index=True)
    previsao_homicidios = Column(Integer, nullable=False)
    previsao_min = Column(Integer, nullable=False)
    previsao_max = Column(Integer, nullable=False)
    n_anos_dados = Column(Integer, nullable=False)
    margem_erro_k = Column(Float, nullable=True) 
    correlacao_temporal_r = Column(Float, nullable=True)
    erro_padrao_se = Column(Float, nullable=True)
    fator_penalidade_fr = Column(Float, nullable=True)
    __table_args__ = (
        UniqueConstraint('municipio', 'ano_previsao', name='_municipio_ano_uc'),
    )

