import string

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Date


engine = create_engine("sqlite:///boletos.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Boleto(Base):
    __tablename__ = "boletos"

    id = Column(Integer, primary_key=True)
    linha_digitavel = Column(String)
    valor = Column(String)
    data_do_documento = Column(String)    
    data_de_vencimento = Column(String)
    beneficiario = Column(String)

Base.metadata.create_all(engine)