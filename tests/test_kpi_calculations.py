import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Ensure we can import modules from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import kpi_calculations

class TestKPICalculations(unittest.TestCase):
    
    def setUp(self):
        # Create a mock DataFrame for testing
        # Reference Dates:
        self.today = datetime.now()
        self.date_recent = self.today - timedelta(days=30)      # 1 month ago
        self.date_old = self.today - timedelta(days=400)        # > 1 year ago (still in 24m)
        self.date_ancient = self.today - timedelta(days=800)    # > 2 years ago (OUT of 24m)
        
        data = {
            "Type de projet": ["Commerce", "Commerce", "Analyse", "Commerce", "Analyse", "Commerce"],
            "Associé": ["AC", "LP", "PB", "Unknown", "GB", "AC"],
            "Date d'entrée": [
                self.date_recent, 
                self.date_recent, 
                self.date_old, 
                self.date_ancient, 
                self.date_recent, 
                self.date_recent
            ],
            "Etat 1": ["En cours", "Signé", "Perdu", "Signé", "En cours", "Signé"],
            "Etat 2": [None, None, None, None, "Signé", None],
            "Date de signature": [
                None, 
                self.date_recent, # Signed recently
                None, 
                self.date_ancient, # Signed long ago (Entry also long ago)
                self.date_recent, # Signed recently
                self.date_ancient # Signed long ago (but Entry was recent) -> Rare case to test logic
            ]
        }
        self.df = pd.DataFrame(data)

    def test_filter_project_type(self):
        """Test basic filtering by project type"""
        filtered = kpi_calculations.filter_data(self.df, "Commerce")
        self.assertEqual(len(filtered), 4) # 4 Commerce rows
        self.assertTrue(all(filtered['Type de projet'] == 'Commerce'))

        filtered_ana = kpi_calculations.filter_data(self.df, "Analyse")
        self.assertEqual(len(filtered_ana), 2)
        
    def test_filter_associates(self):
        """Test filtering by associates list (case insensitive)"""
        associates = ["ac", "pb"] # Lower case input
        filtered = kpi_calculations.filter_data(self.df, "Commerce", associates=associates)
        # Commerce Project + Associate AC or PB. 
        # Rows: 0 (Commerce, AC), 2 (Analyse, PB - Should match associate but filtered by Proj Type if call is consistent)
        # Wait, filter_data filters by Proj Type AND Associate.
        # Row 0: Comm, AC -> Match
        # Row 5: Comm, AC -> Match
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(filtered['Associé'] == 'AC'))

    def test_filter_signed(self):
        """Test filtering by checking is_signed=True against Etat columns"""
        # "Signé" matches in Etat 1 or Etat 2
        filtered = kpi_calculations.filter_data(self.df, "Commerce", is_signed=True)
        # Commerce rows that are signed:
        # Row 1: Commerce, Etat1=Signé
        # Row 3: Commerce, Etat1=Signé
        # Row 5: Commerce, Etat1=Signé
        self.assertEqual(len(filtered), 3)

    def test_count_projects_entry_date_24m(self):
        """
        Verify counts based on Entry Date for standard requests (is_signed=False).
        Should exclude dates older than 24 months.
        """
        # Row 3 is ancient (800 days ago)
        # Others are < 24m (30 or 400 days)
        counts = kpi_calculations.count_projects(self.df, "Commerce")
        total_count = counts.sum()
        
        # Total Commerce rows = 4. 
        # Row 3 is ancient -> Excluded.
        # Expected = 3.
        self.assertEqual(total_count, 3)

    def test_count_projects_signed_date_24m(self):
        """
        Verify counts based on Signature Date when is_signed=True.
        Critical test for recent fix.
        """
        # Commerce Signed rows: 1, 3, 5
        # Row 1: Sign Date = Recent -> Include
        # Row 3: Sign Date = Ancient -> Exclude
        # Row 5: Sign Date = Ancient -> Exclude
        
        counts = kpi_calculations.count_projects(self.df, "Commerce", is_signed=True)
        total_count = counts.sum()
        
        self.assertEqual(total_count, 1)

    def test_count_projects_analyse_signed_mixed_states(self):
        """Test Analyse Signed where 'Signé' might be in Etat 2"""
        # Row 4: Analyse, Etat 2 = Signé, Date Sign = Recent
        # Row 2: Analyse, Not signed
        counts = kpi_calculations.count_projects(self.df, "Analyse", is_signed=True)
        self.assertEqual(counts.sum(), 1)

if __name__ == '__main__':
    unittest.main()
