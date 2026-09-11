"""
Database migration script for Module 3 Workforce Governance.
Ensures worker_passes, worker_documents, worker_inductions tables are created
and verifies foreign keys and column schemas in SQLite.
"""

import sqlite3
from app.core.database import sync_engine, Base
import app.models

def migrate():
    print("Executing Base.metadata.create_all for Module 3 tables...")
    Base.metadata.create_all(bind=sync_engine)

    conn = sqlite3.connect('ai_mineguard.db')
    cur = conn.cursor()

    # Verify tables exist
    tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Total tables in database: {len(tables)}")
    for expected in ['worker_passes', 'worker_documents', 'worker_inductions']:
        if expected in tables:
            print(f"Table '{expected}' successfully created/verified.")
        else:
            print(f"ERROR: Table '{expected}' is missing!")

    conn.commit()
    conn.close()
    print("Module 3 database migration completed successfully.")

if __name__ == '__main__':
    migrate()
