import os
import csv
from typing import Union

def FileValidation(file_path: str) -> bool:
    """
    Validate that a file is a properly formatted CSV file without using chardet.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        bool: True if file is valid CSV, False otherwise
    """
    # 1. Basic file checks
    if not isinstance(file_path, str):
        return False
        
    if not file_path.lower().endswith('.csv'):
        return False
        
    if not os.path.exists(file_path):
        return False
        
    if os.path.getsize(file_path) == 0:
        return False

    # 2. Content validation with multiple encoding attempts
    encodings_to_try = ['utf-8', 'latin-1', 'ascii']  # Common CSV encodings
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Try reading first few lines to validate
                lines = []
                for _ in range(5):  # Check up to 5 lines
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
                
                if not lines:
                    return False
                
                # Try parsing as CSV
                f.seek(0)
                try:
                    # First try with sniffer
                    sample = f.read(1024)
                    f.seek(0)
                    dialect = csv.Sniffer().sniff(sample)
                    f.seek(0)
                    reader = csv.reader(f, dialect)
                except csv.Error:
                    # Fallback to default CSV parsing
                    f.seek(0)
                    reader = csv.reader(f)
                
                # Must have at least header and one data row
                try:
                    header = next(reader)
                    if not header:
                        return False
                        
                    first_row = next(reader)
                    if not first_row:
                        return False
                        
                    # Check for binary data (null bytes)
                    if any('\x00' in field for field in first_row):
                        return False
                        
                    # Basic column consistency check
                    if len(first_row) != len(header):
                        return False
                        
                    return True
                    
                except StopIteration:
                    return False
                    
        except UnicodeDecodeError:
            continue  # Try next encoding
        except Exception as e:
            print(f"Validation error with encoding {encoding}: {str(e)}")
            return False
    
    # If all encodings failed
    return False
