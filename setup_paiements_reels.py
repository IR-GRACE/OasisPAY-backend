#!/usr/bin/env python3
"""
Script pour configurer les paiements réels dans EduPay
Exécute ce script après avoir obtenu tes clés API
"""

import os
import sys
from pathlib import Path

def setup_flutterwave():
    """Configuration Flutterwave"""
    print("\n" + "="*50)
    print("CONFIGURATION FLUTTERWAVE (RDC)")
    print("="*50)
    
    print("\n1. Inscription rapide :")
    print("   • Site : https://dashboard.flutterwave.com/register")
    print("   • Email : ton-email@entreprise.cd")
    print("   • Pays : Democratic Republic of Congo")
    
    print("\n2. Après inscription :")
    print("   • Va dans Settings → API")
    print("   • Copie ta 'Secret Key' (commence par FLWSECK-)")
    
    secret_key = input("\n🎯 Entre ta FLUTTERWAVE_SECRET_KEY : ").strip()
    
    if secret_key and secret_key.startswith("FLWSECK"):
        update_env("FLUTTERWAVE_SECRET_KEY", secret_key)
        print("✅ Flutterwave configuré !")
        return True
    else:
        print("❌ Clé invalide. Format attendu : FLWSECK-xxxxxxxx")
        return False

def setup_wonya():
    """Configuration WonyaPay"""
    print("\n" + "="*50)
    print("CONFIGURATION WONYAPAY (RDC - Mobile Money)")
    print("="*50)
    
    print("\nContacte WonyaSoft :")
    print("   • Email : contact@wonyasoft.com")
    print("   • WhatsApp : +243 81 700 0000")
    print("   • Site : https://wonyasoft.com")
    
    print("\nIls te fourniront :")
    print("   1. WONYA_API_KEY")
    print("   2. WONYA_PROJECT_REF")
    print("   3. URL de ton projet")
    
    api_key = input("\n🎯 Entre ta WONYA_API_KEY : ").strip()
    project_ref = input("🎯 Entre ton WONYA_PROJECT_REF : ").strip()
    
    if api_key and project_ref:
        update_env("WONYA_API_KEY", api_key)
        update_env("WONYA_PROJECT_REF", project_ref)
        update_env("WONYA_BASE_URL", f"https://app.wonyasoft.com/projet-details/{project_ref}")
        print("✅ WonyaPay configuré !")
        return True
    else:
        print("⚠️  Configuration partielle")
        return False

def setup_webhook():
    """Configuration webhook"""
    print("\n" + "="*50)
    print("CONFIGURATION WEBHOOK")
    print("="*50)
    
    print("\nPour les tests LOCAUX :")
    print("   1. Installe ngrok : https://ngrok.com/download")
    print("   2. Lance : ngrok http 8000")
    print("   3. Copie l'URL HTTPS (ex: https://abc123.ngrok.io)")
    
    print("\nPour la PRODUCTION :")
    print("   • Utilise ton domaine (ex: https://edupay.cd)")
    
    webhook_url = input("\n🎯 Entre ton URL de webhook : ").strip()
    
    if webhook_url:
        update_env("WEBHOOK_BASE_URL", f"{webhook_url}/api/payments/webhook")
        print("✅ Webhook configuré !")
        return True
    else:
        print("⚠️  Webhook non configuré")
        return False

def update_env(key, value):
    """Mettre à jour le fichier .env"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print(f"❌ Fichier .env introuvable")
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"\n{key}={value}\n")
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def test_paiement():
    """Tester un paiement"""
    print("\n" + "="*50)
    print("TEST DE PAIEMENT")
    print("="*50)
    
    print("\nPour tester IMMÉDIATEMENT :")
    print("\n1. Avec WonyaPay (déjà partiellement configuré) :")
    print("   curl -X POST http://localhost:8000/api/paiements/wonya/test \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"montant\": 100, \"devise\": \"CDF\", \"execute\": true}'")
    
    print("\n2. Avec Flutterwave (après configuration) :")
    print("   curl -X POST http://localhost:8000/api/paiements/ \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -H \"Authorization: Bearer ton_token\" \\")
    print("     -d '{")
    print("       \"etudiant_id\": 1,")
    print("       \"montant\": 5000,")
    print("       \"devise\": \"CDF\",")
    print("       \"methode_paiement\": \"flutterwave\",")
    print("       \"numero_telephone\": \"0999999999\"")
    print("     }'")

def main():
    print("🚀 CONFIGURATION PAIEMENTS RÉELS EDUPAY")
    print("="*50)
    
    print("\nChoisis les fournisseurs à configurer :")
    print("1. Flutterwave (recommandé - paiements en ligne)")
    print("2. WonyaPay (Mobile Money RDC)")
    print("3. Les deux")
    print("4. Tester seulement")
    
    choix = input("\n🎯 Ton choix (1-4) : ").strip()
    
    if choix in ["1", "3"]:
        setup_flutterwave()
    
    if choix in ["2", "3"]:
        setup_wonya()
    
    if choix != "4":
        setup_webhook()
    
    test_paiement()
    
    print("\n" + "="*50)
    print("🎉 CONFIGURATION TERMINÉE !")
    print("="*50)
    print("\nProchaines étapes :")
    print("1. Redémarre ton API : uvicorn app.main:app --reload")
    print("2. Teste avec les commandes ci-dessus")
    print("3. Pour impressionner tes juristes :")
    print("   • Fais un vrai paiement de 100 CDF")
    print("   • Montre la transaction en temps réel")
    print("   • Affiche le reçu numérique")
    
    print("\n📞 Support rapide :")
    print("• Flutterwave RDC : +243 999 999 999")
    print("• WonyaPay : +243 81 700 0000")

if __name__ == "__main__":
    main()