from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

def GetSession():
    Base = automap_base()
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/SweIoTdb', echo=True)
    Base.prepare(engine, reflect=True, schema='public')
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    return session, Base

def GetModel(table_name):
    session, Base = GetSession()
    table_model = getattr(Base.classes, table_name, None)
    if table_model is None:
        raise ValueError(f"Table model not found for table name: {table_name}")
    return table_model

# map models, you need to create session before calling these
def Users(Base):
    Users = Base.classes.users
    return Users

def GetKeys(Base):
    Keys = Base.classes.rsakeys
    return Keys

def Roles(Base):
    Roles = Base.classes.role
    return Roles

def Producers(Base):
   Producers = Base.classes.producers
   return Producers

def Orders(Base):
   Orders = Base.classes.orders
   return Orders

def Firmwares(Base):
   Firmwares = Base.classes.firmwares
   return Firmwares

def Devices(Base):
   Devices = Base.classes.devices
   return Devices

def Customers(Base):
   Customers = Base.classes.customers
   return Customers

def Config(Base):
   Configs = Base.classes.config
   return Configs

def Batch(Base):
   Batches = Base.classes.batch
   return Batches

# Create table object from model metadata
def CreateTableObject(name, metadata):
   return Table(name, metadata, autoload=True)

   
