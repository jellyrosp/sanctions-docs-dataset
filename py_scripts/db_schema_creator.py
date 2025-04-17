import subprocess
import os

def export_sqlite_schema(db_path, output_sql_path):
    """
    Parameters:
    - db_path (str): Path to the SQLite database file.
    - output_sql_path (str): Path to save the schema .sql file.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"❌ Database not found: {db_path}")

    command = f"sqlite3 {db_path} .schema > {output_sql_path}"
    subprocess.run(command, shell=True, check=True)

    print(f"✅ Schema exported to: {output_sql_path}")



export_sqlite_schema(
    db_path="database/sanctions_list_database.sqlite",
    output_sql_path="database/db_schema.sql"
)
