import uuid

from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine

from src.settings import dbname, host, password, port, user


class EvaluatorStreamModel(SQLModel, table=True):
    __tablename__ = "streams"
    stream_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stream_object: bytes


# SQL Connection
_engine: Engine = None
connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def get_sql_connection() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(connection_string)
        SQLModel.metadata.create_all(_engine)
    return _engine
