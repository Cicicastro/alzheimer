# Import necessary libraries
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import scipy.stats as stats
import dash_bootstrap_components as dbc

# Load datasets
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Create Condition column
df_cross["Condition"] = df_cross["CDR"].apply(lambda x: "Healthy" if x == 0 else "Alzheimer")
df_long["Condition"] = df_long["Group"]

# Filter only "Nondemented" and "Demented" in longitudinal dataset
df_long = df_long[df_long["Condition"].isin(["Nondemented", "Demented"])]

# Define a consistent color palette
custom_palette = {"Healthy": "#1f77b4", "Alzheimer": "#ff7f0e", "Nondemented": "#1f77b4", "Demented": "#ff7f0e"}

# Flask server setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Function to generate graphs
def generate_graphs(df, dataset_name):
    title_prefix = "Cross-Sectional" if dataset_name == "cross" else "Longitudinal"
    x_labels = {"Educ": "Education Level", "EDUC": "Education Level", "SES": "Socioeconomic Status", "nWBV": "Brain Volume"}

    # Histograms
    fig_age = px.histogram(df, x="Age", color="Condition", title=f"{title_prefix} - Age Distribution", color_discrete_map=custom_palette)
    fig_educ = px.histogram(df, x="Educ" if "Educ" in df.columns else "EDUC", color="Condition", title=f"{title_prefix} - {x_labels.get('Educ', 'Education Level')} Distribution", color_discrete_map=custom_palette)
    fig_ses = px.histogram(df, x="SES", color="Condition", title=f"{title_prefix} - Socioeconomic Status Distribution", color_discrete_map=custom_palette)
    fig_nwbv = px.histogram(df, x="nWBV", color="Condition", title=f"{title_prefix} - Brain Volume (nWBV) Distribution", color_discrete_map=custom_palette)

    # Gender prevalence bar chart
    gender_counts = df.groupby(["M/F", "Condition"]).size().reset_index(name="Count")
    gender_counts["Percentage"] = gender_counts.groupby("M/F")["Count"].transform(lambda x: x / x.sum() * 100)

    fig_gender = px.bar(
        gender_counts, x="M/F", y="Percentage", color="Condition",
        title=f"{title_prefix} - Alzheimer Prevalence by Gender",
        color_discrete_map=custom_palette, barmode="group"
    )

    # Statistical tests
    age_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["Age"], df[df["Condition"] == "Alzheimer"]["Age"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"
    educ_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["Educ"], df[df["Condition"] == "Alzheimer"]["Educ"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"
    ses_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["SES"], df[df["Condition"] == "Alzheimer"]["SES"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"
    nwbv_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["nWBV"], df[df["Condition"] == "Alzheimer"]["nWBV"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"

    # Chi-square test for gender differences
    contingency_table = pd.crosstab(df["M/F"], df["Condition"])
    chi2, p_gender, _, _ = stats.chi2_contingency(contingency_table) if not contingency_table.empty else (None, "N/A", None, None)

    # Format p-values
    p_value_text = f"""
    Age - p-value: {age_pval:.5f}  
    Education Level - p-value: {educ_pval:.5f}  
    Socioeconomic Status - p-value: {ses_pval:.5f}  
    Brain Volume (nWBV) - p-value: {nwbv_pval:.5f}  
    Gender - p-value: {p_gender:.5f}
    """

    return [dcc.Graph(figure=fig_age), dcc.Graph(figure=fig_educ), dcc.Graph(figure=fig_ses),
            dcc.Graph(figure=fig_gender), dcc.Graph(figure=fig_nwbv),
            dbc.Alert(p_value_text, color="light", style={"border": "1px solid black"})]

# Layout of the Dash App
app.layout = dbc.Container([
    html.H1("Alzheimer Data Analysis", style={"textAlign": "center"}),

    dcc.Dropdown(
        id="analysis-dropdown",
        options=[
            {"label": "Descriptive Analysis", "value": "descriptive"},
            {"label": "Predictive Analysis (Coming Soon)", "value": "predictive"}
        ],
        value="descriptive",
        clearable=False,
        style={"width": "50%", "margin": "auto"}
    ),

    html.Div(id="content-container")
], fluid=True)

# Callback to update content based on dropdown selection
@app.callback(
    Output("content-container", "children"),
    [Input("analysis-dropdown", "value")]
)
def update_content(analysis_type):
    if analysis_type == "descriptive":
        return [
            html.H2("Cross-Sectional Data", style={"textAlign": "center"}),
            *generate_graphs(df_cross, "cross"),
            html.H2("Longitudinal Data", style={"textAlign": "center"}),
            *generate_graphs(df_long, "long")
        ]
    elif analysis_type == "predictive":
        return html.H2("Predictive Analysis (Coming Soon)", style={"textAlign": "center"})

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)