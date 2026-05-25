"""
dashboard/app.py
Interactive Plotly Dash dashboard for OULAD Student Analytics.
Run: python dashboard/app.py  then open http://localhost:8050
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

from src.sql.queries import (
    get_outcome_distribution, get_outcomes_by_gender,
    get_outcomes_by_disability, get_pass_rate_by_course,
    get_vle_activity_by_outcome, get_avg_score_by_outcome,
    get_outcomes_by_age, get_outcomes_by_imd,
    get_prev_attempts_vs_outcome, get_early_engagement,
)

# ── load all data upfront ──────────────────────────────────────────────────────
outcomes     = get_outcome_distribution()
by_gender    = get_outcomes_by_gender()
by_disability = get_outcomes_by_disability()
by_course    = get_pass_rate_by_course()
by_vle       = get_vle_activity_by_outcome()
by_score     = get_avg_score_by_outcome()
by_age       = get_outcomes_by_age()
by_imd       = get_outcomes_by_imd()
by_attempts  = get_prev_attempts_vs_outcome()
by_early     = get_early_engagement()

BRAND  = "#1E3A5F"
ACCENT = "#2563EB"
COLORS = {
    "Pass": "#16A34A", "Distinction": "#2563EB",
    "Fail": "#DC2626",  "Withdrawn": "#F59E0B",
}

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           title="OULAD Student Analytics")


def kpi(title, value, subtitle="", color=ACCENT):
    return dbc.Card(dbc.CardBody([
        html.P(title, className="text-muted mb-1",
               style={"fontSize": "0.75rem", "fontWeight": "700",
                      "textTransform": "uppercase", "letterSpacing": "0.06em"}),
        html.H3(value, style={"color": color, "fontWeight": "800", "margin": "0"}),
        html.P(subtitle, className="text-muted mt-1 mb-0", style={"fontSize": "0.8rem"}),
    ]), className="shadow-sm h-100",
       style={"borderTop": f"4px solid {color}", "borderRadius": "8px"})


total    = outcomes["n_students"].sum()
pass_pct = outcomes[outcomes["final_result"].isin(["Pass","Distinction"])]["n_students"].sum() / total
with_pct = outcomes[outcomes["final_result"] == "Withdrawn"]["n_students"].sum() / total
fail_pct = outcomes[outcomes["final_result"] == "Fail"]["n_students"].sum() / total

app.layout = dbc.Container([

    # Header
    dbc.Row(dbc.Col(html.Div([
        html.H1("📚 OULAD Student Analytics Dashboard",
                style={"color": BRAND, "fontWeight": "800", "marginBottom": "0"}),
        html.P("Real Data · Open University Learning Analytics Dataset · 32,593 Students",
               className="text-muted", style={"fontSize": "0.9rem"}),
    ], style={"padding": "20px 0 12px"}))),

    # KPIs
    dbc.Row([
        dbc.Col(kpi("Total Students", f"{total:,}", "across all courses"), md=3),
        dbc.Col(kpi("Pass / Distinction", f"{pass_pct:.1%}", "overall pass rate", "#16A34A"), md=3),
        dbc.Col(kpi("Withdrawal Rate", f"{with_pct:.1%}", "students who withdrew", "#F59E0B"), md=3),
        dbc.Col(kpi("Fail Rate", f"{fail_pct:.1%}", "students who failed", "#DC2626"), md=3),
    ], className="mb-4 g-3"),

    # Tabs
    dbc.Tabs([

        # ── Tab 1: Overview ───────────────────────────────────────────────────
        dbc.Tab(label="📊 Overview", tab_id="overview", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id="outcome-pie"), md=5),
                dbc.Col(dcc.Graph(id="course-bar"), md=7),
            ], className="mt-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="score-bar"), md=6),
                dbc.Col(dcc.Graph(id="vle-bar"), md=6),
            ]),
        ]),

        # ── Tab 2: Equity ─────────────────────────────────────────────────────
        dbc.Tab(label="⚖️ Equity Analysis", tab_id="equity", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id="gender-chart"), md=6),
                dbc.Col(dcc.Graph(id="disability-chart"), md=6),
            ], className="mt-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="age-chart"), md=6),
                dbc.Col(dcc.Graph(id="imd-chart"), md=6),
            ]),
        ]),

        # ── Tab 3: Engagement ─────────────────────────────────────────────────
        dbc.Tab(label="🖱️ Engagement", tab_id="engagement", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id="early-engagement"), md=6),
                dbc.Col(dcc.Graph(id="attempts-chart"), md=6),
            ], className="mt-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card(dbc.CardBody([
                        html.H5("💡 Key Finding", className="fw-bold"),
                        html.Hr(),
                        html.P("Students who click more in the first 30 days are significantly more likely to pass. Early engagement is one of the strongest predictors of student success.", className="text-muted"),
                        html.P("Students who earn a Distinction average 3x more early clicks than students who withdraw.", className="fw-semibold"),
                    ]), className="shadow-sm h-100"),
                ], md=4),
                dbc.Col(dcc.Graph(id="vle-active-days"), md=8),
            ]),
        ]),

        # ── Tab 4: SQL Explorer ───────────────────────────────────────────────
        dbc.Tab(label="🗄️ SQL Explorer", tab_id="sql", children=[
            dbc.Row([
                dbc.Col([
                    html.Div(className="mt-3"),
                    html.Label("Choose a SQL Query to Run:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="sql-selector",
                        options=[
                            {"label": "Outcome Distribution", "value": "outcomes"},
                            {"label": "Pass Rate by Course", "value": "courses"},
                            {"label": "VLE Activity by Outcome", "value": "vle"},
                            {"label": "Avg Score by Outcome", "value": "scores"},
                            {"label": "Outcomes by Gender", "value": "gender"},
                            {"label": "Outcomes by Disability", "value": "disability"},
                            {"label": "Early Engagement vs Outcome", "value": "early"},
                        ],
                        value="outcomes", clearable=False,
                    ),
                    html.Div(id="sql-display", className="mt-3 p-3",
                             style={"backgroundColor": "#1E293B", "borderRadius": "8px",
                                    "fontFamily": "monospace", "color": "#94A3B8",
                                    "fontSize": "13px", "whiteSpace": "pre-wrap"}),
                ], md=5),
                dbc.Col([
                    html.Div(className="mt-3"),
                    html.Label("Query Results:", className="fw-bold mb-2"),
                    html.Div(id="sql-results"),
                ], md=7),
            ]),
        ]),

    ], active_tab="overview"),

    html.Hr(className="mt-4"),
    html.P("Data: Open University Learning Analytics Dataset (OULAD) · CC BY 4.0 · Real anonymized student data",
           className="text-center text-muted", style={"fontSize": "0.75rem", "paddingBottom": "16px"}),

], fluid=True, style={"backgroundColor": "#F8FAFC", "minHeight": "100vh"})


# ── callbacks ──────────────────────────────────────────────────────────────────

@app.callback(
    Output("outcome-pie", "figure"),
    Output("course-bar", "figure"),
    Output("score-bar", "figure"),
    Output("vle-bar", "figure"),
    Input("outcome-pie", "id"),
)
def update_overview(_):
    # Pie
    fig1 = px.pie(outcomes, values="n_students", names="final_result",
                  color="final_result",
                  color_discrete_map=COLORS,
                  title="Overall Outcome Distribution",
                  hole=0.4)
    fig1.update_traces(textinfo="percent+label")
    fig1.update_layout(margin=dict(t=40, b=10), showlegend=False)

    # Course pass rates
    fig2 = px.bar(by_course.sort_values("pass_rate_pct"),
                  x="pass_rate_pct", y="code_module", orientation="h",
                  color="pass_rate_pct", color_continuous_scale="Blues",
                  title="Pass Rate by Course (%)",
                  labels={"pass_rate_pct": "Pass Rate (%)", "code_module": "Course"},
                  text="pass_rate_pct")
    fig2.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig2.update_layout(margin=dict(t=40, b=10), coloraxis_showscale=False,
                       plot_bgcolor="#F8FAFC")

    # Scores
    fig3 = px.bar(by_score, x="final_result", y="avg_score",
                  color="final_result", color_discrete_map=COLORS,
                  title="Average Assessment Score by Outcome",
                  labels={"avg_score": "Avg Score (0-100)", "final_result": ""},
                  text="avg_score")
    fig3.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig3.update_layout(margin=dict(t=40, b=10), showlegend=False,
                       plot_bgcolor="#F8FAFC", yaxis_range=[0, 100])

    # VLE clicks
    fig4 = px.bar(by_vle, x="final_result", y="avg_clicks",
                  color="final_result", color_discrete_map=COLORS,
                  title="Average VLE Clicks by Outcome",
                  labels={"avg_clicks": "Avg Clicks", "final_result": ""},
                  text="avg_clicks")
    fig4.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig4.update_layout(margin=dict(t=40, b=10), showlegend=False,
                       plot_bgcolor="#F8FAFC")

    return fig1, fig2, fig3, fig4


@app.callback(
    Output("gender-chart", "figure"),
    Output("disability-chart", "figure"),
    Output("age-chart", "figure"),
    Output("imd-chart", "figure"),
    Input("gender-chart", "id"),
)
def update_equity(_):
    fig1 = px.histogram(by_gender, x="gender", y="n_students",
                        color="final_result", color_discrete_map=COLORS,
                        barmode="group", title="Outcomes by Gender",
                        labels={"n_students": "Students", "gender": "Gender"})
    fig1.update_layout(margin=dict(t=40, b=10), plot_bgcolor="#F8FAFC",
                       legend_title_text="")

    by_dis = by_disability.copy()
    by_dis["label"] = by_dis["disability"].map({"Y": "Has Disability", "N": "No Disability"})
    fig2 = px.histogram(by_dis, x="label", y="n_students",
                        color="final_result", color_discrete_map=COLORS,
                        barmode="group", title="Outcomes by Disability Status",
                        labels={"n_students": "Students", "label": ""})
    fig2.update_layout(margin=dict(t=40, b=10), plot_bgcolor="#F8FAFC",
                       legend_title_text="")

    fig3 = px.histogram(by_age, x="age_band", y="n_students",
                        color="final_result", color_discrete_map=COLORS,
                        barmode="group", title="Outcomes by Age Band",
                        labels={"n_students": "Students", "age_band": "Age Band"})
    fig3.update_layout(margin=dict(t=40, b=10), plot_bgcolor="#F8FAFC",
                       legend_title_text="")

    imd_valid = by_imd[by_imd["imd_band"].str.contains("%", na=False)]
    fig4 = px.histogram(imd_valid, x="imd_band", y="n_students",
                        color="final_result", color_discrete_map=COLORS,
                        barmode="stack", title="Outcomes by Deprivation Level (IMD Band)",
                        labels={"n_students": "Students", "imd_band": "IMD Band"})
    fig4.update_layout(margin=dict(t=40, b=10), plot_bgcolor="#F8FAFC",
                       legend_title_text="", xaxis_tickangle=30)

    return fig1, fig2, fig3, fig4


@app.callback(
    Output("early-engagement", "figure"),
    Output("attempts-chart", "figure"),
    Output("vle-active-days", "figure"),
    Input("early-engagement", "id"),
)
def update_engagement(_):
    fig1 = px.bar(by_early, x="final_result", y="avg_early_clicks",
                  color="final_result", color_discrete_map=COLORS,
                  title="Avg Clicks in First 30 Days by Outcome",
                  labels={"avg_early_clicks": "Avg Early Clicks", "final_result": ""},
                  text="avg_early_clicks")
    fig1.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig1.update_layout(margin=dict(t=40, b=10), showlegend=False,
                       plot_bgcolor="#F8FAFC")

    att = by_attempts[by_attempts["num_of_prev_attempts"] <= 3]
    fig2 = px.histogram(att, x="num_of_prev_attempts", y="n_students",
                        color="final_result", color_discrete_map=COLORS,
                        barmode="group", title="Outcomes by Number of Previous Attempts",
                        labels={"n_students": "Students", "num_of_prev_attempts": "Previous Attempts"})
    fig2.update_layout(margin=dict(t=40, b=10), plot_bgcolor="#F8FAFC",
                       legend_title_text="")

    fig3 = px.bar(by_vle, x="final_result", y="avg_active_days",
                  color="final_result", color_discrete_map=COLORS,
                  title="Average Active Days on Platform by Outcome",
                  labels={"avg_active_days": "Avg Active Days", "final_result": ""},
                  text="avg_active_days")
    fig3.update_traces(texttemplate="%{text:.0f} days", textposition="outside")
    fig3.update_layout(margin=dict(t=40, b=10), showlegend=False,
                       plot_bgcolor="#F8FAFC")

    return fig1, fig2, fig3


SQL_TEXTS = {
    "outcomes": """SELECT
    final_result,
    COUNT(*) AS n_students,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (), 1) AS pct
