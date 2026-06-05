from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/frais", tags=["Frais scolaires"])

@router.get("/", response_model=List[schemas.FraisResponse])
def get_frais(
    ecole_id: Optional[int] = None,
    annee_scolaire: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    query = db.query(models.FraisScolaire)
    if ecole_id:
        query = query.filter(models.FraisScolaire.ecole_id == ecole_id)
    if annee_scolaire:
        query = query.filter(models.FraisScolaire.annee_scolaire == annee_scolaire)
    return query.all()

@router.post("/", response_model=schemas.FraisResponse)
def create_frais(
    frais: schemas.FraisCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_admin)
):
    new_frais = models.FraisScolaire(**frais.dict())
    db.add(new_frais)
    db.commit()
    db.refresh(new_frais)
    return new_frais

@router.put("/{frais_id}", response_model=schemas.FraisResponse)
def update_frais(
    frais_id: int,
    frais_update: schemas.FraisCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_admin)
):
    frais = db.query(models.FraisScolaire).filter(models.FraisScolaire.id == frais_id).first()
    if not frais:
        raise HTTPException(status_code=404, detail="Frais non trouvé")
    
    for key, value in frais_update.dict().items():
        setattr(frais, key, value)
    db.commit()
    db.refresh(frais)
    return frais

@router.delete("/{frais_id}")
def delete_frais(
    frais_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_admin)
):
    frais = db.query(models.FraisScolaire).filter(models.FraisScolaire.id == frais_id).first()
    if not frais:
        raise HTTPException(status_code=404, detail="Frais non trouvé")
    
    db.delete(frais)
    db.commit()
    return {"message": "Frais supprimé"}
