import sys
import os
import pandas as pd
import numpy as np

# This ensures Python finds the 'src' package when running this file directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import dq_config

class DataQualityChecker:
    def __init__(self, config):
        self.config = config

    def check_nulls(self, df):
        results = []
        for col, rules in self.config.items():
            if 'null_pct_max' in rules:
                null_pct = df[col].isnull().mean()
                passed = null_pct <= rules['null_pct_max']
                results.append({'column': col, 'rule': 'null_pct', 'passed': passed, 'severity': 'critical'})
        return results

    def check_ranges(self, df):
        results = []
        for col, rules in self.config.items():
            if 'min' in rules and 'max' in rules:
                passed = df[col].between(rules['min'], rules['max']).all()
                results.append({'column': col, 'rule': 'range', 'passed': passed, 'severity': 'critical'})
        return results

    def check_formats(self, df):
        results = []
        for col, rules in self.config.items():
            if rules.get('format') == 'datetime':
                passed = pd.to_datetime(df[col], errors='coerce').notnull().all()
                results.append({'column': col, 'rule': 'format', 'passed': passed, 'severity': 'warning'})
        return results

    def generate_report(self, df):
        all_results = self.check_nulls(df) + self.check_ranges(df) + self.check_formats(df)
        report = pd.DataFrame(all_results)
        return report.sort_values(by='severity')

# This block allows you to run a quick test by executing: python3 src/data_quality_checker.py
if __name__ == "__main__":
    data = {'amount': [100, 600000], 'gateway': ['Stripe', 'PayU'], 'timestamp': ['2026-01-01', 'invalid']}
    df = pd.DataFrame(data)
    checker = DataQualityChecker(dq_config)
    print(checker.generate_report(df))