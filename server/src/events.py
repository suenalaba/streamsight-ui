from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.supabase_client.client import init_supabase_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Starting lifespan events")
        init_supabase_client()
        yield
    finally:
        print("Shutting down lifespan events")
