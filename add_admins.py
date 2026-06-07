import psycopg2
import bcrypt

conn = psycopg2.connect('postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway')
conn.autocommit = True
cur = conn.cursor()

hash_grace = bcrypt.hashpw('Grace123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
hash_julvier = bcrypt.hashpw('2003'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# GRACE
cur.execute('''
    INSERT INTO admin (email, hashed_password, nom, prenom, telephone, role, actif)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
''', ('Masiyamulimbi4@gmail.com', hash_grace, 'GRACE', 'Administrateur', '+243995030972', 'super_admin', True))

# JULVIER
cur.execute('''
    INSERT INTO admin (email, hashed_password, nom, prenom, telephone, role, actif)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
''', ('stypojulvier009@gmail.com', hash_julvier, 'JULVIER', 'MUKENDI', '0994477720', 'super_admin', True))

print('Admins ajoutes')

cur.execute('SELECT id, email FROM admin')
for row in cur.fetchall():
    print(f'ID: {row[0]} | Email: {row[1]}')

conn.close()
