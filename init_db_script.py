from models import init_db, SessionLocal
from sqlalchemy import text

print("Initializing database...")
try:
    init_db()
    print("Database initialized successfully.")
    
    # Verify connection
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    print("Database connection verified.")
    db.close()
except Exception as e:
    print(f"Error initializing database: {e}")
