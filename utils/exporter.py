import json
import os
def save_json_report(data, output_path="outputs/reports/report.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f" JSON report saved at: {output_path}")

def save_html_report(df, missing, outliers, strong_corr, insights,
                     output_path="outputs/reports/report.html"):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    html_content = f"""
    <html>
    <head>
        <title>Netflix EDA Report</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            h2 {{ color: #D81F26; }}
            table {{ border-collapse: collapse; width: 100%; }}
            table, th, td {{ border: 1px solid #ccc; padding: 8px; }}
            ul {{ line-height: 1.6; }}
        </style>
    </head>
    <body>
        <h1>📊 Netflix EDA Report</h1>

        <h2>1. Dataset Overview</h2>
        {df.head().to_html()}

        <h2>2. Missing Value Report</h2>
        {missing.to_html()}

        <h2>3. Outlier Counts</h2>
        <pre>{outliers}</pre>

        <h2>4. Strong Correlations</h2>
        <pre>{strong_corr}</pre>

        <h2>5. Insights</h2>
        <ul>
            {''.join(f'<li>{i}</li>' for i in insights)}
        </ul>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f" HTML report saved at: {output_path}")

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

def save_pdf_report(insights, output_path="outputs/reports/report.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Netflix EDA Report", styles['Title']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Insights Summary:", styles['Heading2']))
    story.append(Spacer(1, 10))

    for point in insights:
        story.append(Paragraph(f"- {point}", styles['BodyText']))
        story.append(Spacer(1, 5))

    doc.build(story)

    print(f"✅ PDF report saved at: {output_path}")


