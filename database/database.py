import os
from dotenv import load_dotenv
from sqlalchemy.testing.plugin.plugin_base import config
from sqlmodel import create_engine
from sqlmodel import SQLModel, Session
# from dotenv import load_dotenv
# SQLModel_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}/{NAME_NB}"
load_dotenv()
NAME_DB = os.getenv('NAME_DB')
SQLModel_URL = f"sqlite:///./{NAME_DB}"

connect_args = {"check_same_thread": False}
engine = create_engine(SQLModel_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session