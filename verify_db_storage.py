import sqlite3
import json
import os

DB_FILE = "sql_app.db"

def inspect_db():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database file '{DB_FILE}' not found!")
        return

    print(f"✅ Inspecting Database: {DB_FILE}\n")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Check Users
    print("--- Users Table ---")
    try:
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"Total Users: {count}")
        
        cursor.execute("SELECT id, github_username, github_email FROM users LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID: {row[0]} | Username: {row[1]} | Email: {row[2]}")
    except sqlite3.OperationalError as e:
        print(f"❌ Error querying users table: {e}")

    # 2. Check Repositories
    print("\n--- Repositories Table ---")
    try:
        cursor.execute("SELECT count(*) FROM repositories")
        count = cursor.fetchone()[0]
        print(f"Total Repositories: {count}")
        
        cursor.execute("SELECT id, name, full_name, repo_url FROM repositories LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID: {row[0]} | Name: {row[1]} | Full Name: {row[2]}")
    except sqlite3.OperationalError as e:
        print(f"❌ Error querying repositories table: {e}")

    # 3. Check Projects
    print("\n--- Projects Table ---")
    try:
        cursor.execute("SELECT count(*) FROM projects")
        count = cursor.fetchone()[0]
        print(f"Total Projects: {count}")
        
        cursor.execute("SELECT id, project_name, description, features FROM projects LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            pid, name, desc, features_json = row
            try:
                features = json.loads(features_json) if features_json else []
            except:
                features = features_json
                
            print(f"  ID: {pid}")
            print(f"  Project Name: {name}")
            print(f"  Description: {desc[:100]}..." if desc and len(desc) > 100 else f"  Description: {desc}")
            print(f"  Features Type in DB: {type(features_json)}")
            print(f"  Parsed Features: {features}")
            print("-" * 20)
            
    except sqlite3.OperationalError as e:
        print(f"❌ Error querying projects table: {e}")

    # 4. Check Analysis Results
    print("\n--- Analysis Results Table ---")
    try:
        cursor.execute("SELECT count(*) FROM analysis_results")
        count = cursor.fetchone()[0]
        print(f"Total Analysis Results: {count}")
        
        cursor.execute("SELECT id, project_id, created_at, python_files, analysis_data FROM analysis_results ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        for row in rows:
            aid, pid, created, py_files_raw, analysis_raw = row
            print(f"\n  Analysis ID: {aid}")
            print(f"  Project ID: {pid}")
            print(f"  Created At: {created}")
            
            try:
                py_files = json.loads(py_files_raw) if py_files_raw else []
                print(f"  Python Files Found: {len(py_files)}")
                # Show first 3 files
                for f in py_files[:3]:
                    print(f"    - {f}")
                if len(py_files) > 3:
                    print(f"    - ... ({len(py_files)-3} more)")
            except:
                print(f"  Python Files raw: {py_files_raw}")

            try:
                analysis = json.loads(analysis_raw) if analysis_raw else []
                print(f"  Analysis Entries: {len(analysis)}")
                if analysis:
                    print(f"  Sample Analysis Item Keys: {list(analysis[0].keys())}")
            except:
                print(f"  Analysis Data raw len: {len(str(analysis_raw))}")
            print("-" * 30)

    except sqlite3.OperationalError as e:
        print(f"❌ Error querying analysis_results table: {e}")
        print("Note: If this table is missing, run the pipeline once to create it.")

    conn.close()

if __name__ == "__main__":
    inspect_db()
