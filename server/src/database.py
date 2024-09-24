import uuid

from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine


class EvaluatorStreamModel(SQLModel, table=True):
    __tablename__ = "evaluator_streams"
    stream_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stream_object: bytes


# SQL Connection
_engine: Engine = None


def get_sql_connection() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine("postgresql://localhost:5432/hero")
        SQLModel.metadata.create_all(_engine)
    return _engine
