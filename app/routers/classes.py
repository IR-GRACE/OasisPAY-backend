from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Classe
from .auth import get_current_user, require_admin
from typing import Optional

router = APIRouter(prefix="/classes", tags=["classes"])

class ClasseCreate(BaseModel):
    nom: str
    frais_scolarite: Optional[float] = 0

class ClasseUpdate(BaseModel):
    nom: Optional[str] = None
    frais_scolarite: Optional[float] = None

@router.get("/")
def get_classes(db: Session = Depends(get_db)):
    return db.query(Classe).all()

@router.post("/", dependencies=[Depends(require_admin)])
def create_classe(classe: ClasseCreate, db: Session = Depends(get_db)):
    db_classe = Classe(nom=classe.nom, frais_scolarite=classe.frais_scolarite)
    db.add(db_classe)
    db.commit()
    db.refresh(db_classe)
    return db_classe

@router.put("/{classe_id}", dependencies=[Depends(require_admin)])
def update_classe(classe_id: int, classe: ClasseUpdate, db: Session = Depends(get_db)):
    db_classe = db.query(Classe).filter(Classe.id == classe_id).first()
    if not db_classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    if classe.nom is not None:
        db_classe.nom = classe.nom
    if classe.frais_scolarite is not None:
        db_classe.frais_scolarite = classe.frais_scolarite
    db.commit()
    db.refresh(db_classe)
    return db_classe

@router.delete("/{classe_id}", dependencies=[Depends(require_admin)])
def delete_classe(classe_id: int, db: Session = Depends(get_db)):
    db_classe = db.query(Classe).filter(Classe.id == classe_id).first()
    if not db_classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    db.delete(db_classe)
    db.commit()
    return {"message": "Classe supprimée"}

