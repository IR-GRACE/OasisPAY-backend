from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/", response_model=List[schemas.ClasseResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return db.query(models.Classe).all()

@router.post("/", response_model=schemas.ClasseResponse)
def create_classe(
    classe: schemas.ClasseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    new_classe = models.Classe(**classe.dict())
    db.add(new_classe)
    db.commit()
    db.refresh(new_classe)
    return new_classe

@router.get("/{classe_id}", response_model=schemas.ClasseResponse)
def get_classe(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    classe = db.query(models.Classe).filter(models.Classe.id == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    return classe

@router.put("/{classe_id}", response_model=schemas.ClasseResponse)
def update_classe(
    classe_id: int,
    classe_update: schemas.ClasseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    classe = db.query(models.Classe).filter(models.Classe.id == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    
    for key, value in classe_update.dict().items():
        setattr(classe, key, value)
    db.commit()
    db.refresh(classe)
    return classe

@router.delete("/{classe_id}")
def delete_classe(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    classe = db.query(models.Classe).filter(models.Classe.id == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    
    db.delete(classe)
    db.commit()
    return {"message": "Classe supprimée"}

@router.get("/{classe_id}/eleves", response_model=List[schemas.EtudiantResponse])
def get_eleves_by_classe(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    classe = db.query(models.Classe).filter(models.Classe.id == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    return classe.etudiants
