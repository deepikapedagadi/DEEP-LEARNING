import seaborn as sns
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ---- Import your utils ----
from utils.file_loader import load_csv, get_file_info
from utils.summary import col_summary, missing_value_report, top_values_report, numeric_stats, text_stats
from utils.correlation import extract_numeric_duration, compute_correlation, find_strong_correlations
from utils.outliers import detect_outliers, count_outliers
from utils.visualizations import plot_hist, plot_bar, plot_genre_count, plot_corr_hm, plot_box
from utils.exporter import save_json_report, save_html_report, save_pdf_report

#streamlit page config
st.set_page_config(
    page_title="AI Data Analyzer — Netflix", 
    layout="wide", 
    initial_sidebar_state="expanded"
    )

# ---- Helpers and caching ----
@st.cache_data
def load_data_cached(uploaded_file_bytes, path_fallback=None):
    """
    If user uploads a file, use that. Otherwise, attempt to load fallback path.
    Returns dataframe or None.
    """
    if uploaded_file_bytes is not None:
        # uploaded_file_bytes is a BytesIO or UploadedFile
        try:
            df = pd.read_csv(uploaded_file_bytes)
            return df
        except Exception as e:
            st.error(f"Error reading uploaded CSV: {e}")
            return None
    elif path_fallback:
        return load_csv(path_fallback)
    return None

def close_and_show(fig):
    """Display figure in Streamlit and close to avoid overlaps."""
    st.pyplot(fig)
    plt.close(fig)

