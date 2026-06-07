from . import models
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import auth, etudiants, paiements, admin, classes, notifications

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OasisPAY API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(etudiants.router, prefix="/api/v1")
app.include_router(paiements.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(classes.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Bienvenue sur OasisPAY API", "version": "2.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

