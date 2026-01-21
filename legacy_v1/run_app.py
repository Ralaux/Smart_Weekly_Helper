import os
import sys
import tkinter as tk
from tkinter import filedialog
import extract_data
import generate_dashboard

def main():
    """
    Main application entry point.
    Orchestrates file selection, data extraction, and dashboard generation.
    """
    print("=== Smart Weekly Helper ===")
    
    # 0. Select Input File
    print("Veuillez sélectionner le fichier Excel source dans la fenêtre qui s'ouvre...")
    
    # Create hidden root window
    root = tk.Tk()
    root.withdraw() 
    
    file_path = filedialog.askopenfilename(
        title="Sélectionnez le fichier Excel source (Base Stats)",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    
    if not file_path:
        print("Aucun fichier sélectionné. Annulation.")
        input("Appuyez sur Entrée pour quitter...")
        return
        
    print(f"Fichier sélectionné : {file_path}")

    # 1. Extraction
    print("\n1. Extraction des données (Excel -> Excel formaté)...")
    try:
        extract_data.main(file_path)
    except Exception as e:
        print(f"ERREUR lors de l'extraction : {e}")
        input("Appuyez sur Entrée pour quitter...")
        return

    # 2. Dashboard Generation
    print("\n2. Génération du Dashboard (Excel -> HTML)...")
    try:
        generate_dashboard.main()
    except Exception as e:
        print(f"ERREUR lors de la génération du dashboard : {e}")
        input("Appuyez sur Entrée pour quitter...")
        return
    
    print("\nSUCCÈS ! Les fichiers ont été générés.")
    if getattr(sys, 'frozen', False):
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
