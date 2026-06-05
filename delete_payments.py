import psycopg2

conn = psycopg2.connect('postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway')
conn.autocommit = True
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS payments CASCADE')
print('✅ Ancienne table payments supprimée')

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
print('\n📋 Tables restantes:')
for row in cur.fetchall():
    print(f'   - {row[0]}')

conn.close()
