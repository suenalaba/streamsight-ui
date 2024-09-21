from fastapi import FastAPI
from sqlmodel import Session, select

from src.database import Hero, get_sql_connection
from src.routers import (
    algorithm_management,
    data_handling,
    metrics,
    predictions,
    stream_management,
)

app = FastAPI()

@app.get("/", tags=["Healthcheck"])
def healthcheck():
    return {"Server is running, STATUS": "HEALTHY"}

app.include_router(stream_management.router)
app.include_router(algorithm_management.router)
app.include_router(data_handling.router)
app.include_router(predictions.router)
app.include_router(metrics.router)

@app.get("/db-connection", tags=["Healthcheck"])
def get_db_connection():
    with Session(get_sql_connection()) as session:
        statement = select(Hero)
        hero = session.exec(statement).first()
        print(hero)
    return {"Successfully fetched from DB"}

@app.post("/write-to-db", tags=["Healthcheck"])
def write_to_db(hero: Hero):
    try:
        with Session(get_sql_connection()) as session:
            new_hero = Hero(id=hero.id, name=hero.name, secret_name=hero.secret_name, age=hero.age)
            session.add(new_hero)
            session.commit()
    except Exception as e:
        return {"Error": str(e)}    
    return {"Successfully written to DB"}
