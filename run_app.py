import extract_data
import generate_dashboard
import os
import sys

def main():
    print("=== Smart Weekly Helper ===")
    print("1. Extraction des données (Excel -> Excel formaté)...")
    try:
        extract_data.main()
    except Exception as e:
        print(f"ERREUR lors de l'extraction : {e}")
        input("Appuyez sur Entrée pour quitter...")
        return

    print("\n2. Génération du Dashboard (Excel -> HTML)...")
    try:
        generate_dashboard.main()
    except Exception as e:
        print(f"ERREUR lors de la génération du dashboard : {e}")
        input("Appuyez sur Entrée pour quitter...")
        return
    
    print("\nSUCCÈS ! Les fichiers ont été générés.")
    if getattr(sys, 'frozen', False):
        # Pause only if frozen (exe), so window doesn't close immediately
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
