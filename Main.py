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


def generate_html(title, dataframe):
    dataframe = dataframe.reset_index()
    return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial;
                    margin: 30px;
                }}

                h2 {{
                    text-align: center;
                    color: #2c3e50;
                }}

                table {{
                    border-collapse: collapse;
                    width: 70%;
                    margin: auto;
                }}

                th {{
                    background-color: #4CAF50;
                    color: white;
                    text-align: center;
                    padding: 10px;
                }}

                td {{
                    text-align: center;
                    padding: 8px;
                    border: 1px solid #ddd;
                }}

                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h2>{title}</h2>
            {dataframe.to_html(index=False, justify="center")}
        </body>
        </html>
        """

@app.get("/gender-table", response_class=HTMLResponse)
def gender_table():
    gender_rr = (
        df.groupby('Gender')
        .agg(
            N=('Gender', 'count'),
            Responders=('Response_to_Campaign', 'sum')
        )
    )
    gender_rr['Response_Rate'] = (gender_rr['Responders'] / gender_rr['N']) * 100
    gender_rr['Response_Rate'] = gender_rr['Response_Rate'].round(2)
    return generate_html("Gender vs Campaign Response", gender_rr)


# ---------------------------------------------------------
# Product Usage Table
# ---------------------------------------------------------
@app.get("/product-usage-table", response_class=HTMLResponse)
def product_usage_table():
    usage_rr = (
        df.groupby('Product_Usage_Bin')
        .agg(
            N=('Product_Usage_Bin', 'count'),
            Responders=('Response_to_Campaign', 'sum')
        )
    )
    usage_rr['Response_Rate'] = (usage_rr['Responders'] / usage_rr['N']) * 100
    usage_rr['Response_Rate'] = usage_rr['Response_Rate'].round(2)
    return generate_html("Product Usage vs Campaign Response", usage_rr)


# ---------------------------------------------------------
# Age Group Table
# ---------------------------------------------------------
@app.get("/agegroup-table", response_class=HTMLResponse)
def agegroup_table():
    age_rr = (
        df.groupby('AgeGroup')
        .agg(
            N=('AgeGroup', 'count'),
            Responders=('Response_to_Campaign', 'sum')
        )
    )
    age_rr['Response_Rate'] = (age_rr['Responders'] / age_rr['N']) * 100
    age_rr['Response_Rate'] = age_rr['Response_Rate'].round(2)
    return generate_html("Age Group vs Campaign Response", age_rr)


# ---------------------------------------------------------
# Purchase Last Quarter Table
# ---------------------------------------------------------
@app.get("/purchase-last-quarter-table", response_class=HTMLResponse)
def purchase_last_quarter_table():
    purchase_rr = (
        df.groupby('Purchase_Last_Quarter')
        .agg(
            N=('Purchase_Last_Quarter', 'count'),
            Responders=('Response_to_Campaign', 'sum')
        )
    )
    purchase_rr['Response_Rate'] = (purchase_rr['Responders'] / purchase_rr['N']) * 100
    purchase_rr['Response_Rate'] = purchase_rr['Response_Rate'].round(2)
    return generate_html("Purchase Last Quarter vs Campaign Response", purchase_rr)

# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
