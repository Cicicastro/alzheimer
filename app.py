import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import scipy.stats as stats
from flask import Flask

# Criar servidor Flask
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Carregar os datasets
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Ajustar colunas para consistência
df_cross.rename(columns={"Educ": "EDUC"}, inplace=True)

# Criar variável "Condition"
df_cross["Condition"] = df_cross["CDR"].apply(lambda x: "Healthy" if x == 0 else "Alzheimer")
df_long["Condition"] = df_long["Group"]

# Paleta de cores consistente
custom_palette = {"Healthy": "#1f77b4", "Alzheimer": "#ff7f0e", "Nondemented": "#1f77b4", "Demented": "#ff7f0e"}

# Estilo para corrigir scrolling
app.layout = html.Div(
    style={"overflowY": "auto", "height": "100vh", "padding": "10px"},
    children=[
        dcc.Dropdown(
            id="analysis-type",
            options=[
                {"label": "Descriptive Analysis", "value": "descriptive"},
                {"label": "Predictive Analysis", "value": "predictive"}
            ],
            value="descriptive",
            style={"width": "50%", "margin-bottom": "20px"}
        ),
        html.Div(id="output-content")
    ]
)

# Função para criar gráficos
def generate_graphs(df, dataset_name):
    title_prefix = "Cross-Sectional" if dataset_name == "cross" else "Longitudinal"

    # Criar gráficos idênticos aos anteriores
    fig_age = px.histogram(df, x="Age", color="Condition", title=f"{title_prefix} - Age Distribution", color_discrete_map=custom_palette, nbins=20, histnorm="probability")
    fig_educ = px.histogram(df, x="EDUC", color="Condition", title=f"{title_prefix} - Education Level Distribution", color_discrete_map=custom_palette, nbins=10, histnorm="probability")
    fig_ses = px.histogram(df, x="SES", color="Condition", title=f"{title_prefix} - Socioeconomic Status Distribution", color_discrete_map=custom_palette, nbins=5, histnorm="probability")
    fig_nwbv = px.histogram(df, x="nWBV", color="Condition", title=f"{title_prefix} - Brain Volume (nWBV) Distribution", color_discrete_map=custom_palette, nbins=20, histnorm="probability")

# Gráfico de barras percentual para gênero
gender_counts = df.groupby(["M/F", "Condition"]).size().reset_index(name="Count")

# Ajustar o índice antes de calcular a porcentagem
gender_counts["Percentage"] = gender_counts.groupby("M/F")["Count"].transform(lambda x: x / x.sum() * 100)

fig_gender = px.bar(
    gender_counts, x="M/F", y="Percentage", color="Condition",
    title=f"{title_prefix} - Alzheimer Prevalence by Gender",
    color_discrete_map=custom_palette, barmode="group"
)

    # Calcular p-values
    age_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["Age"], df[df["Condition"] == "Alzheimer"]["Age"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"
    educ_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["EDUC"], df[df["Condition"] == "Alzheimer"]["EDUC"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"
    ses_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["SES"], df[df["Condition"] == "Alzheimer"]["SES"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"
    nwbv_pval = stats.ttest_ind(df[df["Condition"] == "Healthy"]["nWBV"], df[df["Condition"] == "Alzheimer"]["nWBV"], nan_policy="omit").pvalue if "Healthy" in df["Condition"].values else "N/A"

    # Chi-Square test for gender
    contingency_table = pd.crosstab(df["M/F"], df["Condition"])
    chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
    gender_pval = p_value

    # Criar um card para os valores de p-value
    p_value_card = html.Div(
        style={"border": "2px solid black", "padding": "10px", "margin-top": "20px", "width": "50%", "background": "white"},
        children=[
            html.H4(f"{title_prefix} - Statistical Test Results"),
            html.P(f"Age - p-value: {age_pval:.5f}" if age_pval != "N/A" else "Age - Not Available"),
            html.P(f"Education Level - p-value: {educ_pval:.5f}" if educ_pval != "N/A" else "Education Level - Not Available"),
            html.P(f"Socioeconomic Status - p-value: {ses_pval:.5f}" if ses_pval != "N/A" else "Socioeconomic Status - Not Available"),
            html.P(f"Brain Volume (nWBV) - p-value: {nwbv_pval:.5f}" if nwbv_pval != "N/A" else "Brain Volume (nWBV) - Not Available"),
            html.P(f"Gender - p-value: {gender_pval:.5f}")
        ]
    )

    return [
        html.Div([
            html.Div(dcc.Graph(figure=fig_age), style={"width": "48%", "display": "inline-block"}),
            html.Div(dcc.Graph(figure=fig_educ), style={"width": "48%", "display": "inline-block"}),
            html.Div(dcc.Graph(figure=fig_ses), style={"width": "48%", "display": "inline-block"}),
            html.Div(dcc.Graph(figure=fig_nwbv), style={"width": "48%", "display": "inline-block"}),
            html.Div(dcc.Graph(figure=fig_gender), style={"width": "48%", "display": "inline-block"})
        ], style={"display": "flex", "flex-wrap": "wrap", "justify-content": "space-around"}),
        p_value_card
    ]

# Callback para atualizar os gráficos
@app.callback(
    Output("output-content", "children"),
    [Input("analysis-type", "value")]
)
def update_content(selected_analysis):
    if selected_analysis == "descriptive":
        return [
            html.H2("Cross-Sectional Data"),
            *generate_graphs(df_cross, "cross"),
            html.H2("Longitudinal Data"),
            *generate_graphs(df_long, "long")
        ]
    elif selected_analysis == "predictive":
        return html.H3("Predictive Analysis will be implemented soon.")
    return html.H3("Select an analysis type.")

# Rodar o app no Hugging Face Spaces
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)