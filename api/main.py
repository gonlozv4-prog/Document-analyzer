from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import create_tables
from api.routes.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title='Analizador de Sentimiento — Banorte',
    version='1.0.0',
    description='API REST para análisis de sentimiento de opiniones de clientes a partir de PDFs.',
    lifespan=lifespan,
)

app.include_router(documents_router)


@app.get('/health')
def health() -> dict:
    return {'status': 'ok'}
