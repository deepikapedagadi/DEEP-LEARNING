import os 
import pandas as pd
#import modules
from utils.file_loader import load_csv, get_file_info
from utils.summary import col_summary, missing_value_report, top_values_report, numeric_stats, text_stats
from utils.correlation import extract_numeric_duration, compute_correlation, find_strong_correlations
from utils.outliers import detect_outliers, count_outliers
from utils.visualizations import plot_hist, plot_bar, plot_genre_count, plot_corr_hm, plot_box
from utils.exporter import save_json_report, save_html_report, save_pdf_report

#ensure o/p folders exist
os.makedirs("outputs/reports", exist_ok=True)
os.makedirs("outputs/charts", exist_ok=True)
def generate_insights(df, missing, strong_corr, outlier_counts):
    insights = []
    # -------------------------------
    # 1. CONTENT TYPE DISTRIBUTION
    # -------------------------------
    if "type" in df.columns:
        type_counts = df["type"].value_counts()
        top_type = type_counts.idxmax()
        percentage = round(type_counts.max() / len(df) * 100, 1)
        insights.append(f"• **{top_type}** dominates the dataset with **{percentage}%** share.")
    # -------------------------------
    # 2. RELEASE YEAR TRENDS
    # -------------------------------
    if "release_year" in df.columns:
        year_mean = int(df["release_year"].mean())
        min_year = int(df["release_year"].min())
        max_year = int(df["release_year"].max())
        if max_year - min_year < 20:
            insights.append("• Content release years are concentrated within last 20 years.")
        else:
            insights.append(f"• Release years range from **{min_year} to {max_year}**, average around **{year_mean}**.")
        # Trend: recent content dominant?
        recent = df[df["release_year"] >= 2010]
        if len(recent) / len(df) > 0.6:
            insights.append("• Majority of Netflix content is from **2010–2020**.")
    # -------------------------------
    # 3. MOST COMMON RATING
    # -------------------------------
    if "rating" in df.columns:
        top_rating = df["rating"].mode()[0]
        insights.append(f"• **{top_rating}** is the most common content rating on Netflix.")
    # -------------------------------
    # 4. GENRE / CATEGORY INSIGHT
    # -------------------------------
    if "listed_in" in df.columns:
        genre_series = df["listed_in"].str.split(", ").explode()
        top_genre = genre_series.mode()[0]
        insights.append(f"• **{top_genre}** appears as the most popular genre/category.")
    # -------------------------------
    # 5. MISSING VALUE INSIGHTS
    # -------------------------------
    if not missing.empty:
        most_missing = missing.loc[missing["missing_values"].idxmax(), 'column']
        missing_count = missing["missing_count"].max()
        insights.append(f"• **{most_missing}** has the highest missing values ({missing_count} records missing).")
    # If many columns missing
        high_missing = missing[missing["missing_percent"] > 40]
        if len(high_missing) > 0:
            cols = ", ".join(high_missing.index)
            insights.append(f"• Columns with very high missing %: **{cols}**.")
    # -------------------------------
    # 6. STRONG CORRELATIONS
    # -------------------------------
    if strong_corr:
        insights.append("• Strong correlations exist between:")
        for item in strong_corr:
            #col1, col2, corr_value = item
            insights.append(f"    → **{item['col1']}** and **{item['col2']}** (corr = {item['correlation']})")
    else:
        insights.append("• No strong numeric correlations detected.")
    # -------------------------------
    # 7. OUTLIER SUMMARY
    # -------------------------------
    for col, count in outlier_counts.items():
        if count > 0:
            insights.append(f"• **{col}** contains {count} outliers detected using IQR method.")
    return insights 
  

