# Smart Weekly Helper

## Description
**Smart Weekly Helper** est un outil d'automatisation conçu pour simplifier le reporting hebdomadaire. 

À partir d'un fichier Excel d'export (Base Stats), l'application :
1. **Extrait et nettoie** les données projets.
2. **Calcule** automatiquement les KPIs pour les départements Commerce et Analyse (Projets entrants, Signatures, Ratios).
3. **Génère** deux fichiers de sortie :
   - 📊 `Donnees_Brutes_KPI.xlsx` : Un fichier Excel contenant tous les tableaux de résultats calculés.
   - 📈 `dashboard_kpi.html` : Un tableau de bord interactif et visuel (graphiques Plotly) consultable dans n'importe quel navigateur web.

## Installation

### Prérequis
- **Python 3.8** ou version supérieure.
- Un terminal de commande (PowerShell, CMD, ou Terminal).

### Installation des dépendances
1. Ouvrez votre terminal ou invite de commande.
2. Naviguez vers le dossier du projet.
3. Installez les librairies nécessaires via `pip` :

```bash
pip install -r requirements.txt
```

*Le fichier `requirements.txt` contient les bibliothèques `pandas`, `plotly`, `openpyxl`, etc.*

## Utilisation

### Lancement rapide
La méthode la plus simple est d'utiliser le script principal qui orchestre tout le processus :

1. Lancez le script :
   ```bash
   python run_app.py
   ```
2. Une fenêtre de dialogue s'ouvre. **Sélectionnez votre fichier Excel source** (ex: `Fichier sivi Stats cce Smart.xlsx`).
3. Laissez l'outil travailler. La console affichera la progression.
4. Une fois terminé ("SUCCÈS !"), vous trouverez les fichiers générés dans le dossier du projet.

### Fichiers Générés
- **`Donnees_Brutes_KPI.xlsx`** : Utilisez ce fichier pour vos analyses chiffrées précises ou pour copier-coller les tableaux.
- **`dashboard_kpi.html`** : Double-cliquez pour ouvrir le rapport visuel dans Chrome, Edge ou Firefox.

## Développement & Maintenance

Le code a été structuré pour être maintenable et respecte les standards PEP 8.

### Structure du projet
- `run_app.py` : Point d'entrée principal (GUI de sélection de fichier).
- `extract_data.py` : Logique d'extraction des données, calcul via `kpi_calculations`, et export Excel.
- `generate_dashboard.py` : Création des graphiques Plotly et génération du HTML.
- `kpi_calculations.py` : Cœur logique contenant les règles de filtrage et de calcul des dates.
- `tests/` : Dossier contenant les tests unitaires.

### Tests Unitaires
Pour vérifier que les calculs sont toujours corrects après une modification, exécutez la suite de tests :

```bash
python -m unittest discover tests
```
*Tous les tests doivent afficher "OK".*
