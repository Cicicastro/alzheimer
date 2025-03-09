import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from flask import Flask

# Create Flask server (required for Hugging Face Spaces)
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Load datasets (já tratados)
df_cross = pd.read_csv("oasis_cross-sectional-processed.csv")
df_long = pd.read_csv("oasis_longitudinal-processed.csv")

# Define dashboard layout
app.layout = html.Div([
    html.H1("Alzheimer's Disease Dashboard", style={'textAlign': 'center'}),

    # KPIs - Resumo dos Principais Resultados
    html.Div([
        html.Div([html.H3("📌 Correlation (Educ & MMSE)"), html.P("r = 0.1999 (p < 0.001)")], className="kpi"),
        html.Div([html.H3("📌 Correlation (Educ & CDR)"), html.P("r = -0.1531 (p = 0.003)")], className="kpi"),
        html.Div([html.H3("📌 Regression"), html.P("Each additional year of education increases MMSE by 0.2565")], className="kpi"),
    ], className="kpi-container"),

    # Dropdown para selecionar o estudo (Cross-Sectional ou Longitudinal)
    html.Label("Select Study Type:", style={"font-weight": "bold"}),
    dcc.RadioItems(
        id='study-selector',
        options=[
            {'label': '📊 Cross-Sectional', 'value': 'cross'},
            {'label': '📈 Longitudinal', 'value': 'long'}
        ],
        value='cross',
        inline=True
    ),

    # Tabs dentro da aba para separar gráficos de MMSE e CDR
    dcc.Tabs(id="education-tabs", value="mmse", children=[
        dcc.Tab(label="MMSE & Education", value="mmse"),
        dcc.Tab(label="CDR & Education", value="cdr")
    ]),

    # Scrollable content container
    html.Div(id='education-analysis-content', style={'height': '80vh', 'overflowY': 'auto'})
])

# Callback para atualizar o conteúdo baseado na escolha do estudo e aba selecionada
@app.callback(
    Output('education-analysis-content', 'children'),
    [Input('study-selector', 'value'),
     Input('education-tabs', 'value')]
)
def update_education_analysis(selected_study, selected_tab):
    if selected_study == 'cross':
        if selected_tab == "mmse":
            fig_mmse_violin = px.violin(df_cross, x="Educ", y="MMSE", box=True, points="all",
                                        title="MMSE Scores by Education Level (Violin Plot)")
            fig_mmse_scatter = px.scatter(df_cross, x="Educ", y="MMSE", trendline="ols",
                                          title="Education vs MMSE (Scatter Plot)")

            return html.Div([
                html.H3("Does Education Affect Alzheimer's Risk? (Cross-Sectional Study)", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig_mmse_violin),
                dcc.Graph(figure=fig_mmse_scatter),
                html.P("✅ Higher education levels are associated with better cognitive function (higher MMSE)."),
                html.P("✅ ANOVA test for MMSE: p-value = 0.00014 (Significant)")
            ])
        else:
            fig_cdr_bar = px.bar(df_cross.groupby("Educ")["CDR"].mean().reset_index(),
                                 x="Educ", y="CDR", title="Average CDR Score by Education Level")

            return html.Div([
                html.H3("Does Education Affect Dementia Severity? (Cross-Sectional Study)", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig_cdr_bar),
                html.P("✅ Individuals with lower education levels tend to have higher dementia severity (higher CDR)."),
                html.P("✅ ANOVA test for CDR: p-value = 0.00142 (Significant)")
            ])
    else:
        if selected_tab == "mmse":
            fig_mmse_violin_long = px.violin(df_long, x="EDUC", y="MMSE", box=True, points="all",
                                             title="MMSE Scores by Education Level Over Time")
            fig_mmse_line = px.line(df_long, x="Visit", y="MMSE", color="EDUC",
                                    title="MMSE Progression Over Time by Education Level")

            return html.Div([
                html.H3("Does Education Affect Cognitive Decline Over Time? (Longitudinal Study)", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig_mmse_violin_long),
                dcc.Graph(figure=fig_mmse_line),
                html.P("✅ Higher education levels slow cognitive decline over time."),
                html.P("✅ Regression: Each additional year of education increases MMSE by 0.2565 points.")
            ])
        else:
            fig_cdr_bar_long = px.bar(df_long.groupby("EDUC")["CDR"].mean().reset_index(),
                                      x="EDUC", y="CDR", title="Average CDR Score by Education Level Over Time")

            return html.Div([
                html.H3("Does Education Affect Dementia Progression? (Longitudinal Study)", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig_cdr_bar_long),
                html.P("✅ Lower education levels are associated with faster dementia progression."),
                html.P("✅ ANOVA for CDR: p-value = 0.00156 (Significant)")
            ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)