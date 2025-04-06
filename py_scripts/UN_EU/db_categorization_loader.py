import sqlite3
import pandas as pd

# Constants
CSV_FILE = 'sanctions/UN_EU/Iran/UN_EU_Iran_data.csv'  # Replace with the actual path
DB_FILE = 'database/sanctions_list_database.sqlite'  # Replace with the path to your SQLite database

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Load CSV
df = pd.read_csv(CSV_FILE)

# These are the category labels to check
category_labels = ['Direct', 'Indirect', 'Activity', 'Profit', 'Family_status']

# Create a map from Reason to reason_id from the DB
cursor.execute("SELECT reason_id, reason FROM Reason")
reason_map = {reason.strip(): rid for rid, reason in cursor.fetchall()}

# Populate Categorization table
for _, row in df.iterrows():
    reason_text = str(row['Reason']).strip()
    reason_id = reason_map.get(reason_text)

    if reason_id is None:
        print(f"Reason not found in DB: {reason_text}")
        continue

    for label in category_labels:
        if int(row[label]) == 1:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO Categorization (reason_id, label) VALUES (?, ?)",
                    (reason_id, label)
                )
            except Exception as e:
                print(f"Error inserting ({reason_id}, {label}): {e}")

# Commit and close
conn.commit()
conn.close()
print("Categorization table populated successfully.")
