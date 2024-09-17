from fastapi import FastAPI
from src.routers import algorithm_management, data_handling, metrics, predictions,  stream_management
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

@app.get("/", tags=["Healthcheck"])
def healthcheck():
    return {"Server is running, STATUS": "HEALTHY"}

app.include_router(stream_management.router)
app.include_router(algorithm_management.router)
app.include_router(data_handling.router)
app.include_router(predictions.router)
app.include_router(metrics.router)

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


engine = create_engine("postgresql://localhost:5432/hero")

@app.get("/db-connection", tags=["Healthcheck"])
def get_db_connection():
    with Session(engine) as session:
        statement = select(Hero)
        hero = session.exec(statement).first()
        print(hero)
    return {"Successfully fetched from DB"}

@app.post("/write-to-db", tags=["Healthcheck"])
def write_to_db(hero: Hero):
    try:
        with Session(engine) as session:
            new_hero = Hero(id=hero.id, name=hero.name, secret_name=hero.secret_name, age=hero.age)
            session.add(new_hero)
            session.commit()
    except Exception as e:
        return {"Error": str(e)}    
    return {"Successfully written to DB"}
