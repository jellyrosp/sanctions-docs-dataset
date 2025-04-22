import pandas as pd
import sqlite3

def update_status_based_cat_from_csv(csv_path, db_path):
    # Load the enriched CSV (with 'Nationality' column)
    df = pd.read_csv(csv_path)

    # Connect to your SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update each individual's nationality based on name or other matching logic
    for _, row in df.iterrows():
        gender = str(row["Gender"]).strip().lower()
        status = row["Status_based"]  # keep as int

        if gender == "female" and status == 1:
            name = str(row["Name"]).strip()

        # Update by matching on Name (you could also use individual_id if available)
            cursor.execute("""
                SELECT reason_id
                FROM Individual
                WHERE name = ?                                      
            """, (name,))
            result = cursor.fetchone()

            if result:
                reason_id = result[0]

                cursor.execute("""
                    INSERT INTO Categorization (reason_id, label)
                    VALUES (?, 'Status_based')            
                """, (reason_id,))
                print(f"✅ Inserted 'Status_based' for {name}")
            else:
                print(f"❌ No reason_id found for {name}")    

    # Commit and close
    conn.commit()
    conn.close()

    print("✅ 'All applicable 'Status_based' labels inserted.")

db_p = "database/sanctions_list_database.sqlite"
csv_p = "sanctions/EU/Syria/EU_syria_data.csv"

update_status_based_cat_from_csv(csv_p, db_p)