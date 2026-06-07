import psycopg2

conn = psycopg2.connect('postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway')
conn.autocommit = True
cur = conn.cursor()

# Supprimer l'ancien compte
cur.execute("DELETE FROM users WHERE email = 'stypojulvier009@mail.com'")
cur.execute("DELETE FROM admin WHERE email = 'stypojulvier009@mail.com'")
cur.execute("DELETE FROM utilisateurs WHERE email = 'stypojulvier009@mail.com'")
cur.execute("DELETE FROM admin_users WHERE email = 'stypojulvier009@mail.com'")

print('Ancien compte supprime')

conn.close()