#main
def main():
    #1. ask for csv
    csv_path = input("Enter csv path (or enter to auto-load netflix dataset): ")
    if csv_path.strip() == "":
        csv_path = "netflix_titles.csv"
        print("Using default")
    #2. load csv
    df = load_csv(csv_path)
    if df is None:
        print("failed to load")
        return
    print("\n file loaded successfully \n")
    #3. print file info
    info = get_file_info(df, csv_path)
    print("Rows:", info["rows"])
    print("Columns:", info["columns"])
    print("Memory:", info["memory"])
    print("File size:", info["file_size_mb"])
    #4. run basic eda
    print("\n Generating col summary \n")
    summary = col_summary(df)
    print("\n Missing values \n")
    missing = pd.DataFrame(missing_value_report(df))
    print("\n Numeric statistics...")
    num_stats = numeric_stats(df)
    print("\n Top values per column...")
    top_vals = top_values_report(df)
    print("\n Text Statistics..")
    text_stats = text_stats(df)
    #5. Extract numeric duration
    print("\n Processing duration column...")
    df = extract_numeric_duration(df)
    if "duration_num" in df.columns:
        df.rename(columns={"duration_num": "duration_in_minutes"}, inplace=True)
    #6. Correlations
    print("\n Computing correlations...")
    corr = compute_correlation(df)
    strong_corr = find_strong_correlations(corr, threshold=0.7) if corr is not None else[]
    #7. Outlier detection
    numeric_cols = ["release_year", "duration_in_minutes"]
    df_outliers = detect_outliers(df, numeric_cols)
    outlier_counts = count_outliers(df, numeric_cols)
    #8. Generate visualizations
    print("\n Creating visualizations...\n")
    plot_hist(df, "release_year", "outputs/charts/release_year_hist.png")
    plot_bar(df, "type", "outputs/charts/type_bar.png")
    plot_bar(df, "rating", "outputs/charts/rating_bar.png")
    plot_genre_count(df, "outputs/charts/top_genres.png")
    if corr is not None:
        plot_corr_hm(corr, "outputs/charts/correlation_heatmap.png")
    plot_box(df, "duration_in_minutes", "outputs/charts/duration_box.png")
    #9. save all reports
    print("\n Saving reports...")
    pd.DataFrame(summary).to_csv("outputs/reports/column_summary.csv")
    missing.to_csv("outputs/reports/missing_values.csv")
    pd.DataFrame(num_stats).to_csv("outputs/reports/numeric_stats.csv")
    pd.DataFrame(top_vals).to_csv("outputs/reports/top_values.csv")
    if corr is not None:    
        corr.to_csv("outputs/reports/correlation_matrix.csv")
    pd.DataFrame(strong_corr).to_csv("outputs/reports/strong_correlations.csv")
    pd.DataFrame(outlier_counts, index=[0]).to_csv("outputs/reports/outlier_counts.csv")
    print(" Analysis Completed Successfully!")

    # 10 Auto Insights
    print("\n Generating insight summary...\n")
    insights = generate_insights(df, missing, strong_corr, df_outliers, outlier_counts)
    print(" AUTO-GENERATED INSIGHTS:\n")
    for point in insights:
        print(point)
    # Save insights
    with open("outputs/reports/insights.txt", "w", encoding="utf-8") as f:
        for point in insights:
            f.write(point + "\n")

    report_data = {
        "summary": summary,
        "missing": missing.to_dict(),
        "outliers": outlier_counts,
        "strong_correlations": strong_corr,
        "insights": insights
    }

    save_json_report(report_data)
    save_html_report(df, missing, outlier_counts, strong_corr, insights)
    save_pdf_report(insights)

# Run script
if __name__ == "__main__":
    main()


"""🧠 Explanation of Flow
✔ Step 1 — User Input

User gives CSV path OR Netflix dataset is auto-loaded.

✔ Step 2 — Load CSV

Uses your file_loader.py.

✔ Step 3 — Show basic metadata

Rows, columns, memory, file size.

✔ Step 4 — Generate full EDA

Column summary

Missing values

Numeric stats

Top values

Text stats

✔ Step 5 — Parse durations

"90 min" → 90
"3 Seasons" → 3

✔ Step 6 — Correlations

Find strongest relationships.

✔ Step 7 — Outliers

Using IQR.

✔ Step 8 — Visualizations

All plots saved inside /outputs/charts/.

✔ Step 9 — Save reports

Everything exported inside /outputs/reports/.

✔ Step 10 — Print key insights

Shows a digest of findings."""

"""
from utils.exporter import save_json_report, save_html_report, save_pdf_report

report_data = {
    "summary": summary,
    "missing": missing.to_dict(),
    "outliers": outlier_counts,
    "strong_correlations": strong_corr,
    "insights": insights
}

save_json_report(report_data)
save_html_report(df, missing, outlier_counts, strong_corr, insights)
save_pdf_report(insights)
"""