from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base  

class EventosTotaisAnuais(Base):
    __tablename__ = "dados_reais_anuais"

    id = Column(Integer, primary_key=True, index=True)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=False, index=True)
    ano = Column(Integer, nullable=False, index=True)
    total_vitimas_ano = Column(Integer, nullable=False)

    municipio = relationship("Municipio", back_populates="dados_reais")

    __table_args__ = (
        UniqueConstraint('municipio_id', 'ano', name='_municipio_id_ano_reais_uc'),
    )