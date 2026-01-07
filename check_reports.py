# check_reports.py

# for testing purposes
import os
import json

def check_reports():
    reports_dir = "interview_reports"
    
    print("=== Checking Interview Reports ===")
    print(f"Reports directory: {os.path.abspath(reports_dir)}")
    print(f"Directory exists: {os.path.exists(reports_dir)}")
    
    if os.path.exists(reports_dir):
        files = os.listdir(reports_dir)
        print(f"\nFiles in directory ({len(files)} total):")
        for file in files:
            filepath = os.path.join(reports_dir, file)
            size = os.path.getsize(filepath)
            print(f"  • {file} ({size} bytes)")
            
            if file.endswith('.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        print(f"    - Report ID: {data.get('report_id', 'N/A')}")
                        print(f"    - Timestamp: {data.get('timestamp', 'N/A')}")
                        print(f"    - Overall Score: {data.get('overall_score', 'N/A')}")
                except Exception as e:
                    print(f"    - Error reading: {e}")
    else:
        print(f"\nCreating directory...")
        os.makedirs(reports_dir, exist_ok=True)
        print(f"Directory created at: {os.path.abspath(reports_dir)}")
    
    print("\n=== Current working directory ===")
    print(f"Working dir: {os.getcwd()}")
    print(f"Contents: {os.listdir('.')}")

if __name__ == "__main__":
    check_reports()