def save_chart_and_display(fig, output_path):
    """Save a matplotlib/seaborn fig to output_path and display in Streamlit"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    st.image(output_path, use_column_width=True)

# ---- Sidebar ----
st.sidebar.title("AI Data Analyzer")
st.sidebar.markdown("Upload a CSV or use the sample Netflix dataset.")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample `netflix_titles.csv` (sample_data/)", value=True)

# Visualization options
st.sidebar.markdown("---")
st.sidebar.subheader("Plot options")
plot_release_hist = st.sidebar.checkbox("Show release year histogram", value=True)
plot_type_bar = st.sidebar.checkbox("Show Movie vs TV bar", value=True)
plot_rating_bar = st.sidebar.checkbox("Show rating distribution", value=True)
plot_genres = st.sidebar.checkbox("Show top genres", value=True)
plot_corr = st.sidebar.checkbox("Show correlation heatmap (numeric)", value=True)
plot_box = st.sidebar.checkbox("Show boxplot for durations", value=True)

# Export options
st.sidebar.markdown("---")
st.sidebar.subheader("Export")
export_json = st.sidebar.button("Export JSON report")
export_html = st.sidebar.button("Export HTML report")
export_pdf = st.sidebar.button("Export PDF report")

st.title(" AI Data Analyzer — Netflix (Streamlit)")

# ---- Load data ----
if uploaded_file is not None:
    df = load_data_cached(uploaded_file)
elif use_sample:
    sample_path = "sample_data/netflix_titles.csv"
    df = load_data_cached(None, path_fallback=sample_path)
else:
    st.info("Please upload a CSV or check 'Use sample' to load the example dataset.")
    st.stop()

# ---- Show basic file info ----
st.header("Dataset Overview")
info = get_file_info(df, uploaded_file.name if uploaded_file else sample_path)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", info["rows"])
col2.metric("Columns", info["columns"])
col3.metric("File size (MB)", f"{info['file_size_mb']}")
col4.metric("Memory (MB)", f"{info['memory_usage_mb']}")

# ---- Quick dataframe preview and download ----
with st.expander("Preview data (first 10 rows)"):
    st.dataframe(df.head(10))

# allow download of the loaded CSV (raw)
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV (loaded)", data=csv_bytes, file_name="loaded_dataset.csv", mime="text/csv")

# ---- Column summary & missing values ----
st.header("Column Summary & Missing Values")
col_summary_list = col_summary(df)
missing = missing_value_report(df)
numeric_statistics = numeric_stats(df)
top_vals = top_values_report(df)
text_statistics = text_stats(df)
missing = missing_value_report(df)
missing_df = pd.DataFrame(missing)
if "missing_values" in missing_df.columns:
    missing_df = missing_df.rename(columns={"missing_values": "missing_count", "percentage": "missing_percent"})

# Show column summary table
st.subheader("Column Summary")
st.table(pd.DataFrame(col_summary_list))

# Missing value table
st.subheader("Missing Values")
st.dataframe(missing_df.sort_values("missing_percent", ascending=False).reset_index(drop=True))

# ---- Parse duration (safe) and add numeric duration column ----
st.header("Duration Parsing & Numeric Columns")
df = extract_numeric_duration(df)  # function should add duration_num or duration_in_minutes
# Normalize to consistent column name expected downstream
if "duration_num" in df.columns and "duration_in_minutes" not in df.columns:
    df["duration_in_minutes"] = df["duration_num"]

st.write("Numeric columns detected:")
st.write(list(df.select_dtypes(include=["int64", "float64"]).columns))

# ---- Correlations & Outliers ----
st.header("Correlations & Outliers")
numeric_cols = [col for col in ["release_year", "duration_in_minutes"] if col in df.columns]
corr = None
if len(numeric_cols) >= 2:
    corr = compute_correlation(df[numeric_cols])
    strong_corre = find_strong_correlations(corr)
    if plot_corr:
        st.subheader("Correlation Matrix")
        fig, ax = plt.subplots(figsize=(6, 4))
        #import seaborn as sns
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
else:
    st.info("Not enough numeric columns for correlation (need at least 2).")

# Outliers
outlier_counts = count_outliers(df, numeric_cols)
st.subheader("Outlier Counts (IQR method)")
st.json(outlier_counts)

# ---- Visualizations ----
st.header("Visualizations")
charts_dir = "outputs/charts"
os.makedirs(charts_dir, exist_ok=True)

# Release year histogram
if "release_year" in df.columns and plot_release_hist:
    st.subheader("Release Year Distribution")
    fig, ax = plt.subplots(figsize=(8, 3.5))
    #import seaborn as sns
    sns.histplot(df["release_year"].dropna(), kde=True, ax=ax)
    ax.set_title("Release Year Histogram")
    st.pyplot(fig)
    fig.savefig(os.path.join(charts_dir, "release_year_hist.png"), bbox_inches="tight")

# Movie vs TV
if "type" in df.columns and plot_type_bar:
    st.subheader("Movie vs TV Show")
    fig, ax = plt.subplots(figsize=(6, 3))
    df["type"].value_counts().plot(kind="bar", ax=ax)
    ax.set_ylabel("Count")
    st.pyplot(fig)
    fig.savefig(os.path.join(charts_dir, "type_bar.png"), bbox_inches="tight")

# Rating distribution
if "rating" in df.columns and plot_rating_bar:
    st.subheader("Ratings Distribution")
    fig, ax = plt.subplots(figsize=(8, 3))
    df["rating"].value_counts().plot(kind="bar", ax=ax)
    st.pyplot(fig)
    fig.savefig(os.path.join(charts_dir, "rating_bar.png"), bbox_inches="tight")

# Top genres
if "listed_in" in df.columns and plot_genres:
    st.subheader("Top Genres")
    genre_series = df["listed_in"].dropna().str.split(", ").explode()
    top_genres = genre_series.value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    #import seaborn as sns
    sns.barplot(x=top_genres.values, y=top_genres.index, ax=ax)
    ax.set_xlabel("Count")
    ax.set_ylabel("Genre")
    st.pyplot(fig)
    fig.savefig(os.path.join(charts_dir, "top_genres.png"), bbox_inches="tight")

# Boxplot for duration
if "duration_in_minutes" in df.columns and plot_box:
    st.subheader("Duration Boxplot")
    fig, ax = plt.subplots(figsize=(6, 3))
    #import seaborn as sns
    sns.boxplot(x=df["duration_in_minutes"].dropna(), ax=ax)
    ax.set_xlabel("Duration (minutes)")
    st.pyplot(fig)
    fig.savefig(os.path.join(charts_dir, "duration_box.png"), bbox_inches="tight")

# ---- Auto-generated insights (rule-based) ----
st.header("Auto-generated Insights")
def generate_insights_ui(df, missing_df, corr_matrix, outlier_counts):
    insights = []

    # type distribution
    if "type" in df.columns:
        type_counts = df["type"].value_counts()
        top_type = type_counts.idxmax()
        pct = round(type_counts.max() / len(df) * 100, 1)
        insights.append(f"{top_type} dominates the dataset with {pct}% share.")

    # release year
    if "release_year" in df.columns:
        min_y, max_y = int(df["release_year"].min()), int(df["release_year"].max())
        mean_y = int(df["release_year"].mean())
        insights.append(f"Release years range from {min_y} to {max_y}, average around {mean_y}.")
        df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
        recent_count = len(df[df["release_year"] >= 2010])
        if recent_count / len(df) > 0.6:
            insights.append("Majority of content is from 2010–2020.")
    # most common rating
    if "rating" in df.columns:
        insights.append(f"Most common rating: {df['rating'].mode()[0]}")

    # top genre
    if "listed_in" in df.columns:
        genre_series = df["listed_in"].dropna().str.split(", ").explode()
        if not genre_series.empty:
            insights.append(f"Top genre: {genre_series.mode()[0]}")

    # missing
    missing_df["missing_percent"] = pd.to_numeric(missing_df["missing_percent"], errors="coerce")
    high_missing = missing_df[missing_df["missing_percent"] > 40]
    if not high_missing.empty:
        insights.append("Columns with >40% missing values: " + ", ".join(high_missing["column"].tolist()))
        # highest missing
        top_missing_row = missing_df.sort_values("missing_percent", ascending=False).iloc[0]
        insights.append(f"Highest missing column: {top_missing_row['column']} ({top_missing_row['missing_percent']}%)")

    # correlations
    if corr_matrix is not None:
        strong = find_strong_correlations(corr_matrix, threshold=0.7)
        if strong:
            for s in strong:
                insights.append(f"Strong correlation: {s['column_1']} vs {s['column_2']} (corr={s['correlation']})")
        else:
            insights.append("No strong numeric correlations detected.")

    # outliers
    for k, v in outlier_counts.items():
        try:
            v = int(v)
        except:
            v = 0
        if v > 0:
            insights.append(f"{k} contains {v} outliers (IQR).")
    return insights

insights_list = generate_insights_ui(df, missing_df, corr, outlier_counts)
for i, it in enumerate(insights_list, 1):
    st.write(f"{i}. {it}")

# ---- Exports and Downloads ----
st.header("Save & Export")

# Prepare report data structure
report_data = {
    "summary": col_summary,
    "missing": missing_df.to_dict(orient="records"),
    "numeric_stats": numeric_statistics,
    "top_values": top_vals,
    "outlier_counts": outlier_counts,
    "insights": insights_list
}

# JSON export
json_bytes = None
if export_json:
    save_json_report(report_data, output_path="outputs/reports/report.json")
    with open("outputs/reports/report.json", "rb") as f:
        json_bytes = f.read()
    st.success("JSON report created.")
    st.download_button("Download JSON report", data=json_bytes, file_name="report.json", mime="application/json")

# HTML export
if export_html:
    save_html_report(df, missing_df, outlier_counts, report_data.get("top_values"), insights_list, output_path="outputs/reports/report.html")
    with open("outputs/reports/report.html", "rb") as f:
        html_bytes = f.read()
    st.success("HTML report created.")
    st.download_button("Download HTML report", data=html_bytes, file_name="report.html", mime="text/html")

# PDF export
if export_pdf:
    save_pdf_report(insights_list, output_path="outputs/reports/report.pdf")
    with open("outputs/reports/report.pdf", "rb") as f:
        pdf_bytes = f.read()
    st.success("PDF report created.")
    st.download_button("Download PDF report", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")

st.markdown("---")
st.caption("Built with ❤️ — AI Data Analyzer")
