from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routers import auth, users, paiements, etudiants, admin, classes, notifications
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OasisPAY API", version="2.0.0")

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(paiements.router, prefix="/api/v1")
app.include_router(etudiants.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(classes.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Bienvenue sur OasisPAY API", "version": "2.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}