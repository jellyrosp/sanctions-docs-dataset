import sqlite3
import pandas as pd

# --- CONFIGURATION ---
CSV_FILE = "sanctions/UN_EU/Iran/UN_EU_Iran_data.csv"  # Your CSV path
DB_FILE = "database/sanctions_list_database.sqlite"  # Your SQLite DB path

# --- CONNECT TO DATABASE ---
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Load CSV
df = pd.read_csv(CSV_FILE)

# Normalize column names
df.columns = [col.strip().lower().replace("-", "_") for col in df.columns]

# --- HELPER: Get reason_id from DB ---
def get_reason_id(reason_text):
    reason_text = reason_text.strip()
    cursor.execute("SELECT reason_id FROM Reason WHERE reason = ?", (reason_text,))
    row = cursor.fetchone()
    return row[0] if row else None

# --- HELPER: Insert or get individual_id ---
def get_or_create_individual(name, gender, case_study, reason_id):
    cursor.execute("""
        SELECT individual_id FROM Individual
        WHERE name = ? AND gender = ? AND case_study = ? AND reason_id = ?
    """, (name, gender, case_study, reason_id))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("""
        INSERT INTO Individual (name, gender, case_study, reason_id)
        VALUES (?, ?, ?, ?)
    """, (name, gender, case_study, reason_id))
    return cursor.lastrowid

# --- PROCESS CSV ---
for _, row in df.iterrows():
    reason_text = str(row['reason']).strip()
    reason_id = get_reason_id(reason_text)

    if not reason_id:
        print(f"[SKIPPED] Reason not found in DB: {reason_text[:80]}...")
        continue

    name = str(row['name']).strip()
    gender = str(row['gender']).strip()
    case_study = str(row['case_study']).strip()

    individual_id = get_or_create_individual(name, gender, case_study, reason_id)
    print(f"[OK] Individual ID {individual_id}: {name}")

# --- FINALIZE ---
conn.commit()
conn.close()
print("✅ Individual table population complete.")
