import sqlite3
import pandas as pd

def load_db(csv_path, doc_title, doc_id):
    DB_FILE = "database/sanctions_list_database.sqlite"

    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load CSV
    df = pd.read_csv(csv_path)
    df.columns = [col.strip().lower() for col in df.columns]  # Normalize column names

    # --- HELPER FUNCTIONS ---
    def get_reason_id(reason_text):
        reason_text = reason_text.strip()
        cursor.execute("SELECT reason_id FROM Reason WHERE reason = ?", (reason_text,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_or_create_individual(name, gender, case_study, reason_id, nationality):
        cursor.execute("""
            SELECT individual_id FROM Individual
            WHERE name = ? AND gender = ? AND case_study = ? AND reason_id = ? AND nationality = ?
        """, (name, gender, case_study, reason_id, nationality))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("""
            INSERT INTO Individual (name, gender, case_study, reason_id, nationality)
            VALUES (?, ?, ?, ?, ?)
        """, (name, gender, case_study, reason_id, nationality))
        return cursor.lastrowid

    def get_individual_id(name, gender, case_study, reason_id):
        cursor.execute("""
            SELECT individual_id FROM Individual
            WHERE name = ? AND gender = ? AND case_study = ? AND reason_id = ?
        """, (name, gender, case_study, reason_id))
        row = cursor.fetchone()
        return row[0] if row else None

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

    def categorization_exists(reason_id, label):
        cursor.execute("""
            SELECT 1 FROM Categorization WHERE reason_id = ? AND label = ?
        """, (reason_id, label))
        return cursor.fetchone() is not None

    # --- Insert unique reasons into Reason table ---
    unique_reasons = df['reason'].dropna().unique()
    for reason in unique_reasons:
        reason = reason.strip()
        cursor.execute("SELECT reason_id FROM Reason WHERE reason = ?", (reason,))
        if cursor.fetchone():
            print(f"[SKIPPED] Already exists: {reason[:80]}...")
            continue
        cursor.execute("INSERT INTO Reason (reason) VALUES (?)", (reason,))
        print(f"[INSERTED] {reason[:80]}...")
    print("✅ Reason table population complete.")

    # --- Insert Individuals ---
    for _, row in df.iterrows():
        reason_text = str(row['reason']).strip()
        reason_id = get_reason_id(reason_text)
        if not reason_id:
            print(f"[SKIPPED] Reason not found in DB: {reason_text[:80]}...")
            continue

        name = str(row['name']).strip()
        gender = str(row['gender']).strip()
        case_study = str(row['case_study']).strip()
        nationality = str(row['nationality']).strip()

        individual_id = get_or_create_individual(name, gender, case_study, reason_id, nationality)
        print(f"[OK] Individual ID {individual_id}: {name}")
    print("✅ Individual table population complete.")

    # --- Insert Sanctions ---
    DOC_TITLE_MAP = {doc_title: doc_id}
    for _, row in df.iterrows():
        reason_text = str(row['reason']).strip()
        reason_id = get_reason_id(reason_text)
        if not reason_id:
            continue

        name = str(row['name']).strip()
        gender = str(row['gender']).strip()
        case_study = str(row['case_study']).strip()
        doc_title_row = str(row['doc_title']).strip()
        start_date = str(row['dates']).strip()

        document_id = DOC_TITLE_MAP.get(doc_title_row)
        if not document_id:
            continue

        individual_id = get_individual_id(name, gender, case_study, reason_id)
        if not individual_id:
            continue

        insert_sanction(document_id, individual_id, start_date)
    print("✅ Sanction table population complete.")

    # --- Insert Categorization (only for female individuals) ---
    category_labels = ['activity_based', 'profit_based', 'family_member_sanctions', 'status_based']

    # Get all reason_ids linked to female individuals
    cursor.execute("SELECT DISTINCT reason_id FROM Individual WHERE LOWER(gender) = 'female'")
    female_reason_ids = set(row[0] for row in cursor.fetchall() if row[0] is not None)
    
    for _, row in df.iterrows():
        reason_text = str(row['reason']).strip()
        reason_id = get_reason_id(reason_text)
        if reason_id is None or reason_id not in female_reason_ids:
            continue

        for label in category_labels:
            if label in df.columns:
                raw_val = row[label]
                try:
                    value = float(raw_val)
                except (ValueError, TypeError):
                    value = 0

                formatted_label = label.title().replace('_', ' ')
                if value == 1.0:
                    if not categorization_exists(reason_id, formatted_label):
                        try:
                            cursor.execute("""
                                INSERT INTO Categorization (reason_id, label) VALUES (?, ?)
                            """, (reason_id, formatted_label))
                            print(f"[INSERTED] Categorization: {formatted_label} for reason_id {reason_id}")
                        except Exception as e:
                            print(f"[ERROR] Categorization ({reason_id}, {formatted_label}): {e}")
                    else:
                        print(f"[SKIPPED] Categorization Already exists: {formatted_label} for reason_id {reason_id}")

    print("✅ Categorization table population complete.")

    # Finalize
    conn.commit()
    conn.close()




csv_p = "sanctions/EU/Zimbabwe/EU_Zimbabwe_data.csv"
load_db(csv_p, "COUNCIL_REGULATION_EU_314_2004_19_February_2004", 26)