import pytest
import pandas as pd
import json
import os
from Backend.converter.data_converter import DataConverter

@pytest.fixture
def sample_table_data():
    return {
        'rows': 2,
        'columns': 2,
        'cells': [
            ['Header 1', 'Header 2'],
            ['Data 1', 'Data 2']
        ]
    }

def test_to_csv(tmp_path, sample_table_data):
    converter = DataConverter()
    output_path = os.path.join(tmp_path, "test")
    
    # Convert to CSV
    csv_path = converter.to_csv(sample_table_data, output_path)
    
    # Verify file exists
    assert os.path.exists(csv_path)
    
    # Verify content
    df = pd.read_csv(csv_path)
    assert df.shape == (2, 2)
    assert df.iloc[0, 0] == 'Header 1'

def test_to_excel(tmp_path, sample_table_data):
    converter = DataConverter()
    output_path = os.path.join(tmp_path, "test")
    
    # Convert to Excel
    excel_path = converter.to_excel(sample_table_data, output_path)
    
    # Verify file exists
    assert os.path.exists(excel_path)
    
    # Verify content
    df = pd.read_excel(excel_path)
    assert df.shape == (2, 2)
    assert df.iloc[0, 0] == 'Header 1'

def test_to_json(tmp_path, sample_table_data):
    converter = DataConverter()
    output_path = os.path.join(tmp_path, "test")
    
    # Convert to JSON
    json_path = converter.to_json(sample_table_data, output_path)
    
    # Verify file exists
    assert os.path.exists(json_path)
    
    # Verify content
    with open(json_path, 'r') as f:
        data = json.load(f)
    assert data == sample_table_data