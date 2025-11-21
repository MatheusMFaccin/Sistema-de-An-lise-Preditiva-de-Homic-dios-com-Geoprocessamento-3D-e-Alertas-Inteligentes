from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base

class Datasus(Base):
    __tablename__ = "datasus"

    id = Column(Integer, primary_key=True, index=True)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=False, index=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False) # Sugiro padronizar como int (1 a 12)
    mortes = Column(Integer, nullable=False)

    municipio = relationship("Municipio", back_populates="datasus")

    __table_args__ = (
        UniqueConstraint('municipio_id', 'ano', 'mes', name='_datasus_municipio_ano_mes_uc'),
    )