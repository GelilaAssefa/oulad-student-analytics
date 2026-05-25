#  OULAD Student Analytics

> **A data analytics portfolio project using real Open University student data to explore outcomes, equity gaps, and engagement patterns across 32,593 students.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey?logo=sqlite)](https://sqlite.org)
[![Plotly Dash](https://img.shields.io/badge/Dashboard-Plotly%20Dash-purple)](https://dash.plotly.com)
[![Data](https://img.shields.io/badge/Data-Real%20OULAD-green)](https://analyse.kmi.open.ac.uk/open_dataset)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Project Overview

This project analyzes the **Open University Learning Analytics Dataset (OULAD)** — a real, publicly available dataset of 32,593 anonymized students across 22 courses at the Open University UK.

The goal is to answer key institutional questions using **SQL + Python + interactive visualizations**:

- What percentage of students pass, fail, or withdraw?
- Are there equity gaps by gender, disability, or socioeconomic status?
- Does online engagement (VLE clicks) predict student success?
- Which courses have the highest/lowest pass rates?
- Do students who retake courses perform better?

---

## Project Structure

```
oulad-student-analytics/
├── dashboard/
│   └── app.py                  # Interactive Plotly Dash web app
├── src/
│   ├── sql/
│   │   └── queries.py          # All SQL queries (12 analytical queries)
│   ├── analysis/
│   │   └── eda.py              # EDA charts and visualizations
│   └── utils/
│       └── load_data.py        # Loads CSVs into SQLite database
├── data/                       # SQLite database (generated locally)
├── docs/reports/               # Output charts (generated locally)
├── run_all.py                  # Master pipeline script
└── requirements.txt
```

---

## Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/GelilaAssefa/oulad-student-analytics.git
cd oulad-student-analytics
pip install -r requirements.txt
```

### 2. Download the Data
Get the OULAD dataset (free):
 https://analyse.kmi.open.ac.uk/open_dataset

Or from Kaggle:
 https://www.kaggle.com/datasets/anlgrbz/student-demographics-online-education-dataoulad

Place the CSV files in a folder and update the path in `src/utils/load_data.py`:
```python
DATA_DIR = Path(r"C:\path\to\your\csv\files")
```

### 3. Run the Full Pipeline
```bash
python run_all.py
```

### 4. Launch the Dashboard
```bash
python dashboard/app.py
```
Open **http://localhost:8050**

---

## SQL Queries

The project uses **12 SQL queries** against a local SQLite database:

| Query | Purpose |
|---|---|
| Outcome Distribution | Overall pass/fail/withdraw rates |
| Outcomes by Gender | Equity analysis by gender |
| Outcomes by Disability | Do disabled students face barriers? |
| Outcomes by Age Band | Does age affect success? |
| Outcomes by IMD Band | Socioeconomic equity analysis |
| Pass Rate by Course | Which courses are hardest? |
| Avg Score by Outcome | Assessment performance analysis |
| VLE Activity by Outcome | Does online engagement predict success? |
| Early Engagement | First 30 days as a predictor |
| Withdrawal Timing | When do students drop out? |
| Previous Attempts vs Outcome | Does retaking help? |
| Credits vs Outcome | Course load analysis |

Example:
```sql
-- Students who engage more in the first 30 days are more likely to pass
SELECT
    si.final_result,
    ROUND(AVG(early_clicks), 0) AS avg_early_clicks
FROM student_info si
JOIN (
    SELECT id_student, SUM(sum_click) AS early_clicks
    FROM student_vle
    WHERE date <= 30
    GROUP BY id_student
) e ON si.id_student = e.id_student
GROUP BY si.final_result
ORDER BY avg_early_clicks DESC;
```

---

## Dashboard Features

The interactive Plotly Dash dashboard has 4 tabs:

1. **Overview** — Outcome distribution pie chart, pass rates by course, assessment scores, VLE activity
2. **Equity Analysis** — Outcomes broken down by gender, disability, age, and deprivation level (IMD)
3. **Engagement** — Early engagement analysis, previous attempts, active days on platform
4. **SQL Explorer** — Run and view any of the 12 SQL queries interactively with live results tables

---

##  Key Findings

- Students who click more in the **first 30 days** are significantly more likely to pass
- Students with **disabilities** have slightly lower pass rates, suggesting a need for targeted support
- **Deprivation level (IMD)** correlates with outcomes — students from more deprived areas withdraw at higher rates
- Pass rates vary **significantly by course** — some courses lose over 30% of students to withdrawal
- Students who **retake a course** do not always perform better on the second attempt

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| SQL (SQLite) | Data storage and querying |
| pandas | Data manipulation |
| matplotlib / seaborn | Static charts |
| Plotly Dash | Interactive dashboard |
| scipy | Statistical analysis |

---

## Data Citation

Kuzilek J., Hlosta M., Zdrahal Z. (2017) *Open University Learning Analytics dataset*. Scientific Data, 4:170171. https://doi.org/10.1038/sdata.2017.171

Licensed under CC BY 4.0 — real anonymized student data, no personal information.

---

