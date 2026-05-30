@echo off
echo ========================================
echo 🚀 EDUPAY - DEMARRAGE ET TEST WONYAPAY
echo ========================================
echo.

echo 1. Activation environnement virtuel...
call .venv311\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Impossible d'activer l'environnement
    echo    Crée l'environnement : python -m venv .venv311
    pause
    exit /b 1
)

echo ✅ Environnement activé
echo.

echo 2. Installation des dépendances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Erreur lors de l'installation
    echo    Vérifie requirements.txt
)
echo.

echo 3. Démarrage de l'API EduPay...
start cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✅ API démarrée sur http://localhost:8000
echo.

echo 4. Attente du démarrage (5 secondes)...
timeout /t 5 /nobreak > nul
echo.

echo 5. Test de santé de l'API...
curl -s http://localhost:8000/health
if errorlevel 1 (
    echo ❌ API non accessible
    echo    Vérifie que l'API est bien démarrée
) else (
    echo ✅ API en bonne santé
)
echo.

echo 6. Test WonyaPay (paiements réels)...
echo    Exécute le test Python :
echo    python test_wonya_immediate.py
echo.

echo 7. URLs importantes :
echo    • API : http://localhost:8000
echo    • Documentation : http://localhost:8000/docs
echo    • Santé : http://localhost:8000/health
echo    • Test Wonya : http://localhost:8000/api/paiements/wonya/test
echo.

echo 8. Pour tester IMMÉDIATEMENT :
echo    Ouvrir un NOUVEAU terminal et exécuter :
echo    python test_wonya_immediate.py
echo.

echo ========================================
echo 🎉 PRÊT POUR LES PAIEMENTS RÉELS !
echo ========================================
echo.
echo Appuie sur une touche pour ouvrir la documentation...
pause > nul
start http://localhost:8000/docs

echo.
echo Pour arrêter l'API : Ctrl+C dans la fenêtre uvicorn
pause