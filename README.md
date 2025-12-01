✅ Project Idea: AI Data Analyzer
You will build a Python tool (CLI or Jupyter Notebook or small Streamlit app) that a user can give any CSV, and the tool automatically generates EDA insights.Think of it like a mini version of Pandas-Profiling.

🔍 Core Features (Your Minimum Viable Product)
1. Upload/Read CSV
Tool should accept any CSV file path.
Load via Pandas.
Show basic file info: number of rows, columns, file size.

2. Basic Summary
For each column:
Data type (int, float, string, datetime), Unique values
Missing values count, Mean/median/mode (for numeric)
Top 5 most frequent values (for categorical)

3. Missing Values Analysis
Show missing values per column
Optionally calculate missing percentage
Highlight columns with high missing values (e.g., >40%)

4. Correlation Insights
For numeric columns: Correlation matrix
Find:
Strong positive correlations (e.g., > 0.7) &  negative correlations (e.g., < -0.7)
This reveals relationships like:
“Price increases when Size increases” & “Age negatively correlates with Salary”

5. Basic Visualizations
Automatically generate:
Histogram for each numeric column, Bar chart for categorical columns
Correlation heatmap & Boxplot for outliers
6. Outlier Detection
Using IQR method:
Detect columns with many outliers
Show count of outliers per column

7. Insights Summary
Generate a short interpretation like:
“Dataset has 10% missing values across 3 columns.”
“Salary has strong correlation (0.82) with Experience.”

⭐ Optional Advanced Features (If you want to go further)
1. Auto Data Cleaning Recommendations
Suggest columns to drop & numeric imputation strategy & categorical filling strategy

2. AI-Powered Insights (Later)

Use an LLM to analyze the summary and write:
Insights in bullets 
Data quality issues & Potential models to build

3. Export Report
Save results as:
PDF, HTML, JSON

Dataset : netflix_titles.csv
structure :
AI-Data-Analyzer/
 ├── main.py
 ├── utils/
 │    ├── file_loader.py
 │    ├── summary.py
 │    ├── visualizations.py
 │    ├── correlation.py
 │    └── outliers.py
 ├── outputs/
 │    ├── charts/
 │    └── reports/
 └── sample_data/

