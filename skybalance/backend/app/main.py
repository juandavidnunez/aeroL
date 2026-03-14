"""
SkyBalance AVL - FastAPI Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import tree, flights, versioning, metrics, queue, stress

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AVL Tree-based airline management system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tree.router,       prefix="/api/tree",      tags=["Tree"])
app.include_router(flights.router,    prefix="/api/flights",   tags=["Flights"])
app.include_router(versioning.router, prefix="/api/versions",  tags=["Versioning"])
app.include_router(metrics.router,    prefix="/api/metrics",   tags=["Metrics"])
app.include_router(queue.router,      prefix="/api/queue",     tags=["Queue"])
app.include_router(stress.router,     prefix="/api/stress",    tags=["Stress"])

@app.get("/")
def root():
    return {"message": "SkyBalance AVL API running"}