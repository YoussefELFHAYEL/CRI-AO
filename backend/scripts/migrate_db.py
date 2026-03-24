import psycopg2
import os

db_url = "postgresql://postgres.gaxngnkvfquwfbshzkcd:,R?7w7tTZq$Y5eE@aws-1-eu-central-1.pooler.supabase.com:5432/postgres"
sql_file = "c:/Users/YoussefElFhayel/OneDrive - Akumenia/Bureau/CRI-AO/backend/sql/schema.sql"

def main():
    try:
        print(f"Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"Reading SQL file: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        print("Executing SQL script statement by statement...")
        # Split by ';' but be careful with functions/triggers if any (none here though)
        statements = sql.split(';')
        for statement in statements:
            stmt = statement.strip()
            if not stmt:
                continue
            try:
                cur.execute(stmt)
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  Skipped: {stmt[:50]}... (Already exists)")
                else:
                    print(f"  Warning: Could not execute: {stmt[:50]}... (Error: {e})")
        
        print("✅ Migration process finished!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    main()
