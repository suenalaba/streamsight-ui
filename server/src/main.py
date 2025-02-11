from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://streamsight-ui.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Healthcheck"])
def healthcheck():
    return {"Status": "HEALTHY"}


app.include_router(stream_management.router)
app.include_router(algorithm_management.router)
app.include_router(data_handling.router)
app.include_router(predictions.router)
app.include_router(metrics.router)
app.include_router(authentication.router)
