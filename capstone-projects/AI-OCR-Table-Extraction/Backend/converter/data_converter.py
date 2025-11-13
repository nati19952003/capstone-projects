import pandas as pd
from typing import List, Dict
import json
import os

class DataConverter:
    @staticmethod
    def to_csv(table_data: Dict, output_path: str) -> str:
        """
        Convert table data to CSV format
        """
        # Write a generic header so pandas will read all rows as data
        df = pd.DataFrame(table_data['cells'])
        # Create generic column names if they don't exist
        cols = [f"col_{i}" for i in range(df.shape[1])]
        df.columns = cols
        csv_path = f"{output_path}.csv"
        df.to_csv(csv_path, index=False, header=True)
        return csv_path
    
    @staticmethod
    def to_excel(table_data: Dict, output_path: str) -> str:
        """
        Convert table data to Excel format
        """
        df = pd.DataFrame(table_data['cells'])
        cols = [f"col_{i}" for i in range(df.shape[1])]
        df.columns = cols
        excel_path = f"{output_path}.xlsx"
        df.to_excel(excel_path, index=False, header=True)
        return excel_path
    
    @staticmethod
    def to_json(table_data: Dict, output_path: str) -> str:
        """
        Convert table data to JSON format
        """
        json_path = f"{output_path}.json"
        with open(json_path, 'w') as f:
            json.dump(table_data, f)
        return json_path