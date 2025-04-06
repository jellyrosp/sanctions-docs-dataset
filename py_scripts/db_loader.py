import sqlite3
import pandas as pd



def load_db(csv_path, doc_title, doc_id):
    DB_FILE = "database/sanctions_list_database.sqlite"  


    # --- CONNECT TO DATABASE ---
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load CSV
    df = pd.read_csv(csv_path)

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


    # --- MAP doc_title to document_id ---
    DOC_TITLE_MAP = {
        doc_title: doc_id,
    }

    # --- HELPER: Get reason_id from DB ---
    def get_reason_id(reason_text):
        reason_text = reason_text.strip()
        cursor.execute("SELECT reason_id FROM Reason WHERE reason = ?", (reason_text,))
        row = cursor.fetchone()
        return row[0] if row else None

    # --- HELPER: Get individual_id from DB ---
    def get_individual_id(name, gender, case_study, reason_id):
        cursor.execute("""
            SELECT individual_id FROM Individual
            WHERE name = ? AND gender = ? AND case_study = ? AND reason_id = ?
        """, (name, gender, case_study, reason_id))
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
        case_study = str(row['case_study']).strip()
        doc_title = str(row['doc_title']).strip()
        start_date = str(row['dates']).strip()

        document_id = DOC_TITLE_MAP.get(doc_title)
        if not document_id:
            print(f"[SKIPPED] Unknown document title: {doc_title}")
            continue

        individual_id = get_individual_id(name, gender, case_study, reason_id)
        if not individual_id:
            print(f"[SKIPPED] Individual not found: {name}")
            continue

        insert_sanction(document_id, individual_id, start_date)

    # --- FINALIZE ---
    conn.commit()
    conn.close()
    print("✅ Sanction table population complete.")

