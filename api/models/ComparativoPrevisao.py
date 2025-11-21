# models/ComparativoPrevisao.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base  

class ComparativoPrevisao(Base):
    __tablename__ = "comparativo_previsoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # FKs para as origens (Rastreabilidade)
    previsao_id = Column(Integer, ForeignKey("previsoes.id"), nullable=False)
    dado_real_id = Column(Integer, ForeignKey("dados_reais_anuais.id"), nullable=True) # Pode ser Null se o ano ainda não fechou
    
    # Redundância controlada para performance de leitura (Analytics)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=False, index=True)
    ano = Column(Integer, nullable=False, index=True)
    
    total_vitimas_ano = Column(Integer, nullable=True) # Nullable, pois o ano pode não ter acabado
    previsao_homicidios = Column(Float, nullable=False)
    previsao_min = Column(Float, nullable=False)
    previsao_max = Column(Float, nullable=False)
    
    classificacao = Column(String, nullable=False, index=True) # Ex: "Dentro da margem", "Erro Crítico"

    # Métricas copiadas (snapshot)
    margem_erro_k = Column(Float, nullable=True)
    
    # Relacionamentos para facilitar acesso aos pais se necessário
    previsao_origem = relationship("Previsao")
    dado_real_origem = relationship("EventosTotaisAnuais")
    municipio = relationship("Municipio")

    __table_args__ = (
        UniqueConstraint('municipio_id', 'ano', name='_municipio_id_ano_comparativo_uc'),
    )