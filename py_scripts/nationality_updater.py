import pandas as pd
import sqlite3

def update_nationality_from_csv(csv_path, db_path):
    # Load the enriched CSV (with 'Nationality' column)
    df = pd.read_csv(csv_path)

    # Connect to your SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update each individual's nationality based on name or other matching logic
    for _, row in df.iterrows():
        name = row['Name'].strip()
        nationality = row['Nationality'].strip()

        # Update by matching on Name (you could also use individual_id if available)
        cursor.execute("""
            UPDATE Individual
            SET nationality = ?
            WHERE name = ?;
        """, (nationality, name))

    # Commit and close
    conn.commit()
    conn.close()

    print("✅ Nationality values updated successfully.")

db_p = "database/sanctions_list_database.sqlite"
csv_p = "sanctions/EU/Syria/EU_syria_data1.csv"

update_nationality_from_csv(csv_p, db_p)