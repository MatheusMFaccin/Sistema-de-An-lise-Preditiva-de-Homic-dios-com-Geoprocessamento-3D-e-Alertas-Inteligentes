from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from db.session import Base  # Importe sua Base declarativa

class ComparativoPrevisao(Base):
    
    __tablename__ = "comparativo_previsoes"

    id = Column(Integer, primary_key=True, index=True)
    
    id_x = Column (Integer, nullable= False, index=True)
    id_y = Column (Integer, nullable= False, index=True)
    # Chaves da união
    municipio = Column(String, nullable=False, index=True)
    ano = Column(Integer, nullable=False, index=True)
    
    # 1. O dado Real
    total_vitimas_ano = Column(Integer, nullable=False)
    
    # 2. O dado Previsto
    # (Estou usando 'previsao_homicidios' com base na nossa última conversa)
    previsao_homicidios = Column(Float, nullable=False)
    previsao_min = Column(Float, nullable=False)
    previsao_max = Column(Float, nullable=False)
    
    # 3. O Resultado (A Classificação)
    classificacao = Column(String, nullable=False, index=True)
    
    # 4. Metadados (Como a previsão foi calculada)
    margem_erro_k = Column(Float, nullable=True)
    correlacao_temporal_r = Column(Float, nullable=True)
    erro_padrao_se = Column(Float, nullable=True)
    fator_penalidade_fr = Column(Float, nullable=True)
    n_anos_dados = Column(Integer, nullable=False)

    # Garante que só podemos ter uma linha de comparação por município/ano
    __table_args__ = (
        UniqueConstraint('municipio', 'ano', name='_municipio_ano_comparativo_uc'),
    )