import os 
import pandas as pd

def load_csv(path):
    """ Loads a CSV file and returns a pandas DataFrame.
    Handles file not found and incorrect format errors.  """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not path.lower().endswith(".csv"):
            raise ValueError(f"Only CSV files are supported.")
        
        df = pd.read_csv(path)
        return df
    
    except Exception as e:
        print(f"Error while loading CSV: {e}")
        return None
    

def get_file_info(df, path):
    """Returns basic metadata about the file: - Number of rows 
    - Number of columns - File size (in MB) - DataFrame memory usage """
    try:
        rows = df.shape[0]
        cols = df.shape[1]
        size_bytes = os.path.getsize(path)  #get file size
        size_mb = round(size_bytes / (1024 * 1024), 2)
        memory_df = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2) 
        info = {
            "rows": rows,
            "columns": cols,
            "file_size_mb": size_mb,
            "memory_usage_mb": memory_df
        }
        return info
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None

