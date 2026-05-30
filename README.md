# EduPay Backend

Backend FastAPI professionnel pour la gestion de paiements Mobile Money et d'une administration simple.

## Fonctionnalités clés

- API d'initiation de paiements Mobile Money
- Webhook de confirmation des paiements
- Persistance SQLite via SQLAlchemy
- Routes d'administration sécurisées par clé API
- Structures de données validées avec Pydantic
- Base prête à intégrer Orange Money, Airtel Money et M-Pesa

## Structure

- `app/main.py` : démarrage FastAPI et configuration générale
- `app/core/config.py` : configuration centralisée et lecture de `.env`
- `app/db/` : gestion de la base de données SQLAlchemy
- `app/routers/payments.py` : endpoints de paiement et webhook
- `app/routers/admin.py` : administration des paiements et des utilisateurs
- `app/schemas/` : modèles Pydantic pour validation et réponses

## Configuration

Copiez `.env.example` en `.env` et renseignez les valeurs suivantes :

- `API_SECRET_KEY`
- `ADMIN_API_KEY`
- `DATABASE_URL` (par défaut `sqlite:///./edupay.db`)
- `WEBHOOK_BASE_URL`
- `MPESA_*`, `ORANGE_*`, `AIRTEL_*` pour les fournisseurs

Exemple :

```bash
cp .env.example .env
```

## Exécution locale

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Liaison avec le frontend

1. Configure l’origine du frontend qui va appeler le backend :
   - copie `.env.example` en `.env`
   - définis `FRONTEND_ORIGINS=http://localhost:3000` ou l’URL de ton frontend

2. Assure-toi que le frontend appelle ces endpoints :
   - `POST /api/payments/initiate`
   - `GET /api/payments/status/{transaction_ref}`
   - `POST /api/payments/webhook/flutterwave` (via Flutterwave)
   - `POST /api/admin/login`
   - routes admin protégées par `X-API-KEY`

3. Exemple simple de requête frontend pour initier un paiement :

```js
const response = await fetch("http://localhost:8000/api/payments/initiate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    etudiant_id: 123,
    montant: 5000,
    devise: "CDF",
    methode_paiement: "flutterwave",
    numero_telephone: "0999999999",
    type_frais: "inscription",
  }),
});
const data = await response.json();
console.log(data);
```

4. Exemple de login admin depuis le frontend :

```js
const login = await fetch("http://localhost:8000/api/admin/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ phone: "0994477720", code: "2003" }),
});
const adminData = await login.json();
console.log(adminData);
```

5. N’oublie pas de passer `X-API-KEY` sur les routes admin sécurisées :

```js
await fetch("http://localhost:8000/api/admin/paiements/pending", {
  headers: {
    "X-API-KEY": "supersecretadminkey",
  },
});
```

## Endpoints principaux

- `GET /` : santé de l'application
- `POST /api/payments/initiate` : créer un paiement
- `GET /api/payments/status/{transaction_ref}` : vérifier le statut
- `POST /api/payments/webhook/{provider}` : recevoir les confirmations fournisseur

## Paiements réels Flutterwave

- `POST /api/payments/initiate` supporte désormais `methode_paiement: flutterwave`
- `provider` reconnus : `mpesa`, `orange`, `airtel`, `mtn`, `flutterwave`
- `redirect_url` peut être retourné pour la redirection Flutterwave
- DRC mapping :
  - `orange` → `Orange Money`
  - `airtel` → `Airtel Money`
  - `mtn` → `MTN Mobile Money`

## Webhook Flutterwave

- `POST /api/payments/webhook/flutterwave`
- Valide le header `verif-hash`
- Utilise `FLUTTERWAVE_SECRET_KEY` pour vérifier l'intégrité du payload
- Met à jour le paiement via `tx_ref`

## Administration

- `POST /api/admin/login` : connexion admin avec téléphone et code
  - `phone`: `0994477720`, `code`: `2003` pour `JULVIER`
  - `phone`: `0995030972`, `code`: `1234` pour `GRACE`

La base de données contient désormais une table `admin_users` et un historique `audit_logs`.
L'administration est donc gérée côté base de données avec audit des actions critiques.

Admin routes protégées par la clé `X-API-KEY` :

- `GET /api/admin/paiements/pending`
- `GET /api/admin/paiements/{paiement_id}`
- `POST /api/admin/paiements/{paiement_id}/status`
- `GET /api/admin/utilisateurs/pending`
- `POST /api/admin/utilisateurs`
- `POST /api/admin/utilisateurs/{user_id}/approve`
- `PUT /api/admin/utilisateurs/{user_id}`
- `DELETE /api/admin/utilisateurs/{user_id}`
- `GET /api/admin/admins`
- `POST /api/admin/admins`
- `PUT /api/admin/admins/{admin_id}`
- `DELETE /api/admin/admins/{admin_id}`
- `GET /api/admin/audit`

## Déploiement

### Container local

Utilisez Docker pour lancer le backend de manière reproductible :

```powershell
docker-compose up --build -d
```

Un script `deploy.ps1` est également fourni :

```powershell
.\deploy.ps1
```

### Exécution manuelle

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Intégration réelle

1. Récupérer et configurer les identifiants API de chaque fournisseur.
2. Implémenter la logique d'appel aux endpoints de paiement du fournisseur.
3. Protéger les webhooks avec signature HMAC ou validation IP.
4. Mettre à jour le paiement en base après confirmation.
5. Activer la notification et l'audit selon vos besoins.
