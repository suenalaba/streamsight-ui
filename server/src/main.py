from fastapi import FastAPI

from src.events import lifespan
from src.routers import (
    algorithm_management,
    authentication,
    data_handling,
    metrics,
    predictions,
    stream_management,
)

app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Healthcheck"])
def healthcheck():
    return {"Server is running, STATUS": "HEALTHY"}


app.include_router(stream_management.router)
app.include_router(algorithm_management.router)
app.include_router(data_handling.router)
app.include_router(predictions.router)
app.include_router(metrics.router)
app.include_router(authentication.router)