FROM student_info
GROUP BY final_result
ORDER BY n_students DESC;""",
    "courses": """SELECT
    code_module,
    COUNT(*) AS total_students,
    ROUND(SUM(CASE WHEN final_result IN
        ('Pass','Distinction') THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 1) AS pass_rate_pct
FROM student_info
GROUP BY code_module
ORDER BY pass_rate_pct DESC;""",
    "vle": """SELECT
    si.final_result,
    ROUND(AVG(total_clicks), 0) AS avg_clicks,
    ROUND(AVG(active_days), 0) AS avg_active_days
FROM student_info si
JOIN (
    SELECT id_student,
        SUM(sum_click) AS total_clicks,
        COUNT(DISTINCT date) AS active_days
    FROM student_vle
    GROUP BY id_student
) v ON si.id_student = v.id_student
GROUP BY si.final_result;""",
    "scores": """SELECT
    si.final_result,
    ROUND(AVG(sa.score), 1) AS avg_score
FROM student_info si
JOIN student_assessment sa
    ON si.id_student = sa.id_student
WHERE sa.score IS NOT NULL
GROUP BY si.final_result
ORDER BY avg_score DESC;""",
    "gender": """SELECT
    gender, final_result,
    COUNT(*) AS n_students
FROM student_info
GROUP BY gender, final_result
ORDER BY gender, n_students DESC;""",
    "disability": """SELECT
    disability, final_result,
    COUNT(*) AS n_students,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER
        (PARTITION BY disability), 1) AS pct
FROM student_info
GROUP BY disability, final_result;""",
    "early": """SELECT
    si.final_result,
    ROUND(AVG(early_clicks), 0) AS avg_early_clicks
FROM student_info si
JOIN (
    SELECT id_student,
        SUM(sum_click) AS early_clicks
    FROM student_vle
    WHERE date <= 30
    GROUP BY id_student
) e ON si.id_student = e.id_student
GROUP BY si.final_result
ORDER BY avg_early_clicks DESC;""",
}

DATA_MAP = {
    "outcomes": outcomes, "courses": by_course,
    "vle": by_vle, "scores": by_score,
    "gender": by_gender, "disability": by_disability,
    "early": by_early,
}


@app.callback(
    Output("sql-display", "children"),
    Output("sql-results", "children"),
    Input("sql-selector", "value"),
)
def update_sql(val):
    sql_text = SQL_TEXTS.get(val, "")
    df = DATA_MAP.get(val, pd.DataFrame())

    table = dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=12,
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": BRAND, "color": "white", "fontWeight": "bold"},
        style_cell={"fontSize": "13px", "padding": "6px 10px"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#F1F5F9"},
        ],
    )
    return sql_text, table


if __name__ == "__main__":
    app.run(debug=True, port=8050)
