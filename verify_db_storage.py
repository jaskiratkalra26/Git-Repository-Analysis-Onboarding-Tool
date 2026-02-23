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

    conn.close()

if __name__ == "__main__":
    inspect_db()
