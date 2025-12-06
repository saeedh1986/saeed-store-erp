from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.core.config import settings
from app.database import engine
# Import ALL models to ensure they are registered with SQLModel.metadata
from app.models import models
from app.routers import inventory as inventory_router
from app.routers import customers as customers_router
from app.routers import orders as orders_router

# Create Tables
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(inventory_router.router, prefix=settings.API_V1_STR)
app.include_router(customers_router.router, prefix=settings.API_V1_STR)
app.include_router(orders_router.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Saeed Store ERP V2 API"}
