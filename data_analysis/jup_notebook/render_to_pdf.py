#!/usr/bin/env python3

import subprocess
import os

def export_notebook_to_pdf(notebook_path):
    """
    Convert a Jupyter Notebook to a PDF without showing code cells.
    
    Args:
        notebook_path (str): Path to the notebook file, e.g., "data_analysis/report.ipynb"
    """
    try:
        subprocess.run([
            "jupyter", "nbconvert",
            "--to", "pdf",
            "--no-input",  # <--- Correct way to hide code inputs
            notebook_path
        ], check=True)
        
        notebook_filename = os.path.basename(notebook_path)
        print(f"✅ Successfully converted '{notebook_filename}' to PDF!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion: {e}")

# Example usage
export_notebook_to_pdf("data_analysis/jup_notebook/report.ipynb")
