import sqlite3
import asyncio
from app.core.database import sync_engine, Base
import app.models

def migrate():
    # 1. Create all missing tables (worker_insurances, worker_leaves, etc.)
    Base.metadata.create_all(bind=sync_engine)

    # 2. Add any missing columns to workers table in SQLite
    conn = sqlite3.connect('ai_mineguard.db')
    cur = conn.cursor()
    existing_cols = [c[1] for c in cur.execute('PRAGMA table_info(workers)').fetchall()]
    
    new_cols = [
        ('blood_group', 'VARCHAR(10)'),
        ('rfid_tag', 'VARCHAR(50)'),
        ('medical_fitness_status', 'VARCHAR(30) DEFAULT "FIT"'),
        ('medical_exam_date', 'DATE'),
        ('medical_expiry_date', 'DATE'),
    ]
    for col, typ in new_cols:
        if col not in existing_cols:
            cur.execute(f'ALTER TABLE workers ADD COLUMN {col} {typ}')
            print(f"Added column {col} to workers")

    conn.commit()
    conn.close()
    print("Database schema migration completed successfully.")

if __name__ == '__main__':
    migrate()
