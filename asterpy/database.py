from sqlalchemy import create_engine, MetaData, Column, Table, Integer, String, DateTime, update, SmallInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Banco de dados
engine = create_engine('sqlite:///aster_dados.db', echo =False)
Base = declarative_base()

# Define a tabela do banco de dados
class Aster(Base):
    __tablename__ = 'aster_data'
    id = Column(Integer, primary_key= True)
    arquivo = Column(String(80), index= True, unique=True)
    data_arquivo = Column(String(11))
    horario = Column(String(15))
    periodo = Column(String(15))
    Phyll = Column(String(30))
    Npv = Column(String(30))
    Qtz = Column(String(30))
    final_check = Column(SmallInteger, default= 0)
    criado_em = Column(DateTime, default=datetime.now)

# Cria a tabela
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def check_register(file):
    x = session.query(Aster).filter_by(arquivo=file).count()
    if x == 0:
        return False
    else:
        return True

def check_final_checker(file):
    check = session.query(Aster).filter_by(arquivo = file).first()
    if check.final_check == 0:
        return False
    else:
        return True

def new_register(file):
    infos = file.split('_')[2]
    date = f"{infos[5:7]}/{infos[3:5]}/{infos[7:11]}"
    hour_table = f"{infos[11:13]}:{infos[13:15]}:{infos[15:17]}"
    hour = int(infos[11:13])
    minutes = int(infos[13:15])
    if hour >= 6 and hour < 18:
        period = 'dia'
    else:
        period = 'noite'

    register = Aster(arquivo=file, data_arquivo=date, horario=hour_table, final_check=0, periodo=period)
    session.add(register)
    session.commit()

# Insere o valor do índice filo no banco de dados
def insert_phyll(file, value):
    row = session.query(Aster).filter_by(arquivo=file).first()
    row.Phyll = value
    session.commit()

# Insere o valor do índice filossilicato no banco de dados
def insert_npv(file, value):
    row = session.query(Aster).filter_by(arquivo=file).first()
    row.Npv = value
    session.commit()

# Insere o valor do índice quatzo no banco de dados
def insert_qtz(file, value):
    row = session.query(Aster).filter_by(arquivo=file).first()
    row.Qtz = value
    session.commit()

def check_phyll(file):
    row = session.query(Aster).filter_by(arquivo=file).first()
    if row.Phyll == None:
        return False
    else:
        return True

def check_npv(file):
    row = session.query(Aster).filter_by(arquivo=file).first()
    if row.Npv == None:
        return False
    else:
        return True

def check_qtz(file):
    row = session.query(Aster).filter_by(arquivo=file).first()
    if row.Qtz == None:
        return False
    else:
        return True

def image_complete(file):
    # Atualiza a tabela -> cena finalizada
    row = session.query(Aster).filter_by(arquivo=file).first()
    row.final_check = 1
    row.criado_em = datetime.now()
    session.commit()