import sqlite3
import pandas as pd

# --- CONFIGURATION ---
CSV_FILE = "sanctions/EU/Russia/EU_russia_data.csv"  # Path to your CSV
DB_FILE = "database/sanctions_list_database.sqlite"  # Path to your SQLite DB

# --- CONNECT TO DATABASE ---
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Load CSV
df = pd.read_csv(CSV_FILE)
df.columns = [col.strip().lower().replace("-", "_") for col in df.columns]

# --- MAP doc_title to document_id ---
DOC_TITLE_MAP = {
    "COUNCIL_REGULATION _EU_ 2024_1485_27_May_2024": 2,
    "COUNCIL_REGULATION_EU_2024_2642_8_October_2024": 3
}

# --- HELPER: Get reason_id from DB ---
def get_reason_id(reason_text):
    reason_text = reason_text.strip()
    cursor.execute("SELECT reason_id FROM Reason WHERE reason = ?", (reason_text,))
    row = cursor.fetchone()
    return row[0] if row else None

# --- HELPER: Get individual_id from DB ---
def get_individual_id(name, gender, nationality, reason_id):
    cursor.execute("""
        SELECT individual_id FROM Individual
        WHERE name = ? AND gender = ? AND nationality = ? AND reason_id = ?
    """, (name, gender, nationality, reason_id))
    row = cursor.fetchone()
    return row[0] if row else None

# --- HELPER: Insert sanction ---
def insert_sanction(document_id, individual_id, start_date):
    cursor.execute("""
        SELECT 1 FROM Sanction WHERE document_id = ? AND individual_id = ?
    """, (document_id, individual_id))
    if cursor.fetchone():
        print(f"[SKIPPED] Sanction already exists: Individual {individual_id}, Document {document_id}")
        return
    cursor.execute("""
        INSERT INTO Sanction (document_id, individual_id, start_date)
        VALUES (?, ?, ?)
    """, (document_id, individual_id, start_date))
    print(f"[INSERTED] Sanction: Individual {individual_id}, Document {document_id}, Date {start_date}")

# --- PROCESS EACH ROW ---
for _, row in df.iterrows():
    reason_text = str(row['reason']).strip()
    reason_id = get_reason_id(reason_text)
    if not reason_id:
        print(f"[SKIPPED] Reason not found: {reason_text[:80]}...")
        continue

    name = str(row['name']).strip()
    gender = str(row['gender']).strip()
    nationality = str(row['nationality']).strip()
    doc_title = str(row['doc_title']).strip()
    start_date = str(row['dates']).strip()

    document_id = DOC_TITLE_MAP.get(doc_title)
    if not document_id:
        print(f"[SKIPPED] Unknown document title: {doc_title}")
        continue

    individual_id = get_individual_id(name, gender, nationality, reason_id)
    if not individual_id:
        print(f"[SKIPPED] Individual not found: {name}")
        continue

    insert_sanction(document_id, individual_id, start_date)

# --- FINALIZE ---
conn.commit()
conn.close()
print("✅ Sanction table population complete.")
