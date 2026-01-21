# Roadmap V2 : "Pure Frontend" (Angular + TypeScript)

## Objectif
Créer une application web **100% Client-Side**.
L'utilisateur accède à une URL, charge son fichier, et tout le traitement se fait dans son navigateur via JavaScript/TypeScript.
**Aucun backend, aucune installation, confidentialité totale (les données restent dans l'onglet du navigateur).**

## Architecture "Serverless Client-Side"
1.  **Hébergement** : Site statique (GitHub Pages, Vercel, Netlify, ou simple fichier HTML/JS).
2.  **Excel Parsing** : Utilisation de la librairie `SheetJS` (`xlsx`) pour lire le fichier Excel directement en JS.
3.  **Logique Métier** : Porting du code Python (`kpi_calculations.py`) vers TypeScript.
4.  **Visualisation** : Utilisation de `Plotly.js` (version JS de la librairie Python utilisée en V1) pour générer les graphiques.

## Stack Technique
-   **Frontend Framework** : **Angular** (TypeScript).
-   **Excel Library** : **xlsx** (SheetJS).
-   **Charting** : **Plotly.js**.
-   **Styling** : **Tailwind CSS** (ou Angular Material).

## Étapes de Développement

### 1. Initialisation du Projet
-   Génération d'un nouveau workspace Angular.
-   Installation des dépendances : `npm install xlsx plotly.js-dist-min`.

### 2. Porting de la Logique Métier (Python -> TypeScript)
C'est la partie la plus critique. Il faut réécrire les algorithmes de filtrage et de calcul.
-   **`KpiService`** :
    -   Implémenter `loadData(file)` : Lecture du binaire Excel.
    -   Implémenter `filterData(...)` : Équivalent de `filter_data` Python.
    -   Implémenter `calculateKpis(...)` : Calcul des sommes par mois.
    -   Gestion des Dates : Utiliser `date-fns` ou l'objet `Date` natif pour gérer la fenêtre de 24 mois.

### 3. Développement des Composants
-   **`UploadComponent`** : Zone de drag & drop. Lit le fichier et le passe au service.
-   **`DashboardComponent`** :
    -   Reçoit les données calculées.
    -   Contient les éléments DOM pour Plotly (`<div id="chart1"></div>`).
    -   Appelle `Plotly.newPlot(...)` avec les configs (couleurs, layout) adaptées de la V1.
-   **`DemoMode`** : Un service générant des données aléatoires pour remplir le Dashboard sans fichier.

### 4. Styling & UX
-   Intégration d'un design propre et réactif.
-   Feedback utilisateur lors du chargement/calcul (Spinner).

## Avantages
-   **Zéro installation** pour le client.
-   **Coût d'hébergement nul** (Static hosting).
-   **Confidentialité garantie**.

---
**Status** : En attente de validation.
