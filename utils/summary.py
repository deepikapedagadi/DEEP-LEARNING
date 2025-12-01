import pandas as pd
def col_summary(df):
    summary = []
    for col in df.columns:
        summary.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "unique_val": df[col].nunique()
        })

    return summary

def missing_value_report(df):
    report = []
    total_rows = len(df)
    for col in df.columns:
        missing = df[col].isna().sum()
        percent = round((missing / total_rows) * 100, 2)
        report.append({
            "column": col,
            "missing_values": missing,
            "percentage": percent
        })
    return report

def top_values_report(df, n=5):
    top_values = {}
    for col in df.columns:
        try:
            top_values[col] = df[col].value_counts().head(n).to_dict()
        except:
            top_values[col] = "Unable to compute"
    return top_values

def numeric_stats(df):
    stats = {}
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    for col in num_cols:
        stats[col] = {
            "mean": df[col].mean(),
            "median": df[col].median(),
            "std": df[col].std(),
            "min": df[col].min(),
            "max": df[col].max() 
        }
    return stats

def text_stats(df):
    text_columns = df.select_dtypes(include = ['object']).columns
    stats = {}
    for col in text_columns:
        try:
            lens = df[col].astype(str).str.len()
            word_counts = df[col].astype(str).apply(lambda x: len(str(x).split()))   
            stats[col] = {
                "avg_len": lens.mean(),
                "max_len": lens.max(),
                "avg_word_count": word_counts.mean(),
                "max_word_count": word_counts.max() 
            }
        except Exception as e:
            stats[col] = "Non-text columns"

    return stats