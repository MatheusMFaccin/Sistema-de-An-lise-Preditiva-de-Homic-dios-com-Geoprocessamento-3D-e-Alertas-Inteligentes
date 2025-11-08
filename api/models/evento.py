from sqlalchemy import Column, Integer, String, Float, Date, PrimaryKeyConstraint,UniqueConstraint
from db.session import Base

class Evento(Base):
    __tablename__ = "eventos"

    uf = Column(String, nullable=False)
    municipio = Column(String, nullable=False)
    mes = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    vitimas = Column(Integer, nullable = False, default=0)
    id = Column(Integer, primary_key=True, index=True)    
    
    __table_args__ = (
        UniqueConstraint('uf', 'municipio', 'ano', 'mes', name='_uf_municipio_ano_mes_uc'),
    )