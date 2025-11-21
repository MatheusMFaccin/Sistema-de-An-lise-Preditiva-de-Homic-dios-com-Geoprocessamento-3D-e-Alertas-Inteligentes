from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Substituímos as strings por uma FK
    municipio_id = Column(Integer, ForeignKey("municipios.id"), nullable=False, index=True)
    
    # Otimização: Se "mes" for numérico (1-12), use Integer (mais rápido). 
    # Se for nome ("Janeiro"), considere mudar para Int ou manter String. Vou assumir Int ou String curta.
    mes = Column(Integer, nullable=False) 
    ano = Column(Integer, nullable=False, index=True)
    vitimas = Column(Integer, nullable=False, default=0)

    # Relacionamento SQLAlchemy
    municipio = relationship("Municipio", back_populates="eventos")

    __table_args__ = (
        
        UniqueConstraint('municipio_id', 'ano', 'mes', name='_municipio_id_ano_mes_uc'),
    )