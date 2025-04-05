import sqlite3
import pandas as pd

# Constants
CSV_FILE = 'sanctions/EU/Russia/EU_russia_data.csv'
DB_FILE = 'database/sanctions_list_database.sqlite'

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Load CSV
df = pd.read_csv(CSV_FILE)

# Normalize column names
df.columns = [col.strip().lower().replace("-", "_") for col in df.columns]

# Define category labels
category_labels = ['direct', 'indirect', 'activity', 'profit', 'family_status']

# Get Reason → reason_id mapping
cursor.execute("SELECT reason_id, reason FROM Reason")
reason_map = {reason.strip(): rid for rid, reason in cursor.fetchall()}

# Populate Categorization table
for _, row in df.iterrows():
    reason_text = str(row['reason']).strip()
    reason_id = reason_map.get(reason_text)

    if reason_id is None:
        print(f"[SKIPPED] Reason not found in DB: {reason_text[:80]}...")
        continue

    for label in category_labels:
        try:
            if int(row[label]) == 1:
                cursor.execute(
                    "INSERT OR IGNORE INTO Categorization (reason_id, label) VALUES (?, ?)",
                    (reason_id, label)
                )
        except Exception as e:
            print(f"[ERROR] Inserting ({reason_id}, {label}): {e}")

# Commit and close
conn.commit()
conn.close()
print("✅ Categorization table populated successfully.")
