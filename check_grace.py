import os
from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway'
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM admin_users WHERE phone = '+243995030972'"))
    row = result.fetchone()
    if row:
        print('GRACE trouvé:')
        print(f'  ID: {row[0]}')
        print(f'  Name: {row[1]}')
        print(f'  Phone: {row[2]}')
        print(f'  Code hash: {row[3][:50]}...')
        print(f'  Is active: {row[5]}')
        print(f'  Created at: {row[6]}')
    else:
        print('GRACE non trouvé')