"""
src/analysis/eda.py
Exploratory Data Analysis — generates all static charts from SQL query results.
Run: python src/analysis/eda.py
"""

from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

ROOT    = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "docs" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

# Color palette
COLORS = {
    "Pass":        "#16A34A",
    "Distinction": "#2563EB",
    "Fail":        "#DC2626",
    "Withdrawn":   "#F59E0B",
}
PALETTE = list(COLORS.values())


def save(fig, name):
    path = REPORTS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"[✓] {name}.png")


# ── 1. Outcome distribution ───────────────────────────────────────────────────

def plot_outcome_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart
    ax = axes[0]
    colors = [COLORS.get(r, "#64748B") for r in df["final_result"]]
    bars = ax.bar(df["final_result"], df["n_students"], color=colors, edgecolor="white", linewidth=1.5)
    for bar, (_, row) in zip(bars, df.iterrows()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                f"{row['pct']}%", ha="center", fontsize=11, fontweight="bold")
    ax.set_title("Student Outcomes — Overall Distribution", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Students", fontsize=11)
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    # Pie chart
    ax2 = axes[1]
    wedge_colors = [COLORS.get(r, "#64748B") for r in df["final_result"]]
    wedges, texts, autotexts = ax2.pie(
        df["n_students"], labels=df["final_result"],
        colors=wedge_colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.8,
    )
    for text in autotexts:
        text.set_fontsize(11)
        text.set_fontweight("bold")
    ax2.set_title("Outcome Share", fontsize=13, fontweight="bold")

    fig.suptitle("OULAD: Open University Student Outcomes (32,593 students)",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "01_outcome_distribution")


# ── 2. Outcomes by gender ──────────────────────────────────────────────────────

def plot_outcomes_by_gender(df: pd.DataFrame):
    pivot = df.pivot_table(index="gender", columns="final_result",
                           values="n_students", fill_value=0)
    # Normalize to percentages
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = np.zeros(len(pivot_pct))
    for result in ["Distinction", "Pass", "Fail", "Withdrawn"]:
        if result not in pivot_pct.columns:
            continue
        vals = pivot_pct[result].values
        ax.bar(pivot_pct.index, vals, bottom=bottom,
               color=COLORS.get(result, "#64748B"), label=result, edgecolor="white")
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v > 5:
                ax.text(i, b + v / 2, f"{v:.0f}%", ha="center", va="center",
                        fontsize=10, fontweight="bold", color="white")
        bottom += vals

    ax.set_title("Student Outcomes by Gender", fontsize=13, fontweight="bold")
    ax.set_ylabel("Percentage of Students (%)", fontsize=11)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(0, 110)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save(fig, "02_outcomes_by_gender")


# ── 3. Outcomes by disability ──────────────────────────────────────────────────

def plot_outcomes_by_disability(df: pd.DataFrame):
    df["disability_label"] = df["disability"].map({"Y": "Has Disability", "N": "No Disability"})
    pivot = df.pivot_table(index="disability_label", columns="final_result",
                           values="n_students", fill_value=0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = np.zeros(len(pivot_pct))
    for result in ["Distinction", "Pass", "Fail", "Withdrawn"]:
        if result not in pivot_pct.columns:
            continue
        vals = pivot_pct[result].values
        ax.bar(pivot_pct.index, vals, bottom=bottom,
               color=COLORS.get(result, "#64748B"), label=result, edgecolor="white")
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v > 5:
                ax.text(i, b + v / 2, f"{v:.0f}%", ha="center", va="center",
                        fontsize=11, fontweight="bold", color="white")
        bottom += vals

    ax.set_title("Student Outcomes by Disability Status", fontsize=13, fontweight="bold")
    ax.set_ylabel("Percentage of Students (%)", fontsize=11)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(0, 110)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save(fig, "03_outcomes_by_disability")


# ── 4. Pass rate by course ─────────────────────────────────────────────────────

def plot_pass_rate_by_course(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5))
    df_sorted = df.sort_values("pass_rate_pct", ascending=True)

    bars = ax.barh(df_sorted["code_module"], df_sorted["pass_rate_pct"],
                   color="#2563EB", edgecolor="white")
    ax.barh(df_sorted["code_module"], df_sorted["withdrawal_rate_pct"],
            left=df_sorted["pass_rate_pct"], color="#F59E0B",
            edgecolor="white", label="Withdrawal Rate")

    for bar, val in zip(bars, df_sorted["pass_rate_pct"]):
        ax.text(val / 2, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}%", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

    ax.set_title("Pass Rate & Withdrawal Rate by Course", fontsize=13, fontweight="bold")
    ax.set_xlabel("Percentage of Students (%)", fontsize=11)
    ax.set_ylabel("Course Code", fontsize=11)
    ax.legend([
        mpatches.Patch(color="#2563EB", label="Pass/Distinction Rate"),
        mpatches.Patch(color="#F59E0B", label="Withdrawal Rate"),
    ], fontsize=10)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    save(fig, "04_pass_rate_by_course")


# ── 5. VLE activity vs outcome ─────────────────────────────────────────────────

def plot_vle_activity(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    colors = [COLORS.get(r, "#64748B") for r in df["final_result"]]

    ax = axes[0]
    bars = ax.bar(df["final_result"], df["avg_clicks"], color=colors, edgecolor="white")
    for bar, val in zip(bars, df["avg_clicks"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"{val:,.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_title("Average VLE Clicks by Outcome", fontsize=13, fontweight="bold")
    ax.set_ylabel("Avg Total Clicks", fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    ax2 = axes[1]
    bars2 = ax2.bar(df["final_result"], df["avg_active_days"], color=colors, edgecolor="white")
    for bar, val in zip(bars2, df["avg_active_days"]):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax2.set_title("Average Active Days by Outcome", fontsize=13, fontweight="bold")
    ax2.set_ylabel("Avg Days Active on Platform", fontsize=11)
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Online Engagement (VLE Activity) vs Student Outcome",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "05_vle_activity_vs_outcome")


# ── 6. Assessment scores vs outcome ──────────────────────────────────────────

def plot_scores_by_outcome(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [COLORS.get(r, "#64748B") for r in df["final_result"]]
    bars = ax.bar(df["final_result"], df["avg_score"], color=colors, edgecolor="white")
    for bar, val in zip(bars, df["avg_score"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}", ha="center", fontsize=11, fontweight="bold")
    ax.set_title("Average Assessment Score by Final Outcome", fontsize=13, fontweight="bold")
    ax.set_ylabel("Average Score (0–100)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.axhline(50, color="red", ls="--", alpha=0.5, label="Pass threshold (50)")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save(fig, "06_scores_by_outcome")


# ── 7. IMD (deprivation) vs outcome ──────────────────────────────────────────

def plot_imd_vs_outcome(df: pd.DataFrame):
    # Keep only valid IMD bands
    df = df[df["imd_band"].str.contains("%", na=False)].copy()
    pivot = df.pivot_table(index="imd_band", columns="final_result",
                           values="n_students", fill_value=0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    # Sort by IMD band (deprivation level)
    try:
        pivot_pct = pivot_pct.loc[sorted(pivot_pct.index,
            key=lambda x: int(x.split("-")[0].replace("%","").strip()))]
    except Exception:
        pass

    fig, ax = plt.subplots(figsize=(13, 5))
    bottom = np.zeros(len(pivot_pct))
    for result in ["Distinction", "Pass", "Fail", "Withdrawn"]:
        if result not in pivot_pct.columns:
            continue
        vals = pivot_pct[result].values
        ax.bar(pivot_pct.index, vals, bottom=bottom,
               color=COLORS.get(result, "#64748B"), label=result, edgecolor="white")
        bottom += vals

    ax.set_title("Outcomes by Deprivation Level (IMD Band)\nHigher % = More Deprived Area",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("IMD Band (Index of Multiple Deprivation)", fontsize=11)
    ax.set_ylabel("% of Students", fontsize=11)
    ax.legend(fontsize=10)
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save(fig, "07_imd_vs_outcome")


# ── 8. Previous attempts vs outcome ──────────────────────────────────────────

def plot_prev_attempts(df: pd.DataFrame):
    df = df[df["num_of_prev_attempts"] <= 4]
    pivot = df.pivot_table(index="num_of_prev_attempts", columns="final_result",
                           values="n_students", fill_value=0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(len(pivot_pct))
    for result in ["Distinction", "Pass", "Fail", "Withdrawn"]:
        if result not in pivot_pct.columns:
            continue
        vals = pivot_pct[result].values
        ax.bar(pivot_pct.index.astype(str), vals, bottom=bottom,
               color=COLORS.get(result, "#64748B"), label=result, edgecolor="white")
        bottom += vals

    ax.set_title("Outcomes by Number of Previous Attempts",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of Previous Attempts", fontsize=11)
    ax.set_ylabel("% of Students", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save(fig, "08_prev_attempts_vs_outcome")


# ── main ───────────────────────────────────────────────────────────────────────

def run_eda():
    from src.sql.queries import (
        get_outcome_distribution, get_outcomes_by_gender,
        get_outcomes_by_disability, get_pass_rate_by_course,
        get_vle_activity_by_outcome, get_avg_score_by_outcome,
        get_outcomes_by_imd, get_prev_attempts_vs_outcome,
    )

    log.info("Running EDA analysis...")
    plot_outcome_distribution(get_outcome_distribution())
    plot_outcomes_by_gender(get_outcomes_by_gender())
    plot_outcomes_by_disability(get_outcomes_by_disability())
    plot_pass_rate_by_course(get_pass_rate_by_course())
    plot_vle_activity(get_vle_activity_by_outcome())
    plot_scores_by_outcome(get_avg_score_by_outcome())
    plot_imd_vs_outcome(get_outcomes_by_imd())
    plot_prev_attempts(get_prev_attempts_vs_outcome())
    log.info(f"\nAll charts saved to {REPORTS}")


if __name__ == "__main__":
    run_eda()
