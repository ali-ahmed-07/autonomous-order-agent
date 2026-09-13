"""
FastAPI application entry point
"""
from fastapi import FastAPI
from app.routes.orders import router as orders_router
from app.database import engine, Base

# Note: tables already exist in phpMyAdmin, so we don't call create_all()
# Base.metadata.create_all(bind=engine)  # only if starting fresh

app = FastAPI(
    title="Autonomous Order Triage & Resolution Agent",
    version="1.0.0",
    description="AI agent that prevents order cancellations by negotiating alternatives for out-of-stock items.",
)

app.include_router(orders_router)


@app.get("/")
def root():
    return {
        "app": "Autonomous Order Triage Agent",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}