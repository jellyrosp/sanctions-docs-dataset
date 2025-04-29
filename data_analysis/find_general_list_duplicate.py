import pandas as pd

import pandas as pd

def find_duplicate_names_list(csv_path):
    """
    Trova l'elenco dei nomi duplicati raggruppati per Regime_name e Designation_source.

    Args:
        csv_path (str): Percorso al file CSV.

    Returns:
        list: Lista dei nomi duplicati trovati.
    """
    # 1. Carica il CSV
    df = pd.read_csv(csv_path)
    
    # 2. Gruppo per Regime_name, Designation_source, Name
    grouped = df.groupby(["Regime_name", "Designation_source", "Name", "Statement_of_reason"]).size().reset_index(name='count')
    
    # 3. Seleziono solo quelli dove il nome appare più di una volta
    duplicates = grouped[grouped["count"] > 1]
    
    # 4. Estrai solo la colonna "Name" come lista
    duplicate_names = duplicates["Name"].tolist()
    
    return duplicate_names



csv_path = "data_analysis/datasets_with_fixed_names/complete_dataset_with_corrected_names.csv"

duplicate_names_list = find_duplicate_names_list(csv_path)

print(duplicate_names_list)
