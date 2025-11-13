import numpy as np
from typing import List, Dict, Tuple, Optional

class TableStructureAnalyzer:
    def __init__(self):
        """
        Initialize the table structure analyzer
        """
        self.row_threshold = 10  # pixel threshold for row detection
        self.col_threshold = 10  # pixel threshold for column detection
    
    def analyze_structure(self, ocr_results: List[Dict]) -> Dict:
        """
        Analyze the table structure from OCR results
        Args:
            ocr_results: List of dictionaries containing OCR results with bbox, text, and confidence
        Returns:
            Dict containing table structure with rows, columns, and cells
        """
        # Extract all bounding boxes
        bboxes = [result['bbox'] for result in ocr_results]
        texts = [result['text'] for result in ocr_results]
        
        # Identify rows based on y-coordinates
        y_coords = [bbox[0][1] for bbox in bboxes]  # Use top-left y-coordinate
        rows = self._cluster_coordinates(y_coords, self.row_threshold)
        
        # Identify columns based on x-coordinates
        x_coords = [bbox[0][0] for bbox in bboxes]  # Use top-left x-coordinate
        columns = self._cluster_coordinates(x_coords, self.col_threshold)
        
        # Create table structure
        table = {
            'rows': len(rows),
            'columns': len(columns),
            'cells': self._assign_cells(bboxes, texts, rows, columns)
        }
        
        return table
    
    def _cluster_coordinates(self, coords: List[float], threshold: int) -> List[List[int]]:
        """
        Cluster coordinates that are close together
        """
        coords = sorted(coords)
        clusters = []
        current_cluster = [coords[0]]
        
        for coord in coords[1:]:
            if coord - current_cluster[-1] <= threshold:
                current_cluster.append(coord)
            else:
                clusters.append(current_cluster)
                current_cluster = [coord]
        
        clusters.append(current_cluster)
        return clusters
    
    def _assign_cells(self, bboxes: List[List[List[int]]], texts: List[str],
                     rows: List[List[float]], columns: List[List[float]]) -> List[List[str]]:
        """
        Assign text to cells based on their position in rows and columns
        """
        # Initialize empty table
        table = [['' for _ in range(len(columns))] for _ in range(len(rows))]
        
        # Assign text to cells
        for bbox, text in zip(bboxes, texts):
            row_idx = self._find_cluster_index(bbox[0][1], rows)
            col_idx = self._find_cluster_index(bbox[0][0], columns)
            if row_idx is not None and col_idx is not None:
                table[row_idx][col_idx] = text
        
        return table
    
    def _find_cluster_index(self, value: float, clusters: List[List[float]]) -> Optional[int]:
        """
        Find which cluster a value belongs to
        Args:
            value: The coordinate value to find the cluster for
            clusters: List of coordinate clusters
        Returns:
            Index of the cluster containing the value, or None if not found
        """
        for i, cluster in enumerate(clusters):
            if min(cluster) <= value <= max(cluster):
                return i
        return None