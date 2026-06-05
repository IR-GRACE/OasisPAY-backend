from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from fastapi.responses import Response
from app.routers import auth, admin, payments, etudiants, notifications
from app.core.config import settings

app = FastAPI(title="Oasis Pay API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    # Create tables at startup (development only). In production use migrations (alembic).
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(etudiants.router, prefix='/api')
app.include_router(notifications.router, prefix='/api')

@app.get("/")
def root():
    return {"message": "Bienvenue sur Oasis Pay API"}

@app.get("/health")
def health():
    return {"status": "ok"}


