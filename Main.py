import requests
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="Skin Clinic Campaign Analysis API")

# ---------------------------------------------------------
# Load and prepare data
# ---------------------------------------------------------
df = pd.read_csv("skin_clinic_campaign.csv")

# Convert Yes/No to 1/0
df['Response_to_Campaign'] = df['Response_to_Campaign'].map({"Yes": 1, "No": 0})

# Clean gender
df['Gender'] = df['Gender'].astype(str).str.strip().str.title()

# ---------------------------------------------------------
# Create product usage bins
# ---------------------------------------------------------
def categorize_usage(x):
    if x <= 4:
        return "1-4"
    elif 5 <= x <= 8:
        return "5-8"
    else:
        return ">8"

df['Product_Usage_Bin'] = df['Unique_Products_Purchased'].apply(categorize_usage)

# ---------------------------------------------------------
# Response model
# ---------------------------------------------------------
class SegmentResponse(BaseModel):
    segment: str
    N: int
    responders: int
    response_rate: float

# ---------------------------------------------------------
# Endpoint: Gender vs Campaign Response
# ---------------------------------------------------------
@app.get("/gender-response", response_model=list[SegmentResponse])
def gender_response():
    gender_rr = (
        df.groupby('Gender')
          .agg(
              N=('Gender', 'count'),
              Responders=('Response_to_Campaign', 'sum')
          )
    )
    gender_rr['RR'] = (gender_rr['Responders'] / gender_rr['N']) * 100

    results = []
    for gender, row in gender_rr.iterrows():
        results.append(
            SegmentResponse(
                segment=gender,
                N=int(row['N']),
                responders=int(row['Responders']),
                response_rate=float(row['RR'])
            )
        )
    return results

# ---------------------------------------------------------
# Endpoint: Product Usage vs Campaign Response
# ---------------------------------------------------------
@app.get("/product-usage-response", response_model=list[SegmentResponse])
def product_usage_response():
    usage_rr = (
        df.groupby('Product_Usage_Bin')
          .agg(
              N=('Product_Usage_Bin', 'count'),
              Responders=('Response_to_Campaign', 'sum')
          )
    )
    usage_rr['RR'] = (usage_rr['Responders'] / usage_rr['N']) * 100

    results = []
    for seg, row in usage_rr.iterrows():
        results.append(
            SegmentResponse(
                segment=seg,
                N=int(row['N']),
                responders=int(row['Responders']),
                response_rate=float(row['RR'])
            )
        )
    return results

# ---------------------------------------------------------
# Endpoint: Age Group vs Campaign Response
# ---------------------------------------------------------
@app.get("/agegroup-response", response_model=list[SegmentResponse])
def agegroup_response():
    age_rr = (
        df.groupby('AgeGroup')
          .agg(
              N=('AgeGroup', 'count'),
              Responders=('Response_to_Campaign', 'sum')
          )
    )
    age_rr['RR'] = (age_rr['Responders'] / age_rr['N']) * 100

    results = []
    for age, row in age_rr.iterrows():
        results.append(
            SegmentResponse(
                segment=age,
                N=int(row['N']),
                responders=int(row['Responders']),
                response_rate=float(row['RR'])
            )
        )
    return results

# ---------------------------------------------------------
# Endpoint: Purchase_Last_Quarter vs Campaign Response
# ---------------------------------------------------------
@app.get("/purchase-last-quarter-response", response_model=list[SegmentResponse])
def purchase_last_quarter_response():
    purchase_rr = (
        df.groupby('Purchase_Last_Quarter')
          .agg(
              N=('Purchase_Last_Quarter', 'count'),
              Responders=('Response_to_Campaign', 'sum')
          )
    )
    purchase_rr['RR'] = (purchase_rr['Responders'] / purchase_rr['N']) * 100

    results = []
    for seg, row in purchase_rr.iterrows():
        results.append(
            SegmentResponse(
                segment=seg,
                N=int(row['N']),
                responders=int(row['Responders']),
                response_rate=float(row['RR'])
            )
        )
    return results


@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    # Gender Analysis
    gender_rr = (
        df.groupby("Gender")
        .agg(
            N=("Gender", "count"),
            Responders=("Response_to_Campaign", "sum"),
        )
    )
    gender_rr["Response_Rate (%)"] = (
        gender_rr["Responders"] / gender_rr["N"] * 100
    ).round(2)
    gender_rr = gender_rr.reset_index()

    # Product Usage Analysis
    usage_rr = (
        df.groupby("Product_Usage_Bin")
        .agg(
            N=("Product_Usage_Bin", "count"),
            Responders=("Response_to_Campaign", "sum"),
        )
    )
    usage_rr["Response_Rate (%)"] = (
        usage_rr["Responders"] / usage_rr["N"] * 100
    ).round(2)
    usage_rr = usage_rr.reset_index()

    # Age Group Analysis
    age_rr = (
        df.groupby("AgeGroup")
        .agg(
            N=("AgeGroup", "count"),
            Responders=("Response_to_Campaign", "sum"),
        )
    )
    age_rr["Response_Rate (%)"] = (
        age_rr["Responders"] / age_rr["N"] * 100
    ).round(2)
    age_rr = age_rr.reset_index()

    # Purchase Last Quarter Analysis
    purchase_rr = (
        df.groupby("Purchase_Last_Quarter")
        .agg(
            N=("Purchase_Last_Quarter", "count"),
            Responders=("Response_to_Campaign", "sum"),
        )
    )
    purchase_rr["Response_Rate (%)"] = (
        purchase_rr["Responders"] / purchase_rr["N"] * 100
    ).round(2)
    purchase_rr = purchase_rr.reset_index()

    html = f"""
    <html>
        <head>
            <title>Campaign Analysis Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 30px;
                    background-color: #f4f4f4;
                }}

                h1 {{
                    text-align: center;
                    color: #2c3e50;
                }}

                h2 {{
                    color: #2c3e50;
                    margin-top: 40px;
                }}

                table {{
                    border-collapse: collapse;
                    width: 90%;
                    margin-bottom: 30px;
                    background-color: white;
                }}

                th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    text-align: center;
                }}

                td {{
                    padding: 8px;
                    text-align: center;
                    border: 1px solid #ddd;
                }}

                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>Skin Clinic Campaign Analysis Dashboard</h1>

            <h2>Gender vs Campaign Response</h2>
            {gender_rr.to_html(index=False)}

            <h2>Product Usage vs Campaign Response</h2>
            {usage_rr.to_html(index=False)}

            <h2>Age Group vs Campaign Response</h2>
            {age_rr.to_html(index=False)}

            <h2>Purchase Last Quarter vs Campaign Response</h2>
            {purchase_rr.to_html(index=False)}
        </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
