import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import scipy.stats as stats
from flask import Flask

# Criar servidor Flask
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Carregar datasets
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Ajustar colunas (para garantir compatibilidade)
df_cross.rename(columns={"Educ": "EDUC"}, inplace=True)

# Criar condição para ambos os datasets
df_cross["Condition"] = df_cross["CDR"].apply(lambda x: "Healthy" if x == 0 else "Alzheimer")
df_long["Condition"] = df_long["Group"]

# Filtrar apenas Nondemented e Demented no longitudinal
df_long = df_long[df_long["Condition"].isin(["Nondemented", "Demented"])]

# Cores para os gráficos
colors_cross = {"Healthy": "#1f77b4", "Alzheimer": "#ff7f0e"}
colors_long = {"Nondemented": "#1f77b4", "Demented": "#ff7f0e"}

# Função para gerar gráficos
def generate_graphs(df, dataset_name, color_map):
    title_prefix = "Cross-Sectional" if dataset_name == "cross" else "Longitudinal"

    fig_age = px.histogram(df, x="Age", color="Condition", title=f"{title_prefix} - Age Distribution", color_discrete_map=color_map)
    fig_educ = px.histogram(df, x="EDUC", color="Condition", title=f"{title_prefix} - Education Level Distribution", color_discrete_map=color_map)
    fig_ses = px.histogram(df, x="SES", color="Condition", title=f"{title_prefix} - Socioeconomic Status Distribution", color_discrete_map=color_map)
    fig_nwbv = px.histogram(df, x="nWBV", color="Condition", title=f"{title_prefix} - Brain Volume (nWBV) Distribution", color_discrete_map=color_map)

    # Criar gráfico de barras percentuais para gênero
    gender_counts = df.groupby(["M/F", "Condition"]).size().reset_index(name="count")
    gender_counts["percentage"] = gender_counts.groupby("M/F")["count"].transform(lambda x: (x / x.sum()) * 100)
    fig_gender = px.bar(gender_counts, x="M/F", y="percentage", color="Condition",
                        title=f"{title_prefix} - Gender Prevalence (%)",
                        barmode="group", color_discrete_map=color_map)

    return fig_age, fig_educ, fig_ses, fig_nwbv, fig_gender

# Função para calcular p-values
def compute_p_values(df):
    age_pval = stats.ttest_ind(df[df["Condition"] == df["Condition"].unique()[0]]["Age"], 
                               df[df["Condition"] == df["Condition"].unique()[1]]["Age"], nan_policy="omit").pvalue
    educ_pval = stats.ttest_ind(df[df["Condition"] == df["Condition"].unique()[0]]["EDUC"], 
                                df[df["Condition"] == df["Condition"].unique()[1]]["EDUC"], nan_policy="omit").pvalue
    ses_pval = stats.ttest_ind(df[df["Condition"] == df["Condition"].unique()[0]]["SES"], 
                               df[df["Condition"] == df["Condition"].unique()[1]]["SES"], nan_policy="omit").pvalue
    nwbv_pval = stats.ttest_ind(df[df["Condition"] == df["Condition"].unique()[0]]["nWBV"], 
                                df[df["Condition"] == df["Condition"].unique()[1]]["nWBV"], nan_policy="omit").pvalue
    # Teste Qui-Quadrado para Gênero
    contingency_table = pd.crosstab(df["M/F"], df["Condition"])
    chi2, p_gender, _, _ = stats.chi2_contingency(contingency_table)

    return age_pval, educ_pval, ses_pval, nwbv_pval, p_gender

# Layout do Dashboard
app.layout = html.Div(
    style={"overflowY": "auto", "height": "100vh", "padding": "10px"},
    children=[
        dcc.Dropdown(
            id="analysis-type",
            options=[
                {"label": "Descriptive Analysis", "value": "descriptive"},
                {"label": "Predictive Analysis", "value": "predictive"}
            ],
            value="descriptive"
        ),
        html.Div(id="output-content")
    ]
)

# Callback para atualizar gráficos
@app.callback(
    Output("output-container", "children"),
    Input("analysis-dropdown", "value")
)
def update_output(analysis_type):
    if analysis_type == "predictive":
        return html.Div([html.H3("Predictive Analysis (Coming Soon!)", style={"text-align": "center"})])

    # Gerar gráficos e p-values para ambos os datasets
    graphs_cross = generate_graphs(df_cross, "cross", colors_cross)
    graphs_long = generate_graphs(df_long, "long", colors_long)

    pvals_cross = compute_p_values(df_cross)
    pvals_long = compute_p_values(df_long)

    # Criar layout dos gráficos
    return html.Div([
        html.H2("Descriptive Analysis - Cross-Sectional", style={"text-align": "center"}),

        html.Div([
            dcc.Graph(figure=graphs_cross[0]), dcc.Graph(figure=graphs_cross[1])
        ], style={"display": "flex", "justify-content": "space-around"}),

        html.Div([
            dcc.Graph(figure=graphs_cross[2]), dcc.Graph(figure=graphs_cross[3])
        ], style={"display": "flex", "justify-content": "space-around"}),

        html.Div([
            dcc.Graph(figure=graphs_cross[4])
        ], style={"text-align": "center"}),

        html.Div([
            html.H4("Statistical Tests (p-values)", style={"text-align": "center"}),
            html.Table([
                html.Tr([html.Th("Variable"), html.Th("p-value")]),
                html.Tr([html.Td("Age"), html.Td(f"{pvals_cross[0]:.5f}")]),
                html.Tr([html.Td("Education Level"), html.Td(f"{pvals_cross[1]:.5f}")]),
                html.Tr([html.Td("Socioeconomic Status"), html.Td(f"{pvals_cross[2]:.5f}")]),
                html.Tr([html.Td("Brain Volume (nWBV)"), html.Td(f"{pvals_cross[3]:.5f}")]),
                html.Tr([html.Td("Gender"), html.Td(f"{pvals_cross[4]:.5f}")])
            ], style={"width": "50%", "margin": "auto", "border": "1px solid black", "text-align": "center"})
        ]),

        html.H2("Descriptive Analysis - Longitudinal", style={"text-align": "center"}),

        html.Div([
            dcc.Graph(figure=graphs_long[0]), dcc.Graph(figure=graphs_long[1])
        ], style={"display": "flex", "justify-content": "space-around"}),

        html.Div([
            dcc.Graph(figure=graphs_long[2]), dcc.Graph(figure=graphs_long[3])
        ], style={"display": "flex", "justify-content": "space-around"}),

        html.Div([
            dcc.Graph(figure=graphs_long[4])
        ], style={"text-align": "center"}),

        html.Div([
            html.H4("Statistical Tests (p-values)", style={"text-align": "center"}),
            html.Table([
                html.Tr([html.Th("Variable"), html.Th("p-value")]),
                html.Tr([html.Td("Age"), html.Td(f"{pvals_long[0]:.5f}")]),
                html.Tr([html.Td("Education Level"), html.Td(f"{pvals_long[1]:.5f}")]),
                html.Tr([html.Td("Socioeconomic Status"), html.Td(f"{pvals_long[2]:.5f}")]),
                html.Tr([html.Td("Brain Volume (nWBV)"), html.Td(f"{pvals_long[3]:.5f}")]),
                html.Tr([html.Td("Gender"), html.Td(f"{pvals_long[4]:.5f}")])
            ], style={"width": "50%", "margin": "auto", "border": "1px solid black", "text-align": "center"})
        ])
    ])

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)