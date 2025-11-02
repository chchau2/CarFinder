from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# =========================
# LOAD AND PREPARE DATA
# =========================
print("Loading data...")
df = pd.read_csv("cars.csv", low_memory=False)
df.columns = df.columns.str.strip().str.lower()

# Clean and convert numeric columns
df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")
df["kms_run"] = pd.to_numeric(df["kms_run"], errors="coerce")
df["yr_mfr"] = pd.to_numeric(df["yr_mfr"], errors="coerce")
df.dropna(subset=["sale_price", "kms_run", "yr_mfr"], inplace=True)

# Hardcoded conversions
INR_TO_USD = 0.012
KM_TO_MILES = 0.621371
df["sale_price_usd"] = (df["sale_price"] * INR_TO_USD).round(2)
df["miles_run"] = (df["kms_run"] * KM_TO_MILES).round(1)

print(f"✅ Loaded {len(df)} rows")

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend")
def recommend():
    try:
        budget = float(request.args.get("budget", 5000))
    except ValueError:
        return jsonify({"error": "Invalid budget"}), 400

    fuel = request.args.get("fuel_type")
    model_query = request.args.get("make")

    filtered = df[df["sale_price_usd"] <= budget]

    # Fuel filter
    if fuel:
        filtered = filtered[
            filtered["fuel_type"].astype(str).str.lower().str.strip() == fuel.lower().strip()
        ]

    # Model filter — safer handling for missing values and mixed types
    if model_query:
        filtered = filtered[
            filtered["make"]
            .astype(str)
            .str.lower()
            .str.contains(model_query.lower().strip(), na=False)
        ]

    ranked = filtered.sort_values(by=["yr_mfr", "miles_run"], ascending=[False, True])
    result = ranked.head(10)[
        ["make", "model", "yr_mfr", "fuel_type", "miles_run", "sale_price_usd"]
    ].to_dict(orient="records")

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)
