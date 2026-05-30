# 🔐 CREDENTIALS ADMINISTRATION EDUPAY

## 👑 **SUPER ADMINISTRATEURS**

### 1. **GRACE (Super Admin)**
```
• Nom : GRACE
• Téléphone : +243 995 030 972
• Email : Masiyamulimbi4@gmail.com
• Code : 2003
• Rôle : super_admin
• Statut : ACTIF
```

### 2. **JULVIER (Admin)**
```
• Nom : JULVIER
• Téléphone : 0994477720
• Code : 2003
• Rôle : admin
• Statut : ACTIF
```

## 🔑 **CLÉS D'ACCÈS**

### Clé API Admin :
```
supersecretadminkey
```
**Utilisation :**
```bash
curl -H "X-API-KEY: supersecretadminkey" \
  http://localhost:8000/api/admin/paiements/pending
```

### Clé Secrète API :
```
changeme
```
**Note :** À changer en production

## 🌐 **URLS D'ADMINISTRATION**

### 1. **Login Admin**
```
POST http://localhost:8000/api/admin/login
```
**Body :**
```json
{
  "phone": "+243995030972",
  "code": "2003"
}
```

### 2. **Dashboard Paiements**
```
GET http://localhost:8000/api/admin/paiements/pending
```
**Header :** `X-API-KEY: supersecretadminkey`

### 3. **Gestion Utilisateurs**
```
GET  /api/admin/utilisateurs/pending
POST /api/admin/utilisateurs
POST /api/admin/utilisateurs/{id}/approve
PUT  /api/admin/utilisateurs/{id}
DELETE /api/admin/utilisateurs/{id}
```

### 4. **Gestion Admins**
```
GET    /api/admin/admins
POST   /api/admin/admins
PUT    /api/admin/admins/{id}
DELETE /api/admin/admins/{id}
```

### 5. **Audit Logs**
```
GET /api/admin/audit
```

## 🚀 **COMMANDES DE TEST RAPIDE**

### Test login GRACE :
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+243995030972", "code": "2003"}'
```

### Test login JULVIER :
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "0994477720", "code": "2003"}'
```

### Liste paiements en attente :
```bash
curl -H "X-API-KEY: supersecretadminkey" \
  http://localhost:8000/api/admin/paiements/pending
```

### Liste tous les admins :
```bash
curl -H "X-API-KEY: supersecretadminkey" \
  http://localhost:8000/api/admin/admins
```

## 📱 **INTERFACE D'ADMINISTRATION**

### Swagger UI (Documentation interactive) :
```
http://localhost:8000/docs
```

### Health Check :
```
http://localhost:8000/health
```

### Root API :
```
http://localhost:8000/
```

## 🛠️ **AJOUTER UN NOUVEL ADMIN**

### Via script Python :
```bash
python add_super_admin.py
```

### Manuellement (SQL) :
```sql
INSERT INTO admin_users (name, phone, code_hash, api_key, is_active)
VALUES (
  'NOUVEL_ADMIN',
  '+243XXXXXXXXX',
  'hash_du_code',  -- Généré avec hash_secret("code")
  'supersecretadminkey',
  1
);
```

## 🔒 **SÉCURITÉ**

### Changer les credentials en production :
1. **Modifier `.env` :**
   ```env
   ADMIN_API_KEY=ta_nouvelle_clé_secrète
   API_SECRET_KEY=ta_clé_jwt_secrète
   ```

2. **Regénérer les hashs :**
   ```python
   from app.core.security import hash_secret
   new_hash = hash_secret("nouveau_code")
   ```

3. **Mettre à jour la base :**
   ```sql
   UPDATE admin_users SET code_hash = 'nouveau_hash' WHERE phone = '+243995030972';
   ```

## 📞 **SUPPORT ADMIN**

### En cas de problème :
1. **Admin oublié :** Exécute `python add_super_admin.py`
2. **Clé API perdue :** Regarde dans `.env` → `ADMIN_API_KEY`
3. **Base corrompue :** Supprime `edupay.db` et redémarre l'API

### Logs d'administration :
```
• Fichier : logs/edupay.log
• Console : uvicorn --log-level debug
• Audit : /api/admin/audit
```

## 🎯 **POUR LA DÉMO JURISTES**

### Scénario admin :
1. **"Je me connecte en tant que super admin GRACE"**
   ```bash
   curl -X POST ... (montre la commande)
   ```

2. **"Je consulte les paiements en attente"**
   ```bash
   curl -H "X-API-KEY: ..." ... (montre les résultats)
   ```

3. **"J'approuve un utilisateur"**
   ```bash
   curl -X POST .../approve (simule l'action)
   ```

4. **"Je consulte les logs d'audit"**
   ```bash
   curl -H "X-API-KEY: ..." /api/admin/audit
   ```

### Points à souligner :
- **"Double authentification : téléphone + code"**
- **"Toutes les actions sont auditées"**
- **"Permissions granulaires par rôle"**
- **"Interface professionnelle Swagger"**

## ⚡ **EXÉCUTION RAPIDE**

### Pour tout configurer :
```bash
# 1. Ajoute GRACE comme super admin
python add_super_admin.py

# 2. Teste la connexion
python add_super_admin.py  # Choisis option 2

# 3. Lance la démo complète
python launch_demo_juristes.py
```

**Ton système d'administration est maintenant COMPLET avec GRACE comme super admin !** 🎉