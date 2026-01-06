# KPI_Euklead:

## Introduction

All KPIs are calculated on the previous 24 months and aggregated monthly.

## KPIs:

### Analyse du protefeuille:

#### Commerce:

- Number of rows with:  
  "Type de projet" = "Commerce"
- Number of rows with:  
  "Type de projet" = "Commerce"  
  AND "Associé" = "AC" "FP" "PB" "DDL" or "CA"
- Number of rows with:  
  "Type de projet" = "Commerce"  
  AND "Associé" = "LP" "DP" "GP" "GB" or "PM"
- Number of rows with "Type de projet" = "Commerce" divided by 15

#### Analyse:

- Number of rows with:  
  "Type de projet" = "Analyse"
- Number of rows with:  
  "Type de projet" = "Analyse"  
  AND "Associé" = "PB" "DDL" or "CA"
- Number of rows with:  
  "Type de projet" = "Analyse"  
  AND "Associé" = "LP" or "GB"

### Analyse des signatures:

#### Commerce:

- Number of rows with:  
  "Type de projet" = "Commerce"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé")
- Number of rows with:  
  "Type de projet" = "Commerce"  
  AND "Associé" = "AC" "FP" "PB" "DDL" or "CA"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé")
- Number of rows with:  
  "Type de projet" = "Commerce"  
  AND "Associé" = "LP" "DP" "GP" "GB" or "PM"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé")
- (Number of rows with:  
  "Type de projet" = "Commerce"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé"))  
  Divided by:  
  (Number of rows with:
  "Type de projet" = "Commerce")
- (Number of rows with:  
  "Type de projet" = "Commerce"  
  AND "Associé" = "AC" "FP" "PB" "DDL" or "CA"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé"))  
  Divided by:  
  (Number of rows with:
  "Type de projet" = "Commerce"  
  AND "Associé" = "AC" "FP" "PB" "DDL" or "CA")
- (Number of rows with:  
  "Type de projet" = "Commerce"  
  AND "Associé" = "LP" "DP" "GP" "GB" or "PM"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé"))  
  Divided by:  
  (Number of rows with:
  "Type de projet" = "Commerce"  
  AND "Associé" = "LP" "DP" "GP" "GB" or "PM")

#### Analyse:

- Number of rows with:  
  "Type de projet" = "Analyse"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé")
- Number of rows with:  
  "Type de projet" = "Analyse"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé")  
  AND "Catégorie" = "Télécoms" "Energie" "Transports" "Copieurs" "Facilities" "Nettoyage / Gardiennage" "Déchets"
- Number of rows with:  
  "Type de projet" = "Analyse"  
  AND ("Etat 1" = "Signé" OR "Etat 2" = "Signé" OR "Etat 3" = "Signé" OR "Etat 4" = "Signé")  
  AND "Catégorie" = "QOFI / Location Engins / EPI" "Matériel IT"

### Tables

For each table, there is one column for each month of the last 24 months and one row for each one of the 9 categories (Smart and Smart +)

- Table 1: Commerce
- Table 2: Analyse
- Table 3: Analyse Signé
