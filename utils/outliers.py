import pandas as pd
def detect_outliers(df, num_cols):
    """
    Detect outlier rows using the IQR method.
    Parameters:
        df (DataFrame): Input data
        numeric_columns (list): List of numerical columns to check
    Returns:
        dict: {column_name: outlier_rows_dataframe}
    """
    outlier_dict = {}
    for col in num_cols:
        if col not in df.columns:
            continue
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR 
        outliers = df[(df[col] < lower_fence) | (df[col] > upper_fence)]
        outlier_dict[col] = outliers

    return outlier_dict


def count_outliers(df, numeric_columns=None):
    outlier_counts = {}
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    #df[col] = pd.to_numeric(df[col], errors='coerce')  # converts non-numeric to NaN
    for col in numeric_columns:
        col_data = pd.to_numeric(df[col], errors='coerce')
        if col_data.dropna().empty: 
            continue
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR
        outlier_count = df[(df[col] < lower_fence) | (df[col] > upper_fence)].shape[0]
        outlier_counts[col] = outlier_count
    return outlier_counts