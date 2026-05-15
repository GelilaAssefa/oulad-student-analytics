"""
src/sql/queries.py
All SQL queries used in the project.
Each function returns a pandas DataFrame by running SQL against the SQLite database.
"""

import sqlite3
import pandas as pd
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "oulad.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


# ── 1. Overall outcome distribution ───────────────────────────────────────────

OUTCOME_DISTRIBUTION = """
SELECT
    final_result,
    COUNT(*) AS n_students,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM student_info
GROUP BY final_result
ORDER BY n_students DESC;
"""

# ── 2. Outcomes by gender ──────────────────────────────────────────────────────

OUTCOMES_BY_GENDER = """
SELECT
    gender,
    final_result,
    COUNT(*) AS n_students
FROM student_info
GROUP BY gender, final_result
ORDER BY gender, n_students DESC;
"""

# ── 3. Outcomes by disability status ──────────────────────────────────────────

OUTCOMES_BY_DISABILITY = """
SELECT
    disability,
    final_result,
    COUNT(*) AS n_students,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY disability), 1) AS pct
FROM student_info
GROUP BY disability, final_result
ORDER BY disability, n_students DESC;
"""

# ── 4. Outcomes by age band ────────────────────────────────────────────────────

OUTCOMES_BY_AGE = """
SELECT
    age_band,
    final_result,
    COUNT(*) AS n_students
FROM student_info
GROUP BY age_band, final_result
ORDER BY age_band, n_students DESC;
"""

# ── 5. Outcomes by IMD band (deprivation — proxy for socioeconomic status) ────

OUTCOMES_BY_IMD = """
SELECT
    imd_band,
    final_result,
    COUNT(*) AS n_students
FROM student_info
WHERE imd_band IS NOT NULL AND imd_band != ''
GROUP BY imd_band, final_result
ORDER BY imd_band, n_students DESC;
"""

# ── 6. Pass rate by course ─────────────────────────────────────────────────────

PASS_RATE_BY_COURSE = """
SELECT
    code_module,
    COUNT(*) AS total_students,
    SUM(CASE WHEN final_result = 'Pass' OR final_result = 'Distinction' THEN 1 ELSE 0 END) AS passed,
    ROUND(
        SUM(CASE WHEN final_result = 'Pass' OR final_result = 'Distinction' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        1
    ) AS pass_rate_pct,
    SUM(CASE WHEN final_result = 'Withdrawn' THEN 1 ELSE 0 END) AS withdrawn,
    ROUND(SUM(CASE WHEN final_result = 'Withdrawn' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS withdrawal_rate_pct
FROM student_info
GROUP BY code_module
ORDER BY pass_rate_pct DESC;
"""

# ── 7. Average assessment score by outcome ────────────────────────────────────

AVG_SCORE_BY_OUTCOME = """
SELECT
    si.final_result,
    ROUND(AVG(sa.score), 1) AS avg_score,
    COUNT(DISTINCT si.id_student) AS n_students
FROM student_info si
JOIN student_assessment sa ON si.id_student = sa.id_student
WHERE sa.score IS NOT NULL
GROUP BY si.final_result
ORDER BY avg_score DESC;
"""

# ── 8. VLE activity (clicks) vs outcome ───────────────────────────────────────

VLE_ACTIVITY_BY_OUTCOME = """
SELECT
    si.final_result,
    ROUND(AVG(total_clicks), 0) AS avg_clicks,
    ROUND(AVG(active_days), 0) AS avg_active_days,
    COUNT(DISTINCT si.id_student) AS n_students
FROM student_info si
JOIN (
    SELECT
        id_student,
        SUM(sum_click) AS total_clicks,
        COUNT(DISTINCT date) AS active_days
    FROM student_vle
    GROUP BY id_student
) vle_summary ON si.id_student = vle_summary.id_student
GROUP BY si.final_result
ORDER BY avg_clicks DESC;
"""

# ── 9. Early engagement (first 30 days) vs outcome ────────────────────────────

EARLY_ENGAGEMENT = """
SELECT
    si.final_result,
    ROUND(AVG(early_clicks), 0) AS avg_early_clicks,
    COUNT(DISTINCT si.id_student) AS n_students
FROM student_info si
JOIN (
    SELECT
        id_student,
        SUM(sum_click) AS early_clicks
    FROM student_vle
    WHERE date <= 30
    GROUP BY id_student
) early ON si.id_student = early.id_student
GROUP BY si.final_result
ORDER BY avg_early_clicks DESC;
"""

# ── 10. Withdrawal timing ─────────────────────────────────────────────────────

WITHDRAWAL_TIMING = """
SELECT
    date_unregistration,
    COUNT(*) AS n_withdrawals
FROM student_registration
WHERE date_unregistration IS NOT NULL
GROUP BY date_unregistration
ORDER BY date_unregistration;
"""

# ── 11. Previous attempts vs outcome ─────────────────────────────────────────

PREV_ATTEMPTS_VS_OUTCOME = """
SELECT
    num_of_prev_attempts,
    final_result,
    COUNT(*) AS n_students
FROM student_info
GROUP BY num_of_prev_attempts, final_result
ORDER BY num_of_prev_attempts, n_students DESC;
"""

# ── 12. Studied credits vs outcome ───────────────────────────────────────────

CREDITS_VS_OUTCOME = """
SELECT
    final_result,
    ROUND(AVG(studied_credits), 0) AS avg_credits,
    MIN(studied_credits) AS min_credits,
    MAX(studied_credits) AS max_credits,
    COUNT(*) AS n_students
FROM student_info
GROUP BY final_result
ORDER BY avg_credits DESC;
"""


# ── runner functions ───────────────────────────────────────────────────────────

def run_query(sql: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn)


def get_outcome_distribution():         return run_query(OUTCOME_DISTRIBUTION)
def get_outcomes_by_gender():           return run_query(OUTCOMES_BY_GENDER)
def get_outcomes_by_disability():       return run_query(OUTCOMES_BY_DISABILITY)
def get_outcomes_by_age():              return run_query(OUTCOMES_BY_AGE)
def get_outcomes_by_imd():              return run_query(OUTCOMES_BY_IMD)
def get_pass_rate_by_course():          return run_query(PASS_RATE_BY_COURSE)
def get_avg_score_by_outcome():         return run_query(AVG_SCORE_BY_OUTCOME)
def get_vle_activity_by_outcome():      return run_query(VLE_ACTIVITY_BY_OUTCOME)
def get_early_engagement():             return run_query(EARLY_ENGAGEMENT)
def get_withdrawal_timing():            return run_query(WITHDRAWAL_TIMING)
def get_prev_attempts_vs_outcome():     return run_query(PREV_ATTEMPTS_VS_OUTCOME)
def get_credits_vs_outcome():           return run_query(CREDITS_VS_OUTCOME)


if __name__ == "__main__":
    print("Testing all queries...\n")
    print("Outcome distribution:")
    print(get_outcome_distribution())
    print("\nPass rate by course:")
    print(get_pass_rate_by_course())
    print("\nVLE activity by outcome:")
    print(get_vle_activity_by_outcome())
