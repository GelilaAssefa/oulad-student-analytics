"""
src/utils/load_data.py
Loads all OULAD CSV files into a local SQLite database.
Run once before any analysis: python src/utils/load_data.py
"""

import os
import sqlite3
import pandas as pd
from pathlib import Path

ROOT     = Path(__file__).resolve().parents[2]
DB_PATH  = ROOT / "data" / "oulad.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Update this path to where your CSV files are
DATA_DIR = Path(os.environ.get("OULAD_DATA_DIR", r"C:\Users\hana1\Downloads\archive"))

FILES = {
    "student_info":         "studentInfo.csv",
    "student_assessment":   "studentAssessment.csv",
    "student_vle":          "studentVle.csv",
    "student_registration": "studentRegistration.csv",
    "assessments":          "assessments.csv",
    "courses":              "courses.csv",
    "vle":                  "vle.csv",
}


def load_all():
    conn = sqlite3.connect(DB_PATH)
    print(f"Loading OULAD data into: {DB_PATH}\n")

    for table_name, filename in FILES.items():
        filepath = DATA_DIR / filename
        if not filepath.exists():
            print(f"  [SKIP] {filename} not found")
            continue
        df = pd.read_csv(filepath)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  [✓] {table_name:25s} → {len(df):>7,} rows  ({filename})")

    conn.close()
    print(f"\nDatabase ready at: {DB_PATH}")


if __name__ == "__main__":
    load_all()
