import psycopg2
import json
import os

db_url = "postgresql://postgres.gaxngnkvfquwfbshzkcd:,R?7w7tTZq$Y5eE@aws-1-eu-central-1.pooler.supabase.com:5432/postgres"

DEMO_DOSSIERS = [
    {
        "reference": "INV-2024-001",
        "company_name": "TechMaroc Solutions SARL",
        "project_type": "Création SARL - Secteur Digital",
        "status": "En cours",
        "current_step": "Vérification des documents",
        "total_steps": 5,
        "completed_steps": 3,
        "investor_name": "Ahmed Benali",
        "investor_phone": "0661234567",
        "history": json.dumps([
            {"date": "2024-01-15", "action": "Dépôt du dossier", "note": "Dossier complet"},
            {"date": "2024-01-18", "action": "Validation initiale", "note": "Documents conformes"},
            {"date": "2024-02-01", "action": "Étude de faisabilité", "note": "Approuvée"},
            {"date": "2024-02-15", "action": "Vérification des documents", "note": "En cours"},
        ]),
    },
    {
        "reference": "INV-2024-002",
        "company_name": "Green Energy RSK SA",
        "project_type": "Création SA - Énergies Renouvelables",
        "status": "Validé",
        "current_step": "Terminé",
        "total_steps": 5,
        "completed_steps": 5,
        "investor_name": "Sara El Fassi",
        "investor_phone": "0662345678",
        "history": json.dumps([
            {"date": "2024-01-10", "action": "Dépôt du dossier", "note": ""},
            {"date": "2024-01-13", "action": "Validation initiale", "note": ""},
            {"date": "2024-01-25", "action": "Étude de faisabilité", "note": "Approuvée"},
            {"date": "2024-02-05", "action": "Vérification juridique", "note": "Conforme"},
            {"date": "2024-02-20", "action": "Validation finale", "note": "Dossier approuvé"},
        ]),
    },
    {
        "reference": "INV-2024-003",
        "company_name": "AgroFood Kénitra SARL",
        "project_type": "Extension - Agroalimentaire",
        "status": "En attente",
        "current_step": "Complément de documents requis",
        "total_steps": 5,
        "completed_steps": 1,
        "investor_name": "Karim Tazi",
        "investor_phone": "0663456789",
        "history": json.dumps([
            {"date": "2024-02-20", "action": "Dépôt du dossier", "note": "Documents manquants signalés"},
        ]),
    },
]

DEMO_STATISTICS = [
    ("Dossiers reçus", 7, "today", "dossiers"),
    ("Dossiers traités", 5, "today", "dossiers"),
    ("Rendez-vous programmés", 12, "today", "rdv"),
    ("Demandes de renseignements", 34, "today", "demandes"),
    ("Nouveaux dossiers", 42, "month", "dossiers"),
    ("Dossiers validés", 28, "month", "dossiers"),
    ("Dossiers en attente", 18, "month", "dossiers"),
    ("Dossiers rejetés", 3, "month", "dossiers"),
    ("Taux de validation (%)", 87, "month", "performance"),
]

def main():
    try:
        print("Connecting to database for seeding...")
        conn = psycopg2.connect(
            db_url,
            connect_timeout=10
        )
        cur = conn.cursor()
        
        # Clear stats
        print("Clearing statistics...")
        cur.execute("DELETE FROM demo_statistics")
        
        # Insert stats
        print("Inserting statistics...")
        for name, val, per, cat in DEMO_STATISTICS:
            cur.execute(
                "INSERT INTO demo_statistics (metric_name, metric_value, period, category) VALUES (%s, %s, %s, %s)",
                (name, val, per, cat)
            )
            
        # Seed dossiers
        print("Seeding dossiers (upsert)...")
        for d in DEMO_DOSSIERS:
            cur.execute("""
                INSERT INTO demo_dossiers (reference, company_name, project_type, status, current_step, total_steps, completed_steps, investor_name, investor_phone, history)
                VALUES (%(reference)s, %(company_name)s, %(project_type)s, %(status)s, %(current_step)s, %(total_steps)s, %(completed_steps)s, %(investor_name)s, %(investor_phone)s, %(history)s)
                ON CONFLICT (reference) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    project_type = EXCLUDED.project_type,
                    status = EXCLUDED.status,
                    current_step = EXCLUDED.current_step,
                    total_steps = EXCLUDED.total_steps,
                    completed_steps = EXCLUDED.completed_steps,
                    investor_name = EXCLUDED.investor_name,
                    investor_phone = EXCLUDED.investor_phone,
                    history = EXCLUDED.history,
                    updated_at = NOW()
            """, d)
        
        conn.commit()
        print("✅ Demo data seeded successfully via JDBC/psycopg2!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Seeding failed: {e}")

if __name__ == "__main__":
    main()
