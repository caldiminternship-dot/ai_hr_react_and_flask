from models import SessionLocal, User, Report
import pandas as pd
from sqlalchemy import text

def view_data():
    db = SessionLocal()
    
    print("\n=== USERS ===")
    users = db.query(User).all()
    if users:
        data = [{"ID": u.id, "Email": u.email, "Created At": u.created_at} for u in users]
        print(pd.DataFrame(data))
    else:
        print("No users found.")

    print("\n=== REPORTS ===")
    reports = db.query(Report).all()
    if reports:
        data = [{"ID": r.id, "User ID": r.user_id, "Score": r.score, "File": r.file_path, "Time": r.timestamp} for r in reports]
        print(pd.DataFrame(data))
    else:
        print("No reports found.")
    
    db.close()

if __name__ == "__main__":
    view_data()
