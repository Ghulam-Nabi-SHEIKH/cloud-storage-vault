from fastapi import FastAPI

from app import models
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud File Optimizer & Smart Vault")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
