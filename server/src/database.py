import uuid

from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine

from src.supabase_client.client import get_supabase_client


class EvaluatorStreamModel(SQLModel, table=True):
    __tablename__ = "streams"
    stream_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stream_object: bytes
    dataset_id: str


class UserToStreamModel(SQLModel, table=True):
    __tablename__ = "user_to_streams"
    user_id: str = Field(primary_key=True)
    stream_id: uuid.UUID = Field(primary_key=True)


# SQL Connection
_engine: Engine = None
# connection_string = f"postgresql://postgres:{password}@db.gbqsbltnpqzpvunwvrpy.supabase.co:5432/${dbname}"
# connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
connection_string = "postgresql://postgres:postgres@localhost:5433/postgres"

def get_sql_connection() -> Engine:
    global _engine
    if _engine is None:
        print("Engine is none")
        _engine = create_engine(connection_string)
        print("Engine created with connection string: ", connection_string)
        SQLModel.metadata.create_all(_engine)
        print("Tables created")
    return _engine


def read_db():
    supabase_client = get_supabase_client()
    response = supabase_client.table("hero").select("*").execute()
    return response
