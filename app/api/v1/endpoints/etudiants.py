from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/etudiants", tags=["Élèves"])

@router.get("/", response_model=List[schemas.EtudiantResponse])
def get_etudiants(
    skip: int = 0,
    limit: int = 100,
    classe_id: Optional[int] = None,
    ecole_id: Optional[int] = None,
    actif: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    query = db.query(models.Etudiant)
    if classe_id:
        query = query.filter(models.Etudiant.classe_id == classe_id)
    if ecole_id:
        query = query.filter(models.Etudiant.ecole_id == ecole_id)
    if actif is not None:
        query = query.filter(models.Etudiant.actif == actif)
    
    if current_user.role == models.RoleEnum.PARENT:
        parent = db.query(models.Parent).filter(models.Parent.email == current_user.email).first()
        if parent:
            query = query.filter(models.Etudiant.parents.any(id=parent.id))
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.EtudiantResponse)
def create_etudiant(
    etudiant: schemas.EtudiantCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_admin)
):
    existing = db.query(models.Etudiant).filter(models.Etudiant.matricule == etudiant.matricule).first()
    if existing:
        raise HTTPException(status_code=400, detail="Matricule déjà utilisé")
    
    new_etudiant = models.Etudiant(**etudiant.dict())
    db.add(new_etudiant)
    db.commit()
    db.refresh(new_etudiant)
    return new_etudiant

@router.get("/{etudiant_id}", response_model=schemas.EtudiantResponse)
def get_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    return etudiant

@router.put("/{etudiant_id}", response_model=schemas.EtudiantResponse)
def update_etudiant(
    etudiant_id: int,
    etudiant_update: schemas.EtudiantCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_admin)
):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    
    for key, value in etudiant_update.dict().items():
        setattr(etudiant, key, value)
    db.commit()
    db.refresh(etudiant)
    return etudiant

@router.delete("/{etudiant_id}")
def delete_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_admin)
):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    
    db.delete(etudiant)
    db.commit()
    return {"message": "Élève supprimé"}

@router.get("/search/{query}")
def search_etudiants(
    query: str,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    results = db.query(models.Etudiant).filter(
        models.Etudiant.nom.ilike(f"%{query}%") | 
        models.Etudiant.prenom.ilike(f"%{query}%") | 
        models.Etudiant.matricule.ilike(f"%{query}%")
    ).limit(20).all()
    return results
