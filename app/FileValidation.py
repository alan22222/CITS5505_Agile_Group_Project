import os
import csv

def FileValidation(file_path):
    """
    Validate if a file is a legitimate CSV file by checking both extension and content.
    
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
    
    try:
        # Try to read the file as CSV
        with open(file_path, 'r') as f:
            # Try to parse the first few lines
            reader = csv.reader(f)
            header = next(reader)  # Read header
            if not header:  # Empty file
                return False
                
            # Try to read a few more lines to check content
            for _ in range(5):  # Check up to 5 rows
                try:
                    next(reader)
                except StopIteration:
                    break
                except csv.Error:
                    return False
                    
        return True
    except (csv.Error, UnicodeDecodeError):
        return False
    except Exception:
        return False

if __name__ == "__main__":
    # Example usage
    file_path = "example.csv"  # Replace with your file path
    if FileValidation(file_path):
        print(f"{file_path} is a valid CSV file.")
    else:
        print(f"{file_path} is not a valid CSV file.")