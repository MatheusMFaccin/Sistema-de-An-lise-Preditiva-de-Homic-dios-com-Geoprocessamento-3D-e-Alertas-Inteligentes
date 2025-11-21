# models/municipio.py
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base

class Municipio(Base):
    __tablename__ = "municipios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True) # Indexado para buscas rápidas por nome
    uf = Column(String(2), nullable=False) # String(2) otimiza espaço para UFs

    # Relacionamentos (Back Populates)
    eventos = relationship("Evento", back_populates="municipio")
    datasus = relationship("Datasus", back_populates="municipio")
    previsoes = relationship("Previsao", back_populates="municipio")
    dados_reais = relationship("EventosTotaisAnuais", back_populates="municipio")
    
    __table_args__ = (
        UniqueConstraint('nome', 'uf', name='_municipio_nome_uf_uc'),
    )