from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base

class Previsao(Base):
    __tablename__ = "previsoes" 

    id = Column(Integer, primary_key=True, index=True)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=False, index=True)
    
    ano_previsao = Column(Integer, nullable=False, index=True)
    
    # Dados estatísticos
    previsao_homicidios = Column(Integer, nullable=False)
    previsao_min = Column(Integer, nullable=False)
    previsao_max = Column(Integer, nullable=False)
    n_anos_dados = Column(Integer, nullable=False)
    
    # Métricas de qualidade do modelo
    margem_erro_k = Column(Float, nullable=True) 
    correlacao_temporal_r = Column(Float, nullable=True)
    erro_padrao_se = Column(Float, nullable=True)
    fator_penalidade_fr = Column(Float, nullable=True)

    municipio = relationship("Municipio", back_populates="previsoes")

    __table_args__ = (
        UniqueConstraint('municipio_id', 'ano_previsao', name='_municipio_id_ano_previsao_uc'),
    )