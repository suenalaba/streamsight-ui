import os
import uuid

from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)


class EvaluatorStreamModel(SQLModel, table=True):
    __tablename__ = "streams"
    stream_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stream_object: bytes


# SQL Connection
_engine: Engine = None
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")
dbname = os.getenv("dbname")
connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def get_sql_connection() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(connection_string)
        SQLModel.metadata.create_all(_engine)
    return _engine
