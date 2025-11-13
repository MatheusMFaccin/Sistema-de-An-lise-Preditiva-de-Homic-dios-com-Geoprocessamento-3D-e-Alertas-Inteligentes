from sqlalchemy import Column, Integer, String, UniqueConstraint
from db.session import Base  

class DadosReaisAnuais(Base):
    
    __tablename__ = "dados_reais_anuais"

    id = Column(Integer, primary_key=True, index=True)
    
    municipio = Column(String, nullable=False, index=True)
    ano = Column(Integer, nullable=False, index=True)
    total_vitimas_ano = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('municipio', 'ano', name='_municipio_ano_reais_uc'),
    )