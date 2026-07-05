import pytest
import pandas as pd
from src.data_quality_checker import DataQualityChecker

def test_dq_checker():
    # Setup: Create dummy data
    data = {'amount': [100, 600000], 'gateway': ['Stripe', 'PayU'], 'timestamp': ['2026-01-01', 'invalid']}
    df = pd.DataFrame(data)
    config = {'amount': {'min': 1, 'max': 500000}, 'timestamp': {'format': 'datetime'}}
    
    checker = DataQualityChecker(config)
    report = checker.generate_report(df)
    
    # Assertions
    assert report[report['rule'] == 'range']['passed'].iloc[0] == False # 600k should fail
    assert report[report['rule'] == 'format']['passed'].iloc[0] == False # 'invalid' should fail