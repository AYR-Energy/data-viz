import json
import os
import pandas as pd

CSV_PATH = "data.csv"
TEMPLATE_PATH = "template4.html"
OUT_DIR = "docs"
OUT_HTML = os.path.join(OUT_DIR, "index.html")

# If your CSV headers differ, map them here:
COLUMN_MAP = {
    "mfg": "mfg",
    "loc": "loc",
    "cap": "cap",
    "oem": "oem",
    "cat": "cat",
    "reg": "reg",
    "lat": "lat",
    "lon": "lon",
}

REQUIRED = ["mfg", "loc", "cap", "oem", "cat", "reg", "lat", "lon"]

def main():
    # Load template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    if "__DATA__" not in template:
        raise ValueError("Template must contain the placeholder __DATA__")

    # Load CSV
    df = pd.read_csv(CSV_PATH)

    # Rename columns if needed
    rename_dict = {}
    for want, have in COLUMN_MAP.items():
        if have != want and have in df.columns:
            rename_dict[have] = want
    if rename_dict:
        df = df.rename(columns=rename_dict)

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}\nFound columns: {list(df.columns)}")

    # Coerce lat/lon to floats and drop bad rows
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])

    # Convert to list of dicts (JSON array)
    records = df[REQUIRED].to_dict(orient="records")

    # JSON for embedding directly into JS
    data_json = json.dumps(records, ensure_ascii=False)

    # Inject into template
    out_html = template.replace("__DATA__", data_json)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(out_html)

    print(f"Wrote {OUT_HTML} with {len(records)} rows from {CSV_PATH}")

if __name__ == "__main__":
    main()
