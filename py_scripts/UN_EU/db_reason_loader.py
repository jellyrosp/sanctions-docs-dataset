import sqlite3
import pandas as pd

# --- CONFIGURATION ---
CSV_FILE = "sanctions/UN_EU/Iran/UN_EU_Iran_data.csv"  # Path to your CSV
DB_FILE = "database/sanctions_list_database.sqlite"  # Path to your SQLite DB

# --- CONNECT TO DATABASE ---
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Load CSV
df = pd.read_csv(CSV_FILE)

# Normalize column names
df.columns = [col.strip().lower().replace("-", "_") for col in df.columns]

# Get unique reasons
unique_reasons = df['reason'].dropna().unique()

# Insert reasons into the Reason table
for reason in unique_reasons:
    reason = reason.strip()
    cursor.execute("SELECT reason_id FROM Reason WHERE reason = ?", (reason,))
    if cursor.fetchone():
        print(f"[SKIPPED] Already exists: {reason[:80]}...")
        continue
    cursor.execute("INSERT INTO Reason (reason) VALUES (?)", (reason,))
    print(f"[INSERTED] {reason[:80]}...")

# Finalize
conn.commit()
conn.close()
print("✅ Reason table population complete.")
