import os
import csv

def FileValidation(file_path):
    """
    Validate if a file is a legitimate CSV file.
    
    Args:
        file_path (str): Path to the file to be validated
        
    Returns:
        bool: True if valid CSV, False otherwise
    """
    # Check file extension
    if not file_path.lower().endswith('.csv'):
        return False
    
    # Check if file exists
    if not os.path.exists(file_path):
        return False
    
    # Check if file is empty
    if os.path.getsize(file_path) == 0:
        return False
    
    # Try to read the file as CSV
    try:
        with open(file_path, 'r', newline='') as csvfile:
            # Try to read first few lines to validate CSV format
            reader = csv.reader(csvfile)
            header = next(reader)  # Read header
            if not header:  # Empty header
                return False
                
            # Try reading a few more rows
            for i, row in enumerate(reader):
                if i >= 10:  # Read up to 10 rows
                    break
    except Exception as e:
        # Any error reading the file means it's not a valid CSV
        return False
    
    return True
