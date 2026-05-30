param(
    [string]$ComposeFile = "docker-compose.yml"
)

Write-Host "Construction et lancement du backend EduPay..."
docker-compose -f $ComposeFile up --build -d

Write-Host "Vérification du statut des services..."
docker-compose -f $ComposeFile ps

Write-Host "Le backend est prêt sur http://localhost:8000"
