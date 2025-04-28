import re
from collections import defaultdict
from itertools import combinations
import csv
import pandas as pd

def normalize_Name(csv_path):
    df = pd.read_csv(csv_path)
    
    # Pulizia dei nomi
    df["Name"] = df["Name"].str.replace(r'\([^)]*\)', '', regex=True)
    df["Name"] = df["Name"].str.replace(r'a\.k\.a\.[^\)]*', '', regex=True, case=False)
    df["Name"] = df["Name"].str.replace(r'\/', ' ', regex=True)
    df["Name"] = df["Name"].str.lower()
    df["Name"] = df["Name"].str.replace(r'[^a-zа-яё\s]', '', regex=True)
    df["Name"] = df["Name"].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    return df  # <<<<<<<< aggiungi questo!

    #print(df.info())
    

def find_duplicates(df, column_name="Name", similarity_threshold=0.7):
    """
    Trova duplicati mantenendo Designation_source e Regime_name, seguendo la logica originale.
    """
    # Mappa: nome originale -> set di parole normalizzate
    normalized_names = {
        row["Name"]: set(str(row[column_name]).split())
        for _, row in df.iterrows()
        if pd.notna(row[column_name]) and isinstance(row[column_name], str)
    }
    
    # Mappa: nome originale -> (designation_source, regime_name)
    source_mapping = {
        row["Name"]: (
            row.get("Designation_source", None),
            row.get("Regime_name", None)
        )
        for _, row in df.iterrows()
        if pd.notna(row[column_name]) and isinstance(row[column_name], str)
    }
    
    potential_duplicates = defaultdict(list)
    seen_pairs = set()
    
    for (name1, tokens1), (name2, tokens2) in combinations(normalized_names.items(), 2):
        if not tokens1 or not tokens2:
            continue
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        similarity = len(intersection) / len(union)
        
        if similarity >= similarity_threshold:
            pair = frozenset([name1, name2])
            if pair not in seen_pairs:
                potential_duplicates[name1].append(name2)
                seen_pairs.add(pair)
    
    return potential_duplicates, source_mapping



def correct_duplicates_in_df(df, Name_dict):
    """
    Corregge i nomi duplicati nel DataFrame, standardizzandoli al nome principale (master name).
    
    Args:
        df (pd.DataFrame): Il DataFrame originale.
        Name_dict (dict): Dizionario {master_name: [list_of_duplicates]}.
    
    Returns:
        pd.DataFrame: DataFrame aggiornato.
    """
    name_correction = {}
    
    # Costruisco una mappa: duplicato -> nome principale
    for master_name, duplicates in Name_dict.items():
        for dup_name in duplicates:
            name_correction[dup_name] = master_name
    
    # Ora sostituisco nel DataFrame
    df_corrected = df.copy()
    df_corrected["Name"] = df_corrected["Name"].apply(
        lambda x: name_correction.get(x, x) if pd.notna(x) else x
    )
    
    return df_corrected




# 1. Normalizza
normalized_df = normalize_Name("data_analysis/complete_dataset_with_dup.csv")

# 2. Trova duplicati
Name_dict, source_mapping = find_duplicates(normalized_df)

# 3. Correggi i duplicati
corrected_df = correct_duplicates_in_df(normalized_df, Name_dict)

# 4. Salva o stampa
corrected_df.to_csv("data_analysis/complete_dataset_with_corrected_names.csv", index=False)
print("\nNomi duplicati corretti e salvati!")



