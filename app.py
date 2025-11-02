from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load your CSV
df = pd.read_csv("cars.csv", sep="\t", low_memory=False)
df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")
df["kms_run"] = pd.to_numeric(df["kms_run"], errors="coerce")
df.dropna(subset=["sale_price", "kms_run"], inplace=True)

# Hardcode conversions
INR_TO_USD = 0.012
KM_TO_MILES = 0.621371
df["sale_price_usd"] = (df["sale_price"] * INR_TO_USD).round(2)
df["miles_run"] = (df["kms_run"] * KM_TO_MILES).round(1)

@app.route("/")
def home():
    return "<h1>🚗 Car Recommender API is Live!</h1><p>Use /recommend?budget=5000</p>"

@app.route("/recommend")
def recommend():
    try:
        budget = float(request.args.get("budget", 5000))
    except:
        return jsonify({"error": "Invalid or missing 'budget' parameter"}), 400

    result = df[df["sale_price_usd"] <= budget]
    result = result.sort_values(by=["yr_mfr", "miles_run"], ascending=[False, True])
    output = result.head(10)[
        ["make", "model", "yr_mfr", "fuel_type", "miles_run", "sale_price_usd"]
    ].to_dict(orient="records")
    return jsonify(output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
