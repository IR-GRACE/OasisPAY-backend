import psycopg2

conn = psycopg2.connect('postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway')
conn.autocommit = True
cur = conn.cursor()

# Ajouter les classes
cur.execute('''
    INSERT INTO classes (nom, niveau) VALUES
    ('6ème Année', 'Primaire'),
    ('5ème Année', 'Primaire'),
    ('4ème Année', 'Primaire'),
    ('3ème Année', 'Moyen'),
    ('2ème Année', 'Moyen'),
    ('1ère Année', 'Moyen'),
    ('2nde', 'Secondaire'),
    ('1ère', 'Secondaire'),
    ('Terminale', 'Secondaire')
    ON CONFLICT (id) DO NOTHING
''')
print('✅ Classes ajoutées')

# Ajouter l'année scolaire
cur.execute('''
    INSERT INTO annees_scolaires (annee, debut, fin, active) VALUES
    ('2024-2025', '2024-09-01', '2025-06-30', true)
    ON CONFLICT (id) DO NOTHING
''')
print('✅ Année scolaire ajoutée')

# Ajouter les matières
cur.execute('''
    INSERT INTO matieres (nom, coefficient) VALUES
    ('Mathématiques', 4),
    ('Français', 4),
    ('Anglais', 3),
    ('Sciences', 3),
    ('Histoire-Géo', 2),
    ('Éducation physique', 1)
    ON CONFLICT (id) DO NOTHING
''')
print('✅ Matières ajoutées')

# Vérifier
cur.execute('SELECT COUNT(*) FROM classes')
print(f'\nTotal classes: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM matieres')
print(f'Total matières: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM annees_scolaires')
print(f'Total années: {cur.fetchone()[0]}')

conn.close()
print('\n✅ Données initiales ajoutées!')
