from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models import Classe
from .auth import require_admin

router = APIRouter(
    prefix="/classes",
    tags=["classes"]
)

class ClasseCreate(BaseModel):
    nom: str
    niveau: Optional[str] = ""
    frais_inscription: Optional[float] = 0
    frais_mensue: Optional[float] = 0

class ClasseUpdate(BaseModel):
    nom: Optional[str] = None
    niveau: Optional[str] = None
    frais_inscription: Optional[float] = None
    frais_mensue: Optional[float] = None

@router.get("/")
def get_classes(db: Session = Depends(get_db)):
    return db.query(Classe).all()

@router.post("/", dependencies=[Depends(require_admin)])
def create_classe(
    classe: ClasseCreate,
    db: Session = Depends(get_db)
):
    new_classe = Classe(
        nom=classe.nom,
        niveau=classe.niveau,
        frais_inscription=classe.frais_inscription,
        frais_mensue=classe.frais_mensue
    )

    db.add(new_classe)
    db.commit()
    db.refresh(new_classe)

    return new_classe

@router.put("/{classe_id}", dependencies=[Depends(require_admin)])
def update_classe(
    classe_id: int,
    classe: ClasseUpdate,
    db: Session = Depends(get_db)
):
    db_classe = (
        db.query(Classe)
        .filter(Classe.id == classe_id)
        .first()
    )

    if not db_classe:
        raise HTTPException(
            status_code=404,
            detail="Classe non trouvée"
        )

    if classe.nom is not None:
        db_classe.nom = classe.nom

    if classe.niveau is not None:
        db_classe.niveau = classe.niveau

    if classe.frais_inscription is not None:
        db_classe.frais_inscription = classe.frais_inscription

    if classe.frais_mensue is not None:
        db_classe.frais_mensue = classe.frais_mensue

    db.commit()
    db.refresh(db_classe)

    return db_classe

@router.delete("/{classe_id}", dependencies=[Depends(require_admin)])
def delete_classe(
    classe_id: int,
    db: Session = Depends(get_db)
):
    db_classe = (
        db.query(Classe)
        .filter(Classe.id == classe_id)
        .first()
    )

    if not db_classe:
        raise HTTPException(
            status_code=404,
            detail="Classe non trouvée"
        )

    db.delete(db_classe)
    db.commit()

    return {"message": "Classe supprimée"}

