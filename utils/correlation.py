import re
import pandas as pd
def extract_numeric_duration(df):
    if "duration" not in df.columns:
        print("no duration col found")
        return df
    def convert(value):
        try:
            value = str(value).lower()
            if "min" in value: #movies" 90 min
                num = re.findall(r"\d+", value)
                return int(num[0]) if num else None
            if "season" in value:  #tvshows 3seasons 1season
                num = re.findall(r"\d+", value)
                return int(num[0]) if num else None
        except Exception as e:
            return None
        return None
    df["duration_in_minutes"] = df["duration"].apply(convert)
    return df

def compute_correlation(df):
    num_df = df.select_dtypes(include=['int64', 'float64'])
    if num_df.empty:
        print("No num cols available for correlation")
        return None
    corr_matrix = num_df.corr()
    return corr_matrix

def find_strong_correlations(corr_matrix, threshold=0.7):
    strong_pairs = []
    if corr_matrix is None or corr_matrix.empty:
        return strong_pairs
    columns = corr_matrix.columns
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            value = corr_matrix.iloc[i, j]
            if pd.notna(value) and abs(value) >= threshold:
                strong_pairs.append({
                    "col_1": columns[i],
                    "col_2": columns[j],
                    "correlation": round(value, 3)
                })
    return strong_pairs
