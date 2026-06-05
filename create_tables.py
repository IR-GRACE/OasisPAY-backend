import psycopg2

conn = psycopg2.connect('postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway')
conn.autocommit = True
cur = conn.cursor()

# 1. Table emplois_du_temps
cur.execute('''
    CREATE TABLE IF NOT EXISTS emplois_du_temps (
        id SERIAL PRIMARY KEY,
        classe_id INTEGER REFERENCES classes(id),
        matiere_id INTEGER REFERENCES matieres(id),
        jour VARCHAR(20),
        heure_debut TIME,
        heure_fin TIME,
        professeur VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table emplois_du_temps créée')

# 2. Table notes
cur.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        etudiant_id INTEGER REFERENCES etudiants(id),
        matiere_id INTEGER REFERENCES matieres(id),
        note DECIMAL(5,2),
        trimestre INTEGER,
        annee_scolaire_id INTEGER REFERENCES annees_scolaires(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table notes créée')

# 3. Table presences
cur.execute('''
    CREATE TABLE IF NOT EXISTS presences (
        id SERIAL PRIMARY KEY,
        etudiant_id INTEGER REFERENCES etudiants(id),
        date DATE,
        present BOOLEAN DEFAULT true,
        justifie BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table presences créée')

# 4. Table depenses
cur.execute('''
    CREATE TABLE IF NOT EXISTS depenses (
        id SERIAL PRIMARY KEY,
        reference VARCHAR(100) UNIQUE,
        description TEXT,
        montant DECIMAL(10,2) NOT NULL,
        categorie VARCHAR(50),
        date_depense TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table depenses créée')

# 5. Table evenements
cur.execute('''
    CREATE TABLE IF NOT EXISTS evenements (
        id SERIAL PRIMARY KEY,
        titre VARCHAR(200) NOT NULL,
        description TEXT,
        date_debut TIMESTAMP,
        date_fin TIMESTAMP,
        type VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table evenements créée')

# 6. Table messages
cur.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        expediteur_id INTEGER,
        destinataire_id INTEGER,
        sujet VARCHAR(255),
        contenu TEXT,
        lu BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('✅ Table messages créée')

print('\n📋 Liste des tables:')
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
for row in cur.fetchall():
    print(f'   - {row[0]}')

conn.close()
print('\n✅ Toutes les tables ont été créées!')
