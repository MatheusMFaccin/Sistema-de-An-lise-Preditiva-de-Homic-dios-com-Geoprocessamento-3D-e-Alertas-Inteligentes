from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from db.session import Base

class Datasus(Base):
    __tablename__ = "datasus"

    id = Column(Integer, primary_key=True, index=True)
    municipio = Column(String, nullable=False)
    mes = Column(String, nullable=False)
    mortes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint( 'municipio', 'ano', 'mes', name='_municipio_ano_mes_dt'),
    )
    
