import psycopg2

conn = psycopg2.connect('postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway')
conn.autocommit = True
cur = conn.cursor()

# 1. Transactions
cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        reference VARCHAR(100) UNIQUE NOT NULL,
        expediteur_id INTEGER,
        destinataire_id INTEGER,
        montant DECIMAL(10,2) NOT NULL,
        frais DECIMAL(10,2) DEFAULT 0,
        devise VARCHAR(10) DEFAULT 'CDF',
        type VARCHAR(50),
        statut VARCHAR(50) DEFAULT 'en_attente',
        methode VARCHAR(50),
        date_transaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table transactions créée')

# 2. Factures
cur.execute('''
    CREATE TABLE IF NOT EXISTS factures (
        id SERIAL PRIMARY KEY,
        reference VARCHAR(100) UNIQUE NOT NULL,
        etudiant_id INTEGER REFERENCES etudiants(id),
        montant DECIMAL(10,2) NOT NULL,
        type_frais VARCHAR(100),
        echeance DATE,
        statut VARCHAR(50) DEFAULT 'impayee',
        date_paiement TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table factures créée')

# 3. Méthodes de paiement
cur.execute('''
    CREATE TABLE IF NOT EXISTS methodes_paiement (
        id SERIAL PRIMARY KEY,
        utilisateur_id INTEGER,
        type VARCHAR(50),
        numero VARCHAR(100),
        operateur VARCHAR(50),
        est_actif BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table methodes_paiement créée')

# 4. Notifications
cur.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id SERIAL PRIMARY KEY,
        utilisateur_id INTEGER,
        titre VARCHAR(255),
        message TEXT,
        type VARCHAR(50),
        lu BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table notifications créée')

# 5. Logs paiement
cur.execute('''
    CREATE TABLE IF NOT EXISTS logs_paiement (
        id SERIAL PRIMARY KEY,
        reference VARCHAR(100),
        action VARCHAR(100),
        statut_avant VARCHAR(50),
        statut_apres VARCHAR(50),
        message TEXT,
        ip_address VARCHAR(50),
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table logs_paiement créée')

# 6. Remboursements
cur.execute('''
    CREATE TABLE IF NOT EXISTS remboursements (
        id SERIAL PRIMARY KEY,
        transaction_reference VARCHAR(100),
        montant DECIMAL(10,2),
        motif TEXT,
        statut VARCHAR(50) DEFAULT 'en_attente',
        approuve_par INTEGER,
        date_remboursement TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table remboursements créée')

# 7. Portefeuilles
cur.execute('''
    CREATE TABLE IF NOT EXISTS portefeuilles (
        id SERIAL PRIMARY KEY,
        utilisateur_id INTEGER UNIQUE,
        solde DECIMAL(10,2) DEFAULT 0,
        devise VARCHAR(10) DEFAULT 'CDF',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table portefeuilles créée')

# 8. API Logs
cur.execute('''
    CREATE TABLE IF NOT EXISTS api_logs (
        id SERIAL PRIMARY KEY,
        endpoint VARCHAR(255),
        methode VARCHAR(10),
        request_body TEXT,
        response_code INTEGER,
        response_body TEXT,
        ip_address VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table api_logs créée')

print('\n📋 Toutes les tables pour paiement électronique sont prêtes!')

conn.close()
