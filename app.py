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

    # Dropdown para selecionar o estudo (Cross-Sectional ou Longitudinal)
    dcc.RadioItems(
        id='study-selector',
        options=[
            {'label': 'Cross-Sectional', 'value': 'cross'},
            {'label': 'Longitudinal', 'value': 'long'}
        ],
        value='cross',
        inline=True
    ),

    # Scrollable content container
    html.Div(id='education-analysis-content', style={'height': '80vh', 'overflowY': 'scroll'})
])

# Callback para atualizar o conteúdo baseado na escolha do estudo
@app.callback(
    Output('education-analysis-content', 'children'),
    [Input('study-selector', 'value')]
)
def update_education_analysis(selected_study):
    if selected_study == 'cross':
        # Gráficos do Cross-Sectional
        fig_educ_dist = px.histogram(df_cross, x="Educ", title="Education Level Distribution")
        fig_mmse_educ = px.box(df_cross, x="Educ", y="MMSE", title="MMSE Scores by Education Level")
        fig_cdr_educ = px.box(df_cross, x="Educ", y="CDR", title="CDR Scores by Education Level")

        return html.Div([
            html.H3("Does Education Affect Alzheimer's Risk? (Cross-Sectional Study)", style={'textAlign': 'center'}),
            html.P("Cross-sectional data suggests that individuals with higher education levels tend to have better cognitive function (higher MMSE) and lower dementia severity (lower CDR)."),
            
            dcc.Graph(figure=fig_educ_dist),
            dcc.Graph(figure=fig_mmse_educ),
            dcc.Graph(figure=fig_cdr_educ),

            html.H4("Statistical Results:"),
            html.P("✅ ANOVA test for MMSE: p-value = 0.00014 (Significant)"),
            html.P("✅ ANOVA test for CDR: p-value = 0.00142 (Significant)"),
            html.P("Conclusion: Higher education levels are associated with better cognitive performance and lower dementia severity.")
        ])

    else:
        # Gráficos do Longitudinal
        fig_mmse_long = px.box(df_long, x="EDUC", y="MMSE", title="MMSE Scores by Education Level Over Time")
        fig_cdr_long = px.box(df_long, x="EDUC", y="CDR", title="CDR Scores by Education Level Over Time")
        fig_mmse_progression = px.line(df_long, x="Visit", y="MMSE", color="EDUC", title="MMSE Progression Over Time by Education Level")

        return html.Div([
            html.H3("Does Education Affect Alzheimer's Progression? (Longitudinal Study)", style={'textAlign': 'center'}),
            html.P("Longitudinal data suggests that individuals with higher education levels tend to maintain higher MMSE scores over time, while those with lower education levels experience more rapid cognitive decline."),
            
            dcc.Graph(figure=fig_mmse_long),
            dcc.Graph(figure=fig_cdr_long),
            dcc.Graph(figure=fig_mmse_progression),

            html.H4("Statistical Results:"),
            html.P(f"✅ Correlation between Education and MMSE: r = 0.1999 (p = 0.00010)"),
            html.P(f"✅ Correlation between Education and CDR: r = -0.1531 (p = 0.00303)"),
            html.P(f"✅ ANOVA for MMSE: p-value = 0.00055 (Significant)"),
            html.P(f"✅ ANOVA for CDR: p-value = 0.00156 (Significant)"),
            html.P(f"✅ Regression: Each additional year of education increases MMSE by 0.2565 points."),
            html.P("Conclusion: Higher education levels slow cognitive decline over time.")
        ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=7860)