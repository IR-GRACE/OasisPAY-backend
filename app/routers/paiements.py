result = await service.initier_paiement(
montant=request.montant,
telephone=request.telephone,
operateur=request.methode_paiement,
reference=f"OASIS_{int(datetime.now().timestamp())}",
description=f"Paiement pour {etudiant.nom} {etudiant.prenom}"
)

paiement = Paiement(
etudiant_id=request.etudiant_id,
montant=request.montant,
type_frais=request.type_frais,
statut="PENDING",
methode_paiement=request.methode_paiement,
numero_telephone=request.telephone,
reference=result.get("reference"),
created_at=datetime.utcnow()
)